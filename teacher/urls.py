from django.urls import path,include

from . import views

from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('teachers',views.TeacherViewset)

urlpatterns = [
    path('',include(router.urls)),
    path('login/',views.LoginView.as_view()),
    path('reactive/',views.ReactiveTeacherView.as_view()),
    path('deactive/',views.DeactiveTeacherView.as_view())
]