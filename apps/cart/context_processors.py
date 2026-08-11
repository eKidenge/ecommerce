from .models import Cart

def cart_total(request):
    """
    Context processor to add cart total to all templates
    """
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            return {
                'cart_total_items': cart.total_items,
                'cart_total_price': cart.total_price,
                'cart_total_quantity': cart.total_quantity,
            }
        except Cart.DoesNotExist:
            return {
                'cart_total_items': 0,
                'cart_total_price': 0,
                'cart_total_quantity': 0,
            }
    else:
        # For anonymous users, you could use session-based cart
        # For now, return empty values
        return {
            'cart_total_items': 0,
            'cart_total_price': 0,
            'cart_total_quantity': 0,
        }