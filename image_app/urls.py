from django.urls import path, include
from rest_framework import routers
from .views import UploadViewSet, ListImages

router = routers.DefaultRouter()
router.register(r'upload', UploadViewSet, basename="upload")


urlpatterns = [
    path('', include(router.urls)),
    path('images/', ListImages.as_view())
]
