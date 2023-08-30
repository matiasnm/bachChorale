from django.urls import path
from . import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", views.index, name="index"),
    path("getChorale", views.getChorale, name="getChorale"),
    path("getPlots/<int:plot>/<int:index>", views.getPlots, name="getPlots"),
    path("getAnalysis/<int:analysis>/<int:index>", views.getAnalysis, name="getAnalysis"),
    path("getSearch/", views.getSearch, name="getSearch")
]

#if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)