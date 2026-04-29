from weasyprint import HTML


def save_pdf(html_content: str, filename: str = "report.pdf"):
    HTML(string=html_content).write_pdf(filename)