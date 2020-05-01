# Generated by Django 2.2.10 on 2020-04-30 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covid', '0007_covidspecificprogram'),
    ]

    operations = [
        migrations.AddField(
            model_name='covidspecificprogram',
            name='budget',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='covidspecificprogram',
            name='component',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='covidspecificprogram',
            name='covid_priority_3_12_Months',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='covidspecificprogram',
            name='covid_recovery_priority',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='covidspecificprogram',
            name='delivery_in_lockdown',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='covidspecificprogram',
            name='kathmandu_activity',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='covidspecificprogram',
            name='partner',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='covidspecificprogram',
            name='program',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='covidspecificprogram',
            name='project_status',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='covidspecificprogram',
            name='providing_ta_to_local_government',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='covidspecificprogram',
            name='second_tier_partner',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='covidspecificprogram',
            name='sector',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]