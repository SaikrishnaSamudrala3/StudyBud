from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

    def clean_username(self):
        return self.cleaned_data['username'].lower()

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']


class UserForm(ModelForm):
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'id': 'avatar'}),
    )

    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']
