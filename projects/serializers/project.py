from rest_framework import serializers
from projects.models import Project
from accounts.models import User
from organizations.models import Organization


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing projects (lightweight)"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    project_manager_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'organization', 'organization_name',
            'status', 'status_display', 'priority', 'priority_display',
            'project_manager', 'project_manager_name',
            'completion_percentage', 'deadline', 'budget',
            'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completion_percentage']
    
    def get_project_manager_name(self, obj):
        return obj.project_manager.get_full_name() if obj.project_manager else None
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class ProjectSerializer(serializers.ModelSerializer):
    """Full serializer for project details"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    project_manager_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'organization', 'organization_name', 'name', 'description',
            'requirements', 'status', 'status_display', 'priority', 'priority_display',
            'deadline', 'budget', 'payment_details',
            'client_name', 'client_email', 'client_phone', 'client_company',
            'project_manager', 'project_manager_name',
            'created_by', 'created_by_name',
            'completion_percentage', 'started_at', 'completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'completion_percentage',
            'started_at', 'completed_at'
        ]
    
    def get_project_manager_name(self, obj):
        return obj.project_manager.get_full_name() if obj.project_manager else None
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None
    
    def validate_organization(self, value):
        """Validate organization exists"""
        if not Organization.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Organization does not exist.")
        return value
    
    def validate_project_manager(self, value):
        """Validate project manager is a valid user"""
        if value and not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Project manager does not exist.")
        return value
    
    def validate_deadline(self, value):
        """Validate deadline is not in the past"""
        from django.utils import timezone
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value
    
    def create(self, validated_data):
        """Create project and set created_by to current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update project and handle status changes"""
        status = validated_data.get('status', instance.status)
        
        # Auto-set started_at when status changes to IN_PROGRESS
        if status == 'IN_PROGRESS' and not instance.started_at:
            from django.utils import timezone
            validated_data['started_at'] = timezone.now()
        
        # Auto-set completed_at when status changes to COMPLETED
        if status == 'COMPLETED' and not instance.completed_at:
            from django.utils import timezone
            validated_data['completed_at'] = timezone.now()
            validated_data['completion_percentage'] = 100
        
        return super().update(instance, validated_data)
