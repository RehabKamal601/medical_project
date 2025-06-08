from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Doctor, Specialty, DoctorAvailability
from .serializers import (
    DoctorSerializer,
    DoctorDetailSerializer,
    SpecialtySerializer,
    DoctorRegistrationSerializer,
    DoctorAvailabilitySerializer
)

class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DoctorRegistrationSerializer
        elif self.action in ['retrieve', 'me']:
            return DoctorDetailSerializer
        return DoctorSerializer

    @action(detail=False, methods=['GET'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        doctor = get_object_or_404(Doctor, user=request.user)
        serializer = self.get_serializer(doctor)
        return Response(serializer.data)

    @action(detail=True, methods=['GET', 'PUT'], permission_classes=[permissions.IsAuthenticated])
    def availability(self, request, pk=None):
        doctor = self.get_object()
        
        if request.method == 'GET':
            availabilities = doctor.availabilities.all()
            serializer = DoctorAvailabilitySerializer(availabilities, many=True)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            if doctor.user != request.user:
                return Response(
                    {"detail": "You can only update your own availability"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = DoctorAvailabilitySerializer(data=request.data, many=True)
            if serializer.is_valid():
                # Clear existing availabilities
                doctor.availabilities.all().delete()
                # Create new availabilities
                for item in serializer.validated_data:
                    DoctorAvailability.objects.create(doctor=doctor, **item)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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