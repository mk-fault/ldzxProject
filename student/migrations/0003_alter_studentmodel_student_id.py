# Generated by Django 4.1.8 on 2023-05-11 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_alter_studentmodel_options_alter_studentmodel_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentmodel',
            name='student_id',
            field=models.CharField(help_text='学号', max_length=20, unique=True, verbose_name='学号'),
        ),
    ]
