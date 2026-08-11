// Main JavaScript for E-Store

$(document).ready(function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
    
    // Quantity input controls
    $('.quantity-input').each(function() {
        const input = $(this).find('input[type="number"]');
        const decrementBtn = $(this).find('.decrement');
        const incrementBtn = $(this).find('.increment');
        
        decrementBtn.on('click', function() {
            let val = parseInt(input.val()) || 0;
            if (val > parseInt(input.attr('min') || 1)) {
                input.val(val - 1).trigger('change');
            }
        });
        
        incrementBtn.on('click', function() {
            let val = parseInt(input.val()) || 0;
            let max = parseInt(input.attr('max')) || 999;
            if (val < max) {
                input.val(val + 1).trigger('change');
            }
        });
    });
    
    // Star rating
    $('.star-rating .star').on('mouseenter', function() {
        const value = $(this).data('value');
        $(this).closest('.star-rating').find('.star').each(function() {
            if ($(this).data('value') <= value) {
                $(this).addClass('active');
            } else {
                $(this).removeClass('active');
            }
        });
    }).on('mouseleave', function() {
        const container = $(this).closest('.star-rating');
        const selected = container.find('.star.selected');
        if (selected.length) {
            const value = selected.data('value');
            container.find('.star').each(function() {
                if ($(this).data('value') <= value) {
                    $(this).addClass('active');
                } else {
                    $(this).removeClass('active');
                }
            });
        } else {
            container.find('.star').removeClass('active');
        }
    }).on('click', function() {
        const container = $(this).closest('.star-rating');
        container.find('.star').removeClass('selected');
        $(this).addClass('selected');
        const ratingInput = container.find('input[type="hidden"]');
        if (ratingInput.length) {
            ratingInput.val($(this).data('value'));
        }
    });
});

// AJAX Functions
function addToCart(productId, quantity = 1, variantId = null) {
    $.ajax({
        url: '/cart/add/',
        method: 'POST',
        data: {
            product_id: productId,
            quantity: quantity,
            variant_id: variantId,
            csrfmiddlewaretoken: getCsrfToken()
        },
        success: function(response) {
            if (response.success) {
                updateCartBadge(response.total_items);
                showToast('Product added to cart!', 'success');
            }
        },
        error: function(xhr) {
            showToast(xhr.responseJSON?.error || 'Failed to add to cart', 'error');
        }
    });
}

function addToWishlist(productId) {
    $.ajax({
        url: '/wishlist/add/',
        method: 'POST',
        data: {
            product_id: productId,
            csrfmiddlewaretoken: getCsrfToken()
        },
        success: function(response) {
            if (response.success) {
                showToast('Added to wishlist!', 'success');
                updateWishlistButton(productId, true);
            }
        },
        error: function() {
            showToast('Failed to add to wishlist', 'error');
        }
    });
}

function removeFromWishlist(productId) {
    $.ajax({
        url: '/wishlist/remove/',
        method: 'POST',
        data: {
            product_id: productId,
            csrfmiddlewaretoken: getCsrfToken()
        },
        success: function(response) {
            if (response.success) {
                showToast('Removed from wishlist', 'info');
                updateWishlistButton(productId, false);
            }
        },
        error: function() {
            showToast('Failed to remove from wishlist', 'error');
        }
    });
}

// Helper Functions
function getCsrfToken() {
    return $('input[name="csrfmiddlewaretoken"]').val() || 
           $('meta[name="csrf-token"]').attr('content') || 
           document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1];
}

function updateCartBadge(count) {
    $('.cart-badge').text(count || 0);
}

function updateWishlistButton(productId, inWishlist) {
    const btn = $(`[data-product-id="${productId}"] .wishlist-btn`);
    if (inWishlist) {
        btn.addClass('text-danger').removeClass('text-muted');
        btn.find('i').addClass('fas').removeClass('far');
    } else {
        btn.removeClass('text-danger').addClass('text-muted');
        btn.find('i').addClass('far').removeClass('fas');
    }
}

function showToast(message, type = 'info') {
    const toastContainer = $('#toast-container');
    if (!toastContainer.length) {
        $('body').append('<div id="toast-container" class="position-fixed bottom-0 end-0 p-3" style="z-index: 9999;"></div>');
    }
    
    const toast = $(`
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('#toast-container').append(toast);
    const bsToast = new bootstrap.Toast(toast[0], { delay: 3000 });
    bsToast.show();
    
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

function showLoading(show = true) {
    if (show) {
        $('body').append(`
            <div class="spinner-overlay">
                <div class="spinner"></div>
            </div>
        `);
    } else {
        $('.spinner-overlay').remove();
    }
}

// Product image gallery
function initProductGallery() {
    $('.thumbnail-images img').on('click', function() {
        const mainImage = $('.main-image img');
        const newSrc = $(this).data('full') || $(this).attr('src');
        mainImage.attr('src', newSrc);
        $('.thumbnail-images img').removeClass('active');
        $(this).addClass('active');
    });
}

// Initialize on page load
$(document).ready(function() {
    initProductGallery();
});