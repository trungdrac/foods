from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, CharField, EmailField, EmailInput

from .models import Dish, User, Rating


class BaseUserForm(UserCreationForm):
    email = EmailField(
        label='Email',
        widget=EmailInput(),
        max_length=50
    )
    first_name = CharField(
        label='First name',
        max_length=50
    )
    last_name = CharField(
        label='Last name',
        max_length=50
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
        return user


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['birthday', 'height', 'weight', 'gender', 'diet_factor']


class DishForm(ModelForm):
    class Meta:
        model = Dish
        fields = ['dish_name', 'description', 'calories', 'is_public', 'ingredients', 'image']


class RatingForm(ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'comment']
