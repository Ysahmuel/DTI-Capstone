from django.http import HttpResponseForbidden
from django.contrib import messages
from django.apps import apps
from django.shortcuts import redirect
from ..models.base_models import DraftModel
from ..mixins.filter_mixins import FilterableDocumentMixin
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

MODEL_MAP = {
    model._meta.model_name: model
    for model in apps.get_models()
    if issubclass(model, DraftModel) and not model._meta.abstract
}

class ApproveDocumentsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if request.user.role == "business_owner":
            return HttpResponseForbidden("You are not allowed to approve documents.")

        document_ids = request.POST.getlist("documents")
        if not document_ids:
            messages.error(request, "No documents selected.")
            return redirect(request.META.get("HTTP_REFERER", "documents:all-documents"))

        updated_count = 0
        for doc in document_ids:
            try:
                model_name, pk = doc.split(":")
                model = MODEL_MAP.get(model_name.lower())
                if not model:
                    continue

                document = model.objects.filter(pk=pk).first()
                if document:
                    document.status = "approved"
                    document.save(update_fields=["status"])
                    updated_count += 1
            except Exception as e:
                print("Error approving:", e)

        messages.success(request, f"{updated_count} document(s) approved successfully.")
        return redirect(request.META.get("HTTP_REFERER", "documents:all-documents"))