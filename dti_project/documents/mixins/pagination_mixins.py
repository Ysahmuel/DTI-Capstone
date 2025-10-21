from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class PaginationMixin:
    """
    Mixin to handle pagination for document list views.
    Works with both QuerySets and combined (chained) iterables.
    """
    paginate_by = 10  # Default items per page

    def get_pagination_params(self):
        """
        Retrieve pagination settings from request.
        Can be overridden or extended for user-customizable page sizes.
        """
        page = self.request.GET.get('page', 1)
        paginate_by = self.request.GET.get('paginate_by', self.paginate_by)
        try:
            paginate_by = int(paginate_by)
        except (TypeError, ValueError):
            paginate_by = self.paginate_by
        return page, paginate_by

    def apply_pagination(self, documents):
        """
        Apply pagination to the given list or queryset.
        Returns the page object.
        """
        page, paginate_by = self.get_pagination_params()

        # Convert to list if it's a chained iterable
        if not hasattr(documents, '__len__'):
            documents = list(documents)

        paginator = Paginator(documents, paginate_by)

        try:
            paginated_docs = paginator.page(page)
        except PageNotAnInteger:
            paginated_docs = paginator.page(1)
        except EmptyPage:
            paginated_docs = paginator.page(paginator.num_pages)

        return paginated_docs

    def get_context_data(self, **kwargs):
        """
        Inject pagination controls and metadata into the context.
        """
        context = super().get_context_data(**kwargs)

        documents = context.get("documents", None)
        if documents is not None and not hasattr(documents, 'paginator'):
            # Apply pagination only if not already paginated
            context["documents"] = self.apply_pagination(documents)

        context["is_paginated"] = True
        context["paginator"] = context["documents"].paginator
        context["page_obj"] = context["documents"]

        return context
