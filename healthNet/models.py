import datetime

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


# Create your models here.
# Put other classes before this


class Hospital(models.Model):
    """
    Hospital holds all hospitals in the Healthnet system
    """
    hospital_name = models.CharField(max_length=30, validators=[RegexValidator(r'\W')], verbose_name="Hospital Name")

    def __str__(self):
        return self.hospital_name


class ContactInformation(models.Model):
    """
    Person is a superclass with which Admins, Doctors, Assistants, and Patients inherit
    Person has a one to one relationship with User
    """
    # Links Person to User model instance

    REQUIRED_FIELDS = (
        'user', 'street_address', 'city_or_town', 'region', 'country', 'zipcode', 'phone_number', 'emergency_contact_1',
        'emergency_contact_2')

    user = models.OneToOneField(User)
    street_address = models.CharField(max_length=50, default="----------", validators=[RegexValidator(r'\w')])
    city_or_town = models.CharField(max_length=25, default="----------", validators=[RegexValidator(r'\w')])
    region = models.CharField(max_length=25, default="----------", verbose_name='State/Region',
                              validators=[RegexValidator(r'\w')])
    country = models.CharField(max_length=25, default="----------", validators=[RegexValidator(r'\w')])
    zipcode = models.CharField(max_length=5, default="----------", validators=[RegexValidator(r'\d')])
    phone_number = models.CharField(max_length=25, default="----------", validators=[RegexValidator(r'\d')])
    emergency_contact_1 = models.CharField(max_length=25, default="----------", validators=[RegexValidator(r'\w')])
    emergency_contact_2 = models.CharField(max_length=25, default="----------", validators=[RegexValidator(r'\w')])

    # email_address = models.EmailField()

    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return "{}, {}".format(self.user.last_name, self.user.first_name)

        # def create_user_profile(sender, instance, created, **kwargs):
        #    if created:
        #        Person.objects.create(user=instance)
        # post_save.connect(create_user_profile, sender=User)

        # I WAS HAVING ISSUES WITH THE first_name AND last_name VARS SO I JUST COMMENTED THEM OUT FOR NOW
        # def __str__(self):
        #    return self.first_name + " "+ self.last_name


class Admin(models.Model):
    """
    Admin holds all admins in the db
    Admin inherits Person and has a one to one relationship with Hospital
    """
    user = models.OneToOneField(User)
    hospital = models.ForeignKey(Hospital, null=True)

    def __str__(self):
        return "{}, {}".format(self.user.last_name, self.user.first_name)


class Doctor(models.Model):
    """

    Doctor holds all doctors in the db
    Doctor inherits Person and has a many to one relationship with Hospital
    """
    user = models.OneToOneField(User)
    specialization = models.CharField(max_length=25, default="None", blank=True, validators=[RegexValidator(r'\w')])
    is_primary_care_physician = models.BooleanField(default=False)
    hospital = models.ForeignKey(Hospital, null=True)

    # secondary_hospital = models.ManyToManyField(Hospital, null=True, blank=True)

    def is_pcp(self):
        return self.is_primary_care_physician

    # def same_hospital_patients(self):
    #    allPatients = User.objects.filter(groups__name__iexact = 'patients')
    #    return allPatients.filter(patient__primary_care_physician__hospital_id__exact = self.hospital_id)

    # patients = models.ForeignKey(same_hospital_patients(), null=True)
    # reasonForAdmission = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return "Dr. {}, {}".format(self.user.last_name, self.user.first_name)


class Assistant(models.Model):
    """
    Assistant holds all assistants in the db
    Assistant inherits Person and has a many to one relationship with Hospital
    """
    user = models.OneToOneField(User)

    assistant_type = models.CharField(max_length=25, blank=True, validators=[RegexValidator(r'\w')])
    hospital = models.ForeignKey(Hospital, null=True)

    def __str__(self):
        return "{}, {}".format(self.user.last_name, self.user.first_name)


