from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_refund_admin_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="NearbyPlace",
            fields=[
                ("place_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("working_hours", models.CharField(blank=True, max_length=255, null=True)),
                ("average_check", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("travel_time_minutes", models.PositiveIntegerField(blank=True, null=True)),
                ("image", models.FileField(blank=True, null=True, upload_to="nearby_places/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "venue",
                    models.ForeignKey(
                        db_column="venue_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nearby_places",
                        to="core.venue",
                    ),
                ),
            ],
            options={
                "db_table": "nearby_place",
            },
        ),
    ]
