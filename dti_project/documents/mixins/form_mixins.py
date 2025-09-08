from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import CreateView
from django.db import transaction
from documents.utils.form_helpers import get_previous_instance

class PrefillFromPreviousSubmissionMixin:
    def get_initial(self):
        previous = super().get_previous()
        previous_instance = get_previous_instance(self.model, self.request.user)
        if previous_instance:
            for field in self.prefill_fields:
                previous[field] = getattr(previous_instance, field, '')
        return previous

class MessagesMixin:
    """Mixin for handling form success and error messages."""
    MAX_ERRORS = 5  # limit number of error fields shown

    def form_invalid(self, form, action=None):
        normalized_errors = {}

        # Collect all errors, skipping status + draft exceptions
        for field, errors in form.errors.items():
            if field == "status":
                continue
            if action == "draft":
                if hasattr(form.instance, "required_for_display") and field not in form.instance.required_for_display():
                    continue

            # Normalize field label (so 'application_type' == 'Application Type')
            field_label = field.replace("_", " ").title()
            normalized_errors.setdefault(field_label, []).extend(errors)

        # Convert back into list of (field_label, errors)
        all_error_fields = list(normalized_errors.items())

        # Show only up to MAX_ERRORS fields
        for field_label, errors in all_error_fields[:self.MAX_ERRORS]:
            for error in errors:
                messages.error(self.request, f"{field_label}: {error}")

        # Show summary if more remain
        remaining = len(all_error_fields) - self.MAX_ERRORS
        if remaining > 0:
            messages.error(self.request, f"+ {remaining} more error(s)...")

        return super().form_invalid(form)

class FormSubmissionMixin:
    def post(self, request, *args, **kwargs):
        # Django normally sets this in dispatch → set it here
        self.object = None  

        action = request.POST.get("action")

        # If UpdateView, fetch existing object
        if hasattr(self, "get_object") and not isinstance(self, CreateView):
            try:
                self.object = self.get_object()
            except:
                self.object = None

        # Use form bound to self.object
        form = self.get_form(self.get_form_class())

        # === PREVIEW MODE (for validation only - don't save) ===
        if action == "preview":
            if form.is_valid():
                # Don't save, just validate formsets
                temp_obj = form.save(commit=False)
                temp_obj.user = request.user
                
                formsets = self.get_formsets(instance=temp_obj)
                if self.formsets_valid(formsets):
                    # All validation passed - this should be handled by the child class
                    # for preview display
                    return self.form_valid(form)
                else:
                    return self.form_invalid(form, action="preview")
            else:
                return self.form_invalid(form, action="preview")

        # === DRAFT MODE ===
        if action == "draft":
            obj = self.object or self.model()

            # Rebind form with files just in case
            form = self.form_class(request.POST, request.FILES, instance=obj)

            # Relax required fields for draft
            display_fields = getattr(obj, "required_for_display", lambda: [])()
            for name, field in form.fields.items():
                if name not in display_fields:
                    field.required = False

            if form.is_valid():
                obj = form.save(commit=False)
                obj.status = "draft"
                obj.user = request.user
                obj.prepare_for_draft()
                obj.save()
                self.object = obj

                # Handle formsets for drafts
                formsets = self.get_formsets(instance=obj)
                
                # For drafts, relax formset validation
                for formset_name, formset in formsets.items():
                    for form_instance in formset:
                        for field_name, field in form_instance.fields.items():
                            if field_name != 'DELETE':  # Keep DELETE field validation
                                field.required = False

                # Always save formsets for drafts, even if they have validation errors
                self.save_formsets(formsets, ignore_errors=True)

                messages.success(request, f"{obj} saved as draft.")
                return redirect("/")
            else:
                # Add draft-specific missing field errors
                missing_fields = [f for f in display_fields if not form.cleaned_data.get(f)]
                for f in missing_fields:
                    form.add_error(f, "This field is required for draft submission.")
                return self.form_invalid(form, action="draft")

        # === SUBMITTED MODE ===
        if action == "submitted":
            if form.is_valid():
                obj = form.save(commit=False)
                obj.status = "submitted"
                obj.user = request.user
                obj.save()
                self.object = obj

                formsets = self.get_formsets(instance=obj)
                if self.formsets_valid(formsets):
                    self.save_formsets(formsets)
                    messages.success(request, f"{obj} submitted successfully.")
                    return redirect(self.get_success_url())
                else:
                    return self.form_invalid(form, action="submitted")

        return self.form_invalid(form, action=action)

