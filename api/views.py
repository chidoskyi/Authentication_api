from datetime import timedelta
import json
from django.shortcuts import get_object_or_404
import secrets
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.utils import timezone 
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from allauth.socialaccount.models import SocialAccount, SocialAccount, SocialToken # type: ignore
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import generics
from .models import User,Meals,Categories,Contact  
from .serializers import UserSerializer,SignUpSerializer,UpdatePasswordSerializer,UserProfileSerializer,MealSerializer,CategorySerializer, ContactSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.utils.timezone import now
from django.views.decorators.csrf import ensure_csrf_cookie 
from django.contrib.auth import get_user_model
import logging
User = get_user_model()

logger = logging.getLogger(__name__)

@api_view(['GET'])
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    This view sets the CSRF cookie and returns a 200 OK response.
    The @ensure_csrf_cookie decorator ensures that the CSRF cookie is set.
    """
    return Response({'detail': 'CSRF cookie set'})

@api_view(['POST'])
def signup_view(request):
    print("Raw Body:", request.body)  # Debug raw request body
    print("Headers:", request.headers)  # Debug request headers
    print("Received signup data:", request.data)  # Debug parsed data

    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Set the user as inactive upon signup
        user.is_active = False
        user.email_verification_token = secrets.token_urlsafe()
        user.email_verification_token_created_at = timezone.now()
        user.save()

        # Send verification email
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{user.email_verification_token}"
        send_mail(
            'Verify your email',
            f'Please click on this link to verify your email: {verification_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)

    print("Validation errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def verify_email(request, token):
    logger.info(f"Attempting to verify email with token: {token}")
    try:
        # Retrieve the user based on the verification token
        user = User.objects.get(email_verification_token=token)
        logger.info(f"Found user: {user.email} for token: {token}")
        
        # Check if the token has expired (24 hours max validity)
        if user.email_verification_token_created_at and user.email_verification_token_created_at + timedelta(hours=24) < timezone.now():
            logger.warning(f"Verification link expired for user: {user.email}")
            return Response({
                'error': 'Verification link has expired. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # If the email is already verified, inform the user
        if user.email_confirmed_at:
            logger.info(f"Email already verified for user: {user.email}")
            # if not user.is_active:  # Ensure the user is active if the email is verified
            #     user.is_active = True
            #     user.save(update_fields=['is_active'])
            return Response({
                'message': 'Email already verified.'
            }, status=status.HTTP_200_OK)

        # Mark the email as confirmed and reset the token fields
        user.email_confirmed_at = timezone.now()
        user.is_email_verified = True  # Mark email as verified
        user.is_active = True  # Ensure the user is active
        user.save(update_fields=[
            'email_confirmed_at', 'is_email_verified', 'is_active',
        ])

        logger.info(f"Successfully verified email for user: {user.email}")
        return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        # Log if the token does not match any user
        logger.error(f"No user found for token: {token}")
        return Response({'error': 'Invalid verification token'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error during email verification: {str(e)}")
        return Response({'error': 'An unexpected error occurred. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@login_required
def get_user_info(request):
    user = request.user

    social_accounts = SocialAccount.objects.filter(user=user)
    print("Social Account for user:", social_accounts)

    social_account = social_accounts.first()

    if not social_account:
        print("No social account for user:", user)
        return redirect('https://food-delivery-prj-react.onrender.com/login/callback/?error=NoSocialAccount')
    
    token = SocialToken.objects.filter(account=social_account, account__provider='google').first()

    if token:
        print('Google token found:', token.token)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return redirect(f'https://food-delivery-prj-react.onrender.com/login/callback/?access_token={access_token}')
    else:
        print('No Google token found for user', user)
        return redirect(f'https://food-delivery-prj-react.onrender.com/login/callback/?error=NoGoogleToken')
    

    
from django.views.decorators.csrf import csrf_exempt    
@csrf_exempt
def validate_google_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            google_access_token = data.get('access_token')
            print(google_access_token)

            if not google_access_token:
                return JsonResponse({'detail': 'Access Token is missing.'}, status=400)
            return JsonResponse({'valid': True})
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON.'}, status=400)
    return JsonResponse({'detail': 'Method not allowed.'}, status=405)
    
    
@login_required
def social_login_complete(request):
    try:
        user = request.user
        refresh = RefreshToken.for_user(user)
        
        return JsonResponse({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)



@api_view(['POST'])
def signin_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Please provide both email and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(email=email, password=password)
    
    if user:
        # Check if the email is verified
        if not user.is_email_verified:
            return Response(
                {'error': 'Email not verified. Please verify your email to proceed.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate tokens and serialize user data
        refresh = RefreshToken.for_user(user)
        serialized_user = UserSerializer(user).data
        serialized_user['uid'] = str(serialized_user['uid'])  # Convert UUID to string for JSON serialization
        
        return Response({
            'user': serialized_user,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
    
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )
  

import logging

logger = logging.getLogger(__name__)  


class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("Received request to update password.")  # Log the request
        serializer = UpdatePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            print("Password updated successfully.")  # Log success
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        else:
            print("Serializer errors:", serializer.errors)  # Log validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # Only allow authenticated users
    parser_classes = [MultiPartParser, FormParser]  # Support file uploads

    def get_object(self):
        """Retrieve the current logged-in user."""
        return self.request.user

    def get(self, request):
        """Retrieve the profile of the logged-in user."""
        user = self.get_object()
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        print("Content-Type:", request.content_type)  # Debugging
        """Update the profile of the logged-in user."""
        user = self.get_object()
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """Partially update the profile of the logged-in user."""
        return self.put(request)  # Reuse the put method with partial=True



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signout_view(request):
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)

    
class MealsView(APIView):

    def get(self, request):
        # Retrieve all meals
        meals = Meals.objects.all()
        # Retrieve meals where toppicks is True
        toppicks = Meals.objects.filter(toppicks=True)
        
        # Serialize the data
        meals_serializer = MealSerializer(meals, many=True)
        toppicks_serializer = MealSerializer(toppicks, many=True)
        
        # Return both serialized data in the response
        response_data = {
            'meals': meals_serializer.data,
            'toppicks': toppicks_serializer.data
        }
        return Response(response_data, status=200)


class MealDetailsView(APIView):

    def get(self, request, pk):
        # Retrieve a single meal object or return a 404 if not found
        meal = get_object_or_404(Meals, pk=pk)
        # Serialize the data
        serializer = MealSerializer(meal)
        # Return the serialized data
        return Response(serializer.data, status=200)


class CategoriesView(APIView):

    def get(self, request):
        # Retrieve all categories
        category = Categories.objects.all()
        # Serialize the data
        serializer = CategorySerializer(category, many=True)
        # Return the serialized data
        return Response(serializer.data, status=200)
    
class ContactView(APIView):

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def get(self, request):
        contact = Contact.objects.all()
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data, status=200)
    
