from django import forms

class GCashPaymentForm(forms.Form):
    reference_number = forms.CharField(max_length=100)
    proof = forms.FileField()
