from django.db import migrations


def create_groups(apps, schema_editor):
    """Создаём группы пользователей."""
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    # Смотритель — может только менять workplace сотрудника
    caretaker, _ = Group.objects.get_or_create(name="caretaker")
    change_employee = Permission.objects.filter(
        codename="change_employee",
        content_type__app_label="employees",
    ).first()
    if change_employee:
        caretaker.permissions.add(change_employee)

    # Администратор — может всё с сотрудниками
    admin_group, _ = Group.objects.get_or_create(name="administrator")
    employee_perms = Permission.objects.filter(
        content_type__app_label="employees",
        codename__in=[
            "add_employee",
            "change_employee",
            "delete_employee",
            "view_employee",
        ],
    )
    admin_group.permissions.add(*employee_perms)


def remove_groups(apps, schema_editor):
    """Откат — удаляем группы."""
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["caretaker", "administrator"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0003_employee_hire_date"),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]