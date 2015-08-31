from django.contrib.auth.models import User

from rest_framework import serializers

from main.models import Hotel, Icon


class IconSerializer(serializers.ModelSerializer):

    # icon = serializers.ImageField()

    class Meta:
        model = Icon
        fields = ('name', 'icon',)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id', 'username',)


class HotelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hotel
        fields =  ('id', 'name', 'address_phone', 'address_line1',)