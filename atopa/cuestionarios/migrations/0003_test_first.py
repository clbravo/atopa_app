# Generated by Django 3.0.6 on 2020-05-19 14:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cuestionarios', '0002_auto_20200519_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='first',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cuestionarios.Test'),
        ),
    ]
