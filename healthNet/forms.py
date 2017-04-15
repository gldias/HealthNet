from django import forms
from django.contrib.auth.models import User

from .models import Patient, Doctor, Admin, Appointment, ContactInformation, MedicalNotes, \
    TestResults, Prescription, Assistant, Admission, Transfer, Hospital


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']


class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = ContactInformation

        fields = ['street_address', 'city_or_town', 'region', 'country', 'zipcode', 'phone_number',
                  'emergency_contact_1', 'emergency_contact_2']


class MedicalNotesPatientSelectForm(forms.ModelForm):
    # patient = forms.ChoiceField(choices=[Patient.objects.all()])

    class Meta:
        model = MedicalNotes

        fields = ['patient']


class MedicalNotesForm(forms.ModelForm):
    class Meta:
        model = MedicalNotes

        fields = ['patient', 'general_comments', 'medical_allergies_or_reactions',
                  'diseases_conditions',
                  'diabetes', 'kidney_disease', 'stroke', 'tuberculosis', 'arrythmia', 'high_blood_pressure',
                  'hepatitis', 'depression', 'coronary_artery_disease', 'asthma', 'thyroid_disease', 'emphysema',
                  'congestive_heart_failure', 'heart_attack', 'seizures', 'sexually_transmitted_disease_type',
                  'eye_problems', 'cancer',
                  'surgeries',
                  'previous_surgery_1', 'type_of_surgery_1', 'reason_for_hospitalization_1', 'location_1', 'date_1',
                  'previous_surgery_2', 'type_of_surgery_2', 'reason_for_hospitalization_2', 'location_2', 'date_2',
                  'previous_surgery_3', 'type_of_surgery_3', 'reason_for_hospitalization_3', 'location_3', 'date_3',
                  'other_surgeries',
                  'medicines',
                  'medicine_name_1', 'dosage_1', 'medicine_name_2', 'dosage_2', 'medicine_name_3',
                  'dosage_3', 'medicine_name_4', 'dosage_4', 'medicine_name_5', 'dosage_5', 'other_medicines',
                  'care_providers',
                  'pharmacy', 'other_care_provider_1', 'reason_for_visit_1', 'other_care_provider_2',
                  'reason_for_visit_2', 'other_care_provider_3', 'reason_for_visit_3',
                  'immunizations',
                  'tetanus', 'influenza', 'pneumonia', 'hepatitis_b',
                  'tests',
                  'cholesterol_test_result',
                  'pap_smear_or_pelvic_test_result', 'mammogram_test_result', 'blood_in_stool_test_result',
                  'hiv_test_result', 'colonoscopy_test_result', 'hepatitis_c_test_result',
                  'family_history',
                  'fh_of_alcoholism_or_drug_use', 'fh_of_cancer', 'fh_of_cancer_type', 'fh_of_diabetes',
                  'fh_of_heart_disease', 'fh_of_high_blood_pressure', 'fh_of_high_cholesterol', 'fh_of_osteoporosis',
                  'fh_of_mental_illness', 'fh_of_stroke', 'fh_of_thyroid_disease', 'fh_of_other_illnesses',
                  'health_habits',
                  'tobacco_use', 't_quantity', 'years_smoking', 'other_tobacco', 'alcohol_use',
                  'a_quantity', 'frequency', 'cut_down', 'other_drugs_s', 'still_using_them', 'other_comments',
                  'personal_history',
                  'feel_sad_or_depressed', 'concerns', 'unmet_need', 'major_life_changes',
                  'spiritual_emotional_support', 'marital_status', 'employment', 'work', 'unemployment_reason',
                  'exercise',
                  'sexual_history',
                  'sexually_active', 'std_risk', 'birth_control', 'children']


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient

        # fields = ['user', 'primary_care_physician', 'contact_information',
        #           'medical_information', 'medical_history']

        fields = ['primary_care_physician', 'insurance_provider', 'insurance_number', 'height', 'weight',
                  'dob']


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_name', 'start_date', 'start_time', 'doctor', 'patient', 'assistant', 'end_date',
                  'end_time']


