from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Doctor, Specialty, DoctorAvailability
from api.models import DoctorProfile, Schedule, Appointment

User = get_user_model()

class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'name', 'description']

class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = DoctorAvailability
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_available']

class DoctorSerializer(serializers.ModelSerializer):
    specialty_name = serializers.CharField(source='specialty.name', read_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'full_name', 'specialty', 'specialty_name', 'profile_image',
            'rating', 'consultation_fee', 'is_available'
        ]

class DoctorDetailSerializer(serializers.ModelSerializer):
    specialty = SpecialtySerializer(read_only=True)
    availabilities = DoctorAvailabilitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'full_name', 'specialty', 'profile_image', 'bio',
            'experience_years', 'rating', 'consultation_fee', 'phone_number',
            'address', 'is_available', 'availabilities', 'created_at', 'updated_at'
        ]

class DoctorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'email', 'password', 'full_name', 'specialty', 'profile_image',
            'bio', 'experience_years', 'consultation_fee', 'phone_number',
            'address'
        ]
    
    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        # Create User instance
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            role='doctor'  # Set role as doctor
        )
        
        # Create Doctor instance
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor

class ScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for doctor's schedule - يستخدم لإدارة جدول مواعيد الدكتور
    """
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time']

    def get_day_name(self, obj):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[obj.day_of_week]

class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating doctor's profile - يستخدم لتحديث بيانات الدكتور
    """
    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'bio', 'experience_years', 'image']

class AppointmentListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing doctor's appointments - يستخدم لعرض قائمة المواعيد
    """
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.user.phone', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient_name', 'patient_phone', 
            'date', 'time', 'status', 'note',
            'created_at'
        ]

class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating appointment status - يستخدم لتحديث حالة الموعد
    """
    class Meta:
        model = Appointment
        fields = ['status', 'note']
        
    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Status must be either 'accepted' or 'rejected'")
        return value 