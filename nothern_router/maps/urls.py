from django.urls import path                                                                                                                           
from . import views

urlpatterns = [ 
    path(r'', views.default_map, name="default"),
    path(r'gannt/', views.gannt, name="gannt"),
]
