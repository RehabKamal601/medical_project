from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentUpdateSerializer

class AppointmentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class DoctorAppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AppointmentPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'note']
    ordering_fields = ['date', 'time', 'created_at']
    ordering = ['-date', '-time']

    def get_queryset(self):
        # Get base queryset for doctor's appointments
        queryset = Appointment.objects.filter(doctor=self.request.user.doctor_profile)

        # Filter by status if provided
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)

        # Filter by date range if provided
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            Q(date__gt=today) | 
            Q(date=today, time__gt=timezone.now().time())
        ).order_by('date', 'time')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            Q(date__lt=today) | 
            Q(date=today, time__lt=timezone.now().time())
        ).order_by('-date', '-time')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        appointment = self.get_object()
        
        # Ensure the doctor owns this appointment
        if appointment.doctor != request.user.doctor_profile:
            return Response(
                {"detail": "You don't have permission to update this appointment"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AppointmentUpdateSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            appointment = serializer.save()
            
            # Return the full appointment data after update
            response_serializer = AppointmentSerializer(appointment)
            return Response(response_serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 