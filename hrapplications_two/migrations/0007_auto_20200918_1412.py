# Generated by Django 3.1.1 on 2020-09-18 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrapplications_two', '0006_remove_legacy_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='approved',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]