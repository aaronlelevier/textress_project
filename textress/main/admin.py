from django.contrib import admin

from main.models import Hotel, UserProfile, Subaccount


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'customer', 'subaccount',)

    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'hotel',)


@admin.register(Subaccount)
class SubaccountAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'sid',)