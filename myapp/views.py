from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import Http404
# from rest_framework.exceptions import ValidationError, PermissionDenied
from .services.user_service import UserService
from .services.app_service import AppService
from .services.subscription_service import SubscriptionService, PlanService
from django.core.exceptions import PermissionDenied, ValidationError

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    try:
        return UserService.register(request)
    except IntegrityError as e:
        return Response({"400": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    return UserService.login(request)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def userProfile(request):
    return UserService.userProfile(request)
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def logout_users(request):
    UserService.logout_user(request)
    return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_app(request):
    app_service = AppService()
    return app_service.create_app(request.data, request.user)

@api_view(['PUT', 'PATCH'])  # 'PUT' for full updates, 'PATCH' for partial updates
@permission_classes([IsAuthenticated])
def update_app(request, pk):
    app_service = AppService()
    try:
        updated_data = app_service.update_app(request.user, pk, request.data)
        return Response(updated_data, status=status.HTTP_200_OK)
    except Http404 as e:
        return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_app(request, app_id):
    app_service = AppService()
    message, status_code = app_service.delete_app_and_subscriptions(request.user, app_id)
    return Response({"response": message}, status=status_code)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_apps(request):
    app_service = AppService()
    response = app_service.get_apps_for_user(request.user)
    return Response(response.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_app(request, app_id):
    app_service = AppService()
    try:
        response_data = app_service.get_app(request.user, app_id)
        return Response(response_data) 
    except Http404 as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_app_subscription(request, app_id):
    subscription_service = SubscriptionService()
    return subscription_service.get_subscription(request.user, app_id)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_subscription(request, pk):
    subscription_service = SubscriptionService()
    try:
        updated_data = subscription_service.update_subscription(request.user, pk, request.data)
        return Response(updated_data, status=status.HTTP_200_OK)
    except Http404 as e:
        return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValidationError as e:
        return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_subscriptions(request):
    subscription_service = SubscriptionService()
    response = subscription_service.get_user_subscriptions(request.user)
    return Response(response.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_plans(request):
    plan_service = PlanService()
    response = plan_service.get_plans()
    return Response(response.data)
