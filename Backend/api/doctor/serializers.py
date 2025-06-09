from rest_framework import serializers
from .models import Doctor, Specialty, DoctorAvailability
from django.contrib.auth import get_user_model
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
            password=password
        )
        
        # Create Doctor instance
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor 