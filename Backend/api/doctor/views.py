from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Doctor, Specialty, DoctorAvailability
from .serializers import (
    DoctorSerializer,
    DoctorDetailSerializer,
    SpecialtySerializer,
    DoctorRegistrationSerializer,
    DoctorAvailabilitySerializer
)
from api.models import Appointment
from api.appointment.serializers import AppointmentSerializer

User = get_user_model()

class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = DoctorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Create user
            user_data = {
                'username': serializer.validated_data['email'],
                'email': serializer.validated_data['email'],
                'password': serializer.validated_data['password']
            }
            user = User.objects.create_user(**user_data)
            
            # Add user to doctor group
            doctor_group = Group.objects.get(name='doctor')
            user.groups.add(doctor_group)
            
            # Create doctor profile
            doctor = Doctor.objects.create(
                user=user,
                full_name=serializer.validated_data['full_name'],
                specialty=serializer.validated_data['specialty'],
                bio=serializer.validated_data.get('bio', ''),
                experience_years=serializer.validated_data.get('experience_years', 0),
                consultation_fee=serializer.validated_data['consultation_fee'],
                phone_number=serializer.validated_data['phone_number'],
                address=serializer.validated_data['address']
            )
            
            return Response(
                DoctorDetailSerializer(doctor).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        doctor = get_object_or_404(Doctor, user=request.user)
        serializer = self.get_serializer(doctor)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        doctor = self.get_object()
        # Get query parameters for filtering
        status_filter = request.query_params.get('status', None)
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)

        # Start with all appointments for this doctor
        appointments = Appointment.objects.filter(doctor=doctor)

        # Apply filters
        if status_filter:
            appointments = appointments.filter(status=status_filter)
        if date_from:
            appointments = appointments.filter(date__gte=date_from)
        if date_to:
            appointments = appointments.filter(date__lte=date_to)

        # Order by date and time
        appointments = appointments.order_by('date', 'time')
        
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def availability(self, request, pk=None):
        doctor = self.get_object()
        
        if request.method == 'GET':
            availabilities = DoctorAvailability.objects.filter(doctor=doctor)
            serializer = DoctorAvailabilitySerializer(availabilities, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Bulk create/update availabilities
            availabilities_data = request.data
            if not isinstance(availabilities_data, list):
                return Response(
                    {"error": "Expected a list of availabilities"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Clear existing availabilities
            DoctorAvailability.objects.filter(doctor=doctor).delete()
            
            # Create new availabilities
            new_availabilities = []
            for availability in availabilities_data:
                availability['doctor'] = doctor.id
                serializer = DoctorAvailabilitySerializer(data=availability)
                if serializer.is_valid():
                    new_availabilities.append(DoctorAvailability(**serializer.validated_data))
                else:
                    return Response(
                        serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            DoctorAvailability.objects.bulk_create(new_availabilities)
            return Response(
                DoctorAvailabilitySerializer(new_availabilities, many=True).data,
                status=status.HTTP_201_CREATED
            )

    @action(detail=True, methods=['post'])
    def update_appointment_status(self, request, pk=None):
        doctor = self.get_object()
        appointment_id = request.data.get('appointment_id')
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')

        try:
            appointment = Appointment.objects.get(
                id=appointment_id,
                doctor=doctor
            )
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if new_status not in ['accepted', 'rejected']:
            return Response(
                {"error": "Invalid status. Must be 'accepted' or 'rejected'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = new_status
        appointment.note = notes
        appointment.save()

        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=['get'])
    def upcoming_appointments(self, request, pk=None):
        doctor = self.get_object()
        today = timezone.now().date()
        appointments = Appointment.objects.filter(
            doctor=doctor,
            date__gte=today
        ).order_by('date', 'time')
        
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def past_appointments(self, request, pk=None):
        doctor = self.get_object()
        today = timezone.now().date()
        appointments = Appointment.objects.filter(
            doctor=doctor,
            date__lt=today
        ).order_by('-date', '-time')
        
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def search(self, request):
        specialty = request.query_params.get('specialty', '')
        name = request.query_params.get('name', '')
        
        queryset = self.get_queryset()
        
        if specialty:
            queryset = queryset.filter(specialty__name__icontains=specialty)
        if name:
            queryset = queryset.filter(full_name__icontains=name)
        
        serializer = DoctorSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def toggle_availability(self, request, pk=None):
        doctor = self.get_object()
        
        if doctor.user != request.user:
            return Response(
                {"detail": "You can only update your own availability status"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        doctor.is_available = not doctor.is_available
        doctor.save()
        
        return Response({
            "status": "success",
            "is_available": doctor.is_available
        }) 