import json
import os
import sys

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext

from healthNet.forms import AppointmentForm, PatientForm, DoctorForm, AdminForm, ContactInfoForm, MedicalNotesForm, \
    TestResultsForm, PrescriptionForm, AssistantForm, AdmissionForm, DischargeForm, RequestTransferForm, \
    AcceptTransferForm
from healthNet.forms import UserForm, MedicalNotesPatientSelectForm
from healthNet.logger import SystemLog
from .models import Doctor, Appointment, Prescription, TestResults, MedicalNotes, Patient, ContactInformation


# Create your views here.


def placeholderPage(request):
    # return HttpResponse("Hello, world. You're at the HealthNet index.")

    add_log(request.user, "viewed the placeholder page")
    return render(request, 'placeholder(TEMPORARY).html')


def homepage(request):
    # return HttpResponse("Hello, world. You're at the HealthNet index.")

    return render(request, 'home.html')


def index(request):
    # return HttpResponse("Hello, world. You're at the HealthNet index.")
    context = RequestContext(request)

    user = User.objects.get(pk=request.user.id)

    is_doctor = False
    is_assist = False
    is_admin = False
    is_patient = False
    is_super = False

    if user in User.objects.filter(groups__name__iexact="doctors"):
        is_doctor = True
    elif user in User.objects.filter(groups__name__iexact="assistants"):
        is_assist = True
    elif user in User.objects.filter(groups__name__iexact="admins"):
        is_admin = True
    elif user in User.objects.filter(groups__name__iexact="patients"):
        is_patient = True
    elif user.is_staff:
        is_super = True

    return render_to_response('index.html', {'is_doctor': is_doctor, 'is_assist': is_assist, 'is_admin': is_admin, 'is_patient': is_patient, 'is_super': is_super}
                              , context)


def doctor_index(request):
    add_log(request.user, "viewed the doctor index page")
    return render(request, 'doctorIndex(DEPRECIATED).html')


@login_required
def admin_index(request):
    add_log(request.user, "viewed the admin index page")
    return render(request, 'adminIndex(DEPRECIATED).html')


@login_required
def assistant_index(request):
    add_log(request.user, "viewed the assistant index page")
    return render(request, 'assistantIndex(DEPRECIATED).html')


################################
##REGISTRATION FOR A PATIENT####
################################
def patient_register(request):
    # Get the request's context
    context = RequestContext(request)

    # Boolean value that tells you if registration was successful
    # Default is False but turns into True when the registration is complete
    registered = False

    # If it's HTTP POST, we want to process data
    if request.method == 'POST':
        # Attempt to grab info from form
        user_form = UserForm(data=request.POST)
        patient_form = PatientForm(data=request.POST)
        contact_info_form = ContactInfoForm(data=request.POST)

        # If two forms are valid...

        if user_form.is_valid() and patient_form.is_valid() and contact_info_form.is_valid():
            # Save user's form data to database
            user = user_form.save(commit=False)

            # Hash password with set_password method
            # After hashing, we can update the user object
            user.set_password(user.password)
            user.save()

            # Now sort out Patient instance
            # Since we set user attributes ourselves, we set commit=False
            # This delays saving the model until we're ready to avoid integrity problems
            patient = patient_form.save(commit=False)
            patient.user = user
            #patient.hospital = Doctor.objects.get(user=).hospital

            #Sets the patients hospital equal to the primary_care_physician's hospital
            #From all the users, get the doctors. From the doctors, get the doctor who has
            #   the same id as the patient's primary_care_physician. From that doctor,
            #   we can get the correct hospital
            patient.hospital = User.objects.filter(groups__name__iexact="doctors").get(
                doctor__id=user.patient.primary_care_physician_id).doctor.hospital

            patient.save()

            contact_info = contact_info_form.save(commit=False)
            contact_info.user = user
            contact_info.save()

            # Update our variable to tell the template registration was successful
            registered = True

            # Adds patient user to 'patients' group

            group, create = Group.objects.get_or_create(name='patients')
            user.groups.add(group)

            # patient.save()

            add_log(user, "registered in the database, as a patient.")

        # Invalid form or forms?
        # Print problems to user and to terminal
        else:
            print(user_form.errors, patient_form.errors, contact_info_form.errors)

    # Not an HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input
    else:
        user_form = UserForm()
        patient_form = PatientForm()
        contact_info_form = ContactInfoForm()

    # Render template depending on the context
    return render_to_response(
        'register.html',
        {'user_form': user_form, 'patient_form': patient_form, 'contact_info_form': contact_info_form,
         'registered': registered},
        context)


