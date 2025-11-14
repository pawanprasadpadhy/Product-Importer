from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.index, name="index"),
    # Upload
    path("upload/", views.upload_csv, name="upload"),
    path(
        "upload/<int:job_id>/progress/", views.upload_progress, name="upload_progress"
    ),
    # Products
    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("products/bulk-delete/", views.bulk_delete, name="bulk_delete"),
    # Webhooks
    path("webhooks/", views.webhook_list, name="webhook_list"),
    path("webhooks/create/", views.webhook_create, name="webhook_create"),
    path("webhooks/<int:webhook_id>/", views.webhook_detail, name="webhook_detail"),
    path("webhooks/<int:webhook_id>/test/", views.webhook_test, name="webhook_test"),
]
