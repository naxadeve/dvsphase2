# Generated by Django 2.0.5 on 2020-03-31 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0099_auto_20200331_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gapanapa',
            name='code',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]