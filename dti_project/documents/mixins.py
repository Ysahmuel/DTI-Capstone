from django.db import transaction
from django.contrib import messages
from itertools import chain

class FormsetMixin:
    formset_class = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = self.formset_class(self.request.POST, instance=getattr(self, 'object', None))
        else:
            context['formset'] = self.formset_class(instance=getattr(self, 'object', None))
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        with transaction.atomic():
            form.instance.user = self.request.user
            self.object = form.save()

            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                messages.success(self.request, f"{self.model._meta.verbose_name} created successfully!")
                return super().form_valid(form)
            else:
                for i, form_errors in enumerate(formset.errors):
                    for field, errors in form_errors.items():
                        message = f"Form {i+1} - {field}: " + "; ".join(errors)
                        messages.error(self.request, message)

                # Display non-form errors, if any
                non_form_errors = formset.non_form_errors()
                if non_form_errors:
                    messages.error(self.request, "Formset error: " + "; ".join(non_form_errors))

                return self.form_invalid(form)
            
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            message = f"{field}: " + "; ".join(errors)
            messages.error(self.request, message)

        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

