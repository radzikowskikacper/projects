from django import forms

class MyDescriptionForm(forms.Form):
    description = forms.CharField(label='Write something about yourself', max_length=1023)
