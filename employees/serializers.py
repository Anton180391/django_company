from rest_framework import serializers

from .models import Employee, EmployeeImage, Skill, SkillLevel


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]


class SkillLevelSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = SkillLevel
        fields = ["id", "skill", "skill_name", "level"]


class EmployeeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeImage
        fields = ["id", "image", "order"]


class EmployeeListSerializer(serializers.ModelSerializer):
    """Краткая информация — для списка."""

    full_name = serializers.CharField(read_only=True)
    experience_days = serializers.IntegerField(read_only=True)
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "experience_days",
            "skills",
            "hire_date",
        ]

    def get_skills(self, obj):
        return [
            {"name": sl.skill.name, "level": sl.level} for sl in obj.skill_levels.all()
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Полная информация — для детальной страницы."""

    full_name = serializers.CharField(read_only=True)
    experience_days = serializers.IntegerField(read_only=True)
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    workplace_number = serializers.IntegerField(
        source="workplace.desk_number", read_only=True
    )
    skill_levels = SkillLevelSerializer(many=True, read_only=True)
    images = EmployeeImageSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "gender",
            "gender_display",
            "hire_date",
            "experience_days",
            "workplace",
            "workplace_number",
            "description",
            "skill_levels",
            "images",
        ]


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """Для создания и обновления."""

    class Meta:
        model = Employee
        fields = [
            "user",
            "gender",
            "first_name",
            "last_name",
            "patronymic",
            "description",
            "hire_date",
            "workplace",
        ]

    def validate(self, data):
        """Вызываем валидатор модели."""
        instance = self.instance or Employee()
        for key, value in data.items():
            setattr(instance, key, value)
        instance.clean()
        return data


class EmployeeWorkplaceSerializer(serializers.ModelSerializer):
    """Для смотрителя — только workplace."""

    class Meta:
        model = Employee
        fields = ["id", "workplace"]
