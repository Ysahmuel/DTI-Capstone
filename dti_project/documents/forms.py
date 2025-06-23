from django import forms
from .models import ProductCovered, SalesPromotionPermitApplication

class SalesPromotionPermitApplicationForm(forms.ModelForm):
    class Meta:
        model = SalesPromotionPermitApplication
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label or name.replace('_', ' ').title()} (Required)"

        # Add 'form-group' class to each widget
        existing_classes = field.widget.attrs.get('class', '')
        field.widget.attrs['class'] = f"{existing_classes} form-group".strip()

class ProductCoveredForm(forms.ModelForm):
    class Meta:
        model = ProductCovered
        fields = '__all__'
        
# Formset for products
ProductCoveredFormSet = forms.modelformset_factory(ProductCovered, form=ProductCoveredForm, extra=1, can_delete=True)