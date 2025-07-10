from django import forms

# Generic formset factory function to reduce redundancy
def create_inline_formset(parent_model, child_model, form_class, fields='__all__', extra=1, can_delete=True, **kwargs):
    """
    Generic function to create inline formsets with consistent defaults.
    
    Args:
        parent_model: The parent model class
        child_model: The child model class
        form_class: The form class to use
        fields: Fields to include (default: '__all__')
        extra: Number of extra forms (default: 1)
        can_delete: Whether forms can be deleted (default: True)
        **kwargs: Additional arguments to pass to inlineformset_factory
    
    Returns:
        The created formset class
    """
    return forms.inlineformset_factory(
        parent_model,
        child_model,
        form=form_class,
        fields=fields,
        extra=extra,
        can_delete=can_delete,
        **kwargs
    )
