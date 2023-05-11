from rest_framework.permissions import BasePermission

class IsAdminOrOwnerPutOnly(BasePermission):
    def has_object_permission(self, request, view,obj):
        # 如果是管理员可以进行操作
        if request.user.is_superuser:
            return True
        # 如果是PUT请求，且是用户本人，可以进行操作
        return request.method == 'PUT' and obj == request.user
            