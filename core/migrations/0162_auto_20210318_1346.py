# Generated by Django 2.2.10 on 2021-03-18 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0161_auto_20210310_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='code',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
