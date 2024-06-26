# Generated by Django 4.1.8 on 2023-06-26 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0007_rename_prefix_offermodel_web_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offermodel',
            name='school',
            field=models.CharField(max_length=30, verbose_name='学校名称'),
        ),
        migrations.AlterField(
            model_name='offermodel',
            name='time',
            field=models.CharField(max_length=20, verbose_name='时间'),
        ),
        migrations.AlterField(
            model_name='offermodel',
            name='web_path',
            field=models.CharField(max_length=50, verbose_name='服务器前缀'),
        ),
    ]
