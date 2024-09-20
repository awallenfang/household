# Generated by Django 5.0.8 on 2024-09-11 16:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0007_alter_user_selected_space'),
        ('todos', '0007_alter_todo_space'),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='assigned_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hub.user'),
        ),
        migrations.CreateModel(
            name='OrderedUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hub.user')),
            ],
        ),
        migrations.CreateModel(
            name='TodoRecurrency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateField(auto_created=True)),
                ('recurrency_turn', models.IntegerField(default=0)),
                ('day_rotation', models.IntegerField(default=7)),
                ('assigned_users', models.ManyToManyField(through='todos.OrderedUser', to='hub.user')),
            ],
        ),
        migrations.AddField(
            model_name='ordereduser',
            name='recurrent_todo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='todos.todorecurrency'),
        ),
        migrations.AddField(
            model_name='todo',
            name='recurrent_state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='todos.todorecurrency'),
        ),
    ]
