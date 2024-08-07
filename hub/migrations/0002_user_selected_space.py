# Generated by Django 5.0.8 on 2024-08-07 08:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='selected_space',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='selected_space', to='hub.sharedspace'),
            preserve_default=False,
        ),
    ]
