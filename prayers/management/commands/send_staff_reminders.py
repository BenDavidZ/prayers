from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django_mandrill.mail import MandrillTemplateMail
from prayers.models import Prayer, Employee

from datetime import datetime
import sys

class Command(BaseCommand):
    help = 'Send email to staff members with 1 or more unprayed requests.'

    # check the day of week. only run script on Thrusday (3)
    d = datetime.now()
    if d.weekday() != 3:
        sys.exit()


    def handle(self, *args, **options):

        user_list = User.objects.filter(is_superuser=False).filter(is_active=True).filter(employee__unprayed_count__gt=0)
        self.stdout.write('Script running...')
        for p in user_list:


            upc = p.employee.unprayed_count
            response_text = "%s,<br><br>New prayer requests were assigned to you recently.<br><br>You currently have %s unprayed for requests." % (p.first_name, upc)


            send_mandrill_email('staff-prayer-reminder', [p.email], context={'prayer_response': response_text})
        self.stdout.write('Script finished.')

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








    # def add_arguments(self, parser):
    #     parser.add_argument('prayer_id', nargs='+', type=int)
    #
    #
    # def handle(self, *args, **options):
    #     for prayer_id in options['prayer_id']:
    #         try:
    #             prayer = Prayer.objects.get(pk=prayer_id)
    #         except Prayer.DoesNotExist:
    #             raise CommandError('Prayer "%s" does not exist' % prayer_id)
    #
    #         self.stdout.write(self.style.SUCCESS('Found prayer for "%s"!' % prayer.user_name))
