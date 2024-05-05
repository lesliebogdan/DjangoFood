from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from vendor.forms import VendorForm
from .utils import detectUser
from .models import User, UserProfile
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

#### custom decorators 

#restrict the vendor from accessing the customer page

def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied
# restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied 

####

# Create your views here.
def registerUser(request):

    if request.user.is_authenticated:
        messages.warning(request, 'You are alreday logged in!')
        return redirect('dashboard')
    elif request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():


            # use the 'create_user' method we already have in our User model
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']


            user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                username = username,
                email = email,
                password = password,
            )
            user.role = User.CUSTOMER
            user.save()

            # message the user
            messages.success(request, 'Your account has been registered successfully!')

            return redirect('registerUser')
        else:
            print('invalid form submission')
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/registerUser.html',context)



def registerVendor(request):

    if request.user.is_authenticated:
        messages.warning(request, 'You are alreday logged in!')
        return redirect('myAccount')

    elif request.method == 'POST':
        # store the data and also create the user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            # create vendor and user etc
            # throw some errors for the issue
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                username = username,
                email = email,
                password = password,
            )
            user.role = User.RESTAURANT
            user.save()

            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request, 'Your vendor account has been created! Please wait for approval and further instructions')
            return redirect('registerVendor')

        else:
            print('invalid form')
            print(form.errors)

    else:

        form = UserForm()
        v_form = VendorForm()

    context = {
        'form':form,
        'v_form':v_form
    }

    return render(request, 'accounts/registerVendor.html',context)


def login(request):

    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    

    elif request.method == 'POST':
        # user wants to login
        # these names come from the html template variable names for the inputs
        email = request.POST['email']
        password = request.POST['password']

        # check if the email/password exist in your DB

        # Django has inbuilt functions for this 
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in!')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login in credentials')
            return redirect('login')
        
    return render(request, 'accounts/login.html')

def logout(request):
    print('LESLIE LOGOUT')
    auth.logout(request)
    messages.info(request, 'You are logged out')
    return redirect('login')

# decortator sends them to the login url if they are not signed in already
### url is still the original url presented to the url path
@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):    
    return render(request,'accounts/custDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request,'accounts/vendorDashboard.html')