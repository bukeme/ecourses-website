# Generated by Django 4.2.1 on 2023-06-15 15:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_alter_course_managers'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Rating',
        ),
    ]