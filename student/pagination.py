from rest_framework.pagination import PageNumberPagination

class StudentPagination(PageNumberPagination):
    page_size = 13
    page_size_query_param = 'page_size'
    max_page_size = 1000