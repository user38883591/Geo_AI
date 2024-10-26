from django.http import HttpResponse
from django.contrib.auth import authenticate, login,logout
from django.conf import settings
import numpy as np
from .models import LeafImage,Product, Order,Commission,Profile,Supplier
from .serializers import LeafImageSerializer, ImageUploadSerializer 
from django.shortcuts import render, redirect,get_object_or_404
from .forms import LeafDiseaseForm,SupplierForm,UserRegisterForm,ProductForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from decimal import Decimal
from django.contrib import messages
import requests 
import torch 
from torchvision import transforms
from PIL import Image
import io



def Home(request):
    user_type = None
    if request.user.is_authenticated:
    
        user_type = getattr(request.user.profile, 'user_type', None)

    return render(request, 'index.html', {'user_type': user_type})

 #Weather API


def get_weather_data(city_name):
    api_key = settings.OPENWEATHER_API_KEY
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def farmer_dashboard(request):
    products = Product.objects.all()
    orders = Order.objects.filter(user=request.user)
    city = request.GET.get('city')  # Get the city from the form submission
    weather_data = get_weather_data(city) if city else None

    return render(request, 'farmers_dashboard.html', {
        'products': products,
        'orders': orders,
        'weather_data': weather_data,
        'city': city
    })
    


#Registration view
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')  
        else:
            messages.error(request, "Registration failed. Please check your inputs.")
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        # print(f"User type: {request.user.profile.user_type}")
        
        if user is not None:
        
            login(request, user)
            
            # Check the user profile type and redirect appropriately
            if hasattr(user, 'profile'):
                if user.profile.user_type == 'farmer':
                    return redirect('farmers_dashboard')  
                elif user.profile.user_type == 'supplier':
                    return redirect('supplier_dashboard') 
            else:
                # Handle case where profile does not exist
                logout(request)
                messages.error(request, "Profile not found. Please contact support.")
                return redirect('login')
        else:
            # Failed authentication
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    
    # Render login page for GET requests
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login') 


def image_upload_view(request):
    if request.method == 'POST':
        form = LeafDiseaseForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['image']
            prediction = predict_image(image)
            return render(request, 'results.html', {'prediction': prediction})
    else:
        form = LeafDiseaseForm()
    return render(request, 'upload_leaf_image.html', {'form': form})

# Load the pre-trained model
from .model_file import CNNModel

model = CNNModel(num_classes=9)
model.load_state_dict(torch.load('main/savedmodels/Leaf_disease_predict_model.pth'))
model.eval()

def predict_image(image):
    # Define the transformations for the input image
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # Preprocess the image
    img = Image.open(io.BytesIO(image.read()))
    img_t = transform(img).unsqueeze(0)

    # Make prediction
    with torch.no_grad():
        output = model(img_t)
        _, predicted = torch.max(output, 1)  # Get the predicted class index
    
    # Map the predicted index to the class name
    class_names = ['Bacterial leaf blight', 'Blight', 'Brown spot', 'Gray_Leaf_Spot', 'Healthy', 'Leaf smut', 'Miner', 'Phoma', 'Rust']
    
    # Get the class name using the predicted index
    predicted_class_name = class_names[predicted.item()]
    
    return predicted_class_name

#market place views

@login_required
def add_product(request):
    try:
        # Check if the user is a supplier
        if request.user.profile.user_type != 'supplier':
            return HttpResponse("Only suppliers can add products.")
    except Profile.DoesNotExist:
        return HttpResponse("User profile not found.")
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')

        product = Product.objects.create(
            supplier=request.user.supplier,
            name=name,
            description=description,
            price=Decimal(price),
            image=image
        )
        return redirect('supplier_dashboard')
    return render(request, 'add_product.html')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_details.html', {'product': product})

    


# Farmer-only place order view
@login_required
def place_order(request, product_id):
    try:
        if request.user.profile.user_type != 'farmer':
            return HttpResponse("Only farmers can place orders.")
    except Profile.DoesNotExist:
        return HttpResponse("User profile not found.")
    
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        total_price = Decimal(product.price) * Decimal(quantity)
        
        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            total_price=total_price
        )
        
        # Calculate and save the commission
        Commission.objects.create(order=order, commission_percentage=Decimal('10.0'))
        return redirect('order_success')
    return render(request, 'place_order.html', {'product': product})
def order_success(request):
    return render(request, 'order_success.html')


# Supplier dashboard to view orders made for their products
@login_required
def supplier_dashboard(request):
    try:
        # Check if the user is a supplier
        if request.user.profile.user_type != 'supplier':
            return HttpResponse("Only suppliers can view this dashboard.")
        
        # Retrieve orders for products belonging to this supplier
        supplier = request.user.supplier
        products = Product.objects.filter(supplier=supplier)
        orders = Order.objects.filter(product__in=products)
        
    except (Profile.DoesNotExist, Supplier.DoesNotExist):
        return HttpResponse("Supplier profile not found.")
    
    return render(request, 'supplier_dashboard.html', {'products': products, 'orders': orders})

def order_success(request):
    return render(request, 'order_success.html')



















