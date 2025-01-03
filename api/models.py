import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator
# Create your models here.

def user_directory_path(instance, filename):
    return 'Profile Photes/{0}/{1}'.format(instance.uid, filename)

class User(AbstractUser):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, blank=True)
    firstname = models.CharField(max_length=100, blank=True)
    lastname = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    email_confirmed_at = models.DateTimeField(null=True)
    phone = models.CharField(max_length=15, blank=True)
    last_sign_in_at = models.DateTimeField(auto_now=True)
    app_metadata = models.JSONField(default=dict)
    user_metadata = models.JSONField(default=dict)
    is_email_verified = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, null=True, blank=True)
    email_verification_token_created_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']
    
    # Adding custom related_name to avoid clashes with the built-in User model
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Custom related name for groups
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',  # Custom related name for user_permissions
        blank=True
    )
    
    def __str__(self):
        return self.username
 
 
class Categories(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    
    def __str__(self):
        return self.title   
    class Meta:
        ordering = ['-uid']  # Default ordering
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Meals(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    toppicks = models.BooleanField(default=False)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-uid']  # Default ordering
        verbose_name = 'Meal'
        verbose_name_plural = 'Meals'
        
class Cart(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meals, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart #{self.uid}"
    
    class Meta:
        ordering = ['-uid']  # Default ordering
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        

class Orders(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meals, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.uid}"
    
    class Meta:
        ordering = ['-uid']  # Default ordering
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        
class Contact(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-uid']  # Default ordering
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        

        


    