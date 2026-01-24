from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from daily_updates.models import DailyUpdate
from daily_updates.serializers import DailyUpdateSerializer, DailyUpdateListSerializer


class DailyUpdateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing daily updates.
    
    list: Get list of daily updates (filtered by user role)
    retrieve: Get daily update details
    create: Create new daily update (DEV, UIUX, PM)
    update: Update daily update (own updates only for DEV/UIUX, own and project updates for PM)
    partial_update: Partially update daily update
    destroy: Delete daily update (own updates only)
    """
    queryset = DailyUpdate.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'user', 'organization', 'date']
    search_fields = ['description', 'user__first_name', 'user__last_name', 'project__name']
    ordering_fields = ['date', 'created_at', 'updated_at']
    ordering = ['-date', '-created_at']
    
    def get_serializer_class(self):
        """Use list serializer for list action, full serializer for others"""
        if self.action == 'list':
            return DailyUpdateListSerializer
        return DailyUpdateSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        queryset = DailyUpdate.objects.select_related(
            'organization', 'project', 'user'
        ).all()
        
        # CEO can see all updates
        if user.is_ceo:
            return queryset
        
        # HR can see all updates (read-only)
        if user.is_hr:
            return queryset
        
        # PM can see own updates and updates for assigned projects
        if user.is_pm:
            return queryset.filter(
                Q(user=user) | Q(project__project_manager=user)
            ).distinct()
        
        # DEV and UIUX can see own updates
        if user.is_dev or user.is_uiux:
            return queryset.filter(user=user)
        
        # BDE can see all updates (read-only)
        if user.is_bde:
            return queryset
        
        # Default: own updates only
        return queryset.filter(user=user)
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve', 'my_updates', 'by_date', 'by_project']:
            # All authenticated users can view (filtered by queryset)
            return [IsAuthenticated()]
        elif self.action == 'create':
            # DEV, UIUX, PM can create
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Users can modify their own updates (checked in check_object_permissions)
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def check_object_permissions(self, request, obj):
        """Check if user has permission to modify this object"""
        super().check_object_permissions(request, obj)
        
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # CEO can modify any update
            if request.user.is_ceo:
                return
            
            # PM can modify own updates and updates for projects they manage
            if request.user.is_pm:
                if obj.user == request.user:
                    return
                if obj.project.project_manager == request.user:
                    return
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You can only modify your own updates or updates for projects you manage.")
            
            # DEV and UIUX can only modify their own updates
            if request.user.is_dev or request.user.is_uiux:
                if obj.user == request.user:
                    return
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You can only modify your own updates.")
            
            # Others cannot modify
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to modify this update.")
    
    def perform_create(self, serializer):
        """Set user and organization when creating daily update"""
        user = self.request.user
        serializer.save(
            user=user,
            organization=user.organization
        )
    
    @action(detail=False, methods=['get'])
    def my_updates(self, request):
        """Get current user's daily updates"""
        updates = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(updates)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(updates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """Get daily updates for a specific date or date range"""
        date_str = request.query_params.get('date')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(date=date)
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__range=[start, end])
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Provide either "date" or both "start_date" and "end_date" parameters.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Get daily updates for a specific project"""
        project_id = request.query_params.get('project_id')
        
        if not project_id:
            return Response(
                {'error': 'project_id parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(project_id=project_id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's daily updates"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(date=today)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
