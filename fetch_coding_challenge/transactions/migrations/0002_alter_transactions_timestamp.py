# Generated by Django 3.2.8 on 2021-10-07 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='timestamp',
            field=models.DateField(),
        ),
    ]