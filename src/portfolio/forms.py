from django import forms


class DateInput(forms.DateInput):
    input_type = 'date'


class DateForm(forms.Form):
    evaluation_date = forms.DateField(widget=DateInput, initial=None)
