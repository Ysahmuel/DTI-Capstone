from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from notifications.utils import send_user_notification
import requests
import base64
import datetime
from io import BytesIO
from users.models import User
from django.conf import settings
from django.contrib import messages
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType
from documents.models import SalesPromotionPermitApplication, OrderOfPayment

def payment_page(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)
    sppa = oop.sales_promotion_permit_application

    total_amount = oop.total_amount or oop.calculate_total()
    
    # Display data
    context = {
        "oop": oop,
        "business_name": sppa.sponsor_name,
        "scope": sppa.coverage,
        "registration_type": "Sales Promotion Permit",
        "transaction_type": "Application",
        "applicant_name": sppa.sponsor_authorized_rep,
        "citizenship": "Filipino",
        "processing_fee": total_amount - oop.doc_stamp_amount,
        "doc_stamp_fee": oop.doc_stamp_amount,
        "total_amount": total_amount,
    }

    # When user proceeds to pay via GCash
    if request.method == "POST" and "proceed" in request.POST:
        payment_method = request.POST.get("payment_method")

    # Payment handling
    if request.method == "POST" and "proceed" in request.POST:
        payment_method = request.POST.get("payment_method")

        if payment_method == "gcash":
            key = base64.b64encode(settings.PAYMONGO_SECRET_KEY.encode()).decode()
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Basic {key}",
            }

            data = {
                "data": {
                    "attributes": {
                        "amount": int(total_amount * 100),  # centavos
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
    # Notify admin/collection agent
    from users.models import User
    admins = User.objects.filter(role__in=["admin", "collection_agent"])

    for admin in admins:
        notification = Notification.objects.create(
            user=admin,
            sender=request.user,
            message=f"{request.user.get_full_name()} has successfully paid for OOP #{oop.pk}.",
            type="info",
            content_type=ContentType.objects.get_for_model(oop),
            object_id=oop.pk,
        )
        send_user_notification(admin.id, notification)

    # Notify business owner
        notification = Notification.objects.create(
            user=oop.sales_promotion_permit_application.user,
            sender=request.user,
            message=f"Your payment for OOP #{oop.pk} was successful and is now pending verification.",
            type="info",
            content_type=ContentType.objects.get_for_model(oop),
            object_id=oop.pk,
        )
        send_user_notification(oop.sales_promotion_permit_application.user.id, notification)

    return render(request, "payments/payment_success.html", {"oop": oop})


def payment_failed(request):
    messages.error(request, "Payment failed or was canceled. Please try again.")
    return render(request, "payments/payment_failed.html")

@login_required
def verify_payment(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)

    if request.user.role not in ["admin", "collection_agent"]:
        messages.error(request, "You do not have permission to verify payments.")
        return redirect('documents-list')

    if oop.payment_status == OrderOfPayment.PaymentStatus.PAID:
        # Just update status
        oop.payment_status = OrderOfPayment.PaymentStatus.VERIFIED
        oop.save()

        # Notify business owner
        notification = Notification.objects.create(
            user=oop.sales_promotion_permit_application.user,
            sender=request.user,
            message=f"Your payment for OOP #{oop.pk} has been verified! You can now download your official receipt.",
            type="approved",
            content_type=ContentType.objects.get_for_model(oop),
            object_id=oop.pk,
        )
        send_user_notification(oop.sales_promotion_permit_application.user.id, notification)

    else:
        messages.warning(request, "Payment must be marked as 'Paid' before verifying.")
    
    return redirect('all-documents')

@login_required
def download_receipt(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)
    sppa = oop.sales_promotion_permit_application

    if oop.payment_status != OrderOfPayment.PaymentStatus.VERIFIED:
        messages.warning(request, "Receipt is only available after verification.")
        return redirect('documents-list')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # HEADER
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, height - 70, "ACKNOWLEDGMENT RECEIPT")
    p.setFont("Helvetica", 9)
    p.drawCentredString(width / 2, height - 85, "(This serves as proof of online payment)")
    p.drawCentredString(width / 2, height - 97,
                        "An official receipt will be issued by the DTI Cashier or authorized payment partner.")

    # PAYMENT INFO
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 130, f"Payment Code: {oop.payment_code or 'N/A'}")
    p.drawString(50, height - 145, f"Reference Code: {sppa.reference_code}")
    p.drawString(50, height - 160, f"Issue Date: {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}")
    p.drawString(50, height - 175, f"Application Name: {sppa.sponsor_name}")
    p.drawString(50, height - 190, f"Authorized Representative: {sppa.sponsor_authorized_rep}")
    p.drawString(50, height - 205, f"Transaction Type: Sales Promotion Permit Application")

    # AMOUNTS
    y = height - 235
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Fee Description")
    p.drawString(300, y, "Amount (₱)")
    p.line(50, y - 2, 550, y - 2)

    processing_fee = (oop.total_amount or 0) - (oop.doc_stamp_amount or 0)
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(50, y, "Processing Fee")
    p.drawRightString(550, y, f"{processing_fee:,.2f}")

    y -= 15
    p.drawString(50, y, "Documentary Stamp Tax")
    p.drawRightString(550, y, f"{oop.doc_stamp_amount or 0:,.2f}")

    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "TOTAL AMOUNT PAID")
    p.drawRightString(550, y, f"{oop.total_amount or 0:,.2f}")
    p.line(400, y - 2, 550, y - 2)

    # FOOTER
    y -= 40
    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Verified By: {request.user.get_full_name()}")
    p.drawString(50, y - 15, f"Date Verified: {datetime.datetime.now().strftime('%d %B %Y')}")

    p.setFont("Helvetica-Oblique", 8)
    p.setFillGray(0.3)
    footer = ("This acknowledgment receipt is system-generated for proof of online payment.\n"
            "The official DTI or LGU receipt will be issued by the authorized cashier or integrated payment gateway as per government policy.")
    p.drawCentredString(width / 2, 80, footer.split('\n')[0])
    p.drawCentredString(width / 2, 68, footer.split('\n')[1])

    p.showPage()
    p.save()
    buffer.seek(0)

    return FileResponse(buffer, content_type='application/pdf', as_attachment=False)
