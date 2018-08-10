from django.urls import path, include
from bbsapp import views
from django.contrib import admin

urlpatterns = [
    path('', views.helw),
    path('admin/', admin.site.urls),
    path('secret/', views.secret),
    path('home/', views.home),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout),
    path('captcha', include('captcha.urls')),
    path('confirm/', views.user_confirm),

]
