# Generated by Django 4.1.8 on 2023-06-23 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0007_studentmodel_offer'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentmodel',
            name='qrcode',
            field=models.FileField(blank=True, help_text='录取通知书二维码', null=True, upload_to='offer/student_offer', verbose_name='录取通知书二维码'),
        ),
    ]
