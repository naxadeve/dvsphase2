# Generated by Django 2.2.10 on 2020-06-05 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0124_auto_20200605_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='fivew',
            name='providing_ta_to_provincial_government',
            field=models.CharField(blank=True, choices=[('NA - Complete', 'NA - Complete'), ('Yes', 'Yes'), ('Partial High', 'Partial High'), ('Partial Low', 'Partial Low'), ('No', 'No')], default='No', max_length=500, null=True),
        ),
    ]
