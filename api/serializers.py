from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import User, Meals, Categories, Cart, Orders, Contact

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uid', 'email','firstname','lastname', 'username', 'profile_picture', 'email_confirmed_at', 
                 'last_sign_in_at', 'email_verification_token_created_at', 'created_at')
        read_only_fields = ('uid', 'email_confirmed_at','email_verification_token_created_at','last_sign_in_at', 'created_at')

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    firstname = serializers.CharField(required=True)
    lastname = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = (
            'email',
            'password',
            # 'username',
            'firstname',
            'lastname',
            # 'phone'
        )
        extra_kwargs = {
            'phone': {'required': False},
            'username': {'required': False}
        }

    def create(self, validated_data):
        # Set username if not provided
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email'].split('@')[0]
            
        user = User.objects.create_user(**validated_data)
        return user
    

class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        # Check if the new_password and confirm_password match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)  # Handle file uploads

    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'profile_picture']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return f"{settings.BACKEND_BASE_URL}{obj.profile_picture.url}"
        return None

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()  # Add this line
    
    class Meta:
        model = Categories
        fields = ['uid', 'title', 'image', 'image_url']
        
        read_only_fields = ['uid']
        
    def get_image(self, obj):
        if obj.image:
            return f"{settings.BACKEND_BASE_URL}{obj.image}"
        
        return None
    def get_image_url(self, obj):
        if obj.image_url:
            return obj.image_url
        return None
    
    
class MealSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)  # Nest the CategorySerializer

    class Meta:
        model = Meals
        fields = ['uid', 'title', 'image', 'category','toppicks', 'price', 'image_url']
        read_only_fields = ['uid']

    def get_image(self, obj):
        if obj.image:
            return f"{settings.BACKEND_BASE_URL}{obj.image}"
        return None

    def get_image_url(self, obj):
        if obj.image_url:
            return obj.image_url
        return None
    

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['uid', 'user', 'meal', 'quantity', 'price', 'created_at', 'updated_at']
        read_only_fields = ['uid', 'created_at', 'updated_at']


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ['uid', 'user', 'meal', 'quantity', 'price', 'created_at', 'updated_at']
        read_only_fields = ['uid', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Custom create method to handle Orders creation."""
        return Orders.objects.create(**validated_data)
    
    
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['uid', 'name', 'email', 'subject', 'message', 'created_at']
        read_only_fields = ['uid', 'created_at']

    def create(self, validated_data):
        """Custom create method to handle Contact creation."""
        return Contact.objects.create(**validated_data)
    
    

 