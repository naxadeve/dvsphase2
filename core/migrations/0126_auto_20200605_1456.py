# Generated by Django 2.2.10 on 2020-06-05 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0125_fivew_providing_ta_to_provincial_government'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='program',
            name='difference',
        ),
        migrations.RemoveField(
            model_name='program',
            name='reported',
        ),
        migrations.RemoveField(
            model_name='program',
            name='reported_percentage',
        ),
        migrations.RemoveField(
            model_name='program',
            name='unallocated',
        ),
        migrations.RemoveField(
            model_name='program',
            name='unreported_percentage',
        ),
        migrations.AlterField(
            model_name='program',
            name='total_budget',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
