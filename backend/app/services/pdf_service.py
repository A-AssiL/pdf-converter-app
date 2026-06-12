from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch


class PDFService:
    def create_pdf(self, text: str, output_path: str):
        pdf = SimpleDocTemplate(output_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        styles = getSampleStyleSheet()
        story = []

        for paragraph in text.split("\n\n"):
            story.append(Paragraph(paragraph.replace("\n", "<br/>"), styles['BodyText']))
            story.append(Spacer(1, 12))

        pdf.build(story)
