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
        if value not in ['pending', 'approved', 'rejected']:
            raise serializers.ValidationError("Status must be either 'approved' or 'rejected'")
        return value 