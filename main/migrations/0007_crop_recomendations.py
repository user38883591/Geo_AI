# Generated by Django 5.1.2 on 2024-10-29 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_supplier_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crop_recomendations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nitrogen', models.FloatField()),
                ('phosphorus', models.FloatField()),
                ('potassium', models.FloatField()),
                ('temperature', models.FloatField()),
                ('humidity', models.FloatField()),
                ('ph', models.FloatField()),
                ('rainfall', models.FloatField()),
                ('recommended_crop', models.CharField(max_length=50)),
                ('prediction_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
