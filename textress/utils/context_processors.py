def user_groups(request):
    context = {
        'user_groups': request.user.groups.values_list('name', flat=True)
    }
    return context
