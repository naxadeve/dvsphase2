# Generated by Django 2.0.5 on 2019-11-13 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0069_auto_20191113_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fivew',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='fivew',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
