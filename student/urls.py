from django.urls import path,include

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('students',views.StudentViewset)

urlpatterns = [
    path('',include(router.urls)),
    path('multi_create/',views.StudentMultiCreateView.as_view(),name='multi_create'),
    path('multi_delete/',views.StudentMultiDeleteView.as_view(),name='multi_delete'),
    path('<int:pk>/',views.StudentDetailView.as_view(),name='detail'),
    path('download/',views.OfferDownloadView.as_view(),name='download'),
]