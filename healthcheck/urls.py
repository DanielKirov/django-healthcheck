from django.conf.urls import patterns, url
from .views import healthcheckview


urlpatterns = patterns('healthcheck.views',
                       #url(r'^more-products/', MoreProductListView.as_view(),
                       #    name="more-product-list"),
                       #url(r'^(?P<slug>[\w-]+)/$', ProductDetailView.as_view(),
                       #    name="product-detail"),
                       url(r'^$', healthcheckview,
                           name="healthcheck"),
                       )