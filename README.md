# E-Commerce Platform

A complete e-commerce website built with Django, featuring secure payment integration, role-based access control, and a modern responsive design.

## 🚀 Features

- **User Authentication**: Registration, login, email verification, password reset
- **Role-Based Access**: Customer, Vendor, Moderator, and Admin roles
- **Product Management**: Categories, brands, variants, stock management
- **Shopping Cart**: Add/remove items, quantity updates, coupon support
- **Payment Integration**: Stripe and M-Pesa payment processing
- **Order Management**: Checkout, order tracking, history, invoices
- **Reviews & Ratings**: Product reviews with helpful voting
- **Wishlist**: Save favorite products
- **Notifications**: Real-time user notifications
- **Dashboard**: Customer dashboard and admin panel
- **Security**: CSRF protection, password validation, rate limiting
- **Responsive Design**: Works on all screen sizes

## 🛠️ Tech Stack

- **Backend**: Django 4.2
- **Database**: PostgreSQL (production) / SQLite (development)
- **Payment**: Stripe API, M-Pesa API
- **Frontend**: Bootstrap 5, Font Awesome
- **Deployment**: Render.com
- **Other**: Gunicorn, WhiteNoise, django-crispy-forms

## 📦 Installation

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, SQLite works for development)
- Virtual environment (recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/eKidenge/ecommerce.git
cd ecommerce

### Step 2: Clone the Repository
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

### Step 3: Install Dependencies
pip install -r requirements.txt


### Step 4: Configure Environment Variables
## Create a .env file in the project root:
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

### Step 5: Run Migrations
python manage.py makemigrations
python manage.py migrate

### Step 6: Create Superuser
python manage.py createsuperuser

### Step 7: Collect Static Files
python manage.py collectstatic

### Step 8: Run Development Server
python manage.py runserver
Visit http://127.0.0.1:8000 to see the application.

### Project Structure
ecommerce/
├── apps/
│   ├── accounts/        # User authentication & profiles
│   ├── products/        # Product management
│   ├── cart/           # Shopping cart
│   ├── orders/         # Order processing
│   ├── payments/       # Payment integration
│   ├── reviews/        # Product reviews
│   ├── wishlist/       # User wishlist
│   ├── notifications/  # User notifications
│   └── dashboard/      # User & admin dashboard
├── ecommerce/          # Project settings
├── static/            # Static files
├── media/             # User uploaded files
├── templates/         # Base templates
├── .env              # Environment variables
├── requirements.txt  # Dependencies
└── README.md         # Documentation

### User Roles
Customer
Browse products

Add to cart and checkout

Manage profile and addresses

View order history

Write reviews

Vendor
Manage products

View orders

Sales analytics

Admin
Full system access

User management

Product management

Order management

Payment monitoring

### Payment Integration
Stripe
Create a Stripe account

Get API keys from Stripe Dashboard

Add keys to .env file

Configure webhook endpoint

M-Pesa (Kenya)
Register as a business on M-Pesa

Get API credentials

Add credentials to .env

Configure callback URLs

🚀 Deployment
Deploy to Render.com
Push code to GitHub

Create account on Render.com

Connect GitHub repository

Add environment variables

Deploy!

Render Configuration
yaml
# render.yaml
services:
  - type: web
    name: ecommerce
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
    startCommand: gunicorn ecommerce.wsgi:application
🔧 Environment Variables
Variable	Description	Required
SECRET_KEY	Django secret key	Yes
DEBUG	Debug mode (True/False)	Yes
ALLOWED_HOSTS	Allowed hosts	Yes
DATABASE_URL	Database connection URL	Yes
STRIPE_PUBLISHABLE_KEY	Stripe publishable key	No
STRIPE_SECRET_KEY	Stripe secret key	No
STRIPE_WEBHOOK_SECRET	Stripe webhook secret	No
🧪 Testing
Run tests:

bash
python manage.py test apps.accounts.tests
python manage.py test apps.products.tests
python manage.py test apps.orders.tests
📱 Screenshots
Add screenshots of your application here

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit changes (git commit -m 'Add some AmazingFeature')

Push to branch (git push origin feature/AmazingFeature)

Open a Pull Request

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

👤 Author
eKidenge

GitHub: @eKidenge

🙏 Acknowledgments
Django Community

Bootstrap Team

Stripe API

M-Pesa API

All open source contributors

📧 Support
For support, email support@ecommerce.com or open an issue on GitHub.

🗺️ Roadmap
□ Mobile app (React Native)
□ Multi-vendor marketplace
□ AI-powered product recommendations
□ Chat support system
□ Advanced analytics
□ Email marketing integration
□ Social media login
□ Product comparison feature
□ Bulk order discounts
□ Subscription products
Built with ❤️ using Django

This README is comprehensive and ready to copy-paste to your GitHub repository. It covers everything from installation to deployment and includes all the necessary information for users and contributors.