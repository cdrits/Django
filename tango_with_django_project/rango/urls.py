from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url('^about', views.about, name='about'),
    url('^category/(?P<category_name_slug>[\w\-]+)/$', views.show_category, name='show_category')
    #                          ^ this is a parameter name. make sure the parameter exists
    #                             in the corresponding view!!
]
