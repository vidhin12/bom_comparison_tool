from django.urls import path
from . import views

app_name = "comparison"

urlpatterns = [
    path("", views.upload_bom_view, name="upload"),
    path("result/<int:pk>/", views.comparison_result_view, name="result"),
    path("download_result/<int:pk>/", views.download_result_view, name="download_result"),
    path("download_result_excel/<int:pk>/", views.download_result_excel_view, name="download_result_excel"),
    path("history/", views.comparison_history_view, name="history"),
]
