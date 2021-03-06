# Generated by Django 2.2.12 on 2020-04-10 13:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('panopticum', '0004_auto_20200322_1402_squashed_0006_auto_20200322_2325'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='componentversionmodel',
            options={'ordering': ['-version'], 'permissions': [('experts_change', 'Component Experts can to change'), ('qa_change', 'QA responsible an to change'), ('program_manager_change', 'Can program manager to change'), ('product_manager_change', 'Can product manager to change'), ('escalation_list_change', 'Can persons in escalation list to change'), ('architect_change', 'Can architect to change')]},
        ),
        migrations.AlterField(
            model_name='componentdependencymodel',
            name='type',
            field=models.CharField(choices=[('sync_rw', 'Requires - Sync R/W'), ('sync_ro', 'Requires - Sync R/O'), ('sync_wo', 'Requires - Sync W/O'), ('async_rw', 'Requires - Async R/W'), ('async_ro', 'Requires - Async R/O'), ('async_wo', 'Requires - Async W/O'), ('includes', 'Includes')], default='sync_rw', help_text='Requires - mean components communicates through API; Sync - component will block if dependent component is not available; Async - component will not be blocked; R/O - read-only dependency; R/W - read/write dependency', max_length=16),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='comments',
            field=models.TextField(blank=True, null=True, verbose_name='Version description'),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='owner_architect',
            field=models.ManyToManyField(blank=True, help_text='People who are in charge of the component architecture', related_name='architect_of', to=settings.AUTH_USER_MODEL, verbose_name='Architects'),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='owner_escalation_list',
            field=models.ManyToManyField(blank=True, help_text='People who are in charge of RnD-side support in case of incidents', related_name='escalation_list_of', to=settings.AUTH_USER_MODEL, verbose_name='Escalation list'),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='owner_expert',
            field=models.ManyToManyField(blank=True, help_text='All people who have experience with given component', related_name='expert_of', to=settings.AUTH_USER_MODEL, verbose_name='Experts'),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='owner_maintainer',
            field=models.ForeignKey(blank=True, help_text='Dev Lead or primary contributor', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='maintainer_of', to=settings.AUTH_USER_MODEL, verbose_name='Maintainer'),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='owner_product_manager',
            field=models.ManyToManyField(blank=True, related_name='product_manager_of', to=settings.AUTH_USER_MODEL, verbose_name='Product Managers'),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='owner_program_manager',
            field=models.ManyToManyField(blank=True, related_name='program_managed_of', to=settings.AUTH_USER_MODEL, verbose_name='Program Managers'),
        ),
        migrations.AlterField(
            model_name='componentversionmodel',
            name='owner_responsible_qa',
            field=models.ForeignKey(blank=True, help_text='QA Lead or primary QA expert', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='responsible_qa_of', to=settings.AUTH_USER_MODEL, verbose_name='Responsible QA'),
        ),
        migrations.AlterField(
            model_name='historicalcomponentversionmodel',
            name='comments',
            field=models.TextField(blank=True, null=True, verbose_name='Version description'),
        ),
        migrations.AlterField(
            model_name='historicalcomponentversionmodel',
            name='owner_maintainer',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='Dev Lead or primary contributor', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Maintainer'),
        ),
        migrations.AlterField(
            model_name='historicalcomponentversionmodel',
            name='owner_responsible_qa',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='QA Lead or primary QA expert', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Responsible QA'),
        ),
    ]
