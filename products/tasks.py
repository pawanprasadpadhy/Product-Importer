import csv
import io
import time
import requests
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from .models import Product, UploadJob, Webhook, WebhookLog


@shared_task(bind=True)
def process_csv_upload(self, job_id, csv_content):
    """Process CSV file upload in background"""
    job = UploadJob.objects.get(id=job_id)
    job.status = "processing"
    job.started_at = timezone.now()
    job.save()

    try:
        # Parse CSV
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)

        # Count total rows first
        rows = list(reader)
        job.total_rows = len(rows)
        job.save()

        # Process in batches
        batch_size = 1000
        processed = 0

        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            products_to_create = []
            products_to_update = []

            for row in batch:
                sku = row.get("sku", "").strip().upper()

                if not sku:
                    continue

                product_data = {
                    "sku": sku,
                    "name": row.get("name", "").strip(),
                    "description": row.get("description", "").strip(),
                    "price": float(row.get("price", 0)),
                }

                # Check if product exists
                try:
                    product = Product.objects.get(sku=sku)
                    for key, value in product_data.items():
                        setattr(product, key, value)
                    products_to_update.append(product)
                except Product.DoesNotExist:
                    products_to_create.append(Product(**product_data))

            # Bulk operations
            with transaction.atomic():
                if products_to_create:
                    Product.objects.bulk_create(
                        products_to_create, ignore_conflicts=True
                    )

                if products_to_update:
                    Product.objects.bulk_update(
                        products_to_update,
                        ["name", "description", "price", "updated_at"],
                    )

            processed += len(batch)
            job.processed_rows = processed
            job.save()

            # Update task progress
            self.update_state(
                state="PROGRESS", meta={"current": processed, "total": job.total_rows}
            )

        # Mark as completed
        job.status = "completed"
        job.completed_at = timezone.now()
        job.save()

        # Trigger webhook
        trigger_webhooks.delay(
            "upload.completed", {"job_id": job_id, "total_rows": job.total_rows}
        )

        return {"status": "completed", "processed": processed}

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()
        raise


@shared_task
def trigger_webhooks(event_type, payload):
    """Trigger webhooks for specific events"""
    webhooks = Webhook.objects.filter(event_type=event_type, is_active=True)

    for webhook in webhooks:
        try:
            start_time = time.time()
            response = requests.post(
                webhook.url,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"},
            )
            response_time_ms = int((time.time() - start_time) * 1000)

            WebhookLog.objects.create(
                webhook=webhook,
                event_type=event_type,
                payload=payload,
                response_code=response.status_code,
                response_time_ms=response_time_ms,
            )
        except Exception as e:
            WebhookLog.objects.create(
                webhook=webhook,
                event_type=event_type,
                payload=payload,
                error_message=str(e),
            )


@shared_task
def bulk_delete_products():
    """Delete all products in background"""
    Product.objects.all().delete()
    return {"status": "completed"}
