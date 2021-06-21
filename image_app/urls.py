from django.urls import path, include
from rest_framework import routers
from .views import UploadViewSet, ImagesWithDetailsViewSet, GenerateExpiringLink, GetImage, ImagesViewSet

router = routers.DefaultRouter()
router.register(r'upload', UploadViewSet, basename="upload")
router.register(r'link', GenerateExpiringLink, basename='link')

urlpatterns = [
    path('', include(router.urls)),
    path('images/', ImagesViewSet.as_view({'get': 'list'})),
    path('images/details/', ImagesWithDetailsViewSet.as_view({'get': 'list'})),
    path('images/details/<str:image_name>', ImagesWithDetailsViewSet.as_view({'get': 'get_one'})),
    path('link/<str:expiring_name>', GetImage.as_view()),
]