class Patient(models.Model):
    """
    Patient holds all patients in the db
    Patient inherits Person and has a many to one relationship with Doctor
    """

    REQUIRED_FIELDS = (
        'user', 'primary_care_physician', 'prescriptions', 'contact_information', 'medical_history',
        'medical_information', 'medical_history')

    user = models.OneToOneField(User, null=True)
    dob = models.DateField(verbose_name='Date of birth', null=True)
    height = models.CharField(max_length=8, default=None, validators=[RegexValidator(r'\w')])
    weight = models.CharField(max_length=10, default=None, validators=[RegexValidator(r'\w')])
    primary_care_physician = models.ForeignKey(Doctor, null=True)
    insurance_provider = models.CharField(max_length=50, default=None, validators=[RegexValidator(r'\w')])
    insurance_number = models.CharField(max_length=10, default=None, validators=[RegexValidator(r'\w')])
    is_admitted = models.BooleanField(default=False)
    pending_transfer = models.BooleanField(default=False)
    hospital_to_transfer = models.ForeignKey(Hospital, null=True, default=None, related_name='transferring_hospital')
    hospital = models.ForeignKey(Hospital, null=True)
    prescriptions = models.TextField(max_length=50, default="")

    def __str__(self):
        return "{}, {}".format(self.user.last_name, self.user.first_name)

    def admit(self):
        self.is_admitted = True

    def discharge(self):
        self.is_admitted = False


