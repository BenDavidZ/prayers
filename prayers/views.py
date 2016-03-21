from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q

from django.contrib.auth.models import User
from prayers.models import Prayer, Employee, PrayerFile
from prayers.models import PrayerForm, StaffAssignForm, UploadFileForm, PrayerResponseForm, DeleteForm
from django_mandrill.mail import MandrillTemplateMail
import csv
import os

tech_support_email = "info@gotandem.com"
test_email = "wlsupport@backtothebible.org"
rejected_emails = ('messages-noreply@linkedin.com',
                   'invitations@linkedin.com',
                   'MBMcAfeeSaaSReport@mcafee.com',
                   'no-reply@dropboxmail.com',
                   'invitation@whereareyounow.net',
                   )

prayer_text = "Thank you for sharing your prayer request with us.\n\nLifting up the prayer needs of our <i>goTandem</i> community is a key part of our ministry. It's my privilege to pray for you and the concerns that are weighing on your heart.\n\nPlease let us know if you have any other requests.\n\nYour friends at <i>goTandem</i>\n\nP.S. We'd also appreciate your prayers for our ministry as we continue to share God's Word with people all over the world.\n\n"

prayer_text_bttb = "Thank you for sharing your prayer request with us.\n\nLifting up the prayer needs of our Back to the Bible family is a key part of our ministry. It's my privilege to pray for you and the concerns that are weighing on your heart.\n\nPlease let us know if you have any other requests.\n\nYour friends at Back to the Bible\n\nP.S. We'd also appreciate your prayers for our ministry as we continue to share God's Word with people all over the world.\n\n"


def all_prayers_filter(request, id):

    # id 1 = unassigned
    # id 2 = prayed | replied
    # id 3 = prayed | no reply
    # id 4 = not prayed | replied
    # id 5 = not prayed | no reply

    if id == "1":
        prayer_list = Prayer.objects.filter(assigned_to__isnull=True).order_by('received_at')
    elif id == "2":
        prayer_list = Prayer.objects.filter(prayed_at__isnull=False).filter(response_at__isnull=False).order_by('received_at')
    elif id == "3":
        prayer_list = Prayer.objects.filter(prayed_at__isnull=False).filter(response_at__isnull=True).order_by('received_at')
    elif id == "4":
        prayer_list = Prayer.objects.filter(prayed_at__isnull=True).filter(response_at__isnull=False).order_by('received_at')
    elif id == "5":
        prayer_list = Prayer.objects.filter(assigned_to__isnull=False).filter(prayed_at__isnull=True).filter(response_at__isnull=True).order_by('received_at')
    else:
        prayer_list = Prayer.objects.all().order_by('received_at')

    paginator = Paginator(prayer_list, 20)
    page = request.GET.get('page')
    try:
        prayers = paginator.page(page)
    except PageNotAnInteger:
        prayers = paginator.page(1)
    except EmptyPage:
        prayers = paginator.page(paginator.num_pages)
    prayer_staff = request.user
    context = {'prayers': prayers, 'prayer_staff': prayer_staff}

    if request.user.is_superuser:
        return render(request, 'prayers/prayer_allprayers.html', context)
    else:
        return render(request, 'prayers/prayerstaff_prayerlist.html', context)


def update_unprayed_count(prayer_info):
    prayer = prayer_info['prayer']
    staff = prayer_info['staff']

    if prayer.assigned_to.username == prayer.curr_assigned_to:
        increment_unprayed_count(staff)
    else:
        old_staff = User.objects.get(username=prayer.curr_assigned_to)
        decrement_unprayed_count(old_staff)
        increment_unprayed_count(staff)
        prayer.curr_assigned_to = staff.username
    prayer.save()


def increment_unprayed_count(staff):
    staff.employee.unprayed_count += 1
    staff.employee.save()


def decrement_unprayed_count(staff):
    staff.employee.unprayed_count -= 1
    staff.employee.save()


# function to strip out the original outgoing email from an email response
def clean_user_request(user_request):
    user_request = user_request
    divider = "<https://gallery.mailchimp.com/ef39ac07e89950ac4b499945b/images/7e2540a7-e4cd-4398-9afc-d03f844ba291.png>"
    new_request, sep, tail = user_request.partition(divider)
    return new_request


