from django import forms
from .models import Profile, TradeHistory, Stock
from django.contrib.auth.models import User
from django.utils import timezone


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number']


class DateInput(forms.DateInput):
    input_type = 'date'


class DateForm(forms.Form):
    start_date = forms.DateField(widget=DateInput, initial=None)
    end_date = forms.DateField(widget=DateInput,  initial=None)


class FilterForm(forms.Form):
    filter_date = forms.DateField(widget=DateInput, initial=timezone.now())


class TradeForm(forms.ModelForm):
    date_time = forms.DateTimeField(initial=timezone.now())

    class Meta:
        model = TradeHistory
        fields = ['user',
                  'stock',
                  'site',
                  'date_time',
                  'name',
                  'site',
                  'num_of_share',
                  'stock_price',
                  'value']


class ChartsForm(forms.ModelForm):
    choices = [
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
    ]
    price = forms.ChoiceField(choices=choices, initial='open')

    class Meta:
        model = TradeHistory
        fields = ['stock']