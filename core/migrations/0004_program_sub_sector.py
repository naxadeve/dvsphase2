# Generated by Django 2.0.4 on 2019-08-12 04:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20190812_0456'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='sub_sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='SubSector', to='core.SubSector'),
        ),
    ]
