# Generated by Django 3.0.6 on 2020-05-19 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuestionarios', '0003_test_first'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='followUp',
            field=models.BooleanField(default=False),
        ),
    ]
