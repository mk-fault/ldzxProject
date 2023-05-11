from rest_framework import serializers

from .models import StudentModel
from utils import funcs

class StudentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentModel
        fields = '__all__'
    
    # def validate_id(self,value):
    #     if not funcs.validate_id_number(value):
    #         raise serializers.ValidationError("身份证信息有误，请检查后重新填写")
    #     return value
    
    def validate_admission_date(self,value):
        if value < 1945 or value > 2099:
            raise serializers.ValidationError("请输入正确的入学年份(1945~2099)")
        return value

    def validate_student_id(self,value):
        if not value.isdigit():
            raise serializers.ValidationError("请输入正确的学号")
        return value
    
