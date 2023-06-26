from rest_framework import serializers

from .models import StudentModel, TypeModel
from utils import funcs

class StudentModelSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=18)
    student_id = serializers.CharField(max_length=20)
    sex = serializers.CharField(max_length=5)
    type = serializers.SlugRelatedField(queryset=TypeModel.objects.all(),slug_field='name',required=True)
    class Meta:
        model = StudentModel
        exclude = ['offer','qrcode']
    
    def validate_id(self,value):
        # 如果是在PUT和PATCH下，则不需要验证身份证号是否存在，但不允许修改身份证号
        if self.context['request'].method in ['PUT','PATCH']:
            obj_id = self.context['request'].path.split('/')[-2]
            try:
                StudentModel.objects.get(id=obj_id)
            except:
                raise serializers.ValidationError("该身份证号下的学生不存在")
            if obj_id == value:
                return value
            else:
                raise serializers.ValidationError("身份证号不可修改")

        try:
            StudentModel.objects.get(id=value)
        except:
            # if not funcs.validate_id_number(value):
            #     raise serializers.ValidationError(f"身份证{value}信息有误，请检查后重新填写")
            return value

        raise serializers.ValidationError(f"身份证[{value}]已存在")
    
    def validate_admission_date(self,value):
        if value < 1945 or value > 2099:
            raise serializers.ValidationError("请输入正确的入学年份(1945~2099)")
        return value

    def validate_student_id(self,value):
        if self.context['request'].method in ['PUT','PATCH']:
            obj_id = self.context['request'].path.split('/')[-2]
            try:
                stu = StudentModel.objects.get(id=obj_id)
            except:
                raise serializers.ValidationError("该身份证号下的学生不存在")
            if value == stu.student_id:
                return value
            
        try:
            StudentModel.objects.get(student_id=value)
        except:
            if not value.isdigit():
                raise serializers.ValidationError(f"考号[{value}]格式有误，请检查后重新填写")
            return value
        raise serializers.ValidationError(f"考号[{value}]已存在")

    def validate_class_num(self,value):
        if value < 1 or value > 99:
            raise serializers.ValidationError("请输入正确的班级(1~99)")
        return value
    
    def validate_sex(self,value):
        if value not in ['男','女']:
            raise serializers.ValidationError("请输入正确的性别(男/女)")
        if value == '男':
            return '1'
        else:
            return '0'
    
class StudentMultiCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=18)
    student_id = serializers.CharField(max_length=20)
    class Meta:
        model = StudentModel
        fields = '__all__'
    
    def validate_id(self,value):
        try:
            StudentModel.objects.get(id=value)
        except:
            # if not funcs.validate_id_number(value):
            #     raise serializers.ValidationError(f"身份证{value}信息有误，请检查后重新填写")
            return value

        raise serializers.ValidationError(f"身份证[{value}]已存在")
    
    def validate_admission_date(self,value):
        if value < 1945 or value > 2099:
            raise serializers.ValidationError("请输入正确的入学年份(1945~2099)")
        return value

    def validate_student_id(self,value):
        try:
            StudentModel.objects.get(student_id=value)
        except:
            if not value.isdigit():
                raise serializers.ValidationError(f"考号[{value}]格式有误，请检查后重新填写")
            return value
        raise serializers.ValidationError(f"考号[{value}]已存在")
    
    def validate_class_num(self,value):
        if value < 1 or value > 99:
            raise serializers.ValidationError("请输入正确的班级(1~99)")
        return value
    

class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentModel
        exclude = ['create_time','update_time','access_count','qrcode']
        read_only_fields = ['sex','name','admission_date','class_num','offer']
        
    
    
    
