# Generated by Django 2.2.10 on 2021-03-30 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0166_faq_termsandcondition'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='sector_budget',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
