# Generated by Django 2.2.10 on 2021-03-10 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0158_auto_20210310_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicatorvalue',
            name='value',
            field=models.CharField(blank=True, default=None, max_length=500, null=True),
        ),
    ]
