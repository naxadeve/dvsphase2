# Generated by Django 2.0.5 on 2019-09-12 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_traveltime'),
    ]

    operations = [
        migrations.AddField(
            model_name='traveltime',
            name='season',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]