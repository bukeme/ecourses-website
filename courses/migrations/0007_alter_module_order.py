# Generated by Django 4.2.1 on 2023-06-08 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_alter_course_discount_module'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='order',
            field=models.IntegerField(blank=True),
        ),
    ]
