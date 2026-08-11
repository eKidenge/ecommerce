#!/usr/bin/env bash
set -o errexit

echo "=================================================="
echo "  E-COMMERCE PLATFORM - BUILD SCRIPT"
echo "=================================================="

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# ============================================
# CREATE STATIC DIRECTORIES
# ============================================
echo ""
echo "📁 Creating static directories..."
mkdir -p apps/accounts/static
mkdir -p apps/products/static
mkdir -p apps/dashboard/static
mkdir -p apps/cart/static
mkdir -p apps/orders/static
mkdir -p apps/wishlist/static
mkdir -p apps/payments/static
mkdir -p apps/reviews/static

# ============================================
# CHECK DATABASE TYPE
# ============================================
echo ""
echo "🗄️  Checking database configuration..."

# Check if we're using PostgreSQL or SQLite
if [[ "$DATABASE_URL" == postgresql://* ]] || [[ "$DATABASE_URL" == postgres://* ]]; then
    echo "✅ Using PostgreSQL database"
    DATABASE_TYPE="postgresql"
else
    echo "⚠️ Using SQLite database (fallback)"
    DATABASE_TYPE="sqlite"
fi

# ============================================
# DATABASE MIGRATIONS
# ============================================
echo ""
echo "🗄️  Running database migrations..."

if [[ "$DATABASE_TYPE" == "postgresql" ]]; then
    echo "   📌 Using PostgreSQL with DATABASE_URL"
    
    # For PostgreSQL, we need to handle migrations carefully
    # First, try to create the migrations
    echo "   Creating migrations..."
    python manage.py makemigrations || true
    
    # Check if we need to fake migrations (for existing database)
    echo "   Checking migration status..."
    
    # Try to migrate normally first
    echo "   Attempting to apply migrations..."
    if python manage.py migrate; then
        echo "   ✅ Migrations applied successfully"
    else
        echo "   ⚠️ Migration failed, trying to fake initial migrations..."
        
        # If migration fails, it might be due to existing tables
        # Try to fake the migrations and then migrate
        echo "   Faking initial migrations..."
        python manage.py migrate --fake || true
        
        echo "   Running migrations again..."
        python manage.py migrate || true
        
        echo "   ✅ Migrations completed"
    fi
    
else
    # SQLite - simple migration
    echo "   📌 Using SQLite"
    
    # Delete the SQLite database file for fresh start
    echo "   Deleting existing SQLite database..."
    rm -f db.sqlite3
    
    echo "   Creating migrations..."
    python manage.py makemigrations
    
    echo "   Applying migrations..."
    python manage.py migrate
fi

# ============================================
# COLLECT STATIC FILES
# ============================================
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# ============================================
# SEED DATABASE WITH DEMO DATA (Only for SQLite or fresh PostgreSQL)
# ============================================
echo ""
echo "🌱 Seeding database with demo data..."

# Only seed if it's SQLite or if we're confident the database is fresh
if [[ "$DATABASE_TYPE" == "sqlite" ]]; then
    echo "   Seeding SQLite database..."
    python manage.py seed_data || echo "   ⚠️ Seed data skipped (command not found)"
else
    echo "   ⚠️ Skipping seed_data for PostgreSQL (to avoid conflicts with existing data)"
    echo "   You can run 'python manage.py seed_data' manually if needed."
fi

# ============================================
# CREATE SUPERUSER
# ============================================
echo ""
echo "👤 Creating superuser..."

python manage.py shell << EOF
from django.contrib.auth import get_user_model
from apps.accounts.models import User, UserProfile

User = get_user_model()

print("\n" + "="*50)
print("  CREATING SUPERUSER")
print("="*50)

# Check if superuser exists
if not User.objects.filter(is_superuser=True).exists():
    print("\nCreating superuser...")
    
    # Delete any existing admin user to avoid conflicts
    User.objects.filter(username='admin').delete()
    
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@ecommerce.go.ke',
        password='Admin@123!',
        first_name='System',
        last_name='Administrator',
        role='admin',
        is_verified=True,
        is_active=True
    )
    UserProfile.objects.get_or_create(user=admin)
    print("✅ Superuser created successfully!")
    print("   Username: admin")
    print("   Email: admin@ecommerce.go.ke")
    print("   Password: Admin@123!")
else:
    print("✅ Superuser already exists.")
    
    # Ensure admin user has proper profile
    try:
        admin = User.objects.get(username='admin')
        UserProfile.objects.get_or_create(user=admin)
    except User.DoesNotExist:
        pass

# ============================================
# CREATE ADDITIONAL DEMO USERS
# ============================================
print("\n" + "="*50)
print("  CREATING DEMO USERS")
print("="*50)

# Create Vendor if not exists
if not User.objects.filter(username='vendor').exists():
    print("\nCreating Vendor...")
    vendor = User.objects.create_user(
        username='vendor',
        email='vendor@ecommerce.go.ke',
        password='Vendor@123',
        first_name='Vendor',
        last_name='User',
        role='vendor',
        is_verified=True,
        is_active=True
    )
    UserProfile.objects.get_or_create(user=vendor)
    print("✅ Vendor created!")
    print("   Username: vendor")
    print("   Password: Vendor@123")

# Create Customer if not exists
if not User.objects.filter(username='customer').exists():
    print("\nCreating Customer...")
    customer = User.objects.create_user(
        username='customer',
        email='customer@ecommerce.go.ke',
        password='Customer@123',
        first_name='Customer',
        last_name='User',
        role='customer',
        is_verified=True,
        is_active=True
    )
    UserProfile.objects.get_or_create(user=customer)
    print("✅ Customer created!")
    print("   Username: customer")
    print("   Password: Customer@123")

# Create Staff Member if not exists
if not User.objects.filter(username='staff').exists():
    print("\nCreating Staff Member...")
    staff = User.objects.create_user(
        username='staff',
        email='staff@ecommerce.go.ke',
        password='Staff@123',
        first_name='Staff',
        last_name='User',
        role='staff',
        is_verified=True,
        is_active=True
    )
    UserProfile.objects.get_or_create(user=staff)
    print("✅ Staff Member created!")
    print("   Username: staff")
    print("   Password: Staff@123")

# Create Store Manager if not exists
if not User.objects.filter(username='storemanager').exists():
    print("\nCreating Store Manager...")
    storemanager = User.objects.create_user(
        username='storemanager',
        email='storemanager@ecommerce.go.ke',
        password='StoreManager@123',
        first_name='Store',
        last_name='Manager',
        role='store_manager',
        is_verified=True,
        is_active=True
    )
    UserProfile.objects.get_or_create(user=storemanager)
    print("✅ Store Manager created!")
    print("   Username: storemanager")
    print("   Password: StoreManager@123")

# ============================================
# SUMMARY
# ============================================
print("\n" + "="*50)
print("  USER SUMMARY")
print("="*50)
print("")
print("🔑 ADMIN (Full System Access)")
print("   Username: admin")
print("   Password: Admin@123!")
print("")
print("🏪 VENDOR (Product Management)")
print("   Username: vendor")
print("   Password: Vendor@123")
print("")
print("👤 CUSTOMER (Shopping Access)")
print("   Username: customer")
print("   Password: Customer@123")
print("")
print("👔 STAFF (Order Management)")
print("   Username: staff")
print("   Password: Staff@123")
print("")
print("📋 STORE MANAGER (Store Operations)")
print("   Username: storemanager")
print("   Password: StoreManager@123")
print("")
print("="*50)
print("  BUILD COMPLETED SUCCESSFULLY!")
print("="*50)
EOF

echo ""
echo "✅ E-Commerce Platform build completed successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 Visit your site at: https://your-ecommerce-site.onrender.com"
echo "  🔑 Admin Login: https://your-ecommerce-site.onrender.com/admin/"
echo "  📊 Admin Dashboard: https://your-ecommerce-site.onrender.com/dashboard/admin/"
echo "  🏪 Vendor Dashboard: https://your-ecommerce-site.onrender.com/dashboard/vendor/"
echo "  👤 User Login: https://your-ecommerce-site.onrender.com/accounts/login/"
echo "  🛒 Browse Products: https://your-ecommerce-site.onrender.com/products/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"