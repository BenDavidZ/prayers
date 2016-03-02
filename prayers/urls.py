from django.conf.urls import patterns, url

from prayers import views

app_name = 'prayers'
urlpatterns = patterns('',
    # LOGIN URLS
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),

    # PRAYERS URLS
    url(r'^$', views.prayer_index, name='index'),
    url(r'^allprayers/$', views.all_prayers_view, name='all-prayers'),
    url(r'^create/$', views.create_prayer, name='create'),
    url(r'^upload/$', views.upload_prayers, name='upload'),
    url(r'^reset/$', views.reset_unprayed_count, name='reset'),
    url(r'^resources/$', views.resources_view, name='resources'),
    url(r'^active-switch/$', views.active_status_switch, name='active-switch'),
    url(r'^(?P<pk>\d+)/$', views.detail_view, name='detail'),
    url(r'^(?P<pk>\d+)/admin-detail/$', views.admin_detail_view, name='admin-detail'),
    url(r'^(?P<pk>\d+)/assign/$', views.assign_prayer, name='assign'),
    url(r'^(?P<pk>\d+)/support/$', views.forward_tech_support, name='support'),
    # url(r'^(?P<pk>\d+)/update/$', views.UpdateView.as_view(), name='update'),
    url(r'^(?P<pk>\d+)/delete/$', views.delete_prayer_request, name='delete'),
    url(r'^(?P<pk>\d+)/complete/$', views.complete_prayer, name='complete'),
    url(r'^(?P<pk>\d+)/respond/$', views.respond_to_prayer, name='respond'),
    url(r'^allprayers/filter=(?P<id>\d+)/$', views.all_prayers_filter, name='all-prayers-filter'),


    # STAFF URLS
    #url(r'^addstaff/$', views.AddStaffView.as_view(), name='staff-add'),
    url(r'^prayerstaff/$', views.PrayerStaffView.as_view(), name='staff-view'),
    #url(r'^prayerstaff/available/$', views.PrayerStaffAvailableView.as_view(), name='staff-availability'),
    url(r'^prayerstaff/(?P<pk>\d+)/$', views.PrayerStaffDetailView.as_view(), name='staff-detail'),
    url(r'^prayerstaff/(?P<pk>\d+)/staffprayerlist/$', views.staff_prayer_list, name='staff-prayerlist'),
    url(r'^prayerstaff/(?P<pk>\d+)/staffprayerlist/filter=(?P<id>\d+)/$', views.staff_prayer_list, name='staff-prayerlist-filter'),
    url(r'^prayerstaff/(?P<pk>\d+)/activate/$', views.staff_active_toggle, name='staff-activate'),
    #url(r'^prayerstaff/(?P<pk>\d+)/assign/$', views.staff_assign, name='staff-assign'),
    #url(r'^prayerstaff/(?P<pk>\d+)/update$', views.PrayerStaffUpdateView.as_view(), name='staff-update'),
    #url(r'^prayerstaff/(?P<pk>\d+)/delete/$', views.PrayerStaffDeleteView.as_view(), name='staff-delete'),


)
