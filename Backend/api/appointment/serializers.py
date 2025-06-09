from rest_framework import serializers
from api.models import Appointment
from api.doctor.serializers import DoctorSerializer
from api.patient.serializers import PatientSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'doctor', 'doctor_details', 
            'patient', 'patient_details',
            'date', 'time', 'status', 'note',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class AppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status', 'note']
        
    def validate_status(self, value):
        valid_statuses = ['approved', 'rejected']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value 