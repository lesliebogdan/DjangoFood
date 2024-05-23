from django.shortcuts import render,get_object_or_404,redirect
from vendor.models import Vendor
from menu.models import FoodItem,Category
from .models import Cart

from marketplace.context_processors import get_cart_counter,get_cart_amounts

from django.db.models import Prefetch,Q

from django.http import HttpResponse, JsonResponse

from django.contrib.auth.decorators import login_required

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

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
                    return JsonResponse({'status':'Success','message':'Increased the cart quantity','cart_counter':get_cart_counter(request),'qty':check_cart.quantity,'cart_amount':get_cart_amounts(request)})
                except:
                    check_cart = Cart.objects.create(user=request.user, fooditem = fooditem, quantity=1)
                    return JsonResponse({'status':'Success','message':'Food item added to cart','cart_counter':get_cart_counter(request),'qty':check_cart.quantity,'cart_amount':get_cart_amounts(request)})

            except:
                return JsonResponse({'status':'Failed','message':'This food does not exist'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid Request'})
    else:

        return JsonResponse({'status':'login_required','message':'Please log in to continue'})
    

def decrease_cart(request,food_id):
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
                    if check_cart.quantity > 1:
                        check_cart.quantity -=1
                        check_cart.save()
                    else:
                        check_cart.delete()
                        check_cart.quantity = 0
                    return JsonResponse({'status':'Success','message':'Decreased the cart quantity','cart_counter':get_cart_counter(request),'qty':check_cart.quantity,'cart_amount':get_cart_amounts(request)})
                except:
                    return JsonResponse({'status':'Failed','message':'You do not have this item in your cart','cart_counter':get_cart_counter(request),'qty':check_cart.quantity,'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'Failed','message':'This food does not exist'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid Request'})
    else:

        return JsonResponse({'status':'login_required','message':'Please log in to continue'})    

@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')

    # want to order by created_at date


    context = {
        'cart_items':cart_items
    }
    return render(request,'marketplace/cart.html',context)


def delete_cart(request,cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with')=='XMLHttpRequest':
            try:
                cart_item = Cart.objects.get(user=request.user,id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'Success','message':'Cart item deleted','cart_counter':get_cart_counter(request),'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'Failed','message':'Cart item does not exist'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid Request'})
        

def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

        vendors = Vendor.objects.filter(vendor_name__icontains=keyword,is_approved=True,user__is_active=True)

        # get vendor ids that has the food item the user is looking for

        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
        
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))

            vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
            user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            for v in vendors:
                v.kms = round(v.distance.km, 1)
        vendor_count = vendors.count()
        context = {
            'vendors': vendors,
            'vendor_count': vendor_count,
        #    'source_location': address,
        }

        return render(request, 'marketplace/listings.html', context)