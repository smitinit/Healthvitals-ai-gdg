import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_overview_pdf(result):
    """Generate a PDF for the Overview section of the analysis result"""
    buffer = io.BytesIO()
    
    # Set up the document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Define styles - create a new stylesheet to prevent conflicts
    styles = getSampleStyleSheet()
    
    # Define new custom styles with unique names
    document_title = ParagraphStyle(
        name='DocumentTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    section_subtitle = ParagraphStyle(
        name='SectionSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=8
    )
    
    normal_text = ParagraphStyle(
        name='NormalText',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5
    )
    
    list_item_style = ParagraphStyle(
        name='ListItemStyle',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=10
    )
    
    # Create content
    content = []
    
    # Title
    content.append(Paragraph("HealthVitals AI - Symptom Analysis Overview", document_title))
    content.append(Spacer(1, 10*mm))
    
    # Urgency Level
    urgency_colors = {
        "low": "#4CAF50",  # Green
        "medium": "#FF9800",  # Orange
        "high": "#F44336"  # Red
    }
    
    content.append(Paragraph("Urgency Level: <font color='{}'>{}</font>".format(
        urgency_colors.get(result.get('urgency', 'medium'), "#FF9800"),
        result.get('urgency', 'medium').upper()
    ), section_subtitle))
    content.append(Spacer(1, 5*mm))
    
    # Primary Recommendation
    content.append(Paragraph("Recommendation:", section_subtitle))
    content.append(Paragraph(result.get('recommendation', 'No recommendation available.'), normal_text))
    content.append(Spacer(1, 5*mm))
    
    # Health Score (if available)
    if 'healthScore' in result:
        content.append(Paragraph(f"Health Score: {result['healthScore']}/10", section_subtitle))
        
        # Add description based on the score
        score = result['healthScore']
        if score >= 8:
            score_desc = "Your health score is very good!"
        elif score >= 6:
            score_desc = "Your health score is good, with some areas for improvement."
        elif score >= 4:
            score_desc = "Your health score indicates medical attention may be needed."
        else:
            score_desc = "Your health score suggests urgent medical attention is recommended."
        
        content.append(Paragraph(score_desc, normal_text))
        content.append(Spacer(1, 5*mm))
    
    # Possible Conditions (moved here to be more prominent)
    if result.get('possibleConditions'):
        content.append(Paragraph("Possible Conditions:", section_subtitle))
        for condition in result.get('possibleConditions', [])[:3]:
            # Condition header
            content.append(Paragraph(
                f"<b>{condition.get('name')} ({condition.get('probability')}%)</b>",
                normal_text
            ))
            # Description (shortened for overview)
            description = condition.get('description', 'No description available.')
            if len(description) > 150:
                description = description[:150] + "..."
            content.append(Paragraph(description, normal_text))
            content.append(Spacer(1, 2*mm))
        content.append(Spacer(1, 3*mm))
    
    # Follow-up Actions
    content.append(Paragraph("Recommended Actions:", section_subtitle))
    actions = []
    for i, action in enumerate(result.get('followUpActions', [])[:3], 1):
        actions.append(Paragraph(f"{i}. {action}", list_item_style))
    
    if actions:
        for action in actions:
            content.append(action)
    else:
        content.append(Paragraph("No specific actions recommended.", normal_text))
    
    content.append(Spacer(1, 5*mm))
    
    # Risk Factors
    content.append(Paragraph("Risk Factors:", section_subtitle))
    risks = []
    for i, risk in enumerate(result.get('riskFactors', [])[:3], 1):
        risks.append(Paragraph(f"{i}. {risk}", list_item_style))
    
    if risks:
        for risk in risks:
            content.append(risk)
    else:
        content.append(Paragraph("No specific risk factors identified.", normal_text))
    
    content.append(Spacer(1, 5*mm))
    
    # Diseases
    if result.get('diseases'):
        content.append(Paragraph("Possible Diseases:", section_subtitle))
        for i, disease in enumerate(result.get('diseases', [])[:3], 1):
            content.append(Paragraph(f"{i}. {disease}", list_item_style))
        content.append(Spacer(1, 5*mm))
    
    # Preventive Measures
    if result.get('preventiveMeasures'):
        content.append(Paragraph("Preventive Measures:", section_subtitle))
        for i, measure in enumerate(result.get('preventiveMeasures', [])[:3], 1):
            content.append(Paragraph(f"{i}. {measure}", list_item_style))
        content.append(Spacer(1, 5*mm))
    
    # Do's and Don'ts
    if result.get('dos') or result.get('donts'):
        content.append(Paragraph("Do's and Don'ts:", section_subtitle))
        
        if result.get('dos'):
            content.append(Paragraph("Do's:", list_item_style))
            for i, do_item in enumerate(result.get('dos', [])[:3], 1):
                content.append(Paragraph(f"{i}. {do_item}", list_item_style))
            content.append(Spacer(1, 3*mm))
        
        if result.get('donts'):
            content.append(Paragraph("Don'ts:", list_item_style))
            for i, dont_item in enumerate(result.get('donts', [])[:3], 1):
                content.append(Paragraph(f"{i}. {dont_item}", list_item_style))
        content.append(Spacer(1, 5*mm))
    
    # Add a medical disclaimer at the end
    content.append(Spacer(1, 10*mm))
    content.append(Paragraph(
        "<i>Disclaimer: This analysis is for informational purposes only and does not constitute medical advice. "
        "Always consult with a qualified healthcare provider for diagnosis and treatment.</i>",
        normal_text
    ))
    
    # Build the PDF
    doc.build(content)
    buffer.seek(0)
    return buffer


