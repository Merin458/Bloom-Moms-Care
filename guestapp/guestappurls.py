from django.contrib import admin
from django.urls import include, path

from .import views

urlpatterns = [
	path('guestindex/', views.guestindex, name='guestindex'),
	path('about/', views.about_us, name='about_us'),
	path('antenatalcare/', views.antenatalcare, name='antenatalcare'),
	path('ultrasound/', views.ultrasound, name='ultrasound'),
	path('consultation/', views.consultation, name='consultation'),
	path('trimestermonitor/', views.trimestermonitor, name='trimestermonitor'),
	path('nutritioncare/', views.nutritioncare, name='nutritioncare'),
	path('safedelivery/', views.safedelivery, name='safedelivery'),
	path('contact/', views.contact, name='contact'),
	path('login/', views.login, name='login'),
]