class MedicalNotes(models.Model):
    patient = models.ForeignKey(Patient)
    doctor_id = models.CharField(max_length=10)
    time = models.DateTimeField(default=timezone.now())
    general_comments = models.TextField(max_length=500, verbose_name='General comments:', null=True, blank=True)
    medical_allergies_or_reactions = models.TextField(max_length=10000, null=True, blank=True)

    # Diseases/conditions
    diseases_conditions = models.CharField(max_length=100, default="", blank=True,
                                           verbose_name='Diseases Conditions -------------------------------------------------------------------------------- comments:')
    diabetes = models.BooleanField(default=False)
    kidney_disease = models.BooleanField(default=False)
    stroke = models.BooleanField(default=False)
    tuberculosis = models.BooleanField(default=False)
    arrythmia = models.BooleanField(default=False)
    high_blood_pressure = models.BooleanField(default=False)
    hepatitis = models.BooleanField(default=False)
    depression = models.BooleanField(default=False)
    coronary_artery_disease = models.BooleanField(default=False)
    asthma = models.BooleanField(default=False)
    thyroid_disease = models.BooleanField(default=False)
    emphysema = models.BooleanField(default=False)
    congestive_heart_failure = models.BooleanField(default=False)
    heart_attack = models.BooleanField(default=False)
    seizures = models.BooleanField(default=False)
    sexually_transmitted_disease_type = models.BooleanField(default=False)
    eye_problems = models.BooleanField(default=False)
    cancer = models.BooleanField(default=False)

    # Surgeries
    surgeries = models.CharField(max_length=100, default="", blank=True,
                                 verbose_name='Surgeries -------------------------------------------------------------------------------- comments:')

    previous_surgery_1 = models.CharField(max_length=100, verbose_name='Previous surgery #1', null=True, blank=True,
                                          validators=[RegexValidator(r'\w')])
    type_of_surgery_1 = models.CharField(max_length=50, verbose_name='Type of surgery #1', null=True, blank=True,
                                         validators=[RegexValidator(r'\w')])
    reason_for_hospitalization_1 = models.CharField(max_length=50, verbose_name='Reason for hospitalization #1',
                                                    null=True, blank=True, validators=[RegexValidator(r'\w')])
    location_1 = models.CharField(max_length=100, verbose_name='Location of surgery #1', null=True, blank=True,
                                  validators=[RegexValidator(r'\w')])
    date_1 = models.DateField(verbose_name='Surgery #1 date', null=True, blank=True)
    previous_surgery_2 = models.CharField(max_length=100, verbose_name='Previous surgery #2', null=True, blank=True,
                                          validators=[RegexValidator(r'\w')])
    type_of_surgery_2 = models.CharField(max_length=50, verbose_name='Type of surgery #2', null=True, blank=True,
                                         validators=[RegexValidator(r'\w')])
    reason_for_hospitalization_2 = models.CharField(max_length=50, verbose_name='Reason for hospitalization #2',
                                                    null=True, blank=True, validators=[RegexValidator(r'\w')])
    location_2 = models.CharField(max_length=100, verbose_name='Location of surgery #2', null=True, blank=True,
                                  validators=[RegexValidator(r'\w')])
    date_2 = models.DateField(verbose_name='Surgery #2 date', null=True, blank=True)
    previous_surgery_3 = models.CharField(max_length=100, verbose_name='Previous surgery #3', null=True, blank=True,
                                          validators=[RegexValidator(r'\w')])
    type_of_surgery_3 = models.CharField(max_length=50, verbose_name='Type of surgery #3', null=True, blank=True,
                                         validators=[RegexValidator(r'\w')])
    reason_for_hospitalization_3 = models.CharField(max_length=50, verbose_name='Reason for hospitalization #3',
                                                    null=True, blank=True, validators=[RegexValidator(r'\w')])
    location_3 = models.CharField(max_length=100, verbose_name='Location of surgery #3', null=True, blank=True,
                                  validators=[RegexValidator(r'\w')])
    date_3 = models.DateField(verbose_name='Surgery #3 date', null=True, blank=True)

    other_surgeries = models.CharField(max_length=100, verbose_name='Other surgeries', null=True, blank=True)

    # Medicines
    medicines = models.CharField(max_length=100, default="", blank=True,
                                 verbose_name='Medicines -------------------------------------------------------------------------------- comments:')

    medicine_name_1 = models.CharField(max_length=50, verbose_name='Medicine #1 name', null=True, blank=True,
                                       validators=[RegexValidator(r'\w')])
    dosage_1 = models.CharField(max_length=10, verbose_name='Medicine #1 dosage', null=True, blank=True,
                                validators=[RegexValidator(r'\w')])
    medicine_name_2 = models.CharField(max_length=50, verbose_name='Medicine #2 name', null=True, blank=True,
                                       validators=[RegexValidator(r'\w')])
    dosage_2 = models.CharField(max_length=10, verbose_name='Medicine #2 dosage', null=True, blank=True,
                                validators=[RegexValidator(r'\w')])
    medicine_name_3 = models.CharField(max_length=50, verbose_name='Medicine #3 name', null=True, blank=True,
                                       validators=[RegexValidator(r'\w')])
    dosage_3 = models.CharField(max_length=10, verbose_name='Medicine #3 dosage', null=True, blank=True,
                                validators=[RegexValidator(r'\w')])
    medicine_name_4 = models.CharField(max_length=50, verbose_name='Medicine #4 name', null=True, blank=True,
                                       validators=[RegexValidator(r'\w')])
    dosage_4 = models.CharField(max_length=10, verbose_name='Medicine #4 dosage', null=True, blank=True,
                                validators=[RegexValidator(r'\w')])
    medicine_name_5 = models.CharField(max_length=50, verbose_name='Medicine #5 name', null=True, blank=True,
                                       validators=[RegexValidator(r'\w')])
    dosage_5 = models.CharField(max_length=10, verbose_name='Medicine #5 dosage', null=True, blank=True,
                                validators=[RegexValidator(r'\w')])
    other_medicines = models.CharField(max_length=100, null=True, blank=True, validators=[RegexValidator(r'\w')])

    # Care providers
    care_providers = models.CharField(max_length=100, default="", blank=True,
                                      verbose_name='Care Providers -------------------------------------------------------------------------------- comments:')

    pharmacy = models.CharField(max_length=100, verbose_name='Preferred pharmacy', null=True, blank=True,
                                validators=[RegexValidator(r'\w')])
    other_care_provider_1 = models.CharField(max_length=100, verbose_name='Other care provider #1', null=True,
                                             blank=True, validators=[RegexValidator(r'\w')])
    reason_for_visit_1 = models.CharField(max_length=100, verbose_name='Reason for visit', null=True, blank=True,
                                          validators=[RegexValidator(r'\w')])
    other_care_provider_2 = models.CharField(max_length=100, verbose_name='Other care provider #2', null=True,
                                             blank=True, validators=[RegexValidator(r'\w')])
    reason_for_visit_2 = models.CharField(max_length=100, verbose_name='Reason for visit', null=True, blank=True,
                                          validators=[RegexValidator(r'\w')])
    other_care_provider_3 = models.CharField(max_length=100, verbose_name='Other care provider #3', null=True,
                                             blank=True, validators=[RegexValidator(r'\w')])
    reason_for_visit_3 = models.CharField(max_length=100, verbose_name='Reason for visit', null=True, blank=True,
                                          validators=[RegexValidator(r'\w')])

    # Immunizations
    immunizations = models.CharField(max_length=100, default="", blank=True,
                                     verbose_name='Immunizations -------------------------------------------------------------------------------- comments:')

    tetanus = models.DateField(null=True, blank=True)
    influenza = models.DateField(null=True, blank=True)
    pneumonia = models.DateField(null=True, blank=True)
    hepatitis_b = models.DateField(null=True, blank=True)

    other_immunization_1 = models.CharField(max_length=50, verbose_name='Other immunization #1 type and date',
                                            null=True, blank=True, validators=[RegexValidator(r'\w')])
    other_immunization_2 = models.CharField(max_length=50, verbose_name='Other immunization #2 type and date',
                                            null=True, blank=True, validators=[RegexValidator(r'\w')])
    other_immunization_3 = models.CharField(max_length=50, verbose_name='Other immunization #3 type and date',
                                            null=True, blank=True, validators=[RegexValidator(r'\w')])

    tests = models.CharField(max_length=100, default="", blank=True,
                             verbose_name='Tests -------------------------------------------------------------------------------- comments:')
    # cholesterol_test_date = models.DateTimeField()

    cholesterol_test_result = models.CharField(max_length=100, verbose_name='Cholesterol test result and date',
                                               null=True, blank=True, validators=[RegexValidator(r'\w')])

    # pap_smear_or_pelvic_test_date = models.DateTimeField()

    pap_smear_or_pelvic_test_result = models.CharField(max_length=100,
                                                       verbose_name='Pap smear or pelvic test result and date',
                                                       null=True, blank=True, validators=[RegexValidator(r'\w')])

    # mammogram_test_date = models.DateTimeField()

    mammogram_test_result = models.CharField(max_length=100, verbose_name='Mammogram test result and date', null=True,
                                             blank=True, validators=[RegexValidator(r'\w')])

    # blood_in_stool_test_date = models.DateTimeField()

    blood_in_stool_test_result = models.CharField(max_length=100, verbose_name='Blood in stool test result and date',
                                                  null=True, blank=True, validators=[RegexValidator(r'\w')])

    # hiv_test_date = models.DateTimeField()

    hiv_test_result = models.CharField(max_length=100, verbose_name='HIV test result and date', null=True, blank=True,
                                       validators=[RegexValidator(r'\w')])

    # colonoscopy_test_date = models.DateTimeField()

    colonoscopy_test_result = models.CharField(max_length=100, verbose_name='colonoscopy test result and date',
                                               null=True, blank=True, validators=[RegexValidator(r'\w')])

    # hepatitis_c_test_date = models.DateTimeField()

    hepatitis_c_test_result = models.CharField(max_length=100, verbose_name='Hepatitis c test result and date',
                                               null=True, blank=True, validators=[RegexValidator(r'\w')])

    # Family history
    family_history = models.CharField(max_length=100, default="", blank=True,
                                      verbose_name='Family History -------------------------------------------------------------------------------- comments:')

    fh_of_alcoholism_or_drug_use = models.CharField(max_length=50, verbose_name='Alcoholism or drug use', null=True,
                                                    blank=True, validators=[RegexValidator(r'\w')])
    fh_of_cancer = models.CharField(max_length=50, verbose_name='Cancer', null=True, blank=True,
                                    validators=[RegexValidator(r'\w')])
    fh_of_cancer_type = models.CharField(max_length=50, verbose_name='Cancer type', null=True, blank=True,
                                         validators=[RegexValidator(r'\w')])
    fh_of_diabetes = models.CharField(max_length=50, verbose_name='Diabetes', null=True, blank=True,
                                      validators=[RegexValidator(r'\w')])
    fh_of_heart_disease = models.CharField(max_length=50, verbose_name='Heart disease', null=True, blank=True,
                                           validators=[RegexValidator(r'\w')])
    fh_of_high_blood_pressure = models.CharField(max_length=50, verbose_name='High blood pressure', null=True,
                                                 blank=True, validators=[RegexValidator(r'\w')])
    fh_of_high_cholesterol = models.CharField(max_length=50, verbose_name='High cholesterol', null=True, blank=True,
                                              validators=[RegexValidator(r'\w')])
    fh_of_osteoporosis = models.CharField(max_length=50, verbose_name='Osteoporosis', null=True, blank=True,
                                          validators=[RegexValidator(r'\w')])
    fh_of_mental_illness = models.CharField(max_length=50, verbose_name='Mental illness', null=True, blank=True,
                                            validators=[RegexValidator(r'\w')])
    fh_of_stroke = models.CharField(max_length=50, verbose_name='Stroke', null=True, blank=True,
                                    validators=[RegexValidator(r'\w')])
    fh_of_thyroid_disease = models.CharField(max_length=50, verbose_name='Thyroid disease', null=True, blank=True,
                                             validators=[RegexValidator(r'\w')])
    fh_of_other_illnesses = models.CharField(max_length=50, verbose_name='Other illnesses', null=True, blank=True,
                                             validators=[RegexValidator(r'\w')])

    health_habits = models.CharField(max_length=100, default="", blank=True,
                                     verbose_name='Health Habits -------------------------------------------------------------------------------- comments:')
    tobacco_use = models.BooleanField(default=False, verbose_name='Do you smoke or use any tobacco products?')
    t_quantity = models.CharField(max_length=100, verbose_name='No. of cigarettes each day', null=True, blank=True,
                                  validators=[RegexValidator(r'\w')])
    years_smoking = models.CharField(max_length=2, verbose_name='How long have you smoked?', null=True, blank=True,
                                     validators=[RegexValidator(r'\w')])
    other_tobacco = models.CharField(max_length=100, verbose_name='Other tobacco products', null=True, blank=True,
                                     validators=[RegexValidator(r'\w')])

    alcohol_use = models.BooleanField(default=False, verbose_name='Do you drink alcohol?')

    a_quantity = models.CharField(max_length=50, verbose_name='How much?', null=True, blank=True,
                                  validators=[RegexValidator(r'\w')])
    frequency = models.CharField(max_length=50, verbose_name='How often?', null=True, blank=True,
                                 validators=[RegexValidator(r'\w')])
    cut_down = models.BooleanField(default=False, verbose_name='Do you feel the need to cut down?')

    # Other drugs
    other_drugs_s = models.BooleanField(default=False, verbose_name='Do you use any other drugs?')
    still_using_them = models.BooleanField(default=False, verbose_name='Are you still using them?')

    other_comments = models.TextField(max_length=1000, null=True, blank=True)

    # Personal History
    personal_history = models.CharField(max_length=100, default="", blank=True,
                                        verbose_name='Personal History -------------------------------------------------------------------------------- comments:')

    feel_sad_or_depressed = models.BooleanField(default=False, verbose_name='Do you often feel sad or depressed?')
    concerns = models.BooleanField(default=False, verbose_name='Do you feel there is something wrong with your body?')
    unmet_need = models.BooleanField(default=False,
                                     verbose_name='Do you have limited access to food, shelter or medical care?')
    major_life_changes = models.BooleanField(default=False,
                                             verbose_name='Have there been any major changes in your life?')
    spiritual_emotional_support = models.BooleanField(default=False,
                                                      verbose_name='Do you have some form of spiritual support?')
    marital_status = models.BooleanField(default=False, verbose_name='Are you married?')
    employment = models.BooleanField(default=False, verbose_name='Are you currently employed?')
    work = models.CharField(max_length=100, verbose_name='If so, where do you work?', null=True, blank=True,
                            validators=[RegexValidator(r'\w')])
    unemployment_reason = models.TextField(max_length=100, verbose_name='Reason for unemployment, if unemployed',
                                           null=True, blank=True)
    exercise = models.CharField(max_length=50, verbose_name='Do you even lift brah?', null=True, blank=True,
                                validators=[RegexValidator(r'\w')])

    # Sexual History
    sexual_history = models.CharField(max_length=100, default="", blank=True,
                                      verbose_name='Sexual History -------------------------------------------------------------------------------- comments:')

    sexually_active = models.BooleanField(default=False, verbose_name='Are you sexually active?')
    std_risk = models.BooleanField(default=False, verbose_name='Do you feel you are at risk for HIV/AIDS?')
    birth_control = models.BooleanField(default=False, verbose_name='Do you use any form of birth control?')
    children = models.IntegerField(verbose_name='How many children do you have, if any?', null=True,
                                   blank=True)

    def __str__(self):
        return "{} -- {} -- {}:{} (UTC)".format(self.patient.__str__(), self.time.date().__str__(),
                                                self.time.hour.__str__(), self.time.minute.__str__())

    def display_fields(self):
        return (
            ('Patient', self.patient),
            ('Doctor', Doctor.objects.get(user_id__exact=self.doctor_id)),
            ('Time', self.time),
            ('General Commments', self.general_comments),
            ('Medical allergies or reactions', self.medical_allergies_or_reactions),
            ('Diseases and conditions', self.diseases_conditions),
            ('Diabetes', self.diabetes), ('Kidney disease', self.kidney_disease), ('Stroke', self.stroke),
            ('Tuberculosis', self.tuberculosis), ('Arrythmia', self.arrythmia),
            ('High blood pressure', self.high_blood_pressure),
            ('Hepatitis', self.hepatitis), ('Depression', self.depression),
            ('Coronary artery disease', self.coronary_artery_disease), ('Asthma', self.asthma),
            ('Thyroid disease', self.thyroid_disease),
            ('Emphysema', self.emphysema),
            ('Congestive heart failure', self.congestive_heart_failure), ('Heart attack', self.heart_attack),
            ('Seizures', self.seizures),
            ('Sexually transmitted disease type', self.sexually_transmitted_disease_type),
            ('Eye problems', self.eye_problems), ('Cancer', self.cancer),
            ('Surgeries', self.surgeries),
            ('Previous surgery #1', self.previous_surgery_1), ('Type of surgery #1', self.type_of_surgery_1),
            ('Reason for hospitalization of surgery #1', self.reason_for_hospitalization_1),
            ('Location of surgery #1', self.location_1),
            ('Date of surgery #1', self.date_1),
            ('Previous surgery #2', self.previous_surgery_2), ('Type of surgery #2', self.type_of_surgery_2),
            ('Reason for hospitalization of surgery #2', self.reason_for_hospitalization_2),
            ('Location of surgery #2', self.location_2),
            ('Date of surgery #2', self.date_2),
            ('Previous surgery #3', self.previous_surgery_3), ('Type of surgery #3', self.type_of_surgery_3),
            ('Reason for hospitalization of surgery #3', self.reason_for_hospitalization_3),
            ('Location of surgery #3', self.location_3),
            ('Date of surgery #3', self.date_3),
            ('Other surgeries', self.other_surgeries),
            ('Medications', self.medicines),
            ('Medicine #1 name', self.medicine_name_1), ('Dosage of medicine #1', self.dosage_1),
            ('Medicine #2 name', self.medicine_name_1), ('Dosage of medicine #2', self.dosage_1),
            ('Medicine #3 name', self.medicine_name_1), ('Dosage of medicine #3', self.dosage_1),
            ('Medicine #4 name', self.medicine_name_1), ('Dosage of medicine #4', self.dosage_1),
            ('Medicine #5 name', self.medicine_name_1), ('Dosage of medicine #5', self.dosage_1),
            ('Other medications', self.other_medicines),
            ('Care providers', self.care_providers),
            ('Primary pharmacy', self.pharmacy), ('Other care provider #1', self.other_care_provider_1),
            ('Reason for visit to care provider #1', self.reason_for_visit_1),
            ('Other care provider #2', self.other_care_provider_2),
            ('Reason for visit to care provider #2', self.reason_for_visit_2),
            ('Other care provider #3', self.other_care_provider_3),
            ('Reason for visit to care provider #3', self.reason_for_visit_3),
            ('Immunizations', self.immunizations),
            ('Tetanus', self.tetanus), ('Influenza', self.influenza), ('Pneumonia', self.pneumonia),
            ('Hepatitis_b', self.hepatitis_b),
            ('Tests', self.tests),
            ('Cholesterol test result', self.cholesterol_test_result),
            ('Pap smear or pelvic test result', self.pap_smear_or_pelvic_test_result),
            ('Mammogram test result', self.mammogram_test_result),
            ('Blood in stool test result', self.blood_in_stool_test_result),
            ('HIV test result', self.hiv_test_result), ('Colonoscopy test result', self.colonoscopy_test_result),
            ('Hepatitis c test result', self.hepatitis_c_test_result),
            ('Family history', self.family_history),
            ('History of alcoholism or drug abuse', self.fh_of_alcoholism_or_drug_use),
            ('History of cancer', self.fh_of_cancer),
            ('Cancer type', self.fh_of_cancer_type),
            ('History of diabetes', self.fh_of_diabetes),
            ('History of heart disease', self.fh_of_heart_disease),
            ('History of high blood pressure', self.fh_of_high_blood_pressure),
            ('History of high cholesterol', self.fh_of_high_cholesterol),
            ('History of osteoporosis', self.fh_of_osteoporosis),
            ('History of mental illness', self.fh_of_mental_illness), ('History of stroke', self.fh_of_stroke),
            ('History of thyroid disease', self.fh_of_thyroid_disease),
            ('History of other illnesses', self.fh_of_other_illnesses),
            ('Health habits', self.health_habits),
            ('Tobacco use', self.tobacco_use), ('Quantity', self.t_quantity), ('Years smoking', self.years_smoking),
            ('Other tobacco', self.other_tobacco),
            ('Alcohol use', self.alcohol_use),
            ('Quantity', self.a_quantity), ('Frequency', self.frequency), ('Feels the need to cut down', self.cut_down),
            ('Other drugs', self.other_drugs_s),
            ('Still using them', self.still_using_them),
            ('Other Comments', self.other_comments),
            ('Personal history', self.personal_history),
            ('Sometimes feel sad or depressed', self.feel_sad_or_depressed), ('Concerns', self.concerns),
            ('Unmet needs', self.unmet_need),
            ('Major life changes', self.major_life_changes),
            ('Spiritual emotional support', self.spiritual_emotional_support), ('marital_status', self.marital_status),
            ('employment', self.employment), ('work', self.work),
            ('Unemployment reason', self.unemployment_reason),
            ('Exercise', self.exercise),
            ('Sexual history', self.sexual_history),
            ('Sexually active?', self.sexually_active), ('STD risk', self.std_risk),
            ('Birth control', self.birth_control), ('Number of children', self.children)
        )


