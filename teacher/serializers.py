import time

from rest_framework import serializers

from django.contrib.auth.models import User
from django.contrib.auth import login,logout

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class TeacherSerializer(serializers.ModelSerializer):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.default_password = '123456'

    class Meta:
        model = User
        fields = ('id','username','is_active','last_login','password')
        read_only_fields = ('id','is_active','last_login')
        extra_kwargs = {
            'password':{
                'write_only':True,
                'required':False,
                'default':None
            }
        }

    def validate(self, attrs):
        password = attrs.get('password')

        # 没有密码则为添加教师或重置密码，无需校验
        if not password:
            return attrs
        
        # 判断密码是否符合要求
        if len(password) < 6 or len(password) > 20:
            raise serializers.ValidationError('密码长度应在6-20位之间')
        if password.isdigit():
            raise serializers.ValidationError('密码不能为纯数字')
        return attrs

    def create(self, validated_data):
        validated_data['password'] = self.default_password  # 添加教师，设置为默认密码
        return User.objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        # 修改密码，以PATCH未传入密码时，设置为默认密码
        # PUT方式传入密码时，设置为传入的密码
        instance.set_password(validated_data.get('password',self.default_password)) 
        instance.save()
        return instance
    
class MyUserTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # 调用父类的validate方法，获取token，实现登录
        data = super().validate(attrs)

        # 更新最后登录时间
        self.user.last_login = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) 
        self.user.save()

        # 将用户信息添加到返回的数据中
        data['id'] = self.user.id
        data['username'] = self.user.username
        
        # 判断是否为简单密码
        if User.check_password(self.user,'123456'):
            data['is_simple'] = True
        else:
            data['is_simple'] = False

        # 判断是否为管理员
        if self.user.is_superuser:
            data['is_admin'] = True
        else:
            data['is_admin'] = False
            
        return data