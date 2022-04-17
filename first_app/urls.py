from django.conf.urls import url
from MyAPI import views
from django.urls import path

# TEMPLATE TAGGING
app_name = "first_app"
urlpatterns = [
    url(r'^$', views.about, name='main'),
    url(r'^forecast/', views.forecast, name='forecast')
]

