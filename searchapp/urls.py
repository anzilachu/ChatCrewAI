from django.urls import path
from .views import *

app_name = 'searchapp'

urlpatterns = [
    path('', search, name='search'),
    path('result/<str:media_type>/<int:result_id>/',result_detail, name='result_detail'),
]