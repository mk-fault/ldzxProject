from typing import Any
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import viewsets

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics import renderPDF

from .models import OfferModel
from student.models import StudentModel
from .serializer import OfferSerializer


import io
from svglib.svglib import svg2rlg
import os
import copy
import re

# Create your views here.
# 录取通知书下载视图
class OfferDownloadView(APIView):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.offer = None

    def get_offer(cls):
        """
        获取启用的录取通知书
        """
        try:
            offer = OfferModel.objects.get(is_using=True)
        except:
            return None
        else:
            return offer
    
    def scale(self,drawing, scaling_factor):
        """
        对矢量图进行缩放
        """
        scaling_x = scaling_factor
        scaling_y = scaling_factor

        drawing.width = drawing.minWidth() * scaling_x
        drawing.height = drawing.height * scaling_y
        drawing.scale(scaling_x, scaling_y)
        return drawing
    
    # 将字符串中的变量替换为字典中的值
    def replace_str(self,ori_str, data):
    # 获取字符串中的变量
        var_list = re.findall(r'{(.*?)}', ori_str)
        # 将变量替换为字典中的值
        for var in var_list:
            ori_str = ori_str.replace('{'+var+'}', ' '+str(data[var])+' ')
        return ori_str
    
    def myfirst(self,canvas,docs):
        """
        绘制背景页面
        """
        canvas.saveState()
        pdfmetrics.registerFont(TTFont('SIMSUN', 'wqy-zenhei.ttc'))
        pdfmetrics.registerFont(TTFont('KAITI', 'ukai.ttc'))

        
        # 绘制背景图片
        # background_image_path = os.path.join(settings.MEDIA_ROOT,'offer','ts.jpg')
        background_image_path = self.offer.background_pic.path

        canvas.drawImage(background_image_path, 0, 0, width=canvas._pagesize[0], height=canvas._pagesize[1])

        # 绘制图标
        # pdf_canvas.drawImage(icon_image_path, 200, 600, width=200, height=200)

        # 绘制矢量图(印章)
        icon_image_path = os.path.join(settings.MEDIA_ROOT,'offer','zhang.svg')
        drawing = svg2rlg(icon_image_path)
        drawing = self.scale(drawing, 1)

        renderPDF.draw(drawing, canvas, 380, 30)

        # 标题
        canvas.setFont('KAITI', 40)
        canvas.setFillColorRGB(255, 0, 0)
        # canvas.setFillColorRGB(255, 0, 0)
        canvas.drawString(200, 550, f'录取通知书')

        # 落款
        canvas.setFont('SIMSUN', 20)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.drawString(400, 100, f'四川省泸定中学')
        canvas.drawString(200, 50, f'校长：                     2023 年 7 月 1 日')
        
        canvas.restoreState()

    def post(self,request):
        # 获取参数
        data = request.data
        id = data.get('id',None)
        student_id = data.get('student_id',None)
        name = data.get('name',None)
        class_num = data.get('class_num',None)
        admission_date = data.get('admission_date',None)
        sex = data.get('sex',None)

        # 判断参数是否完整
        if not id or not student_id or not name or not class_num or not admission_date or not sex:
            return Response({'msg':'请传入完整参数'},status=status.HTTP_400_BAD_REQUEST)
        
        else:
            # 注册字体
            pdfmetrics.registerFont(TTFont('SIMSUN', 'wqy-zenhei.ttc'))
            pdfmetrics.registerFont(TTFont('KAITI', 'ukai.ttc'))
            
            try:
                student = StudentModel.objects.get(**data)
            except:
                return Response({'msg':'未查询到该考生信息'},status=status.HTTP_404_NOT_FOUND)
            
            # 获取启用的录取通知书
            offer = self.get_offer()
            if offer is None:
                return Response({'msg':'未查询到启用的录取通知书，请联系管理员'},status=status.HTTP_404_NOT_FOUND)
            
            self.offer = offer
            
            # 通知书需要的学生信息
            student_data = {
                '姓名': student.name,
                '班级': student.class_num,
                "入学时间": student.admission_date,
                "性别":student.sex,
                "考号":student.student_id,
                "身份证号":student.id,
            }

            # ori_str = f'恭喜你被我校录取，成为我校{student_data["admission_date"]}级的一员，你的录取班级为{student_data["class_num"]}班。请持此通知书于{student_data["admission_date"]}年 9 月 1 日前来我校报到。'
            # 替换通知书中的变量
            ori_str = self.offer.text
            ori_str = self.replace_str(ori_str, student_data)

            # 创建PDF文档对象（用buffer来存储）
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            
            story = []

            # 通知书内容

            # 通知书内容样式
            styles = getSampleStyleSheet()
            st = styles["Normal"]
            st.fontName = 'SIMSUN'
            st.fontSize = 18
            st.leading = 40
            st.textColor = 'black'
            st.firstLineIndent = 40
            st.leftIndent = -20
            st.rightIndent = -20
            st.wordWrap = 'CJK'     # 设置自动换行
            st.alignment = 0        # 左对齐

            # img = Image(os.path.join(settings.MEDIA_ROOT,'offer','sl4.png'), width=300, height=200)
            # story.append(img)
            # story.append(Spacer(1, 200))

            # 学生姓名样式
            nt = copy.deepcopy(st)
            nt.firstLineIndent = 0

            # 加入空行
            story.append(Spacer(1, 300))

            name_para = Paragraph(f'{data["name"]}同学：',nt)
            paragraph = Paragraph(ori_str, st)
            story.append(name_para)
            story.append(paragraph)

            # 绘制印章
            # story.append(Spacer(1, 10))
            # img = Image(os.path.join(settings.MEDIA_ROOT,'offer','sl4.png'), width=200, height=200,hAlign='RIGHT')
            # story.append(img)

            # 生成pdf 
            doc.build(story,onFirstPage=self.myfirst)
        
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="hello.pdf"'

            response.write(buffer.getvalue())

            # 增加下载次数
            student.access_count += 1
            student.save()

            return response
        
class OfferViewset(viewsets.ModelViewSet):
    queryset = OfferModel.objects.all().order_by('-id')
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # 添加录取通知书时，将之前的录取通知书全部设置为不启用
        qs = self.queryset.filter(is_using=True)
        if qs.exists():
            for q in qs:
                q.is_using = False
                q.save()

        # 将新添加的录取通知书设置为启用(booleanfield默认为False)
        serializer.validated_data['is_using'] = True
        return super().perform_create(serializer)
    
    def perform_update(self, serializer):
        # 修改录取通知书时，将之前的录取通知书全部设置为不启用
        if serializer.validated_data.get('is_using',False):
            qs = self.queryset.filter(is_using=True)
            if qs.exists():
                for q in qs:
                    q.is_using = False
                    q.save()
        return super().perform_update(serializer)
