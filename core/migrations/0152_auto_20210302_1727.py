# Generated by Django 2.2.10 on 2021-03-02 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0151_auto_20210226_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='budget_spend',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='program',
            name='total_budget',
            field=models.FloatField(default=0),
        ),
    ]
