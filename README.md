MarketplaceAPI
   A Django REST API for a marketplace platform, enabling user roles (admin, seller, customer), product management, order processing, and inventory tracking. Built with Django, Django REST Framework, and MySQL.
Features

User Roles: Admin, seller, and customer with role-based permissions.
Product Management: Create, update, delete, and list products (POST /api/seller/products/, GET /api/seller/products/{id}/).
Order Processing: Create orders with multiple items, update stock, and log inventory changes (POST /api/customer/orders/).
Inventory Tracking: Log stock changes for restocking or orders.
Error Handling: Resolved migration issues (is_paid, price), 404 errors, and validation for product IDs and stock.
Database: MySQL with migrations for schema consistency.

Technologies

Python 3.12
Django 4.x
Django REST Framework
MySQL
Django Filters

Setup

Clone the repository:git clone https://github.com/yourusername/MarketplaceAPI.git
cd MarketplaceAPI


Create a virtual environment:python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:pip install -r requirements.txt


Configure the database in Marketplace/settings.py:DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


Run migrations:python manage.py makemigrations
python manage.py migrate


Seed initial data (optional):python manage.py shell

from core.models import User, Category, Product
User.objects.create(username='seller1', email='seller1@example.com', password='seller123', role='seller')
Category.objects.create(name='Electronics')
seller = User.objects.get(username='seller1')
category = Category.objects.get(name='Electronics')
Product.objects.create(seller=seller, category=category, name='Product 8', description='Test product 8', price=99.99, stock_quantity=50)


Run the server:python manage.py runserver


Access APIs at http://127.0.0.1:8000/.

API Endpoints

Create Order: POST /customer/orders/
Get Product: GET /seller/products/{id}/
List Orders: GET /customer/orders/
Seller Orders: GET /seller/seller/orders/

Challenges and Solutions

Migration Errors: Fixed missing is_paid column and non-nullable price field by resetting migrations and applying new ones.
404 Errors: Resolved by creating missing products (IDs 8, 9).
Field Naming: Ensured order_date was retained instead of created_at.

License
   MIT License
