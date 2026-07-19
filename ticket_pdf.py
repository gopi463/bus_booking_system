"""
ticket_pdf.py — Generates a professional printable bus ticket PDF using ReportLab.
This completely avoids any Windows encoding/locale issues.
"""
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_ticket_pdf(
    booking_id: int,
    passenger_name: str,
    passenger_email: str,
    bus_name: str,
    bus_company: str,
    from_stop: str,
    to_stop: str,
    travel_date,
    seats: list,
    fare_per_seat: int,
    booked_at=None,
) -> bytes:
    """
    Generate an A4 bus ticket PDF and return its binary bytes.
    """
    buffer = io.BytesIO()
    
    # 1. Set up document template with 0.5 inch margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    
    # 2. Styles
    styles = getSampleStyleSheet()
    
    # Define custom paragraph styles
    title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#ffffff'),
        spaceAfter=2
    )
    tagline_style = ParagraphStyle(
        'HeaderTagline',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.HexColor('#a78bfa'),
    )
    eticket_style = ParagraphStyle(
        'ETicketTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#10b981'),
        alignment=2 # Right aligned
    )
    website_style = ParagraphStyle(
        'ETicketWeb',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#9ca3af'),
        alignment=2 # Right aligned
    )
    
    ref_label_style = ParagraphStyle(
        'RefLabel',
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.HexColor('#4b5563')
    )
    ref_val_style = ParagraphStyle(
        'RefVal',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#10b981')
    )
    ref_date_style = ParagraphStyle(
        'RefDate',
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#6b7280'),
        alignment=2
    )
    
    route_city_style = ParagraphStyle(
        'RouteCity',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#1e1b4b'),
        alignment=1 # Centered
    )
    route_arrow_style = ParagraphStyle(
        'RouteArrow',
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#8b5cf6'),
        alignment=1 # Centered
    )
    
    sec_header_style = ParagraphStyle(
        'SecHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor('#ffffff')
    )
    
    kv_label_style = ParagraphStyle(
        'KVLabel',
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#4b5563')
    )
    kv_value_style = ParagraphStyle(
        'KVValue',
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor('#1e1b4b')
    )
    
    total_lbl_style = ParagraphStyle(
        'TotalLabel',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#d1d5db')
    )
    total_val_style = ParagraphStyle(
        'TotalVal',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#10b981')
    )
    
    instr_style = ParagraphStyle(
        'Instruction',
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#4b5563'),
        leading=11
    )
    
    # Pre-calculated fields
    total_fare = fare_per_seat * len(seats)
    ref_no = f"YT{booking_id:06d}"
    booked_str = (
        booked_at.strftime("%d %b %Y, %I:%M %p") if booked_at
        else datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    )
    travel_str = (
        travel_date.strftime("%d %B %Y")
        if hasattr(travel_date, "strftime")
        else str(travel_date)
    )
    
    # ─── HEADER BANNER ────────────────────────────────────────────────────────
    header_data = [
        [
            Paragraph("YOUTH TRAVELS", title_style),
            Paragraph("E-TICKET", eticket_style)
        ],
        [
            Paragraph("Safe &bull; Premium &bull; Reliable Bus Services Across India", tagline_style),
            Paragraph("www.youthtravels.in", website_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[4.0*inch, 3.25*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1e1b4b')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))
    
    # ─── BOOKING REFERENCE BANNER ─────────────────────────────────────────────
    ref_data = [
        [
            Paragraph("Booking Reference: ", ref_label_style),
            Paragraph(ref_no, ref_val_style),
            Paragraph(f"Booked on: {booked_str}", ref_date_style)
        ]
    ]
    ref_table = Table(ref_data, colWidths=[1.8*inch, 1.8*inch, 3.65*inch])
    ref_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#10b981')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(ref_table)
    story.append(Spacer(1, 10))
    
    # ─── ROUTE VISUAL ─────────────────────────────────────────────────────────
    route_data = [
        [
            Paragraph(from_stop, route_city_style),
            Paragraph("&rarr;", route_arrow_style),
            Paragraph(to_stop, route_city_style)
        ]
    ]
    route_table = Table(route_data, colWidths=[3.2*inch, 0.85*inch, 3.2*inch])
    route_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f5f3ff')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(route_table)
    story.append(Spacer(1, 12))
    
    def add_section_header(title: str):
        sec_table = Table([[Paragraph(title, sec_header_style)]], colWidths=[7.25*inch])
        sec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#8b5cf6')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(sec_table)
        story.append(Spacer(1, 4))
        
    def add_kv_row(label: str, value: str):
        row_table = Table([
            [Paragraph(label, kv_label_style), Paragraph(value, kv_value_style)]
        ], colWidths=[2.2*inch, 5.05*inch])
        row_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#f3f4f6')),
        ]))
        story.append(row_table)
        
    # ─── JOURNEY DETAILS ──────────────────────────────────────────────────────
    add_section_header("JOURNEY DETAILS")
    add_kv_row("Travel Date:", travel_str)
    add_kv_row("Bus Name:", bus_name)
    add_kv_row("Operator:", bus_company)
    add_kv_row("Departure:", "As per operator schedule")
    story.append(Spacer(1, 10))
    
    # ─── PASSENGER DETAILS ────────────────────────────────────────────────────
    add_section_header("PASSENGER DETAILS")
    add_kv_row("Passenger Name:", passenger_name)
    add_kv_row("Email:", passenger_email)
    story.append(Spacer(1, 10))
    
    # ─── SEAT & FARE DETAILS ──────────────────────────────────────────────────
    add_section_header("SEAT & FARE DETAILS")
    add_kv_row("Seats Booked:", ", ".join(sorted(seats)))
    add_kv_row("Number of Seats:", str(len(seats)))
    add_kv_row("Fare Per Seat:", f"INR {fare_per_seat:,}")
    
    # Highlighted Total Row
    total_data = [
        [
            Paragraph("TOTAL AMOUNT PAID:", total_lbl_style),
            Paragraph(f"INR {total_fare:,}", total_val_style)
        ]
    ]
    total_table = Table(total_data, colWidths=[2.2*inch, 5.05*inch])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1e1b4b')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 10))
    
    # ─── PAYMENT STATUS ───────────────────────────────────────────────────────
    add_section_header("PAYMENT STATUS")
    add_kv_row("Payment Status:", "CONFIRMED (Online Payment)")
    story.append(Spacer(1, 10))
    
    # ─── IMPORTANT INSTRUCTIONS ───────────────────────────────────────────────
    add_section_header("IMPORTANT INSTRUCTIONS")
    instructions = [
        "Please carry this e-ticket (printed or on mobile) and a valid government-issued photo ID.",
        "Report at the boarding point at least 15 minutes before departure.",
        "Seats are reserved - no standing passengers allowed.",
        "Rescheduling/Cancellation: Contact operator or Youth Travels support at least 2 hours before departure.",
        "Youth Travels is not liable for delays caused by traffic, weather, or other road conditions.",
    ]
    
    instr_bullets = []
    for i, line in enumerate(instructions, 1):
        instr_bullets.append([
            Paragraph(f"{i}.", instr_style),
            Paragraph(line, instr_style)
        ])
    instr_table = Table(instr_bullets, colWidths=[0.3*inch, 6.95*inch])
    instr_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(instr_table)
    story.append(Spacer(1, 14))
    
    # ─── FOOTER THANK YOU ─────────────────────────────────────────────────────
    divider = Table([[""]], colWidths=[7.25*inch])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.75, colors.HexColor('#e5e7eb')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(divider)
    story.append(Spacer(1, 8))
    
    thankyou_style = ParagraphStyle(
        'ThankYouTitle',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#8b5cf6'),
        alignment=1
    )
    sub_thankyou_style = ParagraphStyle(
        'ThankYouSub',
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.HexColor('#6b7280'),
        alignment=1
    )
    story.append(Paragraph("Thank You for Choosing Youth Travels!", thankyou_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Reference: {ref_no}  |  Have a safe and pleasant journey!", sub_thankyou_style))
    
    # Draw page
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
