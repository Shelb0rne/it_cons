from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_eventimage"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserPrivacySettings",
            fields=[
                ("privacy_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("show_profile_in_reviews", models.BooleanField(default=False)),
                ("allow_email_notifications", models.BooleanField(default=True)),
                ("allow_sms_notifications", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="privacy_settings",
                        to="core.useraccount",
                    ),
                ),
            ],
            options={
                "db_table": "user_privacy_settings",
            },
        ),
    ]
