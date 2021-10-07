from django.urls import path

from . import views

urlpatterns = [
    path('view_all', views.view_all, name='view_all'),
    path('add', views.add, name='add'),
    path('use', views.use, name='use'),
    path('delete', views.delete, name='delete'),
]