"""
URL configuration for emex_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from emex_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('accounts/login/', views.user_login),
    path('upload/', views.upload_file, name='upload_file'),
    path('start/', views.start_process, name='start_process'),
    path('download_results/', views.download_results, name='download_results'),
    path('stop/', views.stop_process, name='stop_process'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
