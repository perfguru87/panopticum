# Generated by Django 2.1 on 2020-01-04 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panopticum', '0021_auto_20200105_0039'),
    ]

    operations = [
        migrations.AddField(
            model_name='componentmodel',
            name='is_library',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Component is a library/framework'),
        ),
    ]