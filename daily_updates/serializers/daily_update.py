from rest_framework import serializers
from daily_updates.models import DailyUpdate
from accounts.models import User
from projects.models import Project
from organizations.models import Organization


class DailyUpdateSerializer(serializers.ModelSerializer):
    """Serializer for Daily Update model"""
    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_id = serializers.IntegerField(source='project.id', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = DailyUpdate
        fields = [
            'id', 'organization', 'organization_name', 'project', 'project_id', 
            'project_name', 'user', 'user_name', 'user_email',
            'description', 'figma_link', 'hours_worked', 'date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() if obj.user else None
    
    def create(self, validated_data):
        """Set the user and organization from the request"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
            if not validated_data.get('organization'):
                validated_data['organization'] = request.user.organization
        return super().create(validated_data)
    
    def validate(self, data):
        """Validate that the project belongs to the user's organization"""
        request = self.context.get('request')
        if request and request.user:
            project = data.get('project')
            if project and project.organization != request.user.organization:
                raise serializers.ValidationError({
                    'project': 'Project must belong to your organization.'
                })
        return data


class DailyUpdateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing daily updates"""
    user_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = DailyUpdate
        fields = [
            'id', 'organization_name', 'project_name', 'user_name',
            'description', 'figma_link', 'hours_worked', 'date',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() if obj.user else None
