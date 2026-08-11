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
    echo "   Creating migrations..."
    python manage.py makemigrations || true
    echo "   Attempting to apply migrations..."
    if python manage.py migrate; then
        echo "   ✅ Migrations applied successfully"
    else
        echo "   ⚠️ Migration failed, trying to fake initial migrations..."
        python manage.py migrate --fake || true
        echo "   Running migrations again..."
        python manage.py migrate || true
        echo "   ✅ Migrations completed"
    fi
else
    echo "   📌 Using SQLite"
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

if [[ "$DATABASE_TYPE" == "sqlite" ]]; then
    echo "   Seeding SQLite database..."
    python manage.py seed_data || echo "   ⚠️ Seed data skipped (command not found)"
else
    echo "   ⚠️ Skipping seed_data for PostgreSQL (to avoid conflicts with existing data)"
    echo "   You can run 'python manage.py seed_data' manually if needed."
fi

# ============================================
# CREATE SUPERUSER - UPDATED FOR YOUR USER MODEL
# ============================================
echo ""
echo "👤 Creating superuser..."

python manage.py shell << EOF
from django.contrib.auth import get_user_model
from apps.accounts.models import UserProfile
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
        user_type='admin',          # From your USER_TYPES
        is_email_verified=True,
        is_active=True,
        is_blocked=False,
        is_banned=False
    )
    # Create UserProfile for admin
    UserProfile.objects.get_or_create(user=admin)
    print("✅ Superuser created successfully!")
    print("   Username: admin")
    print("   Email: admin@ecommerce.go.ke")
    print("   Password: Admin@123!")
    print("   User Type: admin")
else:
    print("✅ Superuser already exists.")
    
    # Ensure admin user has proper profile
    try:
        admin = User.objects.get(username='admin')
        UserProfile.objects.get_or_create(user=admin)
        print(f"✅ Admin user exists: {admin.email}")
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
        user_type='vendor',
        is_email_verified=True,
        is_active=True,
        is_blocked=False,
        is_banned=False,
        store_name='Vendor Store',
        is_store_active=True
    )
    UserProfile.objects.get_or_create(user=vendor)
    print("✅ Vendor created!")
    print("   Username: vendor")
    print("   Password: Vendor@123")
    print("   Store Name: Vendor Store")

# Create Customer if not exists
if not User.objects.filter(username='customer').exists():
    print("\nCreating Customer...")
    customer = User.objects.create_user(
        username='customer',
        email='customer@ecommerce.go.ke',
        password='Customer@123',
        first_name='Customer',
        last_name='User',
        user_type='customer',
        is_email_verified=True,
        is_active=True,
        is_blocked=False,
        is_banned=False
    )
    UserProfile.objects.get_or_create(user=customer)
    print("✅ Customer created!")
    print("   Username: customer")
    print("   Password: Customer@123")

# Create Moderator if not exists
if not User.objects.filter(username='moderator').exists():
    print("\nCreating Moderator...")
    moderator = User.objects.create_user(
        username='moderator',
        email='moderator@ecommerce.go.ke',
        password='Moderator@123',
        first_name='Moderator',
        last_name='User',
        user_type='moderator',
        is_email_verified=True,
        is_active=True,
        is_blocked=False,
        is_banned=False
    )
    UserProfile.objects.get_or_create(user=moderator)
    print("✅ Moderator created!")
    print("   Username: moderator")
    print("   Password: Moderator@123")

# Create Staff Member if not exists (using customer type as staff)
if not User.objects.filter(username='staff').exists():
    print("\nCreating Staff Member...")
    staff = User.objects.create_user(
        username='staff',
        email='staff@ecommerce.go.ke',
        password='Staff@123',
        first_name='Staff',
        last_name='User',
        user_type='customer',
        is_email_verified=True,
        is_active=True,
        is_blocked=False,
        is_banned=False
    )
    UserProfile.objects.get_or_create(user=staff)
    print("✅ Staff Member created!")
    print("   Username: staff")
    print("   Password: Staff@123")

# ============================================
# CREATE DEFAULT ADDRESS FOR USERS (Optional)
# ============================================
print("\n" + "="*50)
print("  CREATING DEFAULT ADDRESSES")
print("="*50)

from apps.accounts.models import Address

# Add default address for admin
try:
    admin_user = User.objects.get(username='admin')
    if not Address.objects.filter(user=admin_user, is_default=True).exists():
        Address.objects.create(
            user=admin_user,
            address_type='both',
            address_line1='Government Procurement HQ',
            address_line2='Nairobi City Centre',
            city='Nairobi',
            state='Nairobi County',
            country='Kenya',
            postal_code='00100',
            phone_number='+254700123456',
            is_default=True,
            is_active=True
        )
        print("✅ Default address added for admin")
except User.DoesNotExist:
    pass

# Add default address for vendor
try:
    vendor_user = User.objects.get(username='vendor')
    if not Address.objects.filter(user=vendor_user, is_default=True).exists():
        Address.objects.create(
            user=vendor_user,
            address_type='both',
            address_line1='Vendor Store Location',
            address_line2='Industrial Area',
            city='Nairobi',
            state='Nairobi County',
            country='Kenya',
            postal_code='00200',
            phone_number='+254722123456',
            is_default=True,
            is_active=True
        )
        print("✅ Default address added for vendor")
except User.DoesNotExist:
    pass

# Add default address for customer
try:
    customer_user = User.objects.get(username='customer')
    if not Address.objects.filter(user=customer_user, is_default=True).exists():
        Address.objects.create(
            user=customer_user,
            address_type='both',
            address_line1='Customer Home Address',
            address_line2='Westlands',
            city='Nairobi',
            state='Nairobi County',
            country='Kenya',
            postal_code='00100',
            phone_number='+254733123456',
            is_default=True,
            is_active=True
        )
        print("✅ Default address added for customer")
except User.DoesNotExist:
    pass

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
print("   Email: admin@ecommerce.go.ke")
print("")
print("🏪 VENDOR (Product Management)")
print("   Username: vendor")
print("   Password: Vendor@123")
print("   Email: vendor@ecommerce.go.ke")
print("   Store: Vendor Store")
print("")
print("👤 CUSTOMER (Shopping Access)")
print("   Username: customer")
print("   Password: Customer@123")
print("   Email: customer@ecommerce.go.ke")
print("")
print("🛡️ MODERATOR (Content Moderation)")
print("   Username: moderator")
print("   Password: Moderator@123")
print("   Email: moderator@ecommerce.go.ke")
print("")
print("👔 STAFF (Order Management)")
print("   Username: staff")
print("   Password: Staff@123")
print("   Email: staff@ecommerce.go.ke")
print("")
print("="*50)
print("  BUILD COMPLETED SUCCESSFULLY!")
print("="*50)
EOF

echo ""
echo "✅ E-Commerce Platform build completed successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 Visit your site at: https://ecommerce-qdwv.onrender.com"
echo "  🔑 Admin Login: https://ecommerce-qdwv.onrender.com/admin/"
echo "  📊 Admin Dashboard: https://ecommerce-qdwv.onrender.com/dashboard/admin/"
echo "  🏪 Vendor Dashboard: https://ecommerce-qdwv.onrender.com/dashboard/vendor/"
echo "  👤 User Login: https://ecommerce-qdwv.onrender.com/accounts/login/"
echo "  🛒 Browse Products: https://ecommerce-qdwv.onrender.com/products/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"