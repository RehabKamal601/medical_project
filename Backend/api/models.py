from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLES)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField()
    bio = models.TextField()
    image = models.ImageField(upload_to='doctors/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

class PatientProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()}"

class Schedule(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ['doctor', 'day_of_week']

    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} - {self.created_at.strftime('%Y-%m-%d %H:%M')}" 