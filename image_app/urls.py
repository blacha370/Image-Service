from django.urls import path
from .views import UploadViewSet, ImagesWithDetailsViewSet, GenerateExpiringLink, GetImage, ImagesViewSet, Login, Navigation


urlpatterns = [
    path('', Navigation.as_view()),
    path('link/', GenerateExpiringLink.as_view({'post': 'create'})),
    path('upload/', UploadViewSet.as_view({'post': 'create'})),
    path('images/', ImagesViewSet.as_view({'get': 'list'})),
    path('images/details/', ImagesWithDetailsViewSet.as_view({'get': 'list'})),
    path('images/details/<str:image_name>', ImagesWithDetailsViewSet.as_view({'get': 'get_one'})),
    path('link/<str:expiring_name>', GetImage.as_view()),
    path('login/', Login.as_view({'post': 'post'}))
]
