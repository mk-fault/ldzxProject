# Generated by Django 4.1.8 on 2023-05-18 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OfferModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('background_pic', models.ImageField(upload_to='offer/background_pic', verbose_name='背景图')),
                ('text', models.TextField(verbose_name='通知书文本内容')),
                ('is_using', models.BooleanField(default=True, verbose_name='是否启用')),
            ],
            options={
                'verbose_name': '录取通知书',
                'verbose_name_plural': '录取通知书',
                'db_table': 'offer',
            },
        ),
    ]
