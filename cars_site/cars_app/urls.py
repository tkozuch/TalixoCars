from django.urls import path

from . import views


urlpatterns = [
    path('car:retrieve', views.get_car),
    path('car:list', views.get_cars_list),
    path('car:add', views.add_car),
    path('car:update', views.update_car),
    path('car:delete', views.delete_car)
]