################################
##REGISTRATION FOR A DOCTOR####
################################
@login_required
def doctor_register(request):
    # Get the request's context
    context = RequestContext(request)

    # Boolean value that tells you if registration was successful
    # Default is False but turns into True when the registration is complete
    registered = False

    # If it's HTTP POST, we want to process data
    if request.method == 'POST':
        # Attempt to grab info from form
        user_form = UserForm(data=request.POST)
        doctor_form = DoctorForm(data=request.POST)

        # If two forms are valid...
        if user_form.is_valid() and doctor_form.is_valid():
            # Save user's form data to database
            user = user_form.save()

            # Hash password with set_password method
            # After hashing, we can update the user object
            user.set_password(user.password)
            user.save()

            # Now sort out Patient instance
            # Since we set user attributes ourselves, we set commit=False
            # This delays saving the model until we're ready to avoid integrity problems
            doctor = doctor_form.save(commit=False)
            doctor.user = user

            # Now we save the Patient model instance
            doctor.save()

            # Update our variable to tell the template registration was successful
            registered = True

            # Adds patient user to 'patients' group
            group, create = Group.objects.get_or_create(name='doctors')
            user.groups.add(group)

            add_log(user, "has been registered in the database, as a doctor.")

        # Invalid form or forms?
        # Print problems to user and to terminal
        else:
            print(user_form.errors, doctor_form.errors)

    # Not an HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input
    else:
        user_form = UserForm()
        doctor_form = DoctorForm()

    # Render template depending on the context
    return render_to_response(
        'doctorRegister.html',
        {'user_form': user_form, 'doctor_form': doctor_form, 'registered': registered},
        context)


################################
##REGISTRATION FOR AN ADMIN####
################################
@login_required
def admin_register(request):
    # Get the request's context
    context = RequestContext(request)

    # Boolean value that tells you if registration was successful
    # Default is False but turns into True when the registration is complete
    registered = False

    # If it's HTTP POST, we want to process data
    if request.method == 'POST':
        # Attempt to grab info from form
        user_form = UserForm(data=request.POST)
        admin_form = AdminForm(data=request.POST)

        # If two forms are valid...
        if user_form.is_valid() and admin_form.is_valid():
            # Save user's form data to database
            user = user_form.save()

            # Hash password with set_password method
            # After hashing, we can update the user object
            user.set_password(user.password)
            user.save()

            # Now sort out Patient instance
            # Since we set user attributes ourselves, we set commit=False
            # This delays saving the model until we're ready to avoid integrity problems
            admin = admin_form.save(commit=False)
            admin.user = user

            # Now we save the Patient model instance
            admin.save()

            # Update our variable to tell the template registration was successful
            registered = True

            # Adds patient user to 'patients' group
            group, create = Group.objects.get_or_create(name='admins')
            user.groups.add(group)

            add_log(user, "has been registered in the database, as an administrator.")

        # Invalid form or forms?
        # Print problems to user and to terminal
        else:
            print(user_form.errors, admin_form.errors)

    # Not an HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input
    else:
        user_form = UserForm()
        admin_form = AdminForm()

    # Render template depending on the context
    return render_to_response(
        'adminRegister.html',
        {'user_form': user_form, 'admin_form': admin_form, 'registered': registered},
        context)


################################
##REGISTRATION FOR AN ADMIN####
################################
@login_required
def assistant_register(request):
    # Get the request's context
    context = RequestContext(request)

    # Boolean value that tells you if registration was successful
    # Default is False but turns into True when the registration is complete
    registered = False

    # If it's HTTP POST, we want to process data
    if request.method == 'POST':
        # Attempt to grab info from form
        user_form = UserForm(data=request.POST)
        assistant_form = AssistantForm(data=request.POST)

        # If two forms are valid...
        if user_form.is_valid() and assistant_form.is_valid():
            # Save user's form data to database
            user = user_form.save()

            # Hash password with set_password method
            # After hashing, we can update the user object
            user.set_password(user.password)
            user.save()

            # Now sort out Patient instance
            # Since we set user attributes ourselves, we set commit=False
            # This delays saving the model until we're ready to avoid integrity problems
            assistant = assistant_form.save(commit=False)
            assistant.user = user

            # Now we save the Patient model instance
            assistant.save()

            # Update our variable to tell the template registration was successful
            registered = True

            # Adds patient user to 'patients' group
            group, create = Group.objects.get_or_create(name='assistants')
            user.groups.add(group)

            add_log(user, "has been registered in the database, as an assistant.")

        # Invalid form or forms?
        # Print problems to user and to terminal
        else:
            print(user_form.errors, assistant_form.errors)

    # Not an HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input
    else:
        user_form = UserForm()
        assistant_form = AssistantForm()

    # Render template depending on the context
    return render_to_response(
        'assistantRegister.html',
        {'user_form': user_form, 'assistant_form': assistant_form, 'registered': registered},
        context)


# This method allows the user to update their information, provided
# that they are already logged in
###
###MAKE SURE TO AUTOPOPULATE THE FIELDS (GET USER PROFILE)
###
###ALSO MAKE SURE TO ALLOW MODIFICATION FOR USERNAME, PASSWORD, AND EMAIL
###
@login_required
def update_patient_profile(request):
    # Get request's context
    context = RequestContext(request)

    # Boolean value that tells you if update was successful
    # Turns into True once update is complete
    successful = False

    # Get user
    # user = User.objects.get(pk=request.user.id)
    user = User.objects.get(pk=request.user.id)

    # Get patient
    patient = user.patient

    # If it's HTTP POST, we want to process data through a form
    if request.method == 'POST':
        # user_update_form = UserForm(request.POST, instance=user)
        update_form = PatientForm(request.POST, instance=patient)
        if update_form.is_valid():  # and user_update_form.is_valid():

            # user_update = user_update_form.save()
            # user_update.set_password(user.password)
            # user_update.save()

            update = update_form.save(commit=True)
            update.user = user
            update.save()

            successful = True

            add_log(user, "updated their account information in the database")
    else:
        # user_update_form = UserForm(instance=user)
        update_form = PatientForm(instance=patient)

    return render_to_response('update.html',
                              {'update_form': update_form, 'successful': successful},
                              context)


