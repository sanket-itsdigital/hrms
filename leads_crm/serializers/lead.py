from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from accounts.models import User
from leads_crm.models import Lead


class LeadSerializer(serializers.ModelSerializer):
    assigned_users = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )
    assigned_users_detail = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            "id",
            "name",
            "company_name",
            "email",
            "phone",
            "stage",
            "expected_revenue",
            "probability",
            "notes",
            "assigned_to",
            "assigned_users",
            "assigned_users_detail",
            "converted_to_project",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "assigned_to",
            "converted_to_project",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        stage = attrs.get("stage") or getattr(self.instance, "stage", None)
        valid_stages = {choice[0] for choice in Lead.STAGE_CHOICES}
        if stage and stage not in valid_stages:
            raise ValidationError({"stage": "Invalid stage value."})
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        organization = getattr(user, "organization", None)
        if not organization:
            raise ValidationError(
                {"organization": "User is not associated with any organization."}
            )

        assigned_users = validated_data.pop("assigned_users", [])
        lead = Lead.objects.create(
            organization=organization,
            created_by=user,
            **validated_data,
        )

        if assigned_users:
            lead.assigned_users.set(assigned_users)
            lead.assigned_to = assigned_users[0]
        else:
            lead.assigned_to = user
            lead.assigned_users.add(user)

        lead.save(update_fields=["assigned_to"])
        return lead

    def update(self, instance, validated_data):
        assigned_users = validated_data.pop("assigned_users", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if assigned_users is not None:
            instance.assigned_users.set(assigned_users)
            instance.assigned_to = assigned_users[0] if assigned_users else None
            instance.save(update_fields=["assigned_to"])

        return instance

    def get_assigned_users_detail(self, obj):
        users = obj.assigned_users.all()
        return [
            {
                "id": user.id,
                "name": user.get_full_name() or user.email,
                "email": user.email,
            }
            for user in users
        ]
