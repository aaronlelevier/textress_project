from django.contrib import admin

from main.models import Hotel, UserProfile, Subaccount
    

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'hotel',)


class HotelAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'customer', 'subaccount',)


class SubaccountAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'sid',)


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Hotel, HotelAdmin)
admin.site.register(Subaccount, SubaccountAdmin)