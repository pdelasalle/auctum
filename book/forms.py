from django import forms

class orderForm(forms.Form):
    address=forms.CharField(max_length=100)
    side=forms.CharField(max_length=100)
    currency=forms.CharField(max_length=100)
    