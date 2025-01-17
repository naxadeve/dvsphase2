# Generated by Django 2.0.5 on 2019-11-13 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0070_auto_20191113_0929'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fivew',
            old_name='consortium_partner_first',
            new_name='consortium_partner_first_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='consortium_partner_second',
            new_name='consortium_partner_second_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='consortium_partner_third',
            new_name='consortium_partner_third_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='district',
            new_name='district_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='implementing_partner_first',
            new_name='implementing_partner_first_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='implementing_partner_fourth',
            new_name='implementing_partner_fourth_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='implementing_partner_second',
            new_name='implementing_partner_second_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='implementing_partner_third',
            new_name='implementing_partner_third_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='local_partner_first',
            new_name='local_partner_first_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='local_partner_second',
            new_name='local_partner_second_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='local_partner_third',
            new_name='local_partner_third_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='municipality',
            new_name='municipality_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='partner_name',
            new_name='partner_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='program_name',
            new_name='program_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='province',
            new_name='province_id',
        ),
        migrations.RenameField(
            model_name='fivew',
            old_name='rp_person',
            new_name='representative_person',
        ),
        migrations.RemoveField(
            model_name='fivew',
            name='type_of_institution',
        ),
        migrations.AddField(
            model_name='partner',
            name='type_of_institution',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