def user_login(request):
    # Get context for user's request
    context = RequestContext(request)

    # If request is an HTTP POST, try to pull out relevant information
    if request.method == 'POST':
        # Gather username and password provided by user
        # This information is obtained from the Login form
        username = request.POST['username']
        password = request.POST['password']

        # Use Django to see if username/password combo is valid
        # Returns a User object if it is
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct
        # If None, no user with matching credentials was found
        if user:
            # Is the account active? Could have been disabled
            if user.is_active:
                # If account is valid and active, we can log the user in
                # We send the user to the calendar page
                login(request, user)

                add_log(user, "logged in")

                # if user in User.objects.filter(groups__name__iexact="doctors"):
                #     return HttpResponseRedirect('/healthNet/doctor/')
                # elif user in User.objects.filter(groups__name__iexact="admins") or user.is_staff:
                #     return HttpResponseRedirect('/healthNet/administrator/')
                # elif user in User.objects.filter(groups__name__iexact="assistants"):
                #     return HttpResponseRedirect('/healthNet/assistant/')
                # else:
                return HttpResponseRedirect('/healthNet/index/')  # user is a patient
            else:
                # An inactive account was used. No logging in
                return HttpResponse("Your account was disabled")
        else:
            # Bad login details, so we can't log the user in
            print('Invalid login details')
            return HttpResponse("Invalid login details supplied.")

    # If request is not a HTTP POST, display the login form
    # This scenario would most likely be a HTTP GET
    else:
        # No context variables to pass to the template system, hence the
        # blank directory object....
        return render_to_response('login.html', {}, context)


# Use the login_required decorator to ensure that only those logged in can access this view
@login_required
def user_logout(request):
    add_log(request.user, "logged out")

    # Since we know the user is logged in, we can just log them out
    logout(request)

    # Take user back to homepage
    return HttpResponseRedirect('/healthNet/')


@login_required
def notes(request):
    # Get the request's context
    context = RequestContext(request)

    # Boolean value that tells you if registration was successful
    # Default is False but turns into True when the registration is complete

    # doctor = Doctor.objects.filter(user_id=request.user.id)
    doctor = Doctor.objects.get(user_id=request.user.id)

    complete = False

    # If it's HTTP POST, we want to process data
    if request.method == 'POST':
        # Attempt to grab info from form
        medical_notes_form = MedicalNotesForm(data=request.POST)
        # If the forms are valid...
        if medical_notes_form.is_valid():

            # if medical_notes_form.is_valid():
            medical_notes = medical_notes_form.save(commit=False)
            medical_notes.doctor_id = doctor.user_id
            medical_notes.save()

            complete = True

            add_log(doctor.user,
                    "added new doctors notes to {}")  # .format(medical_notes_form.general_notes_form.patient))

        # Invalid form or forms?
        # Print problems to user and to terminal
        else:
            print(medical_notes_form.errors)

    # Not an HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input
    else:
        medical_notes_form = MedicalNotesForm()

    # Render template depending on the context

    return render(request, 'medicalNotes.html',
                  {'complete': complete, 'medical_notes_form': medical_notes_form},
                  context)


@login_required
def view_note(request, slug):
    user = User.objects.get(pk=request.user.id)
    note = MedicalNotes.objects.get(pk=slug)
    add_log(user, 'viewed notes')
    return render(request, 'medicalNoteView.html', {'note': note, 'slug': slug})


@login_required
def view_notes(request):
    doctor = Doctor.objects.get(user_id=request.user.id)

    complete = False
    patient_notes = None

    if request.method == 'POST':
        medical_notes_patient_select_form = MedicalNotesPatientSelectForm(data=request.POST)
        if medical_notes_patient_select_form.is_valid():
            medical_notes_patient_select = medical_notes_patient_select_form.save(commit=False)
            patient_ob = medical_notes_patient_select.patient
            # patient_ob = medical_notes_patient_select_form.cleaned_data.get(Patient)
            patient_notes = MedicalNotes.objects.filter(patient__user_id__exact=patient_ob.user.id)
            complete = True
            add_log(doctor.user, "viewed the medical notes for {}".format(patient_ob))
        else:
            print(medical_notes_patient_select_form.errors)
    else:
        medical_notes_patient_select_form = MedicalNotesPatientSelectForm()
        # patient_ob = medical_notes_patient_select_form.patient
    return render(request, 'medicalNotesView.html',
                  {'complete': complete,
                   'medical_notes_patient_select_form': medical_notes_patient_select_form,
                   'patient_notes': patient_notes})


