from django.conf.urls import include, url

urlpatterns = [
    url(r'^_crawler/', include('_crawler.urls'))
]
