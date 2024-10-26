from rest_framework import serializers
from .models import LeafImage,Product,Order

class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def validate_image(self, value):
        return value


class LeafImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeafImage
        fields = ['crop_name', 'description', 'image']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['user', 'product', 'quantity', 'total_price']




