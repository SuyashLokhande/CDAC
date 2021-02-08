from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('res/', views.print1, name='res'),
    path('login/', views.log1, name='res'),
    path('log/', views.log2, name='res'),
    path('reg/', views.reg1, name='reg3'),
    path('logout/', views.lout1, name='reg3'),
    path('signup/', views.sign1, name='res'),
    path('word/', views.word1, name='word2'),
]