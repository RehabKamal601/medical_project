from rest_framework import serializers
from api.models import PatientProfile

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user', 'age', 'gender', 'address',
            'medical_history', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 