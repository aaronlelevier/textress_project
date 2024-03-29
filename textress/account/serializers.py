from rest_framework import serializers

from account.models import Pricing


class PricingSerializer(serializers.ModelSerializer):
    '''For Pricing Biz page and AngJS example Price calculaitons.'''

    class Meta:
        model = Pricing
        fields = ('id', 'hotel', 'cost',)
        read_only_fields = ('created', 'modified',)