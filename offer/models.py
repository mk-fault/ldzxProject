from django.db import models

# Create your models here.
class OfferModel(models.Model):
    background_pic = models.ImageField(upload_to='offer/background_pic',verbose_name='背景图')
    text = models.TextField(verbose_name='通知书文本内容')
    is_using = models.BooleanField(verbose_name='是否启用')

    class Meta:
        db_table = 'offer'
        verbose_name = '录取通知书'
        verbose_name_plural = verbose_name