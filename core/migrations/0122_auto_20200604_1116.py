# Generated by Django 2.2.10 on 2020-06-04 05:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0121_auto_20200604_1102'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gislayer',
            old_name='category',
            new_name='geo_type',
        ),
        migrations.AddField(
            model_name='gislayer',
            name='identifier_key',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='GisPop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, max_length=100, null=True)),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('type', models.CharField(blank=True, max_length=100, null=True)),
                ('layer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='GisPop', to='core.GisLayer')),
            ],
        ),
    ]