def confirm_export(request):
    return render_to_response('exportConfirm.html', {}, context_instance=RequestContext(request))


def export_information(request):
    def confirm(request):

        currUser = User.objects.get(pk=request.user.id)

        patient = Patient.objects.filter(user_id__exact=request.user.id)[0]
        file = '{}/healthNet/export/{}.txt'.format(os.path.dirname(sys.modules['__main__'].__file__),
                                                   request.user.email.__str__())
        prescriptions = []
        for prescription in patient.prescription_set.all():
            prescriptions = prescriptions + [prescription.export()]

        # make sure that patients can't see unreleased test results
        test_results = []
        for testResult in patient.testresults_set.all():
            if testResult.is_released:
                test_results = test_results + [testResult.export()]

        appointments = []
        for appointment in patient.appointment_set.all():
            appointments = appointments + [appointment.export()]

        with open(file, 'w') as outfile:
            outfile.write(
                '{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}' \
                    .format(patient.user.username,
                            patient.user.email,
                            patient.user.last_name,
                            patient.user.first_name,
                            patient.user.password,
                            patient.user.contactinformation.street_address,
                            patient.user.contactinformation.city_or_town,
                            patient.user.contactinformation.region,
                            patient.user.contactinformation.country,
                            patient.user.contactinformation.zipcode,
                            patient.user.contactinformation.phone_number,
                            patient.user.contactinformation.emergency_contact_1,
                            patient.user.contactinformation.emergency_contact_2,
                            patient.dob,
                            patient.height,
                            patient.weight,
                            patient.primary_care_physician.user_id,
                            patient.insurance_provider,
                            patient.insurance_number,
                            prescriptions,
                            test_results,
                            appointments
                            ))
            # Prevent html page from displaying anything

        for filename in os.listdir('{}/healthNet/import'.format(os.path.dirname(sys.modules['__main__'].__file__))):
            filename = '{}/healthNet/import/{}'.format(os.path.dirname(sys.modules['__main__'].__file__), filename)
            # if os.path.isfile(filename):
            csv = []
            file = open(filename, 'r')
            for line in file:
                csv = csv + [line.strip('\n')]

            if Patient.objects.filter(user__username=csv[0]).__len__() == 0:
                user = User(username=csv[0],
                            email=csv[1],
                            last_name=csv[2],
                            first_name=csv[3],
                            password=csv[4]
                            )

                user.save()

                patient = Patient(user=user,
                                  dob=csv[13],
                                  height=csv[14],
                                  weight=csv[15],
                                  primary_care_physician=Doctor.objects.filter(user_id__exact=csv[16])[0],
                                  insurance_provider=csv[17],
                                  insurance_number=csv[18]
                                  )

                patient.save()

                contact_info = ContactInformation(user=user,
                                                  street_address=csv[5],
                                                  city_or_town=csv[6],
                                                  region=csv[7],
                                                  country=csv[8],
                                                  zipcode=csv[9],
                                                  phone_number=csv[10],
                                                  emergency_contact_1=csv[11],
                                                  emergency_contact_2=csv[12]
                                                  )

                contact_info.save()

                group, create = Group.objects.get_or_create(name='patients')
                user.groups.add(group)

                # if csv[19].split(', ').__len__() > 1:
                #     for prescripts in csv[19].split(', '):
                #         prescript = prescripts.strip('[').strip(']').strip("'").split('_')
                #         new_prescript = Prescription(patient_name=prescript[0],
                #                                      drug_name=prescript[1],
                #                                      dosage=prescript[2],
                #                                      reason=prescript[3],
                #                                      doctor=Doctor.objects.filter(user_id__exact=prescript[4])[0]
                #                                      )
                #         new_prescript.save()

                # if csv[20].split(', ').__len__() > 1:
                #     for test_results in csv[20].split(', '):
                #         test_result = test_results.strip('[').strip(']').strip("'").split('_')
                #         new_test_results = TestResults(description=test_result[0],
                #                                        document=os.path,
                #                                        uploaded_at=test_result[2],
                #                                        patient=Patient.objects.filter(user_id__exact=test_result[3])[0],
                #                                        is_released=test_result[4],
                #                                        doctor=Doctor.objects.filter(user_id__exact=test_result[5])[0]
                #                                        )
                #         new_test_results.save()
                #         # TODO Fix document lookup

                # if csv[21].split(', ').__len__() > 1:
                #     for appointments in csv[21].split(', '):
                #         appointment = appointments.strip('[').strip(']').strip("'").split('_')
                #         print(user.id)
                #         print(Patient.objects.filter(user_id__exact=user.id))
                #         new_appointment = Appointment(appointment_name=appointment[0],
                #                                       doctor=Doctor.objects.filter(user_id__exact=appointment[1])[0],
                #                                       patient=Patient.objects.filter(user_id__exact=user.id)[0],
                #                                       assistant=Assistant.objects.filter(user_id__exact=appointment[2])[
                #                                           0],
                #                                       start_time=appointment[3],
                #                                       start_date=appointment[4],
                #                                       end_time=appointment[5],
                #                                       end_date=appointment[6],
                #                                       current_user=User.objects.filter(username__exact=appointment[7])[
                #                                           0]
                #                                       )
                #         new_appointment.save()

                add_log(currUser, 'ran import/export')

        return ''

    complete = False

    def check():
        if True:
            complete = confirm()

    return render_to_response('exportInfo.html',
                              {'complete': complete, 'check': check, 'confirm': confirm(request)},
                              context_instance=RequestContext(request))


