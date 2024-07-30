from django.urls import path
from detector import views


urlpatterns = [
   path('', views.index),
   path('signedupemail/',views.SignedUpEmail, name='signedupemail'),
   path('loginpage/',views.Logedin, name='loginpage'),
   path('mainpage/',views.Mainpage, name='mainpage'),
   path('forgotpass/',views.Forgotpass, name='forgotpass'),
   path('resetpass/<str:emails>',views.Resetpass, name='resetpass'),
]