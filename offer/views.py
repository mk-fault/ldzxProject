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
from .serializers import OfferSerializer
from .pagination import OfferPagination
from .filters import OfferFilter
from student.serializers import StudentInfoSerializer
from utils.funcs import encode_string,generate_qrcode


import io
from svglib.svglib import svg2rlg
import os
import copy
import re
import pdf2image
import tempfile
import psutil


# Create your views here.

class OfferViewset(viewsets.ModelViewSet):
    queryset = OfferModel.objects.all().order_by('-id')
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OfferPagination
    filterset_class = OfferFilter

    def perform_create(self, serializer):
        # 添加录取通知书时，将同类型的录取通知书全部设置为不启用
        qs = self.queryset.filter(type=serializer.validated_data['type'],is_using=True)
        if qs.exists():
            for q in qs:
                q.is_using = False
                q.save()
        # 将新添加的录取通知书设置为启用(booleanfield默认为False)
        serializer.validated_data['is_using'] = True
        return super().perform_create(serializer)
    
    def perform_update(self, serializer):
        # 修改录取通知书时，将同类型的录取通知书全部设置为不启用
        if serializer.validated_data.get('is_using',False):
            qs = self.queryset.filter(type=self.get_object().type,is_using=True)
            if qs.exists():
                for q in qs:
                    q.is_using = False
                    q.save()

        # 修改录取通知书时，将同类型学生原的通知书删除
        qs = StudentModel.objects.filter(type=self.get_object().type)
        if qs.exists():
            for q in qs:
                q.offer.delete()
                q.qrcode.delete()
        return super().perform_update(serializer)


