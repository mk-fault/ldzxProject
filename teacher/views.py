from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser,AllowAny
from rest_framework import mixins

from rest_framework_simplejwt.views import TokenViewBase

from .serializers import TeacherSerializer,MyUserTokenSerializer
from .permissions import IsAdminOrOwnerPutOnly

# Create your views here.

# 教师信息获取视图
# GET：获取全部教师信息(仅管理员)
# POST：添加教师(仅管理员)
# PATCH：重置密码(仅管理员)(默认密码123456)
# PUT: 重置密码(需要传入username)(教师可用，仅允许修改自己的密码)
class TeacherViewset(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin):
    queryset = User.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminOrOwnerPutOnly]




# 教师失活视图
# PATCH：失活教师(仅管理员)
class DeactiveTeacherView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self,request):
        username = request.data.get('username')
        if not username:
            return Response({'msg':'用户名不能为空'},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'msg':'用户不存在'},status=status.HTTP_404_NOT_FOUND)
        user.is_active = False
        user.save()
        return Response({'msg':'失活成功'},status=status.HTTP_200_OK)

# 教师激活视图
# PATCH：激活教师(仅管理员)
class ReactiveTeacherView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self,request):
        username = request.data.get('username')
        if not username:
            return Response({'msg':'用户名不能为空'},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'msg':'用户不存在'},status=status.HTTP_404_NOT_FOUND)
        user.is_active = True
        user.save()
        return Response({'msg':'激活成功'},status=status.HTTP_200_OK)
    
# 登录视图
class LoginView(TokenViewBase):
    serializer_class = MyUserTokenSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(serializer)
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({'msg':'用户名或密码错误'},status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)