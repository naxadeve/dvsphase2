# Generated by Django 2.0.5 on 2019-10-17 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_auto_20191017_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gislayer',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
