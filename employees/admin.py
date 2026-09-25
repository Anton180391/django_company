from django.contrib import admin

from .models import Employee, Skill, SkillLevel


class SkillLevelInline(admin.TabularInline):
    """Инлайн для редактирования навыков прямо на странице сотрудника."""

    model = SkillLevel
    extra = 1


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "last_name", "first_name", "gender", "workplace")
    list_filter = ("gender", "workplace")
    search_fields = ("last_name", "first_name", "patronymic")
    inlines = [SkillLevelInline]


@admin.register(SkillLevel)
class SkillLevelAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "skill", "level")
    list_filter = ("skill", "level")
    search_fields = ("employee__last_name", "skill__name")
