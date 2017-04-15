from django.test import TestCase

from healthNet.models import *
from healthNet.views import *


class AdminTestCase(TestCase):
    def test_admin_creation(self):
        user1 = User.objects.create_user(username="fouyo", email="fouyo4@hotmail.com",
                                         password="error404", first_name="Gwen", last_name="Munson")
        admin1 = Admin(user=user1)
        self.assertEqual(admin1.__str__(), "Munson, Gwen")


class AssistantTestCase(TestCase):
    def test_assistant_creation(self):
        user1 = User.objects.create_user(username="fouyo", email="fouyo4@hotmail.com",
                                         password="error404", first_name="Gwen", last_name="Munson")
        with self.assertRaises(Exception):  # checks to see that you can't create a blank assistant
            assistant1 = Assistant()
            assistant1.save()

        assistant2 = Assistant(user=user1)
        self.assertEqual(assistant2.assistant_type, "----------")  # our default value works correctly
        with self.assertRaises(Exception):
            assistant2.assistant_type = "This is longer than 25 characters and will not be accepted."
            assistant2.save()
        assistant2.assistant_type = "Foot"
        self.assertEqual(assistant2.assistant_type, "Foot")  # can successfully change assistant_type


class PatientTestCase(TestCase):
    def test_patient_creation(self):
        newUser = User.objects.create_user(username="gcm3807", email="gcm3807@rit.edu", password="hamtaro")
        doctor1 = Doctor(user=newUser)
        user4 = User.objects.create_user(username="super mario", email="mariomario@yahoo.com", password="bowser")
        with self.assertRaises(Exception):
            patient1 = Patient()
            patient1.save()
        with self.assertRaises(Exception):
            patient2 = Patient(user=user4, insurance_provider="Liberty Mutual", insurance_number="13376942100",
                               primary_care_physician=doctor1, medical_history="Has an addiction to mushrooms",
                               prescriptions="Prozac")
            patient2.save()


class DoctorTestCase(TestCase):
    def test_doctor(self):
        newUser = User.objects.create_user(username="gcm3807", email="gcm3807@rit.edu", password="hamtaro",
                                           first_name="Not", last_name="Gwen")
        newDoctor = Doctor.objects.create(user=newUser)
        with self.assertRaises(Exception):
            doctor1 = Doctor()
            doctor1.save()
        with self.assertRaises(Exception):
            newDoctor.specialization = "Master of dark arts and the unseen."
            newDoctor.save()
        self.assertEqual(newDoctor.user.username, "gcm3807")
        self.assertEqual(newDoctor.is_primary_care_physician, False)
        with self.assertRaises(Exception):  # can't have a doctor be a part of an invalid hospital
            hospital1 = Hospital(hospital_name="This hospital name is way too long, so it should fail.")
            newDoctor.hospital = hospital1
            newDoctor.save()
        self.assertEqual(newDoctor.__str__(), "Dr. Gwen, Not")  # __str__ method works as planned


class AppointmentTestCase(TestCase):
    def test_appointment_creation(self):
        blankappt = Appointment()
        self.assertEqual(blankappt.appointment_name, "Appointment")  # default value works correctly

        newUser = User.objects.create_user(username="gcm3807", email="gcm3807@rit.edu", password="hamtaro",
                                           first_name="Not", last_name="Gwen")
        newDoctor = Doctor.objects.create(user=newUser)
        newDoctor.save()
        user1 = User.objects.create_user(username="fouyo", email="fouyo4@hotmail.com",
                                         password="error404", first_name="Gwen", last_name="Munson")
        user2 = User.objects.create_user(username="supermario", email="mariomario@hotmail.com",
                                         password="mushroom", first_name="Mario", last_name="Brother")
        newAssistant = Assistant(user=user1)
        newAssistant.save()
        newPatient = Patient(user=user2)
        newPatient.save()
        time = timezone.now()
        appt1 = Appointment(doctor=newDoctor, assistant=newAssistant, patient=newPatient,
                            start_date=time, start_time=time, end_time=time + datetime.timedelta(hours=1),
                            end_date=time)
        appt1.save()
        # Appointment's __str__ method works
        self.assertEqual(appt1.__str__(), "Appointment with {} and {} for {} from {}-{} to {}-{}".format
        (newDoctor, newAssistant, newPatient, time, time, time + datetime.timedelta(hours=1), time))


class LogTestCase(TestCase):
    def test_log_creation(self):
        with self.assertRaises(Exception):
            newUser = User.objects.create_user(username="gcm3807", email="gcm3807@rit.edu", password="hamtaro")
            log1 = SystemLog()
            log1.save()
        time = timezone.now()
        log2 = SystemLog(time=time, operator=newUser, action="Registered today.")
        self.assertEqual(log2.__str__(),
                         "{} - {}, {} - {}".format(time, newUser.last_name, newUser.first_name, "Registered today."))


class MedicalNotesTestCase(TestCase):
    def test_med_notes_creation(self):
        with self.assertRaises(Exception):
            newUser = User.objects.create_user(username="gcm3807", email="gcm3807@rit.edu", password="hamtaro")
            newUser.save()
            time = timezone.now()
            med = MedicalNotes(patient=newUser, time=time)

        pat = Patient(user=newUser)
        pat.save()
        med = MedicalNotes(patient=pat)
        self.assertEqual(False, med.birth_control)  # Default value is indeed false

        with self.assertRaises(Exception):
            med.medicine_name_1 = "This name is more than 50 characters, and, therefore, it should fail."
            med.save()
