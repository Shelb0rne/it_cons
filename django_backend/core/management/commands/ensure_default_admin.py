from django.contrib.auth.hashers import check_password, make_password
from django.core.management.base import BaseCommand

from core.models import AdminAccount


class Command(BaseCommand):
    help = "Create/update default admin account (login=admin, password=admin)"

    def handle(self, *args, **options):
        admin, created = AdminAccount.objects.get_or_create(
            email="admin",
            defaults={
                "password_hash": make_password("admin"),
                "status": AdminAccount.STATUS_ACTIVE,
            },
        )

        updated = False
        if not check_password("admin", admin.password_hash):
            admin.password_hash = make_password("admin")
            updated = True

        if admin.status != AdminAccount.STATUS_ACTIVE:
            admin.status = AdminAccount.STATUS_ACTIVE
            updated = True

        if updated:
            admin.save(update_fields=["password_hash", "status"])

        if created:
            self.stdout.write(self.style.SUCCESS("Created default admin: admin/admin"))
        elif updated:
            self.stdout.write(self.style.SUCCESS("Updated default admin credentials: admin/admin"))
        else:
            self.stdout.write(self.style.SUCCESS("Default admin already exists: admin/admin"))
