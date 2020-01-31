# Generated by Django 2.0.5 on 2020-01-07 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0088_auto_20200107_1708'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fivew',
            old_name='project_id',
            new_name='component_id',
        ),
        migrations.AlterField(
            model_name='fivew',
            name='allocated_budget',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='fivew',
            name='contract_value',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='fivew',
            name='female_beneficiary',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='fivew',
            name='male_beneficiary',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='fivew',
            name='total_beneficiary',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]