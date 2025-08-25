from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from ..constants import ORDER_OF_PAYMENT_FIELD_GROUPS, SALES_PROMOTION_FIELD_GROUPS
from ..mixins import FormStepsMixin, FormSubmissionMixin, FormsetMixin, MessagesMixin
from ..forms import FORMSET_CLASSES, OrderOfPaymentForm, SalesPromotionPermitApplicationForm
from ..models import OrderOfPayment, SalesPromotionPermitApplication
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
class UpdateOrderOfPaymentView(LoginRequiredMixin, MessagesMixin, FormSubmissionMixin, FormStepsMixin, FormsetMixin, UpdateView):
    model = OrderOfPayment
    template_name = 'documents/update_templates/update_order_of_payment.html'
    form_class = OrderOfPaymentForm
    context_object_name = 'order'
    
    FIELD_GROUPS = ORDER_OF_PAYMENT_FIELD_GROUPS

    def post(self, request, *args, **kwargs):
        # Example: check user permission before letting mixin run
        order = self.get_object()
        if order.user != request.user:
            messages.error(request, "You cannot edit this order of payment.")
            return redirect("/")
        
        if order.status != 'draft':
            messages.error(request, 'You can only edit drafts')
            return redirect('/')

        # Fall back to mixin’s handling
        return super().post(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        context['field_groups'] = self.FIELD_GROUPS

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = self.FIELD_GROUPS
        return context

    def get_success_url(self):
        return reverse_lazy('order-of-payment', kwargs={'pk': self.object.pk})