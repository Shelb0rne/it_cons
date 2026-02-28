from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventImage",
            fields=[
                ("image_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("image", models.FileField(upload_to="events/gallery/")),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "event",
                    models.ForeignKey(
                        db_column="event_id",
                        on_delete=models.deletion.CASCADE,
                        related_name="images",
                        to="core.event",
                    ),
                ),
            ],
            options={
                "db_table": "event_image",
            },
        ),
    ]
