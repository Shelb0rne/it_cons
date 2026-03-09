from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_userpaymentmethod_card_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="refund",
            name="admin_comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="refund",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

