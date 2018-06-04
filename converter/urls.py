from django.urls import path

from . import views

app_name = 'converter'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('status/<int:id>/', views.StatusView.as_view(), name='status'),
]
