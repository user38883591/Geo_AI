from django.urls import path
from.import views

urlpatterns = [
    path('', views.Home, name='index'),
    path('upload-leaf/', views.image_upload_view, name='image_leaf_upload'),
    path('products/', views.product_list, name='product_list'),
    path('register/', views.register, name='register'),
    path('supplier-dashboard/', views.supplier_dashboard, name='supplier_dashboard'),
    path('farmer-dashboard/', views.farmer_dashboard, name='farmers_dashboard'),
    path('products/<int:product_id>/', views.product_detail, name='product_details'),
    path('add-product/', views.add_product, name='add_product'),
    path('place-order/<int:product_id>/', views.place_order, name='place_order'),
    path('order/success/', views.order_success, name='order_success'),  
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('predict/', views.predict_view, name='crop_recommendation'),
    # path('weather/', views.weather_view, name='weather'),
]

