from django.db import migrations
from django.contrib.auth.hashers import make_password


VIEWER_GROUP_NAME = "waybill_viewers"
VIEWER_USERNAME = "123"
VIEWER_PASSWORD = "Sasha-717307"


def create_waybill_viewer(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    group, _ = Group.objects.get_or_create(name=VIEWER_GROUP_NAME)
    permissions = Permission.objects.filter(
        codename__in=[
            "view_waybill",
            "view_waybillitem",
        ]
    )
    group.permissions.set(permissions)

    user, created = User.objects.get_or_create(
        username=VIEWER_USERNAME,
        defaults={
            "email": "viewer@transferapp.local",
            "is_active": True,
        },
    )

    if created or not user.has_usable_password():
        user.password = make_password(VIEWER_PASSWORD)
        user.save(update_fields=["password"])

    user.groups.add(group)


def remove_waybill_viewer(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")

    User.objects.filter(username=VIEWER_USERNAME).delete()
    Group.objects.filter(name=VIEWER_GROUP_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("waybills", "0002_waybill_additional_info_waybill_delivery_date_and_more"),
    ]

    operations = [
        migrations.RunPython(create_waybill_viewer, remove_waybill_viewer),
    ]
