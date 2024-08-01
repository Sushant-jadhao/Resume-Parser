from flask import Flask, request, render_template_string
import fitz  # PyMuPDF
import os
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

def extract_text_from_pdf(pdf_path):
    pdf_text = ""
    pdf_document = fitz.open(pdf_path)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pdf_text += page.get_text()
    pdf_document.close()
    return pdf_text

def parse_resume(resume_text):
    resume_json = {
        "personal_details": {
            "name": "",
            "contact": {
                "email": "",
                "phone": "",
                "address": ""
            }
        },
        "education": [],
        "work_experience": [],
        "skills": [],
        "projects": [],
        "publications": [],
        "extracurriculars": []
    }

    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]

    # Extract personal details
    if lines:
        resume_json["personal_details"]["name"] = lines[0]
    
    contact_info = lines[1].split('|')
    if len(contact_info) > 1:
        email = contact_info[0].strip()
        phone = contact_info[1].strip()
        resume_json["personal_details"]["contact"]["email"] = email
        resume_json["personal_details"]["contact"]["phone"] = phone

    # Parse sections
    current_section = None
    for line in lines:
        if 'EDUCATION' in line:
            current_section = 'education'
        elif 'PROJECTS' in line:
            current_section = 'projects'
        elif 'TECHNICAL SKILLS' in line:
            current_section = 'skills'
        elif 'Publications' in line:
            current_section = 'publications'
        elif 'POSITIONS OF RESPONSIBILITY' in line:
            current_section = 'work_experience'
        elif 'EXTRACURRICULARS' in line:
            current_section = 'extracurriculars'
        elif current_section:
            if current_section == 'education':
                resume_json["education"].append(line)
            elif current_section == 'projects':
                resume_json["projects"].append(line)
            elif current_section == 'skills':
                resume_json["skills"].append(line)
            elif current_section == 'publications':
                resume_json["publications"].append(line)
            elif current_section == 'work_experience':
                resume_json["work_experience"].append(line)
            elif current_section == 'extracurriculars':
                resume_json["extracurriculars"].append(line)

    return resume_json

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return render_template_string("<h1>No file part</h1>")
        file = request.files['resume']
        if file.filename == '':
            return render_template_string("<h1>No selected file</h1>")
        if file and file.filename.lower().endswith('.pdf'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            resume_text = extract_text_from_pdf(filepath)
            parsed_resume = parse_resume(resume_text)
            # Render JSON as formatted text on the web page
            return render_template_string('''
            <!doctype html>
            <html>
            <head>
                <title>Parsed Resume</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>Parsed Resume</h1>
                <pre>{{ resume_json | tojson(indent=4) }}</pre>
                <a href="/">Upload Another Resume</a>
            </body>
            </html>
            ''', resume_json=parsed_resume)
        else:
            return render_template_string("<h1>Please upload a PDF file</h1>")
    
    return '''
    <!doctype html>
    <html>
    <head>
        <title>Upload Resume</title>
    </head>
    <body>
        <h1>Upload Resume</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="resume">
            <input type="submit" value="Upload">
        </form>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
