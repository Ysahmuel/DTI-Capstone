import logging
from django.db import transaction
from django.contrib import messages
from itertools import chain
from django.core.exceptions import ImproperlyConfigured
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from .models import ServiceCategory
from django.views.generic import CreateView

logger = logging.getLogger(__name__)

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

                # --- handle formsets too (optional for drafts) ---
                formsets = self.get_formsets(instance=obj)
                if self.formsets_valid(formsets):
                    self.save_formsets(formsets)

                messages.success(request, f"{obj} saved as draft.")
                return redirect("/")  # or self.get_success_url() if you want preview
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

                # --- handle formsets ---
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
    
    def save_formsets(self, formsets):
        """
        Save all valid formsets.
        """
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
    
class ServiceCategoryMixin:
    def get_service_categories_with_services(self):
        """
        Returns a list of service categories, each with their related services.
        Format: [
            {
                "category": <ServiceCategory instance>,
                "services": [<Service instance>, ...]
            },
            ...
        ]
        """
        categories = ServiceCategory.objects.prefetch_related('services')
        return [
            {
                "category": category,
                "services": category.services.all()
            }
            for category in categories
        ]

class TabsSectionMixin:
    """
    Enhanced mixin to add tab sections functionality to DetailViews
    with optional lazy loading, caching, and pagination
    """
    tab_sections_config = None

    # Lazy loading configuration
    enable_lazy_loading = False  # Set to True to enable AJAX lazy loading
    active_tab_param = 'tab'
    page_param = 'page'
    items_per_page = 20
    cache_timeout = 300  # 5 Minutes

    def get_tab_sections_config(self):
        """
        Return the tab sections configuration.
        Can be overridden in subclasses for dynamic configuration.
        """
        if self.tab_sections_config is None:
            raise ImproperlyConfigured(f"{self.__class__.__name__} must define tab_sections_config")
        
        return self.tab_sections_config
    
    def get_active_tab(self):
        """Get the currently active tab from request parameters"""
        if not self.enable_lazy_loading:
            return None
        return self.request.GET.get(self.active_tab_param, self.get_default_active_tab())
    
    def get_default_active_tab(self):
        """Get the default active tab (first one marked as active or first tab)"""
        config = self.get_tab_sections_config()
        for section in config:
            if section.get('active', False):
                return section['id']
        return config[0]['id'] if config else None
    
    def get_cache_key(self, tab_id, page=1):
        """Generate cache key for tab data"""
        return f"tab_data_{self.object.pk}_{tab_id}_page_{page}"
    
    def get_tab_data(self, section_config, page=1):
        """Fetch data for a specific tab section with caching"""
        tab_id = section_config['id']
        cache_key = self.get_cache_key(tab_id, page)
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Fetch fresh data
        data = []
        if 'relation' in section_config:
            relation_name = section_config['relation']
            if hasattr(self.object, relation_name):
                relation = getattr(self.object, relation_name)
                try:
                    queryset = relation.all()
                    
                    # Apply pagination if enabled
                    if self.items_per_page:
                        paginator = Paginator(queryset, self.items_per_page)
                        page_obj = paginator.get_page(page)
                        data = list(page_obj.object_list)
                    else:
                        data = list(queryset)
                        
                except AttributeError:
                    if callable(relation):
                        data = relation()
                    else:
                        data = []

        # Format the data
        formatted_data, field_labels = self.format_tab_data(data)
        
        result = {
            'field_labels': field_labels,
            'data': formatted_data,
            'has_data': bool(formatted_data),
            'count': len(data) if not self.items_per_page else queryset.count() if 'queryset' in locals() else len(data)
        }
        
        # Cache the result
        cache.set(cache_key, result, self.cache_timeout)
        return result
    
    def format_tab_data(self, data):
        """Format raw data for display"""
        formatted_data = []
        field_labels = []
        
        if data:
            model_fields = [
                field for field in data[0]._meta.fields
                if not field.name.startswith('id') and field.name != 'personal_data_sheet'
            ]

            field_labels = []
            for field in model_fields:
                if field.name == "end_date":
                    continue
                elif field.name == "start_date":
                    field_labels.append("Period")
                else:
                    field_labels.append(field.verbose_name.capitalize())

            for obj in data:
                row = []
                for field in model_fields:
                    if field.name == 'end_date':
                        continue
                    elif field.name == 'start_date':
                        start_date = field.value_from_object(obj)
                        end_date = getattr(obj, 'end_date', None)

                        formatted_period = (
                            f"{start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}"
                            if end_date else
                            f"{start_date.strftime('%b %Y')} - Present"
                        )
                        row.append(formatted_period)
                    else:
                        row.append(field.value_from_object(obj))

                formatted_data.append(row)
        
        return formatted_data, field_labels
    
    def get_tab_count_only(self, section_config):
        """Get only the count for a tab section without loading the full data"""
        if 'relation' in section_config:
            relation_name = section_config['relation']
            if hasattr(self.object, relation_name):
                relation = getattr(self.object, relation_name)
                try:
                    if hasattr(relation, 'count'):
                        return relation.count()
                    elif hasattr(relation, 'all'):
                        return relation.all().count()
                    else:
                        # If it's a callable, we need to call it and count
                        data = relation() if callable(relation) else relation
                        return len(data) if data else 0
                except (AttributeError, TypeError):
                    return 0
        return 0

    def get_tab_sections(self):
        """Get tab sections - only load data for active tab if lazy loading is enabled"""
        sections = []
        config = self.get_tab_sections_config()
        active_tab = self.get_active_tab()

        for section_config in config:
            section = section_config.copy()
            
            if self.enable_lazy_loading:
                # Only load data for the active tab
                if section['id'] == active_tab:
                    tab_data = self.get_tab_data(section_config)
                    section.update(tab_data)
                    section['active'] = True  # Mark as active
                else:
                    # For inactive tabs, get count but don't load full data
                    count = self.get_tab_count_only(section_config)
                    section.update({
                        'field_labels': [],
                        'data': [],
                        'has_data': count > 0,
                        'count': count,  # Now this will have the actual count
                        'lazy_load': True,
                        'active': False
                    })
            else:
                # Load all data immediately (original behavior)
                tab_data = self.get_tab_data(section_config)
                section.update(tab_data)
                # Set active based on config
                section['active'] = section_config.get('active', False)

            sections.append(section)
        
        return sections

    def get_context_data(self, **kwargs):
        """Add tab sections and lazy loading config to context"""
        context = super().get_context_data(**kwargs)
        context['tab_sections'] = self.get_tab_sections()
        context['enable_lazy_loading'] = self.enable_lazy_loading
        context['active_tab'] = self.get_active_tab()
        return context
    
    def dispatch(self, request, *args, **kwargs):
        """Handle AJAX requests for lazy loading"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'GET':
            tab_id = request.GET.get('load_tab')
            if tab_id:
                return self.load_tab_content(tab_id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def load_tab_content(self, tab_id):
        """AJAX endpoint to load tab content"""
        config = self.get_tab_sections_config()
        section_config = None
        
        # Find the section configuration
        for section in config:
            if section['id'] == tab_id:
                section_config = section.copy()
                break
        
        if not section_config:
            return JsonResponse({'error': 'Tab not found'}, status=404)
        
        # Get page number
        page = int(self.request.GET.get(self.page_param, 1))
        
        # Load the data
        tab_data = self.get_tab_data(section_config, page)
        section_config.update(tab_data)
        
        # Render the tab content
        html = render_to_string(
            'documents/partials/tab_content.html',
            {'section': section_config},
            request=self.request
        )
        
        return JsonResponse({
            'html': html,
            'count': tab_data['count'],
            'has_data': tab_data['has_data']
        })