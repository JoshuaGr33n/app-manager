from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

#AUTH
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
   ##AUTH
    path('register', views.register, name='register-user'),
    path('login', views.login, name='login'),
    
    ##RESTRICTED  
    path('user', views.userProfile, name='user-profile'),
    path('logout', views.logout_users, name='logout'),
    
    #app
    path('create-app', views.create_app, name='create-app'),
    path('user-apps', views.get_user_apps, name='user-apps'),
    path('app/<uuid:app_id>/', views.get_app, name='app'),
    path('app/<uuid:pk>/update', views.update_app, name='update-app'),
    path('app/<uuid:app_id>/delete', views.delete_app, name='delete-app'),
   
    #subscription
    path('subscriptions/', views.get_user_subscriptions, name='user-subscriptions'),
    path('app/<uuid:app_id>/subscription/', views.get_user_app_subscription, name='app-subscription-detail'),  
    path('subscription/<uuid:pk>/update/', views.update_subscription, name='update-subscription'),
   
    #plan
    path('plans/', views.get_plans, name='plans'),
]

urlpatterns = format_suffix_patterns(urlpatterns)