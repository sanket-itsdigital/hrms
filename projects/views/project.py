from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from projects.models import Project
from projects.serializers import ProjectSerializer, ProjectListSerializer
from accounts.permissions import IsCEO


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing projects.
    
    list: Get list of projects (filtered by user role)
    retrieve: Get project details
    create: Create new project (CEO only)
    update: Update project (CEO/PM only)
    partial_update: Partially update project (CEO/PM only)
    destroy: Delete project (CEO only)
    """
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'organization', 'project_manager']
    search_fields = ['name', 'description', 'client_name', 'client_email', 'client_company']
    ordering_fields = ['created_at', 'updated_at', 'deadline', 'name', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use list serializer for list action, full serializer for others"""
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        queryset = Project.objects.select_related(
            'organization', 'project_manager', 'created_by'
        ).all()
        
        # CEO can see all projects
        if user.is_ceo:
            return queryset
        
        # Project Manager can see assigned projects
        if user.is_pm:
            return queryset.filter(
                Q(project_manager=user) | Q(assignments__user=user)
            ).distinct()
        
        # Developers/UIUX can see projects they're assigned to
        if user.is_dev or user.is_uiux:
            return queryset.filter(assignments__user=user).distinct()
        
        # BDE can see all projects (read-only)
        if user.is_bde:
            return queryset
        
        # HR and others: no access to projects
        return Project.objects.none()
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve', 'statistics', 'my_projects']:
            # Anyone authenticated can view
            return [IsAuthenticated()]
        elif self.action == 'create':
            # Only CEO can create - both permissions must pass
            return [IsAuthenticated(), IsCEO()]
        elif self.action in ['update', 'partial_update', 'assign', 'unassign']:
            # CEO and PM can update (checked in check_object_permissions)
            return [IsAuthenticated()]
        elif self.action == 'destroy':
            # Only CEO can delete - both permissions must pass
            return [IsAuthenticated(), IsCEO()]
        return super().get_permissions()
    
    def check_object_permissions(self, request, obj):
        """Check if user has permission to modify this object"""
        super().check_object_permissions(request, obj)
        
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # CEO can modify any project
            if request.user.is_ceo:
                return
            
            # PM can modify projects they manage
            if request.user.is_pm and obj.project_manager == request.user:
                return
            
            # Others cannot modify
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to modify this project.")
    
    def perform_create(self, serializer):
        """Set created_by when creating project"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign user to project"""
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from projects.models import ProjectAssignment
        from accounts.models import User
        
        try:
            user = User.objects.get(id=user_id)
            assignment, created = ProjectAssignment.objects.get_or_create(
                project=project,
                user=user,
                defaults={'assigned_by': request.user}
            )
            
            if created:
                return Response(
                    {'message': f'User {user.get_full_name()} assigned to project'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'message': 'User already assigned to this project'},
                    status=status.HTTP_200_OK
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        """Unassign user from project"""
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from projects.models import ProjectAssignment
        
        try:
            assignment = ProjectAssignment.objects.get(
                project=project,
                user_id=user_id
            )
            assignment.delete()
            return Response(
                {'message': 'User unassigned from project'},
                status=status.HTTP_200_OK
            )
        except ProjectAssignment.DoesNotExist:
            return Response(
                {'error': 'Assignment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get project statistics"""
        project = self.get_object()
        
        from tasks.models import Task
        
        tasks = Task.objects.filter(project=project)
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='COMPLETED').count()
        in_progress_tasks = tasks.filter(status='IN_PROGRESS').count()
        pending_tasks = tasks.filter(status='PENDING').count()
        
        from projects.models import ProjectAssignment
        assigned_users = ProjectAssignment.objects.filter(project=project).count()
        
        return Response({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'pending_tasks': pending_tasks,
            'completion_percentage': project.completion_percentage,
            'assigned_users': assigned_users,
            'days_remaining': (project.deadline - timezone.now().date()).days if project.deadline else None
        })
    
    @action(detail=False, methods=['get'])
    def my_projects(self, request):
        """Get projects assigned to current user"""
        user = request.user
        queryset = self.get_queryset().filter(
            Q(project_manager=user) | Q(assignments__user=user)
        ).distinct()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
