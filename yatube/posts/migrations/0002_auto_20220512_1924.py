# Generated by Django 2.2.16 on 2022-05-12 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Идентификатор'),
        ),
    ]