@login_required
def patient_calfeed(request):
    user = User.objects.get(pk=request.user.id)
    appointment_list = user.appointment_set.all()

    json_list = []

    add_log(user, "viewed their calendar")

    for appointment in appointment_list:
        appointment_id = appointment.id
        title = appointment.appointment_name
        start = appointment.start_date.isoformat() + 'T' + appointment.start_time.isoformat()
        end = appointment.end_date.isoformat() + 'T' + appointment.end_time.isoformat()
        # url = appointment.

        json_entry = {'title': title, 'id': appointment_id, 'start': start, 'end': end, 'allDay': False}
        json_list.append(json_entry)

    return HttpResponse(json.dumps(json_list), content_type='application/json')


@login_required
def doctor_calfeed(request):
    user = User.objects.get(pk=request.user.id)
    appointment_list = user.doctor.appointment_set.all()

    json_list = []

    add_log(user, "viewed their calendar")

    for appointment in appointment_list:
        appointment_id = appointment.id
        title = appointment.appointment_name
        start = appointment.start_date.isoformat() + 'T' + appointment.start_time.isoformat()
        end = appointment.end_date.isoformat() + 'T' + appointment.end_time.isoformat()
        # url = appointment.

        json_entry = {'title': title, 'id': appointment_id, 'start': start, 'end': end, 'allday': 'false'}
        json_list.append(json_entry)

    return HttpResponse(json.dumps(json_list), content_type='application/json')


def get_assistant_appointment_list(user):
    same_hospital_doctors = User.objects.filter(groups__name__iexact="doctors").filter(
        doctor__hospital_id=user.assistant.hospital_id)

    appointment_list = []
    for docUser in same_hospital_doctors:
        for appt in docUser.doctor.appointment_set.all():
            appointment_list.append(appt)
    return appointment_list


@login_required
def assistant_calfeed(request):
    user = User.objects.get(pk=request.user.id)
    appointment_list = get_assistant_appointment_list(user)

    json_list = [{'title': 'test', 'id': '0', 'start': '2016-09-30'}]

    add_log(user, "viewed their calendar")

    for appointment in appointment_list:
        appointment_id = appointment.id
        title = appointment.appointment_name
        start = appointment.start_date.isoformat() + 'T' + appointment.start_time.isoformat()
        end = appointment.end_date.isoformat() + 'T' + appointment.end_time.isoformat()
        # url = appointment.

        json_entry = {'title': title, 'id': appointment_id, 'start': start, 'end': end, 'allday': 'false'}
        json_list.append(json_entry)

    return HttpResponse(json.dumps(json_list), content_type='application/json')


@login_required
def create_appointment(request):
    # Get the request's context
    context = RequestContext(request)

    # Boolean value that tells you if registration was successful
    # Default is False but turns into True when the registration is complete
    appointment_created = False

    # Get user
    user = User.objects.get(pk=request.user.id)

    # Gets the type of user creating the appointment in the form of a boolean
    # Is used in the createAppt.html file to redirect to correct page after a successful creation
    # of an appointment
    is_doctor = False
    is_assist = False

    if user in User.objects.filter(groups__name__iexact="doctors"):
        is_doctor = True
    elif user in User.objects.filter(groups__name__iexact="assistants"):
        is_assist = True
    # If it's neither, then it is a patient

    # If it's HTTP POST, we want to process data
    if request.method == 'POST':
        # Attempt to grab info from form
        appointment_form = AppointmentForm(data=request.POST)

        # If two forms are valid...
        if appointment_form.is_valid():
            # Save user's form data to database
            appointment = appointment_form.save()
            appointment.current_user = user

            appointment.save()

            # Update our variable to tell the template registration was successful
            appointment_created = True

            add_log(user,
                    "created {} in their calendar.".format(appointment))

        # Invalid form or forms?
        # Print problems to user and to terminal
        else:
            print(appointment_form.errors)

    # Not an HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input
    else:
        appointment_form = AppointmentForm()

    # Render template depending on the context
    return render_to_response(
        'createAppt.html',
        {'appointment_form': appointment_form, 'appointment_created': appointment_created,
         'is_doctor': is_doctor, 'is_assist': is_assist}, context)


