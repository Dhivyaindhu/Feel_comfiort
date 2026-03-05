from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    email        = forms.EmailField(required=True, label='Email Address')
    first_name   = forms.CharField(max_length=50, required=False, label='First Name')
    last_name    = forms.CharField(max_length=50, required=False, label='Last Name')
    phone_number = forms.CharField(max_length=15, required=False, label='Phone Number')

    class Meta:
        model  = CustomUser
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'phone_number', 'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username':     'Choose a username',
            'first_name':   'First name',
            'last_name':    'Last name',
            'email':        'your@email.com',
            'phone_number': 'Phone number (optional)',
            'password1':    'Create password',
            'password2':    'Confirm password',
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-lg',
                'placeholder': placeholders.get(name, field.label),
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email        = self.cleaned_data['email']
        user.first_name   = self.cleaned_data.get('first_name', '')
        user.last_name    = self.cleaned_data.get('last_name', '')
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Username',
            'autofocus': True,
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
        })


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number',
                  'profile_picture', 'mood_preference']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
