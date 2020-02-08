from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^category/all/$', views.category_all, name='category_all'),
    url(r'^category/(?P<slug>[\w-]{3,255})/$', views.category, name='category'),
    url(r'^product/(?P<slug>[\w-]{3,255})/$', views.product, name='product'),
    url(r'^product/(?P<product>[\w-]{3,255})/(?P<variant>[\w-]{3,255})/$',
        views.variant, name='variant'),
]
