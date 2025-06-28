from django import forms
from .models import ProductCovered, SalesPromotionPermitApplication
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, LayoutObject, TEMPLATE_PACK, Fieldset, HTML, Div, Row, Column, Submit
from django.template.loader import render_to_string

class FormsetLayout(LayoutObject):
    template = 'documents/partials/formset.html'

    def __init__(self, formset_name, **kwargs):
        self.formset_name = formset_name
        self.kwargs = kwargs

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        formset = context.get(self.formset_name)
        context.update({
            'formset': formset,
            'formset_name': self.formset_name
        })

        return render_to_string(self.template, context)

class SalesPromotionPermitApplicationForm(forms.ModelForm):
    class Meta:
        model = SalesPromotionPermitApplication
        fields = '__all__'
        exclude = ['date_filed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            # Add 'Required' to required fields' labels
            if field.required:
                field.label = f"{field.label or name.replace('_', ' ').title()} <span class='required-label'>*</span>"

            # Add 'form-group' class to each widget
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_classes} form-group".strip()

        # Set DateInput widgets for date fields
        self.fields['promo_period_start'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-group'})
        self.fields['promo_period_end'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-group'})


class ProductCoveredForm(forms.ModelForm):
    class Meta:
        model = ProductCovered
        fields = ['name', 'brand', 'specifications']
        
# Formset for products
ProductCoveredFormSet = forms.inlineformset_factory(
    SalesPromotionPermitApplication, 
    ProductCovered, 
    form=ProductCoveredForm,
    fields=['name', 'brand', 'specifications'],
    extra=1,
    can_delete=True
)