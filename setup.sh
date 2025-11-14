# setup.sh
#!/bin/bash
set -e

echo "Setting up Product Importer..."

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL database if it doesn't exist
DB_NAME="product_importer_db"
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -wq "$DB_NAME"; then
    echo "Database '$DB_NAME' already exists."
else
    echo "Creating database '$DB_NAME'..."
    sudo -u postgres createdb "$DB_NAME"
fi

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start Redis server: redis-server (if not already running)"
echo "2. Run Django server: python manage.py runserver"
echo "3. Run Celery worker: celery -A product_importer worker --loglevel=info"
