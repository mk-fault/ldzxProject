from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser,AllowAny
from rest_framework import mixins

from .models import StudentModel
from .serializers import StudentModelSerializer
# Create your views here.

class StudentViewset(viewsets.ModelViewSet):
    queryset = StudentModel.objects.all().order_by('student_id')
    serializer_class = StudentModelSerializer
    permission_classes = [AllowAny]

