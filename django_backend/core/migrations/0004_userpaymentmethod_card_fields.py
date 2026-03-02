from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_userprivacysettings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userpaymentmethod",
            name="provider_method_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="userpaymentmethod",
            name="card_number",
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AddField(
            model_name="userpaymentmethod",
            name="holder_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="userpaymentmethod",
            name="expires_at",
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name="userpaymentmethod",
            name="cvv_code",
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