@login_required
def update_appointment(request, slug):
    context = RequestContext(request)

    # Boolean value that tells you if update was successful
    # Turns into True once update is complete
    successful = False

    # Get user
    user = User.objects.get(pk=request.user.id)

    # Gets the type of user creating the appointment in the form of a boolean
    # Is used in the updateAppt.html file to redirect to correct page after a successful creation
    # of an appointment
    is_doctor = False
    is_assist = False

    if user in User.objects.filter(groups__name__iexact="doctors"):
        is_doctor = True
    elif user in User.objects.filter(groups__name__iexact="assistants"):
        is_assist = True
    # If it's neither, then it is a patient

    # Declare appointment variable
    appointment = Appointment()

    # Gets type of user
    # If we know the type of the user, it is easier to get the correct set of appointments
    if is_doctor:
        appointment = user.doctor.appointment_set.get(pk=slug)
    elif is_assist:
        appointment_list = get_assistant_appointment_list(user)
        for appt in appointment_list:
            print(appt.pk == int(slug))
            if appt.pk == int(slug):
                appointment = appt
                print(appointment)
                break
    else:  # user is a patient
        appointment = user.appointment_set.get(pk=slug)

    # If it's HTTP POST, we want to process data through a form
    if request.method == 'POST':
        # user_update_form = UserForm(request.POST, instance=user)
        update_app_form = AppointmentForm(request.POST, instance=appointment)
        if update_app_form.is_valid():  # and user_update_form.is_valid():

            # user_update = user_update_form.save()
            # user_update.set_password(user.password)
            # user_update.save()

            update_app = update_app_form.save(commit=False)
            update_app.current_user = user
            update_app.save()
            successful = True

            add_log(user, "updated {} in their calendar.".format(appointment))
    else:
        # user_update_form = UserForm(instance=user)
        update_appForm = AppointmentForm(instance=appointment)

    return render_to_response('updateApp.html',
                              {'update_appForm': update_appForm, 'appointment': appointment, 'successful': successful,
                               'is_doctor': is_doctor, 'is_assist': is_assist},
                              context)


@login_required
def remove_appointment(request, slug):
    # Get user
    user = User.objects.get(pk=request.user.id)

    # Gets the type of user creating the appointment in the form of a boolean
    # Is used in the delAppt.html file to redirect to correct page after a successful creation
    # of an appointment
    is_doctor = False
    is_assist = False

    if user in User.objects.filter(groups__name__iexact="doctors"):
        is_doctor = True
    elif user in User.objects.filter(groups__name__iexact="assistants"):
        is_assist = True
    # If it's neither, then it is a patient

    # Get appointment and delete it

    appointment = Appointment()
    if is_doctor:
        appointment = user.doctor.appointment_set.get(pk=slug)
    elif is_assist:
        appointment_list = get_assistant_appointment_list(user)
        for appt in appointment_list:
            # print(appt.pk)
            # print(slug)
            print(appt.pk == int(slug))
            if appt.pk == int(slug):
                appointment = appt
                print(appointment)
                break
    else:  # user is a patient
        appointment = user.appointment_set.get(pk=slug)

    add_log(user, "removed {} from their calendar.".format(appointment))

    appointment.delete()

    return render(request, 'delApp.html', {'is_doctor': is_doctor, 'is_assist': is_assist})


def test_result_upload(request):  # TODO Fix address where site is looking for images.
    user = User.objects.get(pk=request.user.id)
    if request.method == 'POST':
        form = TestResultsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            add_log(user, 'uploaded test results')
            return redirect('index')

    else:
        form = TestResultsForm()

    return render(request, 'testUploader.html', {
        'form': form
    })


@login_required
def add_prescription(request):
    # Get the request's context
    context = RequestContext(request)

    # Boolean value that tells you if registration was successful
    # Default is False but turns into True when the registration is complete
    prescription_created = False

    # Get user
    user = User.objects.get(pk=request.user.id)

    # If it's HTTP POST, we want to process data
    if request.method == 'POST':
        # Attempt to grab info from form
        prescription_form = PrescriptionForm(data=request.POST)

        # If two forms are valid...
        if prescription_form.is_valid():
            # Save user's form data to database
            prescription = prescription_form.save()
            prescription.current_user = user

            prescription.save()

            # Update our variable to tell the template registration was successful
            prescription_created = True

            add_log(user, "prescribed {} of {} for {}".format(prescription.dosage, prescription.drug_name,
                                                              prescription.patient_name))

        # Invalid form or forms?
        # Print problems to user and to terminal
        else:
            print(prescription_form.errors)

    # Not an HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input
    else:
        prescription_form = PrescriptionForm()

    # Render template depending on the context
    return render_to_response(
        'addPresc.html',
        {'prescription_form': prescription_form, 'prescription_created': prescription_created}, context)


def patient_medical_info(request):
    user = User.objects.get(pk=request.user.id)
    context = RequestContext(request)
    test_results = TestResults.objects.filter(patient_id=user.patient.id)
    prescriptions = Prescription.objects.filter(patient_name_id=user.patient.id)

    is_doctor = False
    is_assist = False
    is_admin = False

    if user in User.objects.filter(groups__name__iexact="doctors"):
        is_doctor = True
    elif user in User.objects.filter(groups__name__iexact="assistants"):
        is_assist = True

    return render_to_response('patientMedInfo.html', {'test_results': test_results,
                                                      'prescriptions': prescriptions,
                                                      'is_doctor': is_doctor,
                                                      'is_assist': is_assist,},
                              context_instance=RequestContext(request))


