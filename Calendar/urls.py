from django.conf.urls import patterns, url

from Calendar import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^create/', views.create),
    url(r'^makeView/', views.makeView),
    url(r'^edit/(\w+)', views.editRequest),
    url(r'^viewrequest/(\w+)', views.viewRequest),
    url(r'^save/', views.create),
    url(r'^delete/(\w+)', views.deleteRequest),
    url(r'^assign/(\w+)', views.assign),
    url(r'^accounts/login/', 'django.contrib.auth.views.login'),
    url(r'^login/', views.login),
    url(r'^logout/', views.logout_view),
)
