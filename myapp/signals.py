from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import App, Plan, Subscription

@receiver(post_save, sender=App)
def create_free_plan_subscription(sender, instance, created, **kwargs):
    if created:
        # auto add free plan to new app
        free_plan = Plan.objects.get(name="Free")
        Subscription.objects.create(app=instance, plan=free_plan, active=True)
