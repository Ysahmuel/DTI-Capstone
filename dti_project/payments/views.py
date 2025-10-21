from django.contrib.auth.decorators import login_required
import requests
import base64
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from documents.models import SalesPromotionPermitApplication, OrderOfPayment

def payment_page(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)
    sppa = oop.sales_promotion_permit_application

    # Compute totals
    remark_fields = [
        "discount_amount", "premium_amount", "raffle_amount",
        "contest_amount", "redemption_amount", "games_amount",
        "beauty_contest_amount", "home_solicitation_amount",
        "amendments_amount"
    ]
    subtotal = sum(getattr(oop, f, 0) or 0 for f in remark_fields)
    doc_stamp_fee = oop.doc_stamp_amount or 0
    total_amount = subtotal + doc_stamp_fee

    # Display data
    context = {
        "oop": oop,
        "business_name": sppa.sponsor_name,
        "scope": sppa.coverage,
        "registration_type": "Sales Promotion Permit",
        "transaction_type": "Application",
        "applicant_name": sppa.sponsor_authorized_rep,
        "citizenship": "Filipino",
        "processing_fee": subtotal,
        "doc_stamp_fee": doc_stamp_fee,
        "total_amount": total_amount,
    }

    # ✅ When user proceeds to pay via GCash
    if request.method == "POST" and "proceed" in request.POST:
        payment_method = request.POST.get("payment_method")

        if payment_method == "gcash":
            # Encode secret key for authorization header
            key = base64.b64encode(settings.PAYMONGO_SECRET_KEY.encode()).decode()

            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Basic {key}",
            }

            data = {
                "data": {
                    "attributes": {
                        "amount": int(total_amount * 100),  # in centavos
                        "currency": "PHP",
                        "type": "gcash",
                        "redirect": {
                            "success": request.build_absolute_uri(f"/payments/success/{oop.id}/"),
                            "failed": request.build_absolute_uri(f"/payments/failed/{oop.id}/"),
                        }
                    }
                }
            }

            response = requests.post("https://api.paymongo.com/v1/sources", headers=headers, json=data)
            result = response.json()

            if "data" in result:
                checkout_url = result["data"]["attributes"]["redirect"]["checkout_url"]
                return redirect(checkout_url)
            else:
                messages.error(request, "Failed to initialize GCash payment. Please try again.")

    return render(request, "payments/payment-page.html", context)

def payment_success(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)
    if oop.payment_status != OrderOfPayment.PaymentStatus.VERIFIED:
        oop.payment_status = OrderOfPayment.PaymentStatus.PAID
        oop.save()
    messages.success(request, f"✅ Payment for {oop.sales_promotion_permit_application} successful! Awaiting verification.")
    return render(request, "payments/payment_success.html", {"oop": oop})


def payment_failed(request):
    messages.error(request, "❌ Payment failed or was canceled. Please try again.")
    return render(request, "payments/payment_failed.html")

@login_required
def verify_payment(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)

    if request.user.role not in ["admin", "collection_agent"]:
        messages.error(request, "You do not have permission to verify payments.")
        return redirect('documents-list')

    if oop.payment_status == OrderOfPayment.PaymentStatus.PAID:
        oop.payment_status = OrderOfPayment.PaymentStatus.VERIFIED
        oop.save()
        messages.success(request, "✅ Payment verified successfully!")
    else:
        messages.warning(request, "Payment must be marked as 'Paid' before verifying.")
    
    return redirect('all-documents')