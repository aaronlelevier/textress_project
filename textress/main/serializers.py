from django.contrib.auth.models import User

from rest_framework import serializers

from main.models import Hotel, Icon, UserProfile


class IconSerializer(serializers.ModelSerializer):

    # icon = serializers.ImageField()

    class Meta:
        model = Icon
        fields = ('name', 'icon',)


class UserProfileSerializer(serializers.ModelSerializer):
    
    icon = IconSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('icon', 'hotel_group')


class UserSerializer(serializers.ModelSerializer):

    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
            'profile',)
        read_only_fields = ('id', 'username',)


class HotelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hotel
        fields =  ('id', 'name', 'address_phone', 'address_line1',)
