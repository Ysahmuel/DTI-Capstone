from django import forms
from .models import ProductCovered, SalesPromotionPermitApplication, PersonalDataSheet
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, LayoutObject, TEMPLATE_PACK, Fieldset, HTML, Div, Row, Column, Submit
from django.template.loader import render_to_string

class SortForm(forms.Form):
    SORT_CHOICES = [
        ('name_asc', 'Name (A-Z)'),
        ('name_desc', 'Name (Z-A)')
    ]

    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, label='sort_by')

class BaseCustomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self, 'fields'):
            for name, field in self.fields.items():
                # Convert field name to title and replace underscores
                label_text = field.label if field.label else name.replace('_', ' ').title()

                # Add 'Required' to required fields' labels
                if field.required:
                    field.label = f"{label_text} <span class='required-label'>*</span>"
                    field.widget.attrs['placeholder'] = f"Enter {label_text}"
                else:
                    field.label = label_text                

                # Add 'form-group' class to each widget
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{existing_classes} form-group".strip()


class SalesPromotionPermitApplicationForm(BaseCustomForm):
    class Meta:
        model = SalesPromotionPermitApplication
        fields = '__all__'
        exclude = ['date_filed', 'user']
        widgets = {
            'promo_period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-group'}),
            'promo_period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-group'}),
        }

class ProductCoveredForm(BaseCustomForm):
    class Meta:
        model = ProductCovered
        fields = ['name', 'brand', 'specifications']

class PersonalDataSheetForm(BaseCustomForm):
    class Meta:
        model = PersonalDataSheet
        fields = '__all__'
        widgets = {
            'current_address': forms.TextInput(attrs={'class': 'form-group'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-group'})
        }
        
# Formset for products
ProductCoveredFormSet = forms.inlineformset_factory(
    SalesPromotionPermitApplication, 
    ProductCovered, 
    form=ProductCoveredForm,
    fields=['name', 'brand', 'specifications'],
    extra=1,
    can_delete=True
)