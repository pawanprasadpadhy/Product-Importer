from django.contrib import admin
from .models import Product, UploadJob, Webhook, WebhookLog

# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["sku", "name", "description"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(UploadJob)
class UploadJobAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "file_name",
        "status",
        "processed_rows",
        "total_rows",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ["url", "event_type", "is_active", "created_at"]
    list_filter = ["event_type", "is_active"]
    search_fields = ["url"]


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = [
        "webhook",
        "event_type",
        "response_code",
        "response_time_ms",
        "created_at",
    ]
    list_filter = ["event_type", "created_at"]
    readonly_fields = ["created_at"]
