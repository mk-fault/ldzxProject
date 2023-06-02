from django.urls import path,include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('offers',views.OfferViewset)

urlpatterns = [
    path('',include(router.urls)),
    path('download/',views.OfferDownloadView.as_view()),
    path('preview/',views.OfferPreviewView.as_view())
    # path('upload/',views.OfferUploadView.as_view())
]