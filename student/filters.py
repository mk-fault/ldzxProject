from .models import StudentModel
from django_filters import rest_framework as filters

class StudentFilter(filters.FilterSet):
    max_admission_date = filters.NumberFilter(field_name='admission_date',lookup_expr='lte')
    min_admission_date = filters.NumberFilter(field_name='admission_date',lookup_expr='gte')
    max_student_id = filters.CharFilter(field_name='student_id',lookup_expr='lte')
    min_student_id = filters.CharFilter(field_name='student_id',lookup_expr='gte')
    id = filters.CharFilter(field_name='id',lookup_expr='icontains')
    name = filters.CharFilter(field_name='name',lookup_expr='icontains')
    student_id = filters.CharFilter(field_name='student_id',lookup_expr='icontains')
    type = filters.CharFilter(field_name='type__name',lookup_expr='icontains')

    class Meta:
        model = StudentModel
        fields = ['sex','admission_date','max_admission_date','min_admission_date','max_student_id','min_student_id',"student_id","id","class_num","name",'type']