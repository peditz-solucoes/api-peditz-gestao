from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'last_login']
    list_display_links = ['username', 'email']

    def get_queryset(self, request):
        queryset = User.objects.filter(email=request.user.email)
        if request.user.is_superuser:
           queryset = User.objects.all()
        return queryset