def staff_patient_medical_info(request):
    user = User.objects.get(pk=request.user.id)
    context = RequestContext(request)
    user = User.objects.get(pk=request.user.id)
    test_results = TestResults.objects.all()
    prescriptions = Prescription.objects.all()
    patient_prescriptions = []

    is_doctor = False
    is_assist = False
    is_admin = False

    if user in User.objects.filter(groups__name__iexact="doctors"):
        is_doctor = True
    elif user in User.objects.filter(groups__name__iexact="assistants"):
        is_assist = True

    for prescription in prescriptions:
        if prescription.doctor.id == request.user.doctor.id:
            patient_prescriptions.append(prescription)

    add_log(user, 'viewed medical information')
    return render_to_response('viewpatientMedInfo.html', {'test_results': test_results,
                                                          'prescriptions': patient_prescriptions,
                                                          'is_doctor': is_doctor,
                                                          'is_assist': is_assist,},
                              context_instance=RequestContext(request))


def remove_prescription(request, slug):
    # Get user
    user = User.objects.get(pk=request.user.id)

    # Get appointment and delete it
    if user in User.objects.filter(groups__name__iexact="doctors"):
        prescription = user.doctor.prescription_set.get(pk=slug)
        prescription.delete()
        add_log(user, "removed {} for {}".format(prescription.drug_name, prescription.patient_name))
    else:
        add_log(user, "attempted to remove prescription")
        return render(request, 'index.html')

    return render(request, 'delPresc.html', {})


@login_required
def admit_patient(request):
    # Get the request's context
    context = RequestContext(request)

    # Boolean value that tells you if admission was successful
    # Default is False but turns into True when the admission is complete
    patient_admitted = False

    # Get user
    user = User.objects.get(pk=request.user.id)

    # Gets the type of user admitting a patient in the form of a boolean
    # Is used in the patientAdmission.html file to redirect to correct page after a successful creation
    # of an admission
    is_doctor = False
    is_assist = False

    if user in User.objects.filter(groups__name__iexact="doctors"):
        is_doctor = True
    elif user in User.objects.filter(groups__name__iexact="assistants"):
        is_assist = True

    # If it's HTTP POST, we want to process data
    if request.method == 'POST':
        # Attempt to grab info from form
        admission_form = AdmissionForm(request, data=request.POST)

        # If two forms are valid...
        if admission_form.is_valid():
            # Save user's form data to database
            admission = admission_form.save(commit=False)
            # admission.user = user

            # admission.save()

            patient = admission.patient
            patient.is_admitted = True
            patient.save()
            if is_doctor:
                admission.doctor = user.doctor
            elif is_assist:
                admission.assistant = user.assistant

            # Update our variable to tell the template registration was successful
            patient_admitted = True

            add_log(user, "admitted {}".format(patient))

        # Invalid form or forms?
        # Print problems to user and to terminal
        else:
            print(admission_form.errors)

    # Not an HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input
    else:
        admission_form = AdmissionForm(request)

    # Render template depending on the context
    return render_to_response(
        'patientAdmission.html',
        {'admission_form': admission_form, 'patient_admitted': patient_admitted,
         'is_doctor': is_doctor, 'is_assist': is_assist}, context)


@login_required
def discharge_patient(request):
    # Get the request's context
    context = RequestContext(request)

    # Boolean value that tells you if discharge was successful
    # Default is False but turns into True when the discharge is complete
    patient_discharged = False

    # Get user
    user = User.objects.get(pk=request.user.id)

    # If it's HTTP POST, we want to process data
    if request.method == 'POST':
        # Attempt to grab info from form
        discharge_form = DischargeForm(request, data=request.POST)

        # If two forms are valid...
        if discharge_form.is_valid():
            # Save user's form data to database
            discharge = discharge_form.save(commit=False)
            # admission.user = user

            # admission.save()
            patient = discharge.patient
            patient.is_admitted = False
            patient.save()

            discharge.doctor = user.doctor

            discharge.save()

            # Update our variable to tell the template registration was successful
            patient_discharged = True

            add_log(user, "discharged {}".format(patient))

        # Invalid form or forms?
        # Print problems to user and to terminal
        else:
            print(discharge_form.errors)

    # Not an HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input
    else:
        discharge_form = DischargeForm(request)

    # Render template depending on the context
    return render_to_response(
        'patientDischarge.html',
        {'discharge_form': discharge_form, 'patient_discharged': patient_discharged}, context)


