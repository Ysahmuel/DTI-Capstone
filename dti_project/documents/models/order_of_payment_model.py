from decimal import Decimal
from django.db import models
from django.urls import reverse
from ..models.base_models import DraftModel, PeriodModel
from django.utils import timezone
from ..model_choices import REMARKS_CHOICES
from ..utils.model_helpers import remark_amount_fields
from users.models import User




class OrderOfPayment(DraftModel, models.Model):
    class Meta:
        verbose_name = "Order of Payment"
        verbose_name_plural = "Orders of Payment"

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    sales_promotion_permit_application = models.OneToOneField(
        'SalesPromotionPermitApplication',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='order_of_payment'
    )

    name = models.CharField(max_length=55)
    date = models.DateTimeField(default=timezone.now)
    address = models.TextField(max_length=255)

    account_officer_date = models.DateField(null=True, blank=True)
    account_officer_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    # Dynamically include remark-amount fields
    locals().update(remark_amount_fields('discount'))
    locals().update(remark_amount_fields('premium'))
    locals().update(remark_amount_fields('raffle'))
    locals().update(remark_amount_fields('contest'))
    locals().update(remark_amount_fields('redemption'))
    locals().update(remark_amount_fields('games'))
    locals().update(remark_amount_fields('beauty_contest'))
    locals().update(remark_amount_fields('home_solicitation'))
    locals().update(remark_amount_fields('amendments'))

    doc_stamp_remark = models.CharField(max_length=255, blank=True, null=True, choices=REMARKS_CHOICES)
    doc_stamp_amount = models.DecimalField(max_digits=10, decimal_places=2, default=30.00)

    special_collecting_officer_date = models.DateField(null=True, blank=True)
    special_collecting_officer_or_number = models.CharField(max_length=50, blank=True, null=True)
    special_collecting_officer_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    class PaymentStatus(models.TextChoices):
        AWAITING = 'awaiting', 'Awaiting Payment'
        PAID = 'paid', 'Paid'
        VERIFIED = 'verified', 'Verified'
        
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal('0.00')
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices, 
        default=PaymentStatus.AWAITING
    )
    
    def calculate_total(self):
        remark_fields = [
            "discount_amount", "premium_amount", "raffle_amount",
            "contest_amount", "redemption_amount", "games_amount",
            "beauty_contest_amount", "home_solicitation_amount",
            "amendments_amount"
        ]
        subtotal = sum((getattr(self, f, 0) or 0) for f in remark_fields)
        return Decimal(subtotal) + (self.doc_stamp_amount or Decimal('0.00'))

    def save(self, *args, **kwargs):
        # compute total_amount before saving
        try:
            self.total_amount = self.calculate_total()
        except Exception:
            # fallback to 0.00 if calculation fails for any reason
            self.total_amount = Decimal('0.00')
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Orders of Payment'

    def __str__(self):
        return self.get_str_display(f"{self.name} {self.address}")
    
    def get_absolute_url(self):
        return reverse("order-of-payment", args=[self.pk])
    
    def get_update_url(self):
        return reverse("update-order-of-payment", args=[self.pk])