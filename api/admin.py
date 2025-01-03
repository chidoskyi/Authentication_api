from django.contrib import admin
from .models import User,Meals,Categories,Cart,Orders,Contact
from django.contrib.auth.admin import UserAdmin

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('uid', 'username', 'email', 'is_email_verified', 'is_staff', 'is_active')
    list_editable = ('is_staff', 'is_active','is_email_verified')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'email_confirmed_at', 'app_metadata', 'user_metadata', 'is_anonymous')}),
    )
    
@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('uid', 'title', 'image')
    search_fields = ('title',)
    ordering = ('title',)

@admin.register(Meals)
class MealsAdmin(admin.ModelAdmin):
    list_display = ('uid', 'title', 'category', 'price','toppicks', 'image')
    list_filter = ('toppicks', 'category')
    list_editable = ('toppicks','price')
    search_fields = ('title','toppicks', 'category__title')
    ordering = ('title',)
    
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('uid', 'user', 'meal', 'quantity', 'price', 'created_at', 'updated_at')
    search_fields = ('user__username', 'meal__name', 'uid')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('uid', 'created_at', 'updated_at')


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('uid', 'user', 'meal', 'quantity', 'price', 'created_at', 'updated_at')
    search_fields = ('user__username', 'meal__name', 'uid')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('uid', 'created_at', 'updated_at')
    
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'uid')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('uid', 'created_at')




