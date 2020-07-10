# Generated by Django 2.2.10 on 2020-06-30 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0130_auto_20200629_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='district',
            name='bbox',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='gapanapa',
            name='bbox',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='province',
            name='bbox',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]