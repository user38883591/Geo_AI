from django import forms
from .models import LeafImage,Supplier,Product,Crop_recomendations
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.db import IntegrityError




class LeafDiseaseForm(forms.ModelForm):
    class Meta:
        model = LeafImage
        fields = ['crop_name','description','image']
class CropRecommendationForm(forms.ModelForm):
    class Meta:
        model = Crop_recomendations
        fields = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']
        labels = {
            'nitrogen': 'Nitrogen',
            'phosphorus': 'Phosphorus',
            'potassium': 'Potassium',
            'temperature': 'Temperature (°C)',
            'humidity': 'Humidity (%)',
            'ph': 'pH',
            'rainfall': 'Rainfall (mm)',
        }
        widgets = {
            'nitrogen': forms.NumberInput(attrs={'placeholder': 'Enter Nitrogen', 'class': 'form-control', 'step': '0'}),
            'phosphorus': forms.NumberInput(attrs={'placeholder': 'Enter Phosphorus', 'class': 'form-control', 'step': '0'}),
            'potassium': forms.NumberInput(attrs={'placeholder': 'Enter Potassium', 'class': 'form-control', 'step': '0'}),
            'temperature': forms.NumberInput(attrs={'placeholder': 'Enter Temperature in °C', 'class': 'form-control', 'step': '0.01'}),
            'humidity': forms.NumberInput(attrs={'placeholder': 'Enter Humidity in %', 'class': 'form-control', 'step': '0.01'}),
            'ph': forms.NumberInput(attrs={'placeholder': 'Enter pH value', 'class': 'form-control', 'step': '0.01'}),
            'rainfall': forms.NumberInput(attrs={'placeholder': 'Enter Rainfall in mm', 'class': 'form-control', 'step': '0.01'}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'email', 'contact', 'address']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image']



class UserRegisterForm(UserCreationForm):
    USER_TYPES = (
        ('farmer', 'Farmer'),
        ('supplier', 'Supplier'),
    )
    
    user_type = forms.ChoiceField(choices=USER_TYPES, required=True)
    farm_acreage = forms.DecimalField(required=False, max_digits=10, decimal_places=2)
    crop_cultivated = forms.CharField(required=False, max_length=100)
    location = forms.CharField(required=False, max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()

        user_type = self.cleaned_data.get('user_type')
        profile, created = Profile.objects.get_or_create(
            user=user,
             defaults={
                'user_type': user_type,
                'farm_acreage': self.cleaned_data.get('farm_acreage') if user_type == 'farmer' else None,
                 'crop_cultivated': self.cleaned_data.get('crop_cultivated') if user_type == 'farmer' else None,
                'location': self.cleaned_data.get('location') if user_type == 'farmer' else None,
             }
        )
        
        if not created:
            profile.user_type = user_type
            if user_type == 'farmer':
                profile.farm_acreage = self.cleaned_data.get('farm_acreage')
                profile.crop_cultivated = self.cleaned_data.get('crop_cultivated')
                profile.location = self.cleaned_data.get('location')
            profile.save()

        return user