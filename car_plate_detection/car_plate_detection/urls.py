from django.urls import path
from detection import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('result/', views.result, name='result'),
    path('detected-plates/', views.detected_plates_view, name='detected_plates'),
    path('car/<str:plate_number>/', views.car_details, name='car_details'),

]
