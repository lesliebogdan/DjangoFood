from django.shortcuts import render,get_object_or_404
from vendor.models import Vendor
from menu.models import FoodItem,Category
from .models import Cart

from marketplace.context_processors import get_cart_counter

from django.db.models import Prefetch

from django.http import HttpResponse, JsonResponse

# Create your views here.

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True,user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors':vendors,
        'vendor_count':vendor_count
    }
    return render(request, 'marketplace/listings.html',context)


def vendor_detail(request,vendor_slug):
    vendor = get_object_or_404(Vendor,vendor_slug=vendor_slug)
    fooditems = FoodItem.objects.filter(vendor = vendor)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor':vendor,
        'categories':categories,
        'cart_items':cart_items
    }
    return render(request, 'marketplace/vendor_detail.html',context)

def add_to_cart(request,food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with')=='XMLHttpRequest':
            # check if the food item exists, if so add it.
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # check if the user has already added the food item to the cart
                # if they have, increment qty
                # else - add it with qty =1
                try: 
                    check_cart = Cart.objects.get(user=request.user, fooditem = fooditem)
                    # increase cart qty
                    check_cart.quantity +=1
                    check_cart.save()
                    return JsonResponse({'status':'Success','message':'Increased the cart quantity','cart_counter':get_cart_counter(request),'qty':check_cart.quantity})
                except:
                    check_cart = Cart.objects.create(user=request.user, fooditem = fooditem, quantity=1)
                    return JsonResponse({'status':'Success','message':'Food item added to cart','cart_counter':get_cart_counter(request),'qty':check_cart.quantity})

            except:
                return JsonResponse({'status':'Failed','message':'This food does not exist'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid Request'})
    else:

        return JsonResponse({'status':'Failed','message':'Please log in to continue'})