# Generated by Django 2.0.5 on 2020-04-01 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0103_auto_20200331_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='is_covid',
            field=models.BooleanField(default=False),
        ),
    ]
