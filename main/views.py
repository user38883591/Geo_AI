from django.http import HttpResponse
from django.contrib.auth import authenticate, login,logout
from django.conf import settings
import numpy as np
from .models import LeafImage,Crop_recomendations,Product, Order,Commission,Profile,Supplier
from .serializers import LeafImageSerializer, ImageUploadSerializer 
from django.shortcuts import render, redirect,get_object_or_404
from .forms import LeafDiseaseForm,SupplierForm,UserRegisterForm,ProductForm,CropRecommendationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import logging
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
    farm_acreage = None
    crop_cultivated = None
    location = None
    
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        user_type = profile.user_type if profile else None

        # Fetch farm details if the user is a farmer
        if user_type == 'farmer':
            farm_acreage = profile.farm_acreage
            crop_cultivated = profile.crop_cultivated
            location = profile.location

    city = request.GET.get('city', 'YourDefaultCity')
    weather_data = get_weather_data(city) if city else None

    return render(request, 'index.html', {
        'user_type': user_type,
        'city': city,
        'weather_data': weather_data,
        'farm_acreage': farm_acreage,
        'crop_cultivated': crop_cultivated,
        'location': location
    })


 
 
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


logger = logging.getLogger(__name__)
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            # Redirect based on user type
            if hasattr(user, 'profile'):
                return redirect('index' if user.profile.user_type == 'farmer' else 'supplier_dashboard')
            else:
                logout(request)
                messages.error(request, "Profile not found. Please contact support.")
                return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
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



from .model_file import make_prediction  # Import the make_prediction function from the file where you load the model and scalers

crop_dict = {
    1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
    8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
    14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
    19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
}

def predict_view(request):
    result = None
    past_predictions = Crop_recomendations.objects.all().order_by('-prediction_date')[:10]  # Last 10 predictions

    if request.method == 'POST':
        form = CropRecommendationForm(request.POST)
        if form.is_valid():
            # Get cleaned data from the form
            input_features = [
                form.cleaned_data['nitrogen'],
                form.cleaned_data['phosphorus'],
                form.cleaned_data['potassium'],
                form.cleaned_data['temperature'],
                form.cleaned_data['humidity'],
                form.cleaned_data['ph'],
                form.cleaned_data['rainfall'],
            ]

            # Make a prediction
            prediction = make_prediction(input_features)
            predicted_index = prediction[0]
            result = crop_dict.get(predicted_index, "Unknown")  # Map the index to crop name

            # Save prediction to the database
            saved_prediction = form.save(commit=False)
            saved_prediction.recommended_crop = result
            saved_prediction.save()

    else:
        form = CropRecommendationForm()

    return render(request, 'crop_recommendation.html', {
        'form': form,
        'result': result,
        'past_predictions': past_predictions
    })

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



















