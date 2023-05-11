from django.db import models

# Create your models here.
class StudentModel(models.Model):
    id = models.CharField(max_length=18,primary_key=True,verbose_name='身份证号',help_text='身份证号')
    name = models.CharField(max_length=20,verbose_name='姓名',help_text='姓名')
    student_id = models.CharField(max_length=20,verbose_name='学号',help_text='学号',unique=True)
    sex_choice = ((1,'男'),(0,'女'))
    sex = models.CharField(choices=sex_choice,max_length=1,verbose_name='性别',help_text='性别')
    admission_date = models.SmallIntegerField(verbose_name='入学日期',help_text='入学日期')
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间',help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间',help_text='更新时间')
    access_count = models.IntegerField(default=0,verbose_name='访问次数',help_text='访问次数')

    class Meta:
        db_table = 'student'
        verbose_name = '学生'
        verbose_name_plural = verbose_name