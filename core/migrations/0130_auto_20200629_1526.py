# Generated by Django 2.2.10 on 2020-06-29 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0129_program_iati'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nepalsummary',
            name='value',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]