@login_required
def request_transfer(request):
    # Get the request's context
    context = RequestContext(request)

    # Boolean value that tells you if admission was successful
    # Default is False but turns into True when the admission is complete
    request_sent = False

    # Get user
    user = User.objects.get(pk=request.user.id)

    # Gets the type of user admitting a patient in the form of a boolean
    # Is used in the patientAdmission.html file to redirect to correct page after a successful creation
    # of an admission
    is_doctor = False
    is_admin = False

    if user in User.objects.filter(groups__name__iexact="doctors"):
        is_doctor = True
        user = user.doctor
    elif user in User.objects.filter(groups__name__iexact="admins"):
        is_admin = True
        user = user.admin

    #sendingHospital = user.hospital
    #patientList = Patient.objects.filter(hospital=sendingHospital)

    # If it's HTTP POST, we want to process data
    if request.method == 'POST':
        # Attempt to grab info from form
        request_form = RequestTransferForm(request, data=request.POST)

        # If two forms are valid...
        if request_form.is_valid():
            # Save user's form data to database
            transfer = request_form.save(commit=False)
            # admission.user = user

            # admission.save()

            #transfer.sendingHospital = user.hospital
            #transfer.pending = True
            transfer.patient.pending_transfer = True
            transfer.patient.hospital_to_transfer = transfer.receivingHospital
            transfer.patient.save()
            transfer.save()

            # Update our variable to tell the template registration was successful
            request_sent = True

            add_log(User.objects.get(pk=request.user.id), "requested a transfer")

        # Invalid form or forms?
        # Print problems to user and to terminal
        else:
            print(request_form.errors)

    # Not an HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input
    else:
        request_form = RequestTransferForm(request)
        #request_form.patient = Patient.objects.filter(hospital=user.hospital)
        #request_form.receivingHospital = Hospital.objects.exclude(hospital_name__exact=user.hospital.hospital_name)

    # Render template depending on the context
    return render_to_response(
        'requestTransfer.html',
        {'request_form': request_form, 'request_sent': request_sent,
         'is_doctor': is_doctor, 'is_admin': is_admin}, context)


@login_required
def accept_transfer(request):
    # Get the request's context
    context = RequestContext(request)

    # Boolean value that tells you if admission was successful
    # Default is False but turns into True when the admission is complete
    request_accepted = False

    # Get user
    user = User.objects.get(pk=request.user.id)

    # Gets the type of user admitting a patient in the form of a boolean
    # Is used in the patientAdmission.html file to redirect to correct page after a successful creation
    # of an admission
    is_doctor = False
    is_admin = False

    if user in User.objects.filter(groups__name__iexact="doctors"):
        is_doctor = True
        user = user.doctor
    elif user in User.objects.filter(groups__name__iexact="admins"):
        is_admin = True
        user = user.admin

    # If it's HTTP POST, we want to process data
    if request.method == 'POST':
        # Attempt to grab info from form
        accept_form = AcceptTransferForm(request, data=request.POST)

        # If two forms are valid...
        if accept_form.is_valid():
            # Save user's form data to database
            accept = accept_form.save(commit=False)

            patient = accept.patient
            patient.hospital = user.hospital
            patient.pending_transfer = False
            patient.save()

            #accept.pending = False
            #accept.approved = True
            accept.save()

            # Update our variable to tell the template registration was successful
            request_accepted = True

            add_log(User.objects.get(pk=request.user.id), "accepted a transfer")

        # Invalid form or forms?
        # Print problems to user and to terminal
        else:
            print(accept_form.errors)

    # Not an HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input
    else:
        accept_form = AcceptTransferForm(request)
        #accept_form.patient = Transfer.objects.filter(pending__exact=True).filter(receivingHospital=user.hospital)
        #accept_form.patient = Patient.objects.filter(hospital=user.hospital).filter(transfer__pending__exact=True)

    # Render template depending on the context
    return render_to_response(
        'acceptTransfer.html',
        {'accept_form': accept_form, 'request_accepted': request_accepted,
         'is_doctor': is_doctor, 'is_admin': is_admin}, context)


def update_test(request, slug):
    # Get user
    user = User.objects.get(pk=request.user.id)

    # Get test and release it
    if user in User.objects.filter(groups__name__iexact="doctors"):
        test = user.doctor.testresults_set.get(pk=slug)
        test.is_released = True
        test.save()
        add_log(user, "released {} results for {}".format(test.description, test.patient))
    else:
        add_log(user, "attempted to release a test")
        return render(request, 'index.html')

    return render(request, 'releaseTest.html', {})


def view_log(request):
    user = User.objects.get(pk=request.user.id)

    is_doctor = False
    is_assist = False
    is_admin = False

    if user in User.objects.filter(groups__name__iexact="doctors"):
        is_doctor = True
        user = user.doctor
    elif user in User.objects.filter(groups__name__iexact="assistants"):
        is_assist = True
        user = user.assistant
    elif user in User.objects.filter(groups__name__iexact="admins"):
        is_admin = True
        user = user.admin
    else:
        user = user.patient

    user_hospital = user.hospital_id

    logs = SystemLog.objects.filter(hospital_id__exact=user_hospital)

    return render(request, 'viewLogs.html', {'logs': logs, 'is_doctor': is_doctor, 'is_assist': is_assist, 'is_admin': is_admin})


def add_log(user, action='unspecified action'):
    new_log = SystemLog(operator=user, action=action)

    if user in User.objects.filter(groups__name__iexact="doctors"):
        user = user.doctor
    elif user in User.objects.filter(groups__name__iexact="assistants"):
        user = user.assistant
    elif user in User.objects.filter(groups__name__iexact="patients"):
        user = user.patient
    elif user in User.objects.filter(groups__name__iexact="admins"):
        user = user.admin
    else:
        return

    new_log.hospital = user.hospital

    new_log.save()
