from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.conf import settings
from django.shortcuts import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser,AllowAny,IsAuthenticated
from rest_framework import mixins

from .models import StudentModel
from .serializers import StudentModelSerializer,StudentMultiCreateSerializer
from .filters import StudentFilter

import pandas as pd
import datetime
import os
from reportlab.pdfbase.ttfonts import TTFont # 字体类
from reportlab.pdfbase import pdfmetrics   # 注册字体
from reportlab.pdfgen import canvas # 画布类

# Create your views here.

# 管理学生信息视图
class StudentViewset(viewsets.ModelViewSet):
    queryset = StudentModel.objects.all().order_by('student_id')
    serializer_class = StudentModelSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StudentFilter

# 批量添加学生视图
class StudentMultiCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        obj = request.data.get('students')
        try:
            df = pd.read_excel(obj)
        except:
            return Response({'msg':'文件格式错误,请传入xlsx文件'},status=status.HTTP_400_BAD_REQUEST)

        # 检查上传的数据中是否存在身份证号重复
        duplicates = list(df[df.duplicated(['身份证号'], keep=False)]['身份证号'].unique())
        if duplicates:
            return Response({'msg':f'身份证{duplicates}存在重复值,请检查后重新提交'})
        
        # 检查上传的数据中是否存在考号重复
        duplicates = list(df[df.duplicated(['考号'], keep=False)]['考号'].unique())
        if duplicates:
            return Response({'msg':f'考号{duplicates}存在重复值,请检查后重新提交'})

        # 将DF转化为字典
        data_list = df.to_dict(orient='records')
        sex_dict = {'男':1,'女':0}
        for data in data_list:
            data['性别'] = sex_dict[data['性别']]
            data['id'] = data.pop('身份证号')
            data['name'] = data.pop('姓名')
            data['sex'] = data.pop('性别')
            data['student_id'] = data.pop('考号')
            data['admission_date'] = data.pop('入学时间')
            data['class_num'] = data.pop('班级')
            # StudentModel.objects.update_or_create(id=data['身份证号'],name=data['姓名'],sex=data['性别'],student_id=data['学号'],admission_date=data['入学时间'])
        
        # 反序列化
        ser = StudentMultiCreateSerializer(data=data_list,many=True)
        if ser.is_valid():
            ser.save()
            default_storage.save(f'{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.xlsx',obj)
            return Response(ser.data,status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)

# 批量删除学生视图
class StudentMultiDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        data = request.data
        d_type = data.get('delete_type')
        d_list = data.get('delete_list')
        if not d_type:
            return Response({'msg':'请传入删除的类型(id or student_id)'},status=status.HTTP_400_BAD_REQUEST)
        
        if not d_list:
            return Response({'msg':'请传入删除的列表'},status=status.HTTP_400_BAD_REQUEST)

        # 按照身份证号删除
        if d_type == 'id':
            for id in d_list:
                try:
                    StudentModel.objects.get(id=id).delete()
                except:
                    return Response({'msg':f'身份证为[{id}]的学生不存在，请刷新后重试'},status=status.HTTP_404_NOT_FOUND)
            return Response({'msg':'删除成功'},status=status.HTTP_204_NO_CONTENT)
        
        # 按照学号删除
        elif d_type == 'student_id':
            for student_id in d_list:
                try:
                    StudentModel.objects.get(student_id=student_id).delete()
                except:
                    return Response({'msg':f'考号为[{student_id}]的学生不存在，请刷新后重试'},status=status.HTTP_404_NOT_FOUND)
            return Response({'msg':'删除成功'},status=status.HTTP_204_NO_CONTENT)
        
        # 按照入学时间删除
        elif d_type == 'admission_date':
            for admission_date in d_list:
                try:
                    StudentModel.objects.filter(admission_date=admission_date).delete()
                except:
                    return Response({'msg':'删除失败，请稍后重试'},status=status.HTTP_404_NOT_FOUND)
            return Response({'msg':'删除成功'},status=status.HTTP_204_NO_CONTENT)
        
        else:
            return Response({'msg':'删除类型错误'},status=status.HTTP_400_BAD_REQUEST)

# 单个学生查询视图
class StudentDetailView(generics.RetrieveAPIView):
    queryset = StudentModel.objects.all()
    serializer_class = StudentModelSerializer
    permission_classes = [AllowAny]

# 录取通知书下载视图
class OfferDownloadView(APIView):
    def post(self,request):
        data = request.data
        id = data.get('id',None)
        if id:
            pdfmetrics.registerFont(TTFont('SIMSUN', 'wqy-zenhei.ttc'))
            pdfmetrics.registerFont(TTFont('KAITI', 'ukai.ttc'))
            try:
                student = StudentModel.objects.get(id=id)
            except:
                return Response({'msg':'学生不存在'},status=status.HTTP_404_NOT_FOUND)
            student_data = {
                'name': student.name,
                'class_num': student.class_num,
                "admission_date": student.admission_date
            }
            background_image_path = os.path.join(settings.MEDIA_ROOT,'ts.jpg')
            icon_image_path = os.path.join(settings.MEDIA_ROOT,'21.jpg')

            # 创建PDF画布
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="admission_letter.pdf"'
            pdf_canvas = canvas.Canvas(response)
            

            # 绘制背景图片
            pdf_canvas.drawImage(background_image_path, 0, 0, width=pdf_canvas._pagesize[0], height=pdf_canvas._pagesize[1])

            # 绘制图标
            pdf_canvas.drawInlineImage(icon_image_path, 200, 600, width=200, height=200)

            # 标题
            pdf_canvas.setFont('KAITI', 40)
            pdf_canvas.setFillColorRGB(255, 0, 0)
            pdf_canvas.drawString(200, 550, f'录取通知书')

            # 添加学生信息
            pdf_canvas.setFont('SIMSUN', 20)
            pdf_canvas.setFillColorRGB(0, 0, 0)
            pdf_canvas.drawString(80, 500, f'{student_data["name"]} 同学:')
            pdf_canvas.drawString(80, 450, f'恭喜你被我校录取，成为我校 {student_data["admission_date"]} 级的一员，你的')
            pdf_canvas.drawString(40, 400, f'录取班级为 {student_data["class_num"]} 班。请持此通知书于 {student_data["admission_date"]} 年 9 月 1 日前')
            pdf_canvas.drawString(40, 350, f'来我校报到。')

            # 落款
            pdf_canvas.drawString(400, 100, f'四川省泸定中学')
            pdf_canvas.drawString(200, 50, f'校长：                     2023 年 7 月 1 日')


            # 保存PDF文件
            pdf_canvas.save()

            return response
        return Response({'msg':'请传入学生id'},status=status.HTTP_400_BAD_REQUEST)
    