class FormsetMixin:
    formset_classes = {}  # Example: {'employee': EmployeeBackgroundFormset, 'training': TrainingsAttendedFormset}

    def get_formsets(self, instance=None):
        """
        Get all formsets for the view.
        Override this method to customize formset creation.
        """
        formsets = {}
        
        if self.request.method == 'POST':
            for key, formset_class in self.formset_classes.items():
                prefix = key.replace('-', '_')
                formsets[key] = formset_class(
                    self.request.POST,
                    instance=instance,
                    prefix=prefix
                )
        else:
            for key, formset_class in self.formset_classes.items():
                prefix = key.replace('-', '_')
                formsets[key] = formset_class(
                    instance=instance,
                    prefix=prefix
                )
        
        return formsets
    
    def get_context_data(self, **kwargs):
        """
        Add formsets to the context.
        """
        context = super().get_context_data(**kwargs)
        
        # Get the instance if it exists
        instance = getattr(self, 'object', None)
        
        # Get formsets using the proper method
        formsets = self.get_formsets(instance=instance)
        
        # Add formsets to context
        context['formsets'] = {}
        for key, formset in formsets.items():
            context[f'{key}_formset'] = formset  # Keep individual formset context variables
            context['formsets'][key] = formset   # Add to formsets dict
        
        return context
    
    def formsets_valid(self, formsets):
        """
        Check if all formsets are valid.
        """
        return all(formset.is_valid() for formset in formsets.values())
    
    def save_formsets(self, formsets, ignore_errors=False):
        """Override to handle draft mode formset saving."""
        if ignore_errors:
            # For drafts, save individual valid forms even if formset as a whole isn't valid
            for formset_name, formset in formsets.items():
                for form_instance in formset:
                    if form_instance.is_valid() and form_instance.cleaned_data:
                        # Check if form has actual data (not just DELETE=False)
                        has_data = any(
                            form_instance.cleaned_data.get(field) 
                            for field in form_instance.cleaned_data 
                            if field not in ['DELETE', 'id']
                        )
                        if has_data:
                            try:
                                instance = form_instance.save(commit=False)
                                # Set the foreign key to the main object
                                fk_field = getattr(instance, formset.fk.name)
                                if not fk_field:
                                    setattr(instance, formset.fk.name, self.object)
                                instance.save()
                            except Exception as e:
                                # In draft mode, continue even if individual form save fails
                                print(f"Draft formset form save error (continuing): {e}")
        else:
            # Normal formset saving for submitted mode
            for formset in formsets.values():
                formset.save()

    def form_valid(self, form):
        print("=== DEBUG: form_valid called ===")
        print(f"POST data keys: {list(self.request.POST.keys())}")
        
        # Check for formset data in POST
        for key in self.formset_classes.keys():
            total_forms_key = f"{key}-TOTAL_FORMS"
            print(f"Looking for {total_forms_key}: {self.request.POST.get(total_forms_key)}")
        
        context = self.get_context_data()
        instance = form.instance

        with transaction.atomic():
            instance.user = self.request.user
            self.object = form.save()

            # Get formsets with the saved instance
            formsets = self.get_formsets(instance=self.object)
            
            print(f"Formsets created: {list(formsets.keys())}")
            
            # Debug each formset
            for key, formset in formsets.items():
                print(f"Formset {key}:")
                print(f"  - Is valid: {formset.is_valid()}")
                print(f"  - Total forms: {formset.total_form_count()}")
                print(f"  - Errors: {formset.errors}")
                print(f"  - Non-form errors: {formset.non_form_errors()}")

            # Validate all formsets
            all_valid = True
            for key, formset in formsets.items():
                if not formset.is_valid():
                    all_valid = False

            if all_valid:
                # Save them if valid
                self.save_formsets(formsets)
                messages.success(self.request, f"{self.model._meta.verbose_name} created successfully!")
                return super().form_valid(form)
            else:
                # Collect formset errors
                for key, formset in formsets.items():
                    for i, form_errors in enumerate(formset.errors):
                        for field, errors in form_errors.items():
                            message = f"{key.capitalize()} Form {i+1} - {field}: " + "; ".join(errors)
                            messages.error(self.request, message)
                    non_form_errors = formset.non_form_errors()
                    if non_form_errors:
                        messages.error(self.request, f"{key.capitalize()} Formset error: " + "; ".join(non_form_errors))
                return self.form_invalid(form)

class FormStepsMixin:
    form_steps = []  # Default empty list

    def get_form_steps(self):
        """
        Automatically generate form_steps from FIELD_GROUPS and formset_classes
        """
        steps = []

        # Add fieldsets from FIELD_GROUPS
        if hasattr(self, 'FIELD_GROUPS'):
            for group in self.FIELD_GROUPS:
                if isinstance(group, str):
                    if hasattr(self, 'additional_sections') and group in self.additional_sections:
                        # Insert at this position
                        if group == 'service_categories':
                            steps.append(('multiple_choice', group))
                        else:
                            steps.append(('section', group))
                else:
                    # Valid 3-tuple fieldset
                    steps.append(('fieldset', group))


        # Handle leftover additional_sections not placed manually
        if hasattr(self, 'additional_sections'):
            already_included = [s[1] for s in steps]
            for section in self.additional_sections:
                if section not in already_included:
                    if section == 'service_categories':
                        steps.append(('multiple_choice', section))
                    else:
                        steps.append(('section', section))

        # Add formsets from formset_classes
        if hasattr(self, 'formset_classes'):
            for formset_key in self.formset_classes.keys():
                steps.append(('formset', formset_key))

        return steps

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get form steps (either manually defined or auto-generated)
        if hasattr(self, 'form_steps') and self.form_steps:
            form_steps = self.form_steps
        else:
            form_steps = self.get_form_steps()

        if form_steps:
            context['total_parts'] = len(form_steps)
            context['enumerated_steps'] = []

            for i, step in enumerate(form_steps, 1):
                step_type = step[0]
                step_data = step[1]

                if step_type == 'fieldset':
                    context['enumerated_steps'].append((i, 'fieldset', step_data))

                elif step_type == 'formset':
                    formset_key = step_data
                    formset = context['formsets'][formset_key]
                    context['enumerated_steps'].append((i, 'formset', formset_key, formset))

                elif step_type == 'section':
                    context['enumerated_steps'].append((i, 'section', step_data))

                elif step_type == 'multiple_choice':
                    context['enumerated_steps'].append((i, 'multiple_choice', step_data))

        return context