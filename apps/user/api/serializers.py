from dataclasses import field
from pickle import TRUE
from pyexpat import model
from peditz import settings
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from dj_rest_auth.serializers import LoginSerializer
from apps.user.models import User
from django.utils.translation import gettext_lazy as _

from django.urls import exceptions as url_exceptions

from rest_framework import exceptions, serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True, 'min_length': 4}}
        read_only_fields = ('is_active', 'is_staff')
        fields = (
            'email',
            'password',
            'first_name',
            'last_name',
            'is_active', 
            'is_staff',
            # 'user_permissions'
        )

    def save(self, request):
        user = User(
            email=self.data.get('email'),
            first_name=self.data.get('first_name'),
            last_name=self.data.get('last_name'),
            is_active=True,
            is_staff=True,
            username=self.data.get('email'),
            password=make_password(self.validated_data['password'])
        )
        user.save()
        return user

        

class UserLoginSerializer(LoginSerializer):
    
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        user = self.get_auth_user(username, email, password)

        if not user:
            msg = _('Inválid credentials!')
            raise exceptions.ValidationError(msg)

        # Did we get back an active user?
        self.validate_auth_user_status(user)

        # If required, is the email verified?
        if 'dj_rest_auth.registration' in settings.INSTALLED_APPS:
            self.validate_email_verification_status(user)

        attrs['user'] = user
        return attrs
        