class Appointment(models.Model):
    """
    Appointment stores all appointments in the db
    """
    appointment_name = models.CharField(max_length=50, default="Appointment")
    doctor = models.ForeignKey(Doctor, null=True)
    patient = models.ForeignKey(Patient, null=True)
    assistant = models.ForeignKey(Assistant, null=True)
    hospital = models.ForeignKey(Hospital, null=True)
    start_time = models.TimeField(default=timezone.now)
    start_date = models.DateField(default=timezone.now() + datetime.timedelta(days=1))
    end_time = models.TimeField(default=timezone.now() + datetime.timedelta(hours=1))
    end_date = models.DateField(default=timezone.now() + datetime.timedelta(days=1))
    current_user = models.ForeignKey(User, null=True)

    def __str__(self):
        return "{} with {} and {} for {} from {}-{} to {}-{}".format(self.appointment_name, self.doctor,
                                                                     self.assistant, self.patient, self.start_time,
                                                                     self.start_date, self.end_time, self.end_date)

    def export(self):
        return '{}_{}_{}_{}_{}_{}_{}_{}'.format(self.appointment_name, self.doctor.user_id,
                                                self.assistant.user_id, self.start_time, self.start_date,
                                                self.end_time, self.end_date, self.current_user.username)


class TestResults(models.Model):
    """
    Links uploaded files to doctors and patients
    """
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/', default='static/header.jpg')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient)
    is_released = models.BooleanField(default=False)
    doctor = models.ForeignKey(Doctor)

    def __str__(self):
        return 'Released: {}. {} uploaded at {} for {} by {} FileName: {}'.format(self.is_released,
                                                                                  self.description,
                                                                                  self.uploaded_at,
                                                                                  self.patient,
                                                                                  self.doctor,
                                                                                  self.document.name)

    def export(self):
        return '{}_{}_{}_{}_{}_{}'.format(self.description, self.document.name, self.uploaded_at, self.patient.user_id,
                                          self.is_released,
                                          self.doctor.user_id)


