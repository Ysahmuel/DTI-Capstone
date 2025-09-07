import datetime
from django.utils import timezone
from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields.files import FieldFile
from django.utils.dateformat import format as date_format

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
    
class PreviewContextMixin:
    detail_groups = None  # each view must set this

    def get_preview_context(self, form):
        """Builds preview context using configured detail groups"""
        if not form.is_valid():
            return {"preview_errors": form.errors}

        instance = form.instance

        # Set default values for preview
        if not getattr(instance, "user", None):
            instance.user = getattr(self.request, "user", None)

        if hasattr(instance, "date_filed") and not instance.date_filed:
            instance.date_filed = timezone.now().date()

        if hasattr(instance, "date") and not instance.date:
            instance.date = timezone.now().date()

        groups = []

        for group in (self.detail_groups or []):
            if len(group) == 3:
                group_name, fields, _ = group
            else:
                group_name, fields = group

            group_fields = []
            for label, field in fields:
                raw_value = form.cleaned_data.get(field) or getattr(instance, field, None)

                # Handle file fields: show filename
                if isinstance(raw_value, FieldFile):
                    value = raw_value.name if raw_value.name else "-"
                elif isinstance(raw_value, (datetime.datetime, datetime.date)):
                    value = date_format(raw_value, "M j, Y")
                # Handle empty or null values
                elif raw_value in [None, ""]:
                    value = "-"
                else:
                    value = str(raw_value)

                group_fields.append({
                    "label": label,
                    "value": value
                })

            groups.append({
                "name": group_name,
                "fields": group_fields
            })

        return {"preview_groups": groups}