# development function. resets unprayed_count for all users to 0
@login_required
def reset_unprayed_count(request):
    all_staff = User.objects.all()
    for staff in all_staff:
        staff.employee.unprayed_count = 0
        staff.employee.save()

    return HttpResponseRedirect(reverse('prayers:index'))


# development function. toggles active status for all users (except superusers)
@login_required
def active_status_switch(request):
    all_staff = User.objects.filter(is_superuser=False)
    if all_staff[0].is_active:
        for staff in all_staff:
            staff.is_active = False
            staff.save()
    else:
        for staff in all_staff:
            staff.is_active = True
            staff.save()

    return HttpResponseRedirect(reverse('prayers:staff-view'))


def forward_tech_support(request, pk):
    prayer = get_object_or_404(Prayer, id=pk)

    if not prayer.tech_support:
        user_email = prayer.user_email
        user_name = prayer.user_name
        user_request = prayer.user_request
        prayer.tech_support = True
        prayer.save()
        prayer_response = user_name + '\\n' + user_email + '\\n' + user_request
        messages.success(request, 'Message forwarded to Tech Support. Thanks!')
        send_mandrill_email('Prayer Request Response', [tech_support_email], context={'prayer_response': prayer_response})

    return HttpResponseRedirect(reverse('prayers:admin-detail', args=[pk]))


@login_required
def upload_prayers(request):

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            prayer_file = request.FILES['prayer_file']
            try:
                PrayerFile.objects.create(file_name=prayer_file.name)
            except IntegrityError:
                messages.error(request, 'This file already uploaded.')
                return HttpResponseRedirect(reverse('prayers:upload'))

            if prayer_file.name[-4:].lower() != ".csv":
                messages.error(request, 'Invalid file type. Please enter a .csv file.')
                return HttpResponseRedirect(reverse('prayers:upload'))
            else:
                reader = csv.reader(prayer_file, delimiter=',', quotechar='"')
                rownum = 0
                for row in reader:
                    if rownum == 0:
                        if row[0] != "Subject":
                            messages.error(request, 'Invalid data. Please enter properly formatted .csv file.')
                            return HttpResponseRedirect(reverse('prayers:upload'))
                        else:
                            rownum += 1
                    else:
                        if row:
                            # note: because of how outlook exports emails, emails from
                            # internal sources will be skipped because they'll
                            # fail the '@' symbol check. should only be a problem
                            # for prayer requests forwarded from another email box.
                            if row[3] in (rejected_emails) or '@' not in row[3]:
                                rownum += 1
                            else:
                                user_name = row[2]
                                user_email = row[3]
                                user_request = row[1]
                                received_at = row[6]
                                email_subject = row[0]
                                if "goTandem" in row[5]:
                                    originating_ministry = "goTandem"
                                    response_text = prayer_text
                                elif "Bible" in row[5]:
                                    originating_ministry = "Back to the Bible"
                                    response_text = prayer_text_bttb
                                else:
                                    originating_ministry = "Unknown"
                                    response_text = prayer_text_bttb
                                new_request = clean_user_request(user_request)
                                new_prayer = Prayer.objects.create(
                                    email_subject=unicode(email_subject, errors='ignore'),
                                    user_name=unicode(user_name, errors='ignore'),
                                    user_email=user_email,
                                    user_request=unicode(new_request, errors='ignore'),
                                    originating_ministry=originating_ministry,
                                    response_text=response_text,
                                    received_at=received_at
                                )
                                new_prayer.save()
                                rownum += 1

                return HttpResponseRedirect(reverse('prayers:index'))
    else:
        form = UploadFileForm()

    return render(request, 'prayers/prayer_upload.html', {'form': form})


def user_login(request):
    context = RequestContext(request)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('prayers:index'))
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
            return HttpResponseRedirect(reverse('prayers:login'))
    else:
        return render_to_response('prayers/login.html', {}, context)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('prayers:index'))


