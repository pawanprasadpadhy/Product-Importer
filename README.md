# Product Importer

A Django-based web application for importing and managing products from CSV files with webhook support.

## Features

- Upload CSV files with up to 500,000 products
- Real-time progress tracking
- Product CRUD operations
- Bulk delete functionality
- Webhook configuration and management
- Asynchronous processing with Celery
- PostgreSQL database

## Tech Stack

- **Backend**: Django 4.2
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render

## Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd product-importer
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create PostgreSQL database:
```bash
createdb product_importer_db
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Create superuser:
```bash
python manage.py createsuperuser
```

8. Collect static files:
```bash
python manage.py collectstatic
```

### Running the Application

1. Start Django development server:
```bash
python manage.py runserver
```

2. Start Celery worker (in a new terminal):
```bash
celery -A product_importer worker --loglevel=info
```

3. Start Redis (if not running as service):
```bash
redis-server
```

4. Access the application:
- Main app: http://localhost:8000
- Admin panel: http://localhost:8000/admin

## CSV Format

Your CSV file should have the following columns:
```
sku,name,description,price
PROD001,Product Name,Product description,19.99
```

## API Endpoints

### Products
- `GET /products/` - List products with filters
- `POST /products/create/` - Create a product
- `GET /products/<id>/` - Get product details
- `PUT /products/<id>/` - Update a product
- `DELETE /products/<id>/` - Delete a product
- `POST /products/bulk-delete/` - Delete all products

### Upload
- `POST /upload/` - Upload CSV file
- `GET /upload/<job_id>/progress/` - Get upload progress

### Webhooks
- `GET /webhooks/` - List webhooks
- `POST /webhooks/create/` - Create a webhook
- `GET /webhooks/<id>/` - Get webhook details
- `PUT /webhooks/<id>/` - Update a webhook
- `DELETE /webhooks/<id>/` - Delete a webhook
- `POST /webhooks/<id>/test/` - Test a webhook

## Deployment to Render

1. Push code to GitHub

2. Create new Web Service on Render:
   - Connect your repository
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn product_importer.wsgi:application`

3. Add PostgreSQL database

4. Add Redis instance

5. Configure environment variables:
   - `DATABASE_URL`
   - `REDIS_URL`
   - `SECRET_KEY`
   - `DEBUG=False`

6. Create Celery worker service:
   - Start Command: `celery -A product_importer worker --loglevel=info`

## Testing

Run tests:
```bash
python manage.py test
```

