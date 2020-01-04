# Generated by Django 2.1 on 2020-01-04 21:39

from django.db import migrations
import panopticum.models


class Migration(migrations.Migration):

    dependencies = [
        ('panopticum', '0020_auto_20191230_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='componentversionmodel',
            name='dev_build_jenkins_job',
            field=panopticum.models.SmartTextField(blank=True, default='', help_text='Multiple links allowed', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='dev_commit_link',
            field=panopticum.models.SmartTextField(blank=True, default='', help_text='Multiple links allowed', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='dev_docs',
            field=panopticum.models.SmartTextField(blank=True, default='', help_text='Multiple links allowed', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='dev_jira_component',
            field=panopticum.models.SmartTextField(blank=True, default='', help_text='Multiple links allowed', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='dev_public_docs',
            field=panopticum.models.SmartTextField(blank=True, default='', help_text='Multiple links allowed', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='dev_public_repo',
            field=panopticum.models.SmartTextField(blank=True, default='', help_text='Multiple links allowed', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='dev_raml',
            field=panopticum.models.SmartTextField(blank=True, default='', help_text='Multiple links allowed', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='dev_repo',
            field=panopticum.models.SmartTextField(blank=True, default='', help_text='Multiple links allowed', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='datacentermodel',
            name='grafana',
            field=panopticum.models.SmartTextField(blank=True, default='', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='datacentermodel',
            name='info',
            field=panopticum.models.SmartTextField(blank=True, default='', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='datacentermodel',
            name='metrics',
            field=panopticum.models.SmartTextField(blank=True, default='', verbose_name=''),
        ),
    ]