class TestResultsForm(forms.ModelForm):
    class Meta:
        model = TestResults

        fields = ('doctor', 'document', 'patient', 'description', 'is_released')


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient_name', 'drug_name', 'dosage', 'reason', 'doctor']


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'is_primary_care_physician', 'hospital']


class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['hospital']


class AssistantForm(forms.ModelForm):
    class Meta:
        model = Assistant
        fields = ['assistant_type', 'hospital']


class AdmissionForm(forms.ModelForm):
    patient = forms.ModelChoiceField(queryset=Patient.objects.none(), label='Select Patient')

    class Meta:
        model = Admission
        fields = ['patient', 'reason_for_admission']

    def __init__(self, request, *args, **kwargs):
        super(AdmissionForm, self).__init__(*args, **kwargs)
        if request.user:
            user = request.user

            if user in User.objects.filter(groups__name__iexact="doctors"):
                user = user.doctor
            elif user in User.objects.filter(groups__name__iexact="assistants"):
                user = user.assistant

            queryset = Patient.objects.filter(hospital=user.hospital)

        else:
            queryset = Patient.objects.all()

        self.fields['patient'].queryset = queryset


class DischargeForm(forms.ModelForm):
    patient = forms.ModelChoiceField(queryset=Patient.objects.none(), label='Select Patient')

    class Meta:
        model = Admission
        fields = ['patient']

    def __init__(self, request, *args, **kwargs):
        super(DischargeForm, self).__init__(*args, **kwargs)
        if request.user:
            user = request.user

            if user in User.objects.filter(groups__name__iexact="doctors"):
                user = user.doctor
            elif user in User.objects.filter(groups__name__iexact="assistants"):
                user = user.assistant

            queryset = Patient.objects.filter(is_admitted__exact=True).filter(hospital=user.hospital)

        else:
            queryset = Patient.objects.all()

        self.fields['patient'].queryset = queryset


class RequestTransferForm(forms.ModelForm):
    receivingHospital = forms.ModelChoiceField(queryset=Hospital.objects.none(), label='Send Patient To:')

    patient = forms.ModelChoiceField(queryset=Patient.objects.none(), label='Select Patient')

    class Meta:
        model = Transfer
        fields = ['patient', 'receivingHospital']

    def __init__(self, request, *args, **kwargs):
        super(RequestTransferForm, self).__init__(*args, **kwargs)
        if request.user:
            user = request.user

            if user in User.objects.filter(groups__name__iexact="doctors"):
                user = user.doctor
            elif user in User.objects.filter(groups__name__iexact="admins"):
                user = user.admin

            queryset1 = Hospital.objects.exclude(hospital_name__exact=user.hospital.hospital_name)
            queryset2 = Patient.objects.filter(hospital=user.hospital)
        else:
            queryset1 = Hospital.objects.all()
            queryset2 = Patient.objects.all()
        self.fields['receivingHospital'].queryset = queryset1
        self.fields['patient'].queryset = queryset2


class AcceptTransferForm(forms.ModelForm):
    patient = forms.ModelChoiceField(queryset=Patient.objects.none(), label='Select Patient')

    class Meta:
        model = Transfer
        fields = ['patient']

    def __init__(self, request, *args, **kwargs):
        super(AcceptTransferForm, self).__init__(*args, **kwargs)
        if request.user:
            user = request.user

            if user in User.objects.filter(groups__name__iexact="doctors"):
                user = user.doctor
            elif user in User.objects.filter(groups__name__iexact="admins"):
                user = user.admin

            queryset = Patient.objects.filter(pending_transfer__exact=True).filter(hospital_to_transfer=user.hospital)
        else:
            queryset = Patient.objects.all()
        self.fields['patient'].queryset = queryset
