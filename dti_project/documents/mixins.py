from django.db import transaction
from django.contrib import messages
from itertools import chain

class FormsetMixin:
    formset_classes = {}  # Example: {'employee': EmployeeBackgroundFormset, 'training': TrainingsAttendedFormset}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = getattr(self, 'object', None)

        # Add all formsets to context
        for key, formset_class in self.formset_classes.items():
            if self.request.POST:
                context[f'{key}_formset'] = formset_class(self.request.POST, instance=instance)
            else:
                context[f'{key}_formset'] = formset_class(instance=instance)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        instance = form.instance

        with transaction.atomic():
            instance.user = self.request.user
            self.object = form.save()

            # Validate all formsets
            all_valid = True
            for key in self.formset_classes:
                formset = context[f'{key}_formset']
                formset.instance = self.object
                if not formset.is_valid():
                    all_valid = False

            if all_valid:
                # Save them if valid
                for key in self.formset_classes:
                    context[f'{key}_formset'].save()

                messages.success(self.request, f"{self.model._meta.verbose_name} created successfully!")
                return super().form_valid(form)
            else:
                # Collect formset errors
                for key in self.formset_classes:
                    formset = context[f'{key}_formset']
                    for i, form_errors in enumerate(formset.errors):
                        for field, errors in form_errors.items():
                            message = f"{key.capitalize()} Form {i+1} - {field}: " + "; ".join(errors)
                            messages.error(self.request, message)
                    non_form_errors = formset.non_form_errors()
                    if non_form_errors:
                        messages.error(self.request, f"{key.capitalize()} Formset error: " + "; ".join(non_form_errors))
                return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            message = f"{field}: " + "; ".join(errors)
            messages.error(self.request, message)

        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class FormStepsMixin:
    form_steps = []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_steps'] = self.form_steps
        return context
