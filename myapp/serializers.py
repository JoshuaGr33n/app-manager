from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from .models import App, Subscription, Plan
from datetime import timedelta
from django.utils import timezone

from rest_framework.authtoken.models import Token
from .authentication import token_expire_handler, expires_in, is_token_expired
from django.contrib.auth import authenticate, login

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'email', 'phone')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        validated_data['is_active'] = True
        user = super().create(validated_data)
        token, _ = Token.objects.get_or_create(user=user)
        is_expired, token_key = token_expire_handler(token)
        user.token = token_key
        user.expires_in = expires_in(token)
        user.message = "User Registered Successfully"
        return user
    
    def validate_first_name(self, value):
        # Ensure the first name is not empty
        if not value:
            raise serializers.ValidationError("First name cannot be empty.")
        # Check for alphabetic characters (and possibly spaces, apostrophes, or hyphens)
        if not all(char.isalpha() or char in " '-" for char in value):
            raise serializers.ValidationError("First name must contain only letters, apostrophes, hyphens, or spaces.")
        return value

    def validate_last_name(self, value):
        # Ensure the last name is not empty
        if not value:
            raise serializers.ValidationError("Last name cannot be empty.")
        # Check for alphabetic characters (and possibly spaces, apostrophes, or hyphens)
        if not all(char.isalpha() or char in " '-" for char in value):
            raise serializers.ValidationError("Last name must contain only letters, apostrophes, hyphens, or spaces.")
        return value
    
    def validate_phone(self, value):
        # ensure phone is only digits
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        # ensure phone is 10 digits
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be 10 digits long.")
        return value
    
    def validate_password(self, value):
        validate_password(value)
        return value
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)   
    
    def create(self, validated_data):
        # no object is created so this will be left empty
         pass
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Incorrect Login credentials")

        # after successful authentication
        token, _ = Token.objects.get_or_create(user=user)
        if is_token_expired(token.key):
            token.delete()
            token = Token.objects.create(user=user)

        is_expired, token_key = token_expire_handler(token)
        user.token = token_key
        user.expires_in = expires_in(token)
        user.message = "Login Successful"
               
        return user
    

class AuthResponseSerializer(serializers.ModelSerializer):
    token = serializers.CharField()
    token_expires_in = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['fullname', 'message','email', 'username', 'token', 'token_expires_in']

    def get_fullname(self, user):
        return f"{user.first_name} {user.last_name}"   
    
    def get_message(self, user):
        return user.message 
    
    def get_token_expires_in(self, user):
        return user.expires_in  
 
 
class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ['id', 'user', 'name', 'description']
        read_only_fields = ['user']

class AppUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ['name', 'description']  
        read_only_fields = ['user']
        
class SubscriptionSerializer(serializers.ModelSerializer):
    app = serializers.CharField(source='app.name', read_only=True)
    plan = serializers.CharField(source='plan.name', read_only=True)
    plan_price = serializers.CharField(source='plan.price', read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'app', 'plan', 'plan_price', 'active', 'start_date', 'end_date']


class SubscriptionUpdateSerializer(serializers.ModelSerializer):
    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all())
    plan_name = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = Subscription
        fields = ['plan','plan_name', 'active', 'end_date'] 

    def update(self, instance, validated_data):
        if 'plan' in validated_data and validated_data['plan'] != instance.plan:
            # Update the start_date to today
            instance.start_date = timezone.now().date()
            # Add another 30 days for the end_date
            instance.end_date = instance.start_date + timedelta(days=30)
        
        instance.plan = validated_data.get('plan', instance.plan)
        instance.active = validated_data.get('active', instance.active)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.save()
        return instance
    

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'price']
        read_only_fields = ['name', 'price']
        
    