# Generated by Django 2.0.5 on 2019-09-25 07:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20190925_0744'),
    ]

    operations = [
        migrations.RenameField(
            model_name='indicatorvalue',
            old_name='gapanapa',
            new_name='gapanapa_id',
        ),
        migrations.RenameField(
            model_name='indicatorvalue',
            old_name='indicator',
            new_name='indicator_id',
        ),
    ]