def prayer_index(request):
    prayer_list = []
    # Create list of all Unassigned Prayers for Superuser
    if request.user.is_superuser:
        prayer_list = Prayer.objects.filter(assigned_to__isnull=True).order_by('received_at')
        prayer_count = prayer_list.count()

    # Create list of all unprayed Prayers assigned to currently logged in user.
    else:
        prayer_list = Prayer.objects.filter(assigned_to__username=request.user.username, prayed_at__isnull=True).order_by('received_at')
        prayer_count = prayer_list.count()

    paginator = Paginator(prayer_list, 10)
    page = request.GET.get('page')
    try:
        prayers = paginator.page(page)
    except PageNotAnInteger:
        prayers = paginator.page(1)
    except EmptyPage:
        prayers = paginator.page(paginator.num_pages)

    context = {'prayers': prayers, 'prayer_count': prayer_count}
    return render(request, 'prayers/index.html', context)


@login_required
def create_prayer(request):
    if request.method == 'POST':
        form = PrayerForm(request.POST)
        if form.is_valid():
            prayer = form.save(commit=False)
            if prayer.originating_ministry == "Back to the Bible":
                prayer.response_text = prayer_text_bttb
            else:
                prayer.response_text = prayer_text
            prayer.save()
            messages.success(request, 'Prayer saved. Thank you.')
            return HttpResponseRedirect(reverse('prayers:index'))
    else:
        form = PrayerForm()
    return render(request, 'prayers/prayer_create.html', {'form': form})


@login_required
def resources_view(request):
    return render(request, 'prayers/prayer_resources.html')


@login_required
def detail_view(request, pk):
    prayer = get_object_or_404(Prayer, id=pk)
    prayer_staff = User.objects.filter(is_superuser=False).filter(is_active=True)
    form = PrayerResponseForm(initial={'response_text': prayer.response_text})
    return render(request, 'prayers/prayer_detail.html', {'prayer': prayer, 'prayer_staff': prayer_staff, 'form': form})


@login_required
def admin_detail_view(request, pk):
    prayer = get_object_or_404(Prayer, id=pk)
    prayer_staff = User.objects.filter(is_superuser=False).filter(is_active=True).exclude(username=prayer.assigned_to).order_by('employee__unprayed_count', 'username')
    search_string = request.GET.get('q')

    return render(request, 'prayers/prayer_detail_admin.html', {'prayer': prayer, 'prayer_staff': prayer_staff, 'search_string': search_string})


@login_required
def delete_prayer_request(request, pk):
    prayer = Prayer.objects.get(id=pk)
    if request.method == 'POST':

        # if the prayer was assigned, decrement unprayed count for assigned user
        # before deleting

        if prayer.assigned_to:
            staff = User.objects.get(username=prayer.assigned_to)
            decrement_unprayed_count(staff)

        prayer.delete()
        messages.success(request, 'Prayer deleted.')
        return HttpResponseRedirect(reverse('prayers:index'))
    else:
        form = DeleteForm()
    return render(request, 'prayers/prayer_confirm_delete.html', {'form': form, 'prayer': prayer})


def assign_prayer(request, pk):
    prayer = get_object_or_404(Prayer, id=pk)

    # assigned_to list presented in template as : username - (x) with x being
    # unprayed_count for user. split off the username from rest when trying
    # to find User.

    staff = get_object_or_404(User, username=request.POST['assigned_to'].split(" ")[0])
    prayer.assigned_to = staff
    prayer.assigned_at = timezone.now()

    # if a prayer is new...
    if not prayer.reassign:
        prayer.reassign = True
        prayer.curr_assigned_to = staff.username
    prayer.save()

    update_unprayed_count({'prayer': prayer, 'staff': staff})
    messages.success(request, 'Request assigned.')

    return HttpResponseRedirect(reverse('prayers:index'))


def all_prayers_view(request):

    if request.GET.get('q'):
        search_string = request.GET.get('q')
        prayers = Prayer.objects.filter(Q(user_name__contains=search_string) | Q(user_email__contains=search_string))
        context = {'prayers': prayers, 'search_string': search_string}
        return render(request, 'prayers/prayer_allprayers.html', context)
    else:

        prayer_list = Prayer.objects.all().order_by('-created_at')
        paginator = Paginator(prayer_list, 20)
        page = request.GET.get('page')
        try:
            prayers = paginator.page(page)
        except PageNotAnInteger:
            prayers = paginator.page(1)
        except EmptyPage:
            prayers = paginator.page(paginator.num_pages)
        context = {'prayers': prayers}
        return render(request, 'prayers/prayer_allprayers.html', context)


