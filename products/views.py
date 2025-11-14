import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, UploadJob, Webhook, WebhookLog
from .tasks import process_csv_upload, trigger_webhooks, bulk_delete_products
from celery.result import AsyncResult
import time


# Create your views here.
def index(request):
    """Main dashboard"""
    return render(request, "products/index.html")


@csrf_exempt
@require_http_methods(["POST"])
def upload_csv(request):
    """Handle CSV file upload"""
    if "file" not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    uploaded_file = request.FILES["file"]

    # Create upload job
    job = UploadJob.objects.create(file_name=uploaded_file.name)

    # Read file content
    csv_content = uploaded_file.read().decode("utf-8")

    # Start celery task
    task = process_csv_upload.delay(job.id, csv_content)

    return JsonResponse({"job_id": job.id, "task_id": task.id, "status": "started"})


def upload_progress(request, job_id):
    """Get upload job progress"""
    job = get_object_or_404(UploadJob, id=job_id)

    progress = 0
    if job.total_rows > 0:
        progress = int((job.processed_rows / job.total_rows) * 100)

    return JsonResponse(
        {
            "job_id": job.id,
            "status": job.status,
            "progress": progress,
            "processed_rows": job.processed_rows,
            "total_rows": job.total_rows,
            "error_message": job.error_message,
        }
    )


def product_list(request):
    """List products with filtering and pagination"""
    # Get filter parameters
    search = request.GET.get("search", "")
    is_active = request.GET.get("is_active", "")
    page = request.GET.get("page", 1)

    # Build query
    products = Product.objects.all().order_by("-created_at")

    if search:
        products = products.filter(
            Q(sku__icontains=search)
            | Q(name__icontains=search)
            | Q(description__icontains=search)
        )

    if is_active:
        products = products.filter(is_active=is_active == "true")

    # Paginate
    paginator = Paginator(products, 50)
    page_obj = paginator.get_page(page)

    # Return JSON for API calls
    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            {
                "products": list(page_obj.object_list.values()),
                "page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_count": paginator.count,
            }
        )

    return render(
        request,
        "products/list.html",
        {"products": page_obj, "search": search, "is_active": is_active},
    )


@csrf_exempt
@require_http_methods(["POST"])
def product_create(request):
    """Create a new product"""
    data = json.loads(request.body)

    try:
        product = Product.objects.create(
            sku=data["sku"].upper(),
            name=data["name"],
            description=data.get("description", ""),
            is_active=data.get("is_active", True),
        )

        # Trigger webhook
        trigger_webhooks.delay(
            "product.created",
            {"id": product.id, "sku": product.sku, "name": product.name},
        )

        return JsonResponse(
            {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "description": product.description,
                "is_active": product.is_active,
            },
            status=201,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def product_detail(request, product_id):
    """Get, update, or delete a product"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == "GET":
        return JsonResponse(
            {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "description": product.description,
                "is_active": product.is_active,
            }
        )

    elif request.method == "PUT":
        data = json.loads(request.body)

        product.name = data.get("name", product.name)
        product.description = data.get("description", product.description)
        product.is_active = data.get("is_active", product.is_active)
        product.save()

        # Trigger webhook
        trigger_webhooks.delay(
            "product.updated",
            {"id": product.id, "sku": product.sku, "name": product.name},
        )

        return JsonResponse(
            {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "description": product.description,
                "is_active": product.is_active,
            }
        )

    elif request.method == "DELETE":
        product_data = {"id": product.id, "sku": product.sku, "name": product.name}
        product.delete()

        # Trigger webhook
        trigger_webhooks.delay("product.deleted", product_data)

        return JsonResponse({"status": "deleted"})


@csrf_exempt
@require_http_methods(["POST"])
def bulk_delete(request):
    """Delete all products"""
    task = bulk_delete_products.delay()
    return JsonResponse({"task_id": task.id, "status": "started"})


# Webhook views
def webhook_list(request):
    """List all webhooks"""
    if request.headers.get("Accept") == "application/json":
        webhooks = Webhook.objects.all().order_by("-created_at")
        return JsonResponse({"webhooks": list(webhooks.values())})

    webhooks = Webhook.objects.all()
    return render(request, "products/webhooks.html", {"webhooks": webhooks})


@csrf_exempt
@require_http_methods(["POST"])
def webhook_create(request):
    """Create a new webhook"""
    data = json.loads(request.body)

    webhook = Webhook.objects.create(
        url=data["url"],
        event_type=data["event_type"],
        is_active=data.get("is_active", True),
    )

    return JsonResponse(
        {
            "id": webhook.id,
            "url": webhook.url,
            "event_type": webhook.event_type,
            "is_active": webhook.is_active,
        },
        status=201,
    )


@csrf_exempt
def webhook_detail(request, webhook_id):
    """Get, update, or delete a webhook"""
    webhook = get_object_or_404(Webhook, id=webhook_id)

    if request.method == "GET":
        return JsonResponse(
            {
                "id": webhook.id,
                "url": webhook.url,
                "event_type": webhook.event_type,
                "is_active": webhook.is_active,
            }
        )

    elif request.method == "PUT":
        data = json.loads(request.body)

        webhook.url = data.get("url", webhook.url)
        webhook.event_type = data.get("event_type", webhook.event_type)
        webhook.is_active = data.get("is_active", webhook.is_active)
        webhook.save()

        return JsonResponse(
            {
                "id": webhook.id,
                "url": webhook.url,
                "event_type": webhook.event_type,
                "is_active": webhook.is_active,
            }
        )

    elif request.method == "DELETE":
        webhook.delete()
        return JsonResponse({"status": "deleted"})


@csrf_exempt
@require_http_methods(["POST"])
def webhook_test(request, webhook_id):
    """Test a webhook"""
    webhook = get_object_or_404(Webhook, id=webhook_id)

    test_payload = {"test": True, "webhook_id": webhook.id, "timestamp": time.time()}

    trigger_webhooks.delay(webhook.event_type, test_payload)

    return JsonResponse({"status": "test_sent"})
