# Generated by Django 3.2 on 2021-07-10 10:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Recipes', '0005_recipecategory_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipecategory',
            name='slug',
        ),
    ]