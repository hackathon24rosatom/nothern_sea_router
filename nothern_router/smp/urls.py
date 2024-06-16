from django.urls import path                                                                                                                           
from . import views

urlpatterns = [ 
    path(r'inference/', views.ships, name="smp"),
]