# 录取通知书下载视图
class OfferDownloadView(APIView):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.offer = None
        self.qrcode = None

    @classmethod
    def get_offer(cls,type):
        """
        获取启用的录取通知书
        """
        try:
            offer = OfferModel.objects.get(type=type,is_using=True)
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
    
    
    def replace_str(self,ori_str, data):
        """
        替换字符串中的变量
        """
    # 获取字符串中的变量
        var_list = re.findall(r'{(.*?)}', ori_str)
        # 将变量替换为字典中的值
        for var in var_list:
            try:
                ori_str = ori_str.replace('{'+var+'}', ' '+str(data[var])+' ')
            except:
                return None
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

        # 绘制二维码
        qrcode_path = self.qrcode
        canvas.drawImage(qrcode_path, 50, 50, width=80, height=80)
        canvas.setFont('SIMSUN', 10)
        canvas.drawString(45,25,'扫码验证录取通知书')

        # 绘制矢量图(印章)
        icon_image_path = os.path.join(settings.MEDIA_ROOT,'offer','static','ldzx.svg')
        
        drawing = svg2rlg(icon_image_path)
        drawing = self.scale(drawing, 0.45)

        renderPDF.draw(drawing, canvas, 380, 20)

        # 标题
        canvas.setFont('KAITI', 40)
        canvas.setFillColorRGB(255, 0, 0)
        # canvas.setFillColorRGB(255, 0, 0)
        canvas.drawString(200, 650, f'录取通知书')

        # 落款
        canvas.setFont('SIMSUN', 20)
        canvas.setFillColorRGB(0, 0, 0)
        # canvas.drawString(400, 100, f'四川省泸定中学')
        # canvas.drawString(395, 50, f'2023 年 7 月 1 日')
        canvas.drawString(400, 100, self.offer.school)
        canvas.drawString(395, 50, self.offer.time)
        
        canvas.restoreState()

    def post(self,request):
        # 获取参数
        data = request.data
        id = data.get('id',None)
        student_id = data.get('student_id',None)
        name = data.get('name',None)

        # 判断参数是否完整
        if not id or not student_id or not name:
            return Response({'msg':'请传入完整参数'},status=status.HTTP_400_BAD_REQUEST)
        
        else:  
            try:
                student = StudentModel.objects.get(**data)
            except:
                return Response({'msg':'未查到录取信息！请检查姓名、身份证号、准考证号是否输入正确！'},status=status.HTTP_404_NOT_FOUND)

            # 判断服务器中是否已经存在该学生的录取通知书
            if student.offer:
                # 增加下载次数
                student.access_count += 1
                student.save()
                # 返回学生信息
                serializer = StudentInfoSerializer(student)
                return Response(serializer.data,status=status.HTTP_200_OK)
            
            # 注册字体
            pdfmetrics.registerFont(TTFont('SIMSUN', 'wqy-zenhei.ttc'))
            pdfmetrics.registerFont(TTFont('KAITI', 'ukai.ttc'))

            # 获取启用的录取通知书
            offer = self.get_offer(student.type)
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
            if ori_str is None:
                return Response({'msg':'通知书设置错误，请联系管理员'},status=status.HTTP_400_BAD_REQUEST)

            # 获取系统内存使用情况
            mem = psutil.virtual_memory()

            # 剩余内存量（单位：Mb）
            free = mem.free / 1024 / 1024

            # 打印内存使用情况
            if free < 100:
                return Response({'msg':'当前访问量过大，请稍后重试'},status=status.HTTP_400_BAD_REQUEST)

            # 创建PDF文档对象

            if not os.path.exists(os.path.join(settings.MEDIA_ROOT,'offer','student_offer',f'{student.admission_date}',f'{student.type}')):
                os.makedirs(os.path.join(settings.MEDIA_ROOT,'offer','student_offer',f'{student.admission_date}',f'{student.type}'))
            
            # 编码后的身份证号作为pdf和二维码的文件名
            encoded_id = encode_string(student.id)

            #  避免文件名重复
            while StudentModel.objects.filter(offer=f'offer/student_offer/{student.admission_date}/{student.type}/{encoded_id}.pdf').exists():
                encoded_id = encode_string(student.id + 'm')

            # 通知书路径
            pdf_path = os.path.join(settings.MEDIA_ROOT,'offer','student_offer',f'{student.admission_date}',f'{student.type}',f'{encoded_id}.pdf')
            qr_path = os.path.join(settings.MEDIA_ROOT,'offer','student_offer',f'{student.admission_date}',f'{student.type}',f'{encoded_id}.jpg')

            # 生成二维码
            web_path = self.offer.web_path
            offer_web_path = 'http://' + web_path + '/media/offer/student_offer/' + f'{student.admission_date}/' + f'{student.type}/' + f'{encoded_id}.pdf'
            generate_qrcode(offer_web_path,qr_path)
            self.qrcode = qr_path
            

            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            
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
            story.append(Spacer(1, 200))

            name_para = Paragraph(f'{name}同学：',nt)
            paragraph = Paragraph(ori_str, st)
            story.append(name_para)
            story.append(paragraph)

            # 绘制印章
            # story.append(Spacer(1, 10))
            # img = Image(os.path.join(settings.MEDIA_ROOT,'offer','sl4.png'), width=200, height=200,hAlign='RIGHT')
            # story.append(img)

            # 生成pdf 
            doc.build(story,onFirstPage=self.myfirst)

            # 更新学生的录取通知书
            student.offer = f'offer/student_offer/{student.admission_date}/{student.type}/{encoded_id}.pdf'
            # 更新学生的录取通知书二维码
            student.qrcode = f'offer/student_offer/{student.admission_date}/{student.type}/{encoded_id}.jpg'
        
            # 返回pdf文件
            # response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="offer.pdf"'
            # response.write(buffer.getvalue())

            # 增加下载次数
            student.access_count += 1
            student.save()

            # 序列化学生信息
            serializer = StudentInfoSerializer(student)

            return Response(serializer.data,status=status.HTTP_200_OK)
    
