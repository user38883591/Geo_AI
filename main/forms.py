from django import forms
from .models import LeafImage,Supplier,Product
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.db import IntegrityError




class LeafDiseaseForm(forms.ModelForm):
    class Meta:
        model = LeafImage
        fields = ['crop_name','description','image']


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

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()  # Save the user first
        
        # Get the selected user type from the form data
        user_type = self.cleaned_data.get('user_type')
        
        # Check if the profile already exists before creating one
        profile, created = Profile.objects.get_or_create(user=user, defaults={'user_type': user_type})
        
        # If the profile already exists, update its user_type
        if not created:
            profile.user_type = user_type
            profile.save()

        return user