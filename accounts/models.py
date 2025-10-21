# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string

# ---------------- Custom User Model ----------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('management', 'Management'),
    )

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='doctor')
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def generate_password(self, length=8):
        """Generate a random password (kept for registration use)."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def generate_otp(self):
        """Generate a 6-digit OTP (string)."""
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.save(update_fields=['otp'])
        return self.otp

    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"


# ---------------- Patient File Model (for doctor uploads) ----------------
class PatientFile(models.Model):
    doctor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'doctor'},
        related_name='patient_files'
    )
    patient_name = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=50, default='UnknownID')
    disease = models.CharField(max_length=200, default='Unknown')
    file = models.FileField(upload_to='patient_files/', blank=False, null=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    access_email = models.EmailField(blank=True, null=True)  # recipient email for access

    def generate_otp(self):
        """Generate and persist a 6-digit OTP for this file."""
        self.otp = str(random.randint(100000, 999999))
        self.save(update_fields=['otp'])
        return self.otp

    def clear_otp(self):
        self.otp = None
        self.save(update_fields=['otp'])

    def __str__(self):
        return f"{self.patient_name} - {self.file.name}"


# ---------------- Patient Model (for management uploads / full records) ----------------
class Patient(models.Model):
    # Personal Info
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField()
    national_id = models.CharField(max_length=50, blank=True, default='')

    # Medical Info
    medical_history = models.TextField(blank=True, default='')
    diagnosis = models.TextField(blank=True, default='')
    lab_results = models.TextField(blank=True, default='')
    imaging_reports = models.TextField(blank=True, default='')
    prescriptions = models.TextField(blank=True, default='')
    immunizations = models.TextField(blank=True, default='')
    gender = models.CharField(max_length=20, blank=True, default='')

    # Financial Info
    insurance_details = models.TextField(blank=True, default='')
    payment_info = models.TextField(blank=True, default='')
    bank_account = models.CharField(max_length=50, blank=True, default='')

    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patients')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Generated PDF containing the full patient record
    pdf_file = models.FileField(upload_to='patient_pdfs/', blank=True, null=True)

    # OTP & sharing
    otp = models.CharField(max_length=6, blank=True, null=True)
    access_email = models.EmailField(blank=True, null=True)  # email of other management allowed to access

    def generate_otp(self):
        """Generate and persist a 6-digit OTP for PDF access."""
        self.otp = str(random.randint(100000, 999999))
        self.save(update_fields=['otp'])
        return self.otp

    def clear_otp(self):
        self.otp = None
        self.save(update_fields=['otp'])

    def __str__(self):
        return f"{self.full_name} - uploaded by {self.uploaded_by.username}"
