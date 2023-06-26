from django.db import models
from student.models import TypeModel
# from django.db.models.signals import pre_delete
# from django.dispatch import receiver

# Create your models here.
class OfferModel(models.Model):
    background_pic = models.ImageField(upload_to='offer/background_pic',verbose_name='背景图')
    text = models.TextField(verbose_name='通知书文本内容')
    is_using = models.BooleanField(verbose_name='是否启用')
    school = models.CharField(max_length=30,verbose_name='学校名称')
    time = models.CharField(max_length=20,verbose_name='时间')
    web_path = models.CharField(max_length=50,verbose_name='服务器前缀')
    type = models.ForeignKey(TypeModel,on_delete=models.SET_NULL,verbose_name='学生类型',help_text='学生类型',null=True,blank=True)

    class Meta:
        db_table = 'offer'
        verbose_name = '录取通知书'
        verbose_name_plural = verbose_name

# # 信号处理函数
# @receiver(pre_delete, sender=OfferModel)
# def delete_related_image(sender, instance, **kwargs):
#     # 获取图片字段的值
#     image = instance.background_pic

#     # 检查字段值是否存在，并删除本地存储文件
#     if image:
#         image.delete(save=False)