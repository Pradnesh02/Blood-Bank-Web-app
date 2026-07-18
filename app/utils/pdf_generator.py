from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.models.blood_stock import BloodStock
from app.models.donor import Donor
from app.models.request import BloodRequest
from datetime import datetime
import io

def generate_blood_bank_pdf():
    """
    Generates a professional inventory and status PDF report.
    Returns: BytesIO object stream containing PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()
    
    RED = colors.HexColor('#B71C1C')
    DARK_TEXT = colors.HexColor('#212121')
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=RED,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#757575'),
        spaceAfter=15
    )
    
    section_style = ParagraphStyle(
        'DocSec',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=DARK_TEXT,
        spaceBefore=12,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=DARK_TEXT,
        spaceAfter=6
    )
    
    # 1. Document Title & Timestamp
    story.append(Paragraph("🩸 Blood Bank Management System", title_style))
    story.append(Paragraph(f"Inventory Summary & Activity Report - Generated {datetime.utcnow().strftime('%d %B %Y %H:%M UTC')}", subtitle_style))
    
    # 2. Executive Metrics Summary
    total_donors = Donor.query.count()
    total_requests = BloodRequest.query.count()
    pending = BloodRequest.query.filter_by(status='Pending').count()
    approved = BloodRequest.query.filter_by(status='Approved').count()
    rejected = BloodRequest.query.filter_by(status='Rejected').count()
    
    summary_txt = (
        f"This status report presents inventory levels and transactions logged. "
        f"Currently, the system catalogs <b>{total_donors}</b> active donors. A total of "
        f"<b>{total_requests}</b> blood requests have been logged: <b>{approved}</b> approved, "
        f"<b>{pending}</b> pending, and <b>{rejected}</b> rejected."
    )
    story.append(Paragraph(summary_txt, body_style))
    story.append(Spacer(1, 10))
    
    # 3. Blood Stock Inventory Table
    story.append(Paragraph("Current Inventory Stock", section_style))
    stock_data = [['Blood Group', 'Units Available', 'Inventory Status']]
    critical_groups = []
    
    for group in ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']:
        stock = BloodStock.query.filter_by(blood_group=group).first()
        units = stock.units if stock else 0
        
        if units == 0:
            status = 'Depleted'
            critical_groups.append(group)
        elif units < 5:
            status = 'Critical Low'
            critical_groups.append(group)
        elif units < 10:
            status = 'Low Warning'
        else:
            status = 'Sufficient'
            
        stock_data.append([group, f"{units} Units", status])
        
    table = Table(stock_data, colWidths=[150, 150, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), RED),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FDECEA'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
    ]))
    
    # Stylize the status cells depending on severity
    for idx, row in enumerate(stock_data[1:], start=1):
        status_val = row[2]
        if status_val in ['Depleted', 'Critical Low']:
            table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, idx), (2, idx), colors.HexColor('#C62828')),
                ('FONTNAME', (2, idx), (2, idx), 'Helvetica-Bold')
            ]))
        elif status_val == 'Low Warning':
            table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, idx), (2, idx), colors.HexColor('#EF6C00')),
            ]))
        else:
            table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, idx), (2, idx), colors.HexColor('#2E7D32')),
            ]))
            
    story.append(table)
    story.append(Spacer(1, 10))
    
    # 4. Inventory Alert Section
    if critical_groups:
        story.append(Paragraph("🚨 Active Inventory Restock Alerts", section_style))
        alert_txt = f"Inventory units for blood types <b>{', '.join(critical_groups)}</b> have fallen below safety limits (<5 units). Contact fit donors immediately."
        story.append(Paragraph(alert_txt, body_style))
        story.append(Spacer(1, 10))
        
    doc.build(story)
    buffer.seek(0)
    return buffer
