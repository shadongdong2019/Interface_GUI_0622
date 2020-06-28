from django.urls import path, re_path
from . import views

app_name = 'interface_frame'
urlpatterns = [
    path('',views.main_GUI),
    path('index/',views.main_GUI),
    # re_path('^file_download', views.file_down, name="file_down"),
    # re_path('^getallpath', views.get_all_path, name="get_all_path")
]
