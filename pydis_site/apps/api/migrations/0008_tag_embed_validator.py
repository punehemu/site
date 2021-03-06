# Generated by Django 2.1.1 on 2018-09-23 10:07

import pydis_site.apps.api.models.bot.tag
import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='embed',
            field=django.contrib.postgres.fields.jsonb.JSONField(help_text='The actual embed shown by this tag.', validators=[pydis_site.apps.api.models.bot.tag.validate_tag_embed]),
        ),
    ]
