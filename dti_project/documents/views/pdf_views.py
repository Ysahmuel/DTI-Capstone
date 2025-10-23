from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from documents.models import OrderOfPayment

@login_required
def view_oop(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)

    # Generate PDF in memory
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, 800, "Order of Payment (OOP)")

    p.setFont("Helvetica", 10)
    p.drawString(50, 780, f"OOP Reference Code: {oop.pk:06d}")
    p.drawString(50, 765, f"Date Issued: {oop.date.strftime('%d %b %Y') if oop.date else 'N/A'}")
    p.drawString(50, 750, f"Name: {oop.name}")
    p.drawString(50, 735, f"Address: {oop.address}")

    # List the fees from the remark fields dynamically
    remark_prefixes = [
        "discount", "premium", "raffle", "contest",
        "redemption", "games", "beauty_contest",
        "home_solicitation", "amendments"
    ]
    y_position = 720
    for prefix in remark_prefixes:
        amount = getattr(oop, f"{prefix}_amount", 0) or 0
        if amount > 0:
            remark = getattr(oop, f"get_{prefix}_remark_display", lambda: "")()
            p.drawString(50, y_position, f"{prefix.replace('_',' ').title()}: Php {amount:,.2f} {remark}")
            y_position -= 15

    # DocStamp
    p.drawString(50, y_position, f"Documentary Stamp Tax: Php {oop.doc_stamp_amount or 0:,.2f}")
    y_position -= 15
    p.drawString(50, y_position, f"Total Amount: Php {oop.total_amount or 0:,.2f}")

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="OOP_{oop.pk}.pdf"'
    return response
