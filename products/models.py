from django.db import models
from django.utils import timezone

# Create your models here.


class Product(models.Model):
    sku = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["is_active"]),
        ]

    def save(self, *args, **kwargs):
        # Ensure SKU is case-insensitive
        self.sku = self.sku.upper()
        super().save(*args, **kwargs)


class UploadJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    file_name = models.CharField(max_length=255)
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "upload_jobs"


class Webhook(models.Model):
    EVENT_TYPES = [
        ("product.created", "Product Created"),
        ("product.updated", "Product Updated"),
        ("product.deleted", "Product Deleted"),
        ("upload.completed", "Upload Completed"),
    ]

    url = models.URLField(max_length=500)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "webhooks"


class WebhookLog(models.Model):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    response_code = models.IntegerField(null=True)
    response_time_ms = models.IntegerField(null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "webhook_logs"
