# Generated by Django 3.0.6 on 2020-05-26 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='evaluacion',
            field=models.BooleanField(default=False),
        ),
    ]
