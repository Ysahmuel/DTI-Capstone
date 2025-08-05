from django.db import models  
from documents.model_choices import PERMIT_FEE_REMARK_CHOICES


def remark_amount_fields(prefix):
    return {
        f"{prefix}_remark": models.CharField(max_length=255, blank=True, null=True, choices=PERMIT_FEE_REMARK_CHOICES),
        f"{prefix}_amount": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text=f"{prefix} amount in ₱"),
    }