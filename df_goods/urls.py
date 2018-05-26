from django.conf.urls import include, url
import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^list(\d+)_(\d+)_(\d+)/$', views.list, name="list"),
    url(r'^(\d+)/$', views.detail),
    url(r'^search/$', views.MySearchView()),

]
