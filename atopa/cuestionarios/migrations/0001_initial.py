# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-02 10:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teacher', '0001_initial'),
        ('alumnos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlumnoTests',
            fields=[
                ('username', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('answer', models.BooleanField(default=False)),
                ('idAl', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alumnos.Alumno')),
            ],
        ),
        migrations.CreateModel(
            name='Grupo_edad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grupoedad', models.CharField(max_length=30)),
                ('franjaedad', models.CharField(default=0, max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Pregunta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pregunta', models.TextField(max_length=500)),
                ('grupo_edad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuestionarios.Grupo_edad')),
            ],
        ),
        migrations.CreateModel(
            name='Preguntas_test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuestionarios.Pregunta')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=32, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Creation date')),
                ('uploaded', models.BooleanField(default=False)),
                ('downloaded', models.BooleanField(default=False)),
                ('closed', models.BooleanField(default=False)),
                ('clase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alumnos.Clase')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tipo_estructura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=3)),
                ('descripcion', models.TextField(blank=True, max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Tipo_pregunta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=3)),
                ('descripcion', models.TextField(blank=True, max_length=300)),
            ],
        ),
        migrations.AddField(
            model_name='test',
            name='estructura',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuestionarios.Tipo_estructura'),
        ),
        migrations.AddField(
            model_name='test',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='test',
            name='year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.Year'),
        ),
        migrations.AddField(
            model_name='preguntas_test',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuestionarios.Test'),
        ),
        migrations.AddField(
            model_name='pregunta',
            name='tipo_estructura',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuestionarios.Tipo_estructura'),
        ),
        migrations.AddField(
            model_name='pregunta',
            name='tipo_pregunta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuestionarios.Tipo_pregunta'),
        ),
        migrations.AddField(
            model_name='alumnotests',
            name='idTest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cuestionarios.Test'),
        ),
    ]
