from django.contrib import admin
from .models import LeafImage,Supplier,Order,Commission,Profile,Product,Crop_recomendations

admin.site.register(LeafImage)
admin.site.register(Supplier)
admin.site.register(Order)
admin.site.register(Profile)
admin.site.register(Product)
admin.site.register(Crop_recomendations)
@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('order', 'commission_percentage', 'commission_amount', 'date_earned')
    list_filter = ('date_earned',)  
    search_fields = ('order__id', 'order__user__username')  
    readonly_fields = ('commission_amount',) 


# Register your models here.
