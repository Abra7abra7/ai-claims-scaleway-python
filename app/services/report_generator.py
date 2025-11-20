from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, Optional
import app.db.models as models


class ReportGenerator:
    """
    PDF Report Generator for AI Claims Analysis.
    Generates professional PDF reports from analysis results.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style (check if it doesn't already exist)
        if 'CustomBody' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomBody',
                parent=self.styles['Normal'],
                fontSize=10,
                leading=14,
                alignment=TA_JUSTIFY,
                spaceAfter=10
            ))
        
        # Recommendation style
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            spaceAfter=12,
            alignment=TA_CENTER
        ))
    
    def generate_pdf(
        self,
        claim: models.Claim,
        analysis_result: Dict[str, Any],
        model_used: str,
        prompt_id: str,
        sources: Optional[list] = None
    ) -> bytes:
        """
        Generate PDF report from claim analysis.
        
        Args:
            claim: Claim instance
            analysis_result: Analysis result dictionary
            model_used: Model used for analysis
            prompt_id: Prompt ID used
            sources: Optional list of RAG source documents
            
        Returns:
            PDF file as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Build story (content)
        story = []
        
        # Header
        story.extend(self._build_header(claim))
        
        # Claim information
        story.extend(self._build_claim_info(claim))
        
        # Analysis summary
        story.extend(self._build_analysis_summary(analysis_result))
        
        # Recommendation
        story.extend(self._build_recommendation(analysis_result))
        
        # Reasoning
        story.extend(self._build_reasoning(analysis_result))
        
        # Confidence
        story.extend(self._build_confidence(analysis_result))
        
        # Missing information
        if analysis_result.get('missing_info'):
            story.extend(self._build_missing_info(analysis_result))
        
        # Additional fields (fraud detection, medical codes, etc.)
        story.extend(self._build_additional_fields(analysis_result))
        
        # RAG sources
        if sources:
            story.extend(self._build_sources(sources))
        
        # Page break before metadata
        story.append(PageBreak())
        
        # Metadata
        story.extend(self._build_metadata(claim, model_used, prompt_id))
        
        # Footer disclaimer
        story.extend(self._build_footer())
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _build_header(self, claim: models.Claim) -> list:
        """Build report header"""
        elements = []
        
        # Title
        title = Paragraph("AI Claims Analysis Report", self.styles['CustomTitle'])
        elements.append(title)
        
        # Subtitle
        created_at_str = claim.created_at.strftime("%d.%m.%Y %H:%M") if claim.created_at else "N/A"
        subtitle_text = f"Claim ID: {claim.id} | Date: {created_at_str} | Country: {claim.country}"
        subtitle = Paragraph(subtitle_text, self.styles['Subtitle'])
        elements.append(subtitle)
        
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _build_claim_info(self, claim: models.Claim) -> list:
        """Build claim information section"""
        elements = []
        
        # Section header
        header = Paragraph("Claim Information", self.styles['SectionHeader'])
        elements.append(header)
        
        # Table data
        data = [
            ['Claim ID:', str(claim.id)],
            ['Country:', claim.country],
            ['Status:', claim.status],
            ['Documents:', str(len(claim.documents))],
            ['Created:', claim.created_at.strftime("%d.%m.%Y %H:%M") if claim.created_at else "N/A"]
        ]
        
        # Create table
        table = Table(data, colWidths=[5*cm, 10*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _build_analysis_summary(self, analysis_result: Dict[str, Any]) -> list:
        """Build analysis summary section"""
        elements = []
        
        header = Paragraph("Analysis Summary", self.styles['SectionHeader'])
        elements.append(header)
        
        return elements
    
    def _build_recommendation(self, analysis_result: Dict[str, Any]) -> list:
        """Build recommendation section"""
        elements = []
        
        recommendation = analysis_result.get('recommendation', 'N/A')
        
        # Color based on recommendation
        color_map = {
            'APPROVE': colors.green,
            'REJECT': colors.red,
            'INVESTIGATE': colors.orange
        }
        color = color_map.get(recommendation, colors.black)
        
        # Create styled paragraph
        rec_style = ParagraphStyle(
            'ColoredRecommendation',
            parent=self.styles['Recommendation'],
            textColor=color
        )
        
        text = f"<b>Recommendation: {recommendation}</b>"
        para = Paragraph(text, rec_style)
        elements.append(para)
        elements.append(Spacer(1, 0.3*cm))
        
        return elements
    
    def _build_reasoning(self, analysis_result: Dict[str, Any]) -> list:
        """Build reasoning section"""
        elements = []
        
        header = Paragraph("Reasoning", self.styles['SectionHeader'])
        elements.append(header)
        
        reasoning = analysis_result.get('reasoning', 'No reasoning provided.')
        para = Paragraph(reasoning, self.styles.get('CustomBody', self.styles['Normal']))
        elements.append(para)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _build_confidence(self, analysis_result: Dict[str, Any]) -> list:
        """Build confidence section"""
        elements = []
        
        confidence = analysis_result.get('confidence', 0)
        if isinstance(confidence, (int, float)):
            confidence_pct = f"{confidence * 100:.1f}%"
        else:
            confidence_pct = "N/A"
        
        text = f"<b>Confidence Score:</b> {confidence_pct}"
        para = Paragraph(text, self.styles['BodyText'])
        elements.append(para)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _build_missing_info(self, analysis_result: Dict[str, Any]) -> list:
        """Build missing information section"""
        elements = []
        
        header = Paragraph("Missing Information", self.styles['SectionHeader'])
        elements.append(header)
        
        missing_info = analysis_result.get('missing_info', [])
        if missing_info:
            items_html = "<br/>".join([f"• {item}" for item in missing_info])
            para = Paragraph(items_html, self.styles['BodyText'])
            elements.append(para)
        else:
            para = Paragraph("No missing information identified.", self.styles['BodyText'])
            elements.append(para)
        
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _build_additional_fields(self, analysis_result: Dict[str, Any]) -> list:
        """Build additional fields specific to prompt type"""
        elements = []
        
        # Fraud detection fields
        if 'fraud_risk_score' in analysis_result:
            header = Paragraph("Fraud Detection Analysis", self.styles['SectionHeader'])
            elements.append(header)
            
            fraud_score = analysis_result.get('fraud_risk_score', 0)
            if isinstance(fraud_score, (int, float)):
                fraud_pct = f"{fraud_score * 100:.1f}%"
            else:
                fraud_pct = "N/A"
            
            text = f"<b>Fraud Risk Score:</b> {fraud_pct}"
            para = Paragraph(text, self.styles['BodyText'])
            elements.append(para)
            
            red_flags = analysis_result.get('red_flags', [])
            if red_flags:
                text = "<b>Red Flags:</b><br/>" + "<br/>".join([f"• {flag}" for flag in red_flags])
                para = Paragraph(text, self.styles['BodyText'])
                elements.append(para)
            
            elements.append(Spacer(1, 0.5*cm))
        
        # Medical analysis fields
        if 'medical_codes_found' in analysis_result:
            header = Paragraph("Medical Analysis", self.styles['SectionHeader'])
            elements.append(header)
            
            codes = analysis_result.get('medical_codes_found', [])
            if codes:
                text = "<b>Medical Codes Found:</b><br/>" + "<br/>".join([f"• {code}" for code in codes])
                para = Paragraph(text, self.styles['BodyText'])
                elements.append(para)
            
            treatment = analysis_result.get('treatment_appropriateness', '')
            if treatment:
                text = f"<b>Treatment Appropriateness:</b><br/>{treatment}"
                para = Paragraph(text, self.styles['BodyText'])
                elements.append(para)
            
            elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _build_sources(self, sources: list) -> list:
        """Build RAG sources section"""
        elements = []
        
        header = Paragraph("Reference Documents Used", self.styles['SectionHeader'])
        elements.append(header)
        
        text = "The following policy documents were referenced for this analysis:<br/><br/>"
        for source in sources:
            filename = source.get('filename', 'Unknown')
            doc_type = source.get('document_type', 'Unknown')
            similarity = source.get('similarity', 0)
            text += f"• {filename} ({doc_type}) - Relevance: {similarity:.2%}<br/>"
        
        para = Paragraph(text, self.styles['BodyText'])
        elements.append(para)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _build_metadata(self, claim: models.Claim, model_used: str, prompt_id: str) -> list:
        """Build metadata section"""
        elements = []
        
        header = Paragraph("Report Metadata", self.styles['SectionHeader'])
        elements.append(header)
        
        data = [
            ['AI Model:', model_used],
            ['Analysis Type:', prompt_id],
            ['Generated:', datetime.utcnow().strftime("%d.%m.%Y %H:%M UTC")]
        ]
        
        table = Table(data, colWidths=[5*cm, 10*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _build_footer(self) -> list:
        """Build footer with disclaimer"""
        elements = []
        
        disclaimer_text = (
            "<i>This report was generated by an AI system and should be reviewed by a qualified professional. "
            "The recommendations provided are based on automated analysis and may require human verification. "
            "This document is confidential and intended solely for internal use.</i>"
        )
        
        para = Paragraph(disclaimer_text, self.styles['BodyText'])
        elements.append(para)
        
        return elements

