# Generated by Django 2.0.5 on 2019-09-30 05:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_auto_20190930_0540'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='program',
            name='budget',
        ),
    ]