class Prescription(models.Model):
    """
    Prescription stores all prescription in the db
    """

    # patient = models.ForeignKey(Patient, null=True)
    patient_name = models.ForeignKey(Patient, null=True)
    drug_name = models.CharField(max_length=75, default="----------", validators=[RegexValidator(r'\w')])
    dosage = models.CharField(max_length=20, default="per Day", validators=[RegexValidator(r'\w')])
    reason = models.TextField(max_length=200)
    doctor = models.ForeignKey(Doctor)

    def __str__(self):
        return "{} is taking {} with a daily dose of {}. Reason: {}.".format(self.patient_name, self.drug_name,
                                                                             self.dosage, self.reason)

    def export(self):
        return '{}_{}_{}_{}_{}'.format(self.patient_name, self.drug_name, self.dosage, self.reason, self.doctor.user_id)


class Admission(models.Model):
    # TODO Utilize start date and end date for each admission object

    patient = models.ForeignKey(Patient, null=True)
    doctor = models.ForeignKey(Doctor, null=True)
    assistant = models.ForeignKey(Assistant, null=True)
    reason_for_admission = models.TextField(max_length=50, default="")

    # start_date = models.DateField(default=timezone.now().date())
    # end_date = models.DateField(default=timezone.now().date()+timezone.now().date().day)

    def __str__(self):
        return '{} admitted by Dr. {} and {}. Reason: {}'.format(self.patient.__str__(),
                                                                 self.doctor.__str__(),
                                                                 self.assistant.__str__(),
                                                                 self.reason_for_admission)


class Transfer(models.Model):
    # approved = models.BooleanField(default=False)
    # pending = models.BooleanField(default=False)
    patient = models.ForeignKey(Patient, null=True)
    # sendingHospital = models.ForeignKey(Hospital, null=True, related_name='hospital_sending_request')
    receivingHospital = models.ForeignKey(Hospital, null=True)