class OfferPreviewView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.offer = None
  
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
    
    
    def replace_str(self,ori_str, data):
        """
        替换字符串中的变量
        """
    # 获取字符串中的变量
        var_list = re.findall(r'{(.*?)}', ori_str)
        # 将变量替换为字典中的值
        for var in var_list:
            try:
                ori_str = ori_str.replace('{'+var+'}', ' '+str(data[var])+' ')
            except:
                return None
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

        # 绘制二维码
        qrcode_path = os.path.join(settings.MEDIA_ROOT,'offer','static','qrcode.jpg')
        canvas.drawImage(qrcode_path, 50, 50, width=80, height=80)
        canvas.setFont('SIMSUN', 10)
        canvas.drawString(45,25,'扫码验证录取通知书')

        # 绘制印章
        icon_image_path = os.path.join(settings.MEDIA_ROOT,'offer','static','ldzx.svg')
        
        drawing = svg2rlg(icon_image_path)
        drawing = self.scale(drawing, 0.45)

        renderPDF.draw(drawing, canvas, 380, 20)

        # icon_image_path = os.path.join(settings.MEDIA_ROOT,'offer','ldzx.png')
        # canvas.drawImage(icon_image_path, 200, 600, width=200, height=200)

        # 标题
        canvas.setFont('KAITI', 40)
        canvas.setFillColorRGB(255, 0, 0)
        # canvas.setFillColorRGB(255, 0, 0)
        canvas.drawString(200, 650, f'录取通知书')

        # 落款
        canvas.setFont('SIMSUN', 20)
        canvas.setFillColorRGB(0, 0, 0)
        # canvas.drawString(400, 100, f'四川省泸定中学')
        # canvas.drawString(395, 50, f'2023 年 7 月 1 日')
        canvas.drawString(400, 100, self.offer.school)
        canvas.drawString(395, 50, self.offer.time)
        
        canvas.restoreState()

    def get(self,request):

        # 获取通知书信息
        offer_id = request.query_params.get('offer_id', None)
        try:
            self.offer = OfferModel.objects.get(id=offer_id)
        except:
            return Response({'msg':'通知书不存在'},status=status.HTTP_404_NOT_FOUND)

        # 模拟学生信息
        student = {
            "id": "513322200003140011",
            "name": "张三",
            "student_id": "18041817",
            "class_num": 1,
            "sex": 1,
            "admission_date": 2023
        }
    
        # 注册字体
        pdfmetrics.registerFont(TTFont('SIMSUN', 'wqy-zenhei.ttc'))
        pdfmetrics.registerFont(TTFont('KAITI', 'ukai.ttc'))
        
        # 通知书需要的学生信息
        student_data = {
            '姓名': student['name'],
            '班级': student['class_num'],
            "入学时间": student['admission_date'],
            "性别":student['sex'],
            "考号":student['student_id'],
            "身份证号":student['id'],
        }

        # ori_str = f'恭喜你被我校录取，成为我校{student_data["admission_date"]}级的一员，你的录取班级为{student_data["class_num"]}班。请持此通知书于{student_data["admission_date"]}年 9 月 1 日前来我校报到。'
        # 替换通知书中的变量
        ori_str = self.offer.text
        ori_str = self.replace_str(ori_str, student_data)
        if ori_str is None:
            return Response({'msg':'通知书内容错误,请按照要求进行设置'},status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
        story.append(Spacer(1, 200))

        name_para = Paragraph(f'{student["name"]}同学：',nt)
        paragraph = Paragraph(ori_str, st)
        story.append(name_para)
        story.append(paragraph)

        # 绘制印章
        # page_width, page_height = A4
        # story.append(Spacer(1, 10))
        # img = Image(os.path.join(settings.MEDIA_ROOT,'offer','ldzx.png'), width=200, height=200,hAlign='RIGHT',vAlign='BOTTOM')
        # story.append(img)

        # 生成pdf 
        doc.build(story,onFirstPage=self.myfirst)


        # 将pdf文件写入到临时文件中,并转换为图片
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_filename = tmp_file.name
            tmp_file.write(buffer.getvalue())

        buffer.close()
        # output_dir = os.path.join(settings.MEDIA_ROOT,'temp')  # 图像输出目录
        # output_prefix = 'test'  # 图像文件名前缀

        images = pdf2image.convert_from_path(tmp_filename)
        os.remove(tmp_filename)

        buffer = io.BytesIO()
        for i, image in enumerate(images):
            image.save(buffer, 'JPEG')

        response = HttpResponse(buffer.getvalue(), content_type='image/jpeg')
        buffer.close()
        
        return response
