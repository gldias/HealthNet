from django.conf.urls import url, include
from django.views.generic.base import RedirectView

from . import views

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    url(r'feed/', views.patient_calfeed, name='feed'),
    url(r'docFeed/', views.doctor_calfeed, name='docFeed'),
    url(r'assFeed/', views.assistant_calfeed, name='assFeed'),

    url(r'^pat_register/$', views.patient_register, name='pat_register'),
    url(r'^doc_register/$', views.doctor_register, name='doc_register'),
    url(r'^admin_register/$', views.admin_register, name='admin_register'),
    url(r'^assistant_register/$', views.assistant_register, name='assistant_register'),

    url(r'^$', views.homepage, name='homepage'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),

    url(r'^patient_medical_info', views.patient_medical_info, name='patient_medical_info'),
    url(r'^staff_patient_medical_info', views.staff_patient_medical_info, name='staff_patient_medical_info'),

    url(r'^updatePatient/$', views.update_patient_profile, name='updatePatient'),
    url(r'^newAppt/', views.create_appointment, name='newAppt'),

    url(r'^index/$', views.index, name='index'),
    url(r'^doctor/$', views.doctor_index, name='doctorIndex'),
    url(r'^administrator/$', views.admin_index, name='adminIndex'),
    url(r'^assistant/$', views.assistant_index, name='assistantIndex'),

    url(r'^updateApp/(?P<slug>[0-9]+)/$', views.update_appointment, name='updateApp'),
    url(r'^delApp/(?P<slug>[0-9]+)/$', views.remove_appointment, name='delApp'),
    url(r'testUpload', views.test_result_upload, name='testUploader'),
    url(r'testUpdate/(?P<slug>[0-9]+)/$', views.update_test, name='updateTest'),

    url(r'^newNote/$', views.notes, name='notes'),
    url(r'^viewNotes/$', views.view_notes, name='viewNotes'),
    url(r'^viewNote/(?P<slug>[0-9]+)/$', views.view_note, name='viewNote'),
    url(r'^viewLogs/$', views.view_log, name='viewLog'),
    url(r'^requestTransfer/$', views.request_transfer, name='requestTransfer'),
    url(r'^acceptTransfer/$', views.accept_transfer, name='acceptTransfer'),

    url(r'^addPresc/$', views.add_prescription, name='addPresc'),
    url(r'^admission/$', views.admit_patient, name='admit_patient'),
    url(r'^discharge/$', views.discharge_patient, name='discharge_patient'),
    url(r'^delPresc/(?P<slug>[0-9]+)/$', views.remove_prescription, name='delPresc'),

    url(r'^confirmExport/$', views.confirm_export, name='confirm_export'),
    url(r'^exportInfo/$', views.export_information, name='export_information'),

    url(r'^placeholder/$', views.placeholderPage, name='placeholder'),

    url(r'^favicon\.ico$', favicon_view),

    url(r'^messages/', include('django_messages.urls')),

]
