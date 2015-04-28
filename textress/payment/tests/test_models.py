import stripe
import pytest
from model_mommy import mommy

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from ..models import Customer, Subscription, Plan

# Set Stripe Key for All tests
stripe.api_key = settings.STRIPE_SECRET_KEY


########
# PLAN #
########
def stripe_remove_plans():
    stripe.api_key = settings.STRIPE_SECRET_KEY
    plans = stripe.Plan.all()
    for plan in plans.data:
        plan.delete()

def stripe_create_plan():
    return Plan.objects.create(amount=1000, interval="month", id="Bronze",
        currency="usd", sms_per_month=500, price_per_extra=.055)

def stripe_create_plan_two():
    return Plan.objects.create(amount=2000, interval="month", id="Silver",
        currency="usd", sms_per_month=100, price_per_extra=.0525)


class PlanTests(TestCase):

    def setUp(self):
        stripe_remove_plans()

    def test_create(self):
        # Django Plan
        plan = stripe_create_plan()
        assert isinstance(plan, Plan)
        assert str(plan) == plan.id

        # Stripe Plan
        plan_stripe = stripe.Plan.retrieve(str(plan.name))
        assert plan_stripe.name == plan.name
        assert plan_stripe.amount == plan.amount

    def test_get_plan_fail(self):
        plan = stripe_create_plan()
        with pytest.raises(stripe.error.InvalidRequestError):
            plan_stripe = stripe.Plan.retrieve("wrong plan name")

    def test_delete(self):
        # 1 Plan exists
        plan = stripe_create_plan()
        assert len(Plan.objects.all()) == 1
        stipe_plans = stripe.Plan.all()
        assert len(stipe_plans.data) == 1

        # Delete Plan in Django, and Stripe Plan is also deleted
        plan.delete()
        assert len(Plan.objects.all()) == 0
        stipe_plans = stripe.Plan.all()
        assert stipe_plans.data == []











