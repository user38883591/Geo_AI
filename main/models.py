from django.db import models
from django.contrib.auth.models import User


class LeafImage(models.Model):
    crop_name = models.CharField(max_length=100)  
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='leaf_disease_images/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop_name} - {self.upload_date}"

class Supplier(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)  # Link Supplier to User
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name

class Product(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user}"
    

class Commission(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_earned = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate commission amount
        self.commission_amount = (self.commission_percentage / 100) * self.order.total_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commission for Order {self.order.id}"


class Profile(models.Model):
    USER_TYPES = (
        ('farmer', 'Farmer'),
        ('supplier', 'Supplier'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"