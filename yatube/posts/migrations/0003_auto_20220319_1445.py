# Generated by Django 2.2.19 on 2022-03-19 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20220319_1332'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='descriptiom',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='group',
            old_name='text',
            new_name='title',
        ),
        migrations.AddField(
            model_name='group',
            name='slug',
            field=models.SlugField(null=True, unique=True),
        ),
    ]
