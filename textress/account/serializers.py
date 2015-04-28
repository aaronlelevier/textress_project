from rest_framework import serializers

from .models import Pricing


class PricingSerializer(serializers.ModelSerializer):
    '''For Pricing Biz page and AngJS example Price calculaitons.'''

    class Meta:
        model = Pricing
        fields = ('id', 'tier', 'tier_name', 'desc', 'price', 'start', 'end',
            'created', 'modified')
        read_only_fields = ('created', 'modified',)