# Generated by Django 2.2.10 on 2021-02-19 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0140_feedbackform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackform',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
