# Generated by Django 2.0.5 on 2020-04-20 09:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0110_auto_20200420_1531'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ttmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(blank=True, max_length=500, null=True)),
                ('project_code', models.CharField(blank=True, max_length=50, null=True)),
                ('district_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='TtmpDistrict', to='core.District')),
                ('municipality_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='TtmpGapaNapa', to='core.GapaNapa')),
                ('partner_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='TtmpPartner', to='core.Partner')),
                ('program_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='TtmpProgram', to='core.Program')),
                ('province_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='TtmpProvince', to='core.Province')),
                ('supplier_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='TtmpSupplier', to='core.Partner')),
            ],
        ),
    ]
