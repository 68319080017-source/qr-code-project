import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from typing import List
from app.models.asset import Asset

class ReportService:
    @staticmethod
    def generate_excel_report(assets: List[Asset]) -> str:
        """
        Generate an Excel report for the given assets and return the file path.
        """
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, "assets_report.xlsx")
        
        data = [{
            "Asset Code": a.asset_code,
            "Name": a.name,
            "Category": a.category,
            "Building": a.building,
            "Room": a.room,
            "Status": a.status,
            "Responsible": a.responsible_person
        } for a in assets]
        
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        return filepath

    @staticmethod
    def generate_pdf_report(assets: List[Asset]) -> str:
        """
        Generate a PDF report for the given assets and return the file path.
        """
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, "assets_report.pdf")
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        
        styles = getSampleStyleSheet()
        title = Paragraph("Asset Report", styles['Title'])
        elements.append(title)
        
        data = [["Asset Code", "Name", "Category", "Status"]]
        for a in assets:
            data.append([a.asset_code, a.name, a.category or "-", a.status])
            
        table = Table(data)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)
        elements.append(table)
        
        doc.build(elements)
        return filepath