def generate_details_pdf(result):
    """Generate a detailed PDF with all analysis results"""
    buffer = io.BytesIO()
    
    # Set up the document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Define styles - create a new stylesheet to prevent conflicts
    styles = getSampleStyleSheet()
    
    # Define new custom styles with unique names
    document_title = ParagraphStyle(
        name='DetailDocumentTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    section_subtitle = ParagraphStyle(
        name='DetailSectionSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=8
    )
    
    section_title = ParagraphStyle(
        name='DetailSectionTitle',
        parent=styles['Heading3'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=6
    )
    
    normal_text = ParagraphStyle(
        name='DetailNormalText',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5
    )
    
    list_item_style = ParagraphStyle(
        name='DetailListItemStyle',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=10
    )
    
    # Create content
    content = []
    
    # Title
    content.append(Paragraph("HealthVitals AI - Detailed Symptom Analysis", document_title))
    content.append(Spacer(1, 10*mm))
    
    # Urgency Level
    urgency_colors = {
        "low": "#4CAF50",  # Green
        "medium": "#FF9800",  # Orange
        "high": "#F44336"  # Red
    }
    
    content.append(Paragraph("Urgency Level: <font color='{}'>{}</font>".format(
        urgency_colors.get(result.get('urgency', 'medium'), "#FF9800"),
        result.get('urgency', 'medium').upper()
    ), section_subtitle))
    content.append(Spacer(1, 5*mm))
    
    # Primary Recommendation
    content.append(Paragraph("Recommendation:", section_subtitle))
    content.append(Paragraph(result.get('recommendation', 'No recommendation available.'), normal_text))
    content.append(Spacer(1, 8*mm))
    
    # Health Score (if available)
    if 'healthScore' in result:
        content.append(Paragraph(f"Health Score: {result['healthScore']}/10", section_subtitle))
        
        # Add description based on the score
        score = result['healthScore']
        if score >= 8:
            score_desc = "Your health score is very good!"
        elif score >= 6:
            score_desc = "Your health score is good, with some areas for improvement."
        elif score >= 4:
            score_desc = "Your health score indicates medical attention may be needed."
        else:
            score_desc = "Your health score suggests urgent medical attention is recommended."
        
        content.append(Paragraph(score_desc, normal_text))
        content.append(Spacer(1, 8*mm))
    
    # Possible Conditions
    content.append(Paragraph("Possible Conditions:", section_subtitle))
    for condition in result.get('possibleConditions', [])[:3]:
        # Condition header
        content.append(Paragraph(
            f"<b>{condition.get('name')} ({condition.get('probability')}%)</b>",
            section_title
        ))
        # Description
        content.append(Paragraph(condition.get('description', 'No description available.'), normal_text))
        
        # Check if there's condition-specific data
        condition_name = condition.get('name', '')
        condition_data = result.get('conditionSpecificData', {}).get(condition_name, {})
        
        # Recommended Actions for this condition
        if condition_data and 'recommendedActions' in condition_data and condition_data['recommendedActions']:
            content.append(Paragraph("Recommended Actions:", section_title))
            for i, action in enumerate(condition_data['recommendedActions'][:3], 1):
                content.append(Paragraph(f"{i}. {action}", list_item_style))
            content.append(Spacer(1, 3*mm))
        
        # Preventive Measures for this condition
        if condition_data and 'preventiveMeasures' in condition_data and condition_data['preventiveMeasures']:
            content.append(Paragraph("Preventive Measures:", section_title))
            for i, measure in enumerate(condition_data['preventiveMeasures'][:3], 1):
                content.append(Paragraph(f"{i}. {measure}", list_item_style))
        
        content.append(Spacer(1, 5*mm))
    
    # General Follow-up Actions
    content.append(Paragraph("Follow-up Actions:", section_subtitle))
    for i, action in enumerate(result.get('followUpActions', [])[:3], 1):
        content.append(Paragraph(f"{i}. {action}", normal_text))
    content.append(Spacer(1, 8*mm))
    
    # Meal Recommendations
    if result.get('mealRecommendations') and any(result['mealRecommendations'].values()):
        content.append(Paragraph("Meal Recommendations:", section_subtitle))
        
        # Breakfast
        if result['mealRecommendations'].get('breakfast'):
            content.append(Paragraph("Breakfast:", section_title))
            for i, meal in enumerate(result['mealRecommendations']['breakfast'][:3], 1):
                content.append(Paragraph(f"{i}. {meal}", normal_text))
            content.append(Spacer(1, 3*mm))
        
        # Lunch
        if result['mealRecommendations'].get('lunch'):
            content.append(Paragraph("Lunch:", section_title))
            for i, meal in enumerate(result['mealRecommendations']['lunch'][:3], 1):
                content.append(Paragraph(f"{i}. {meal}", normal_text))
            content.append(Spacer(1, 3*mm))
        
        # Dinner
        if result['mealRecommendations'].get('dinner'):
            content.append(Paragraph("Dinner:", section_title))
            for i, meal in enumerate(result['mealRecommendations']['dinner'][:3], 1):
                content.append(Paragraph(f"{i}. {meal}", normal_text))
            
        # Diet Note
        if result['mealRecommendations'].get('note'):
            content.append(Paragraph(f"<i>{result['mealRecommendations']['note']}</i>", normal_text))
        
        content.append(Spacer(1, 8*mm))
    
    # Exercise Plan
    if result.get('exercisePlan'):
        content.append(Paragraph("Exercise Plan:", section_subtitle))
        for i, exercise in enumerate(result.get('exercisePlan', [])[:3], 1):
            content.append(Paragraph(f"{i}. {exercise}", normal_text))
        content.append(Spacer(1, 8*mm))
    
    # Ayurvedic Medication
    if result.get('ayurvedicMedication') and result['ayurvedicMedication'].get('recommendations'):
        content.append(Paragraph("Ayurvedic Medication:", section_subtitle))
        
        for recommendation in result['ayurvedicMedication']['recommendations'][:3]:
            # Name
            content.append(Paragraph(f"<b>{recommendation.get('name', 'Ayurvedic Medicine')}</b>", section_title))
            
            # Description
            if recommendation.get('description'):
                content.append(Paragraph("<b>Description:</b>", normal_text))
                content.append(Paragraph(recommendation['description'], normal_text))
                content.append(Spacer(1, 2*mm))
            
            # Importance
            if recommendation.get('importance'):
                content.append(Paragraph("<b>Why It's Important:</b>", normal_text))
                content.append(Paragraph(recommendation['importance'], normal_text))
                content.append(Spacer(1, 2*mm))
            
            # Benefits
            if recommendation.get('benefits'):
                content.append(Paragraph("<b>Benefits:</b>", normal_text))
                content.append(Paragraph(recommendation['benefits'], normal_text))
            
            content.append(Spacer(1, 5*mm))
        
        content.append(Spacer(1, 5*mm))
    
    # Reports Required
    if result.get('reportsRequired'):
        content.append(Paragraph("Reports Required:", section_subtitle))
        
        for report in result.get('reportsRequired', [])[:3]:
            content.append(Paragraph(f"<b>{report.get('name', 'Medical Test')}</b>", section_title))
            
            if report.get('purpose'):
                content.append(Paragraph("<b>Purpose:</b>", normal_text))
                content.append(Paragraph(report['purpose'], normal_text))
                content.append(Spacer(1, 2*mm))
            
            if report.get('benefits'):
                content.append(Paragraph("<b>Benefits:</b>", normal_text))
                content.append(Paragraph(report['benefits'], normal_text))
                content.append(Spacer(1, 2*mm))
            
            if report.get('analysisDetails'):
                content.append(Paragraph("<b>Analysis Details:</b>", normal_text))
                content.append(Paragraph(report['analysisDetails'], normal_text))
                content.append(Spacer(1, 2*mm))
            
            if report.get('preparationRequired'):
                content.append(Paragraph("<b>Preparation Required:</b>", normal_text))
                content.append(Paragraph(report['preparationRequired'], normal_text))
                content.append(Spacer(1, 2*mm))
            
            if report.get('recommendationReason'):
                content.append(Paragraph("<b>Recommendation Reason:</b>", normal_text))
                content.append(Paragraph(report['recommendationReason'], normal_text))
            
            content.append(Spacer(1, 5*mm))
    
    # Add a medical disclaimer at the end
    content.append(Spacer(1, 10*mm))
    content.append(Paragraph(
        "<i>Disclaimer: This analysis is for informational purposes only and does not constitute medical advice. "
        "Always consult with a qualified healthcare provider for diagnosis and treatment.</i>",
        normal_text
    ))
    
    # Build the PDF
    doc.build(content)
    buffer.seek(0)
    return buffer 