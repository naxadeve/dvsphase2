# Generated by Django 2.0.5 on 2019-09-26 04:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_auto_20190925_0843'),
    ]

    operations = [
        migrations.RenameField(
            model_name='program',
            old_name='marker',
            new_name='marker_value',
        ),
    ]
