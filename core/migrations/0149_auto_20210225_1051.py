# Generated by Django 2.2.10 on 2021-02-25 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0148_project_approved_budget'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='partner_id',
            field=models.ManyToManyField(blank=True, null=True, related_name='ProjectPartner', to='core.Partner'),
        ),
        migrations.AlterField(
            model_name='partner',
            name='type_of_institution',
            field=models.CharField(blank=True, choices=[('Government', 'Government'), ('International NGO', 'International NGO'), ('National NGO', 'National NGO'), ('Multilateral', 'Multilateral'), ('Private Sector', 'Private Sector'), ('Local Government', 'Local Government'), ('Other Public Sector', 'Other Public Sector'), ('Regional NGO', 'Regional NGO'), ('Partner Country based NGO', 'Partner Country based NGO'), ('Public Private Partnership', 'Public Private Partnership'), ('Foundation', 'Foundation'), ('Private Sector in Provider Country', 'Private Sector in Provider Country'), ('Academic, Training and Research', 'Academic, Training and Research'), ('Private Sector in Aid Recipient Country', 'Private Sector in Aid Recipient Country'), ('Private Sector in Third Country', 'Private Sector in Third Country'), ('Academic, Training and Research', 'Academic, Training and Research'), ('Other', 'Other')], max_length=100, null=True),
        ),
    ]
