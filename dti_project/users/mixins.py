from django.contrib import messages
from django.http import JsonResponse

class FormSubmissionMixin:
    def form_invalid(self, form):
        print("=== FORM_INVALID CALLED ===")
        print(f"All form errors: {form.errors}")

        # Add error messages to Django messages
        for field, error_list in form.errors.items():
            for error in error_list:
                if field == '__all__':
                    messages.error(self.request, f"{error}")
                else:
                    field_name = field.replace('_', ' ').title()
                    messages.error(self.request, f"{field_name}: {error}")

        # AJAX response (minimal, since frontend will display Django messages)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False}, status=400)

        return super().form_invalid(form)