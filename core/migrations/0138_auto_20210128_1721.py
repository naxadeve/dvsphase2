# Generated by Django 2.2.10 on 2021-01-28 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0137_auto_20210128_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fivew',
            name='designation',
            field=models.CharField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name='fivew',
            name='remarks',
            field=models.CharField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name='fivew',
            name='reporting_line_ministry',
            field=models.CharField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name='fivew',
            name='status',
            field=models.CharField(choices=[('ongoing', 'Ongoing'), ('completed', 'Completed')], default='ongoing', max_length=1500),
        ),
    ]
