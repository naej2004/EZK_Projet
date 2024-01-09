# Generated by Django 5.0 on 2023-12-27 12:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Numero',
            fields=[
                ('idNumero', models.AutoField(primary_key=True, serialize=False)),
                ('Numero', models.CharField(max_length=45)),
                ('Quantite', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Numero',
                'verbose_name_plural': 'Numeros',
                'db_table': 'Numero',
            },
        ),
        migrations.AlterField(
            model_name='pneu',
            name='Numero',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='myapp.numero'),
        ),
    ]