# Generated by Django 2.2.10 on 2020-06-30 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0131_auto_20200630_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='district',
            name='bbox',
            field=models.CharField(blank=True, max_length=600, null=True),
        ),
        migrations.AlterField(
            model_name='gapanapa',
            name='bbox',
            field=models.CharField(blank=True, max_length=600, null=True),
        ),
        migrations.AlterField(
            model_name='province',
            name='bbox',
            field=models.CharField(blank=True, max_length=600, null=True),
        ),
    ]
