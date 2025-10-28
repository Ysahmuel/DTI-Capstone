from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from documents.models import OrderOfPayment
import os


@login_required
def view_oop(request, oop_id):
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)

    # === FONT SETUP ===
    font_path = "C:/Windows/Fonts/DejaVuSans.ttf"
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/arial.ttf"
    pdfmetrics.registerFont(TTFont("UnicodeFont", font_path))
    FONT = "UnicodeFont"

    # === PDF SETUP ===
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # === HEADER ===
    logo_path = "static/images/dti_logo.png"  # adjust path if needed
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 60, height - 120, width=50, height=50, preserveAspectRatio=True, mask='auto')

    p.setFont(FONT, 10)
    p.drawCentredString(width / 2 + 40, height - 60, "Department of Trade and Industry")
    p.drawCentredString(width / 2 + 40, height - 75, "DTI Albay Provincial Office")
    p.drawCentredString(width / 2 + 40, height - 90, "2/F DBP Bldg., Quezon Ave. Extn., Legazpi City")

    p.setFont(FONT, 11)
    p.drawCentredString(width / 2 + 40, height - 120, "ORDER OF PAYMENT")
    p.setFont(FONT, 10)
    p.drawCentredString(width / 2 + 40, height - 135, "Sales Promotion Permit Fees")

    # === INFO SECTION ===
    y = height - 160
    p.setFont(FONT, 9)
    p.drawString(60, y, f"Name: {oop.name or ''}")
    p.drawString(60, y - 15, f"Address: {oop.address or ''}")
    p.drawString(400, y, f"Date: {oop.date.strftime('%d %b %Y') if oop.date else ''}")

    # === TABLE SETUP ===
    left_x = 60
    right_x = 500
    top_y = y - 50
    row_height = 18

    # Column positions
    col_fee = left_x + 150
    col_remarks = left_x + 300
    col_amount = right_x  # right edge

    # === HEADER ROW ===
    p.setFont(FONT, 9)
    p.rect(left_x, top_y - row_height, right_x - left_x, row_height, stroke=1, fill=0)
    p.drawString(left_x + 5, top_y - 12, "PERMIT FEE FOR")
    p.drawString(col_fee + 5, top_y - 12, "REMARKS")
    p.drawRightString(col_amount - 5, top_y - 12, "AMOUNT (₱)")

    # Draw vertical column lines
    p.line(col_fee, top_y, col_fee, top_y - (row_height * 12))
    p.line(col_remarks, top_y, col_remarks, top_y - (row_height * 12))
    p.line(left_x, top_y, left_x, top_y - (row_height * 12))
    p.line(right_x, top_y, right_x, top_y - (row_height * 12))

    # === FEE ITEMS ===
    fee_items = [
        "Discount",
        "Premium",
        "Raffle",
        "Contest",
        "Redemption",
        "Games",
        "Beauty Contest",
        "Home Solicitation",
        "Amendments",
        "DocStamp",
    ]
    amounts = [
        oop.discount_amount or 0,
        oop.premium_amount or 0,
        oop.raffle_amount or 0,
        oop.contest_amount or 0,
        oop.redemption_amount or 0,
        oop.games_amount or 0,
        oop.beauty_contest_amount or 0,
        oop.home_solicitation_amount or 0,
        oop.amendments_amount or 0,
        oop.doc_stamp_amount or 30.00,
    ]

    # Draw each fee row
    y_pos = top_y - row_height
    for i, fee in enumerate(fee_items):
        # Horizontal line
        p.line(left_x, y_pos - row_height, right_x, y_pos - row_height)
        # Fee name
        p.drawString(left_x + 5, y_pos - 12, fee)
        # Amount right-aligned in last column
        p.drawRightString(col_amount - 5, y_pos - 12, f"₱ {amounts[i]:,.2f}" if amounts[i] else "₱")
        y_pos -= row_height

    # === TOTAL ROW (FULL WIDTH WITH BOXES) ===
    p.line(left_x, y_pos, right_x, y_pos)  # line above TOTAL row
    y_pos -= row_height

    # Draw TOTAL row box
    p.rect(left_x, y_pos, right_x - left_x, row_height, stroke=1, fill=0)
    p.line(col_fee, y_pos, col_fee, y_pos + row_height)
    p.line(col_remarks, y_pos, col_remarks, y_pos + row_height)

    p.setFont(FONT, 9)
    p.drawString(left_x + 5, y_pos + 5, "TOTAL")
    p.drawRightString(col_amount - 5, y_pos + 5, f"₱ {oop.total_amount or 0:,.2f}")

    # === OFFICER BOXES ===
    officer_y = y_pos - 70
    box_width = 180
    box_height = 50

    # Account Officer
    p.rect(80, officer_y, box_width, box_height)
    p.setFont(FONT, 9)
    p.drawString(120, officer_y + 35, "Account Officer")
    p.setFont(FONT, 8)
    p.drawString(90, officer_y + 20, "Date: ____________________")
    p.drawString(90, officer_y + 5, "Signature: _______________")

    # Special Collecting Officer
    p.rect(310, officer_y, box_width, box_height)
    p.setFont(FONT, 9)
    p.drawString(340, officer_y + 35, "Special Collecting Officer")
    p.setFont(FONT, 8)
    p.drawString(320, officer_y + 20, "Date: ____________________    O.R. No.: ____________")
    p.drawString(320, officer_y + 5, "Signature: _______________")

    # === REMARKS SECTION ===
    p.setFont(FONT, 9)
    p.drawString(60, officer_y - 25, "REMARKS:")
    remarks = [
        "R - Several provinces / cities / municipalities within a single region",
        "P - Single province / city / municipality",
        "X - 2 or more regions excluding Metro Manila",
        "A - Additional fees due to reassessment of premium and prizes",
    ]
    p.setFont(FONT, 8)
    yy = officer_y - 38
    for line in remarks:
        p.drawString(65, yy, line)
        yy -= 12

    # === FINALIZE PDF ===
    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="OOP_{oop.pk}.pdf"'
    return response
