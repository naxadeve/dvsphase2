# Generated by Django 2.2.10 on 2021-02-19 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0139_auto_20210215_1407'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=500, null=True)),
                ('email', models.CharField(blank=True, max_length=500, null=True)),
                ('type', models.CharField(blank=True, max_length=500, null=True)),
                ('subject', models.CharField(blank=True, max_length=500, null=True)),
                ('your_feedback', models.TextField(blank=True, null=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='feedbackfiles')),
            ],
        ),
    ]
