from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Specialty(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Specialties"

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    full_name = models.CharField(max_length=255)
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True)
    profile_image = models.ImageField(upload_to='doctors/', null=True, blank=True)
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Doctor Availabilities"
        unique_together = ['doctor', 'day_of_week']

    def __str__(self):
        return f"{self.doctor.full_name} - {self.get_day_of_week_display()}" 