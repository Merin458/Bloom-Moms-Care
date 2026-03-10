"""
URL configuration for BloomMomsproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path,include
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include (('adminapp.adminappurls', 'adminapp'), namespace='adminapp')),
    path('guest/',include (('guestapp.guestappurls', 'guestapp'), namespace='guestapp')),
    path('doctor/',include (('doctorapp.doctorappurls', 'doctorapp'), namespace='doctorapp')),
    path('patient/',include (('patientapp.patientappurls', 'patientapp'), namespace='patientapp')),
    path('notifications/', include(('notificationapp.urls', 'notificationapp'), namespace='notificationapp')),
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
