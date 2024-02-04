from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import App, Subscription, Plan
from rest_framework.authtoken.models import Token

class AppTestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        # self.client.login(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.plan, _ = Plan.objects.get_or_create(name='Free', defaults={'price': 0.00})
        Plan.objects.get_or_create(name='Standard', price=10.00)
        Plan.objects.get_or_create(name='Pro', price=25.00)

        
    def test_create_app(self):
        url = reverse('create-app') 
        data = {'name': 'Test App', 'description': 'This is a test app.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(App.objects.count(), 1)
        self.assertEqual(App.objects.get().name, 'Test App')
    
    def test_update_app(self):
        app = App.objects.create(user=self.user, name='facebook', description='Social Media')
        url = reverse('update-app', args=[app.id])
        data = {'name': 'Updated App', 'description': 'Updated description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.name, 'Updated App')    
        
    def test_delete_app(self):
        app = App.objects.create(user=self.user, name='App to Delete', description='App description')
        Subscription.objects.create(app=app, plan=self.plan)
        url = reverse('delete-app', args=[app.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(App.objects.count(), 0)
        self.assertEqual(Subscription.objects.count(), 0)
    
    def test_get_user_apps(self):
         # Create apps for both users
        App.objects.create(name='User1 App1', description='App owned by user1', user=self.user)
        App.objects.create(name='User1 App2', description='Another app owned by user1', user=self.user)
        App.objects.create(name='User2 App1', description='App owned by user2', user=self.user2)  # This should not be returned

        url = reverse('user-apps')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that only the apps belonging to user1 are returned
        self.assertEqual(len(response.data), 2)  # Assuming the response data is a list of app objects

        # Verify that each returned app belongs to user1
        for app_data in response.data:
            self.assertEqual(app_data['user'], self.user.id)  # Assuming the response includes user IDs

        # Verify the names of the apps to ensure the correct ones are returned
        app_names = {app['name'] for app in response.data}
        self.assertIn('User1 App1', app_names)
        self.assertIn('User1 App2', app_names)
        self.assertNotIn('User2 App1', app_names)    
    
    def test_get_own_app(self):
        # Create an app for user1
        self.app_user1 = App.objects.create(name='User1 App', description='An app owned by user1', user=self.user)
        # Test retrieving an app that belongs to the authenticated user
        url = reverse('app', args=[self.app_user1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.app_user1.id))
        self.assertEqual(response.data['name'], self.app_user1.name)
        self.assertEqual(response.data['user'], self.user.id)  # Ensure your serializer includes the user field

    def test_get_other_user_app(self):
        # Create an app for user2
        self.app_user2 = App.objects.create(name='User2 App', description='An app owned by user2', user=self.user2)

        # Test retrieving an app that does not belong to the authenticated user
        url = reverse('app', args=[self.app_user2.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)   
        
    def test_get_user_subscriptions(self):
        self.app = App.objects.create(user=self.user, name='User App', description='App Description')
        self.subscription = Subscription.objects.get(app=self.app)
        
        # Another user's app and subscription for permission testing
        self.other_user = get_user_model().objects.create_user(username='otheruser', password='password')
        self.other_app = App.objects.create(user=self.other_user, name='Other User App', description='Other App Description')
        self.other_subscription = Subscription.objects.get(app=self.other_app)
        
        url = reverse('user-subscriptions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming the response contains a list of subscriptions
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.subscription.id))
        
    def test_get_user_app_subscription(self):
        self.app = App.objects.create(user=self.user, name='User App', description='App Description')
        self.subscription = Subscription.objects.get(app=self.app)
        
        url = reverse('app-subscription-detail', args=[self.app.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.subscription.id))
    
    def test_update_subscription(self):
        self.app = App.objects.create(user=self.user, name='User App', description='App Description')
        self.subscription = Subscription.objects.get(app=self.app)
        
        url = reverse('update-subscription', args=[self.subscription.id])
        updated_data = {'active': False}
        response = self.client.patch(url, updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subscription.refresh_from_db()
        self.assertFalse(self.subscription.active)
    
    def test_get_plans(self):   
        url = reverse('plans')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response contains exactly three plans
        self.assertEqual(len(response.data), 3)
        
        # Extract plan names from the response
        plan_names = [plan['name'] for plan in response.data]
        
        # Verify that all expected plans are in the response
        for plan_name in ['Free', 'Standard', 'Pro']:
            self.assertIn(plan_name, plan_names)    

    
