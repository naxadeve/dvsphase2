# Generated by Django 2.0.4 on 2019-08-19 04:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20190819_0407'),
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fivew',
            name='organization_name',
        ),
        migrations.AddField(
            model_name='fivew',
            name='partner_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Partner', to='core.Partner'),
        ),
    ]
