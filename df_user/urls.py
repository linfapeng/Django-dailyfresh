from django.conf.urls import include, url
from django.contrib import admin
import views

urlpatterns = [
    url(r'^register/$', views.register),
    url(r'^register_handle/$', views.register_handle),
    url(r'^register_exist/$', views.register_exist),
    url(r'^login/$', views.login),
    url(r'^login_handle/$', views.login_handle),
    url(r'^info/$', views.user_center_info),
    url(r'^order(\d+)/$', views.user_center_order),
    url(r'^site/$', views.user_center_site),
    url(r'^logout/', views.logout),

]