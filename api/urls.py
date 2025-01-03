from django.urls import path
from .views import get_csrf_token, get_user_info, me_view, signin_view, signout_view, signup_view, social_login_complete, validate_google_token, verify_email
from .views import UpdatePasswordView, UserProfileUpdateView, MealsView, MealDetailsView, CategoriesView, ContactView

urlpatterns = [
    path('signup/', signup_view, name='auth-signup'),
    path('signin/', signin_view, name='auth-signin'),
    path('update-password/', UpdatePasswordView.as_view(), name='update-password'),
    path('update-profile/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('meals/', MealsView.as_view(), name='meals-list'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('meals/<uuid:pk>/', MealDetailsView.as_view(), name='meal-detail'),
    path('categories/', CategoriesView.as_view(), name='categories-list'),
    path('signout/', signout_view, name='auth-signout'),
    path('me/', me_view, name='auth-me'),
    path('csrf/', get_csrf_token, name='get_csrf_token'),
    path('verify-email/<str:token>', verify_email, name='verify_email'),
    path('user-info/', get_user_info, name='get_user_info'),
    # Callback URLs
    
    path('validate_token/', validate_google_token, name='validate_google_token'),
    path('social-login-complete/', social_login_complete, name='social-login-complete'),
]
