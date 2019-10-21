# Generated by Django 2.0.5 on 2019-10-18 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_auto_20191017_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gapanapa',
            name='geography',
            field=models.CharField(choices=[('Terai', 'Terai'), ('Hill', 'Hill'), ('Shivalik', 'Shivalik'), ('Mountain', 'Mountain'), ('High Mountain', 'High Mountain')], default='Terai', max_length=50),
        ),
        migrations.AlterField(
            model_name='gapanapa',
            name='gn_type_en',
            field=models.CharField(choices=[('Rural municipality', 'Rural municipality'), ('Urban municipality', 'Urban municipality'), ('Designated area', 'Designated area'), ('Sub metropolitan', 'Sub metropolitan'), ('Metropolitan', 'Metropolitan')], default='Rural municipality', max_length=50),
        ),
        migrations.AlterField(
            model_name='gapanapa',
            name='gn_type_np',
            field=models.CharField(choices=[('Development area', 'Development area'), ('Gaunpalika', 'Gaunpalika'), ('Hunting reserve', 'Hunting reserve'), ('Nagarpalika', 'Nagarpalika'), ('Mahanagarpalika', 'Mahanagarpalika'), ('Upamahanagarpalika', 'Upamahanagarpalika'), ('Wildlife reserve', 'Wildlife reserve'), ('Watershed and wildlife reserve', 'Watershed and wildlife reserve')], default='Gaunpalika', max_length=50),
        ),
    ]