def respond_to_prayer(request, pk):
    prayer = get_object_or_404(Prayer, id=pk)

    prayer.response_by = request.POST['username']
    prayer.response_at = timezone.now()
    prayer.response_text = request.POST['response_text'].replace("\n", "<br>").strip()

    # if on Development server, send responses to different email address.

    if os.environ.get('DEV_STAGE') == "Development":
        response_address = "ben.zuehlke@gotandem.com"
    else:
        response_address = prayer.user_email

    if prayer.originating_ministry == 'goTandem':
        send_mandrill_email('goTandem - Prayer Request Response', [response_address], context={'prayer_response': prayer.response_text})
    else:
        send_mandrill_email('BttB - Prayer Request Response', [response_address], context={'prayer_response': prayer.response_text})
    messages.success(request, "Response sent.")
    prayer.save()

    return HttpResponseRedirect(reverse('prayers:detail', args=[pk]))


def send_mandrill_email(template_name, email_to, context=None, curr_site=None):
    if context is None:
        context = {}
    message = {
        'to': [],
        'global_merge_vars': []
    }

    for em in email_to:
        message['to'].append({'email': em})

    for k, v in context.items():
        message['global_merge_vars'].append(
            {'name': k, 'content': v}
        )

    MandrillTemplateMail(template_name, [], message).send()


def complete_prayer(request, pk):
    try:
        p = Prayer.objects.get(pk=pk)
    except Prayer.DoesNotExist:
        raise Http404

    p.prayed_by = p.assigned_to.username
    p.prayed_at = timezone.now()
    p.save()

    staff = User.objects.get(username=p.assigned_to.username)
    staff.employee.unprayed_count = Prayer.objects.filter(assigned_to=staff, prayed_at__isnull=True).count()
    staff.employee.save()
    messages.success(request, 'Prayer marked as complete.')
    return HttpResponseRedirect(reverse('prayers:index'))


class DeleteView(generic.DeleteView):
    model = Prayer
    success_url = reverse_lazy('prayers:index')


class PrayerStaffView(generic.ListView):
    model = User
    template_name = 'prayers/prayerstaff_list.html'
    queryset = User.objects.all().exclude(is_superuser=True).order_by('username')


def staff_prayer_list(request, pk, id=0):

    # id 0 = all prayers for user
    # id 2 = prayed | replied
    # id 3 = prayed | no reply
    # id 4 = not prayed | replied
    # id 5 = not prayed | no reply

    if id == "2":
        prayer_list = Prayer.objects.filter(assigned_to=pk).filter(prayed_at__isnull=False).filter(response_at__isnull=False).order_by('received_at')
    elif id == "3":
        prayer_list = Prayer.objects.filter(assigned_to=pk).filter(prayed_at__isnull=False).filter(response_at__isnull=True).order_by('received_at')
    elif id == "4":
        prayer_list = Prayer.objects.filter(assigned_to=pk).filter(prayed_at__isnull=True).filter(response_at__isnull=False).order_by('received_at')
    elif id == "5":
        prayer_list = Prayer.objects.filter(assigned_to=pk).filter(prayed_at__isnull=True).filter(response_at__isnull=True).order_by('received_at')
    else:
        prayer_list = Prayer.objects.filter(assigned_to=pk).order_by('-created_at')

    prayer_staff = User.objects.get(id=pk)

    paginator = Paginator(prayer_list, 15)
    page = request.GET.get('page')
    try:
        prayers = paginator.page(page)
    except PageNotAnInteger:
        prayers = paginator.page(1)
    except EmptyPage:
        prayers = paginator.page(paginator.num_pages)

    context = {'prayers': prayers, 'prayer_staff': prayer_staff}
    return render(request, 'prayers/prayerstaff_prayerlist.html', context)


def staff_active_toggle(request, pk):
    staff = User.objects.get(id=pk)
    if staff.is_active:
        staff.is_active = False
    else:
        staff.is_active = True
    staff.save()
    return HttpResponseRedirect(reverse('prayers:staff-view'))


class PrayerStaffDetailView(generic.DetailView):
    model = User
    template_name = 'prayers/prayerstaff_detail.html'
