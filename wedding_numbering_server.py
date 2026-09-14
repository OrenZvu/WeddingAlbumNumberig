from flask import Flask, render_template_string, request, send_file, jsonify
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, white
from PyPDF2 import PdfReader, PdfWriter
import io
import os
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

DESIGN_COORDINATES = {
    "2": {
        "1": [{"number": 1, "x": 1786, "y": 408}, {"number": 2, "x": 512, "y": 420}],
        "2": [{"number": 1, "x": 1983, "y": 414}, {"number": 2, "x": 1536, "y": 238}, {"number": 3, "x": 1550, "y": 527}, {"number": 4, "x": 1601, "y": 745}, {"number": 5, "x": 1280, "y": 190}, {"number": 6, "x": 1320, "y": 343}, {"number": 7, "x": 1263, "y": 641}, {"number": 8, "x": 1010, "y": 136}, {"number": 9, "x": 1015, "y": 417}, {"number": 10, "x": 1004, "y": 711}, {"number": 11, "x": 307, "y": 417}],
        "3": [{"number": 1, "x": 1985, "y": 408}, {"number": 2, "x": 1499, "y": 165}, {"number": 3, "x": 1479, "y": 386}, {"number": 4, "x": 1493, "y": 714}, {"number": 5, "x": 1061, "y": 431}, {"number": 6, "x": 685, "y": 162}, {"number": 7, "x": 745, "y": 420}, {"number": 8, "x": 634, "y": 680}, {"number": 9, "x": 208, "y": 371}],
        "4": [{"number": 1, "x": 1934, "y": 397}, {"number": 2, "x": 1365, "y": 255}, {"number": 3, "x": 1399, "y": 612}, {"number": 4, "x": 748, "y": 371}, {"number": 5, "x": 202, "y": 145}, {"number": 6, "x": 219, "y": 408}, {"number": 7, "x": 196, "y": 683}],
        "5": [{"number": 1, "x": 1758, "y": 428}, {"number": 2, "x": 944, "y": 125}, {"number": 3, "x": 583, "y": 139}, {"number": 4, "x": 788, "y": 388}, {"number": 5, "x": 964, "y": 711}, {"number": 6, "x": 646, "y": 694}, {"number": 7, "x": 253, "y": 454}],
        "6": [{"number": 1, "x": 2008, "y": 414}, {"number": 2, "x": 1681, "y": 422}, {"number": 3, "x": 1297, "y": 417}, {"number": 4, "x": 976, "y": 411}, {"number": 5, "x": 617, "y": 417}, {"number": 6, "x": 253, "y": 400}],
        "7": [{"number": 1, "x": 2108, "y": 207}, {"number": 2, "x": 2113, "y": 629}, {"number": 3, "x": 1709, "y": 454}, {"number": 4, "x": 1368, "y": 235}, {"number": 5, "x": 1380, "y": 604}, {"number": 6, "x": 993, "y": 414}, {"number": 7, "x": 338, "y": 400}],
        "8": [{"number": 1, "x": 2034, "y": 439}, {"number": 2, "x": 1675, "y": 145}, {"number": 3, "x": 1667, "y": 434}, {"number": 4, "x": 1684, "y": 725}, {"number": 5, "x": 1328, "y": 420}, {"number": 6, "x": 711, "y": 386}, {"number": 7, "x": 199, "y": 374}],
        "9": [{"number": 1, "x": 1792, "y": 267}, {"number": 2, "x": 2065, "y": 703}, {"number": 3, "x": 1687, "y": 714}, {"number": 4, "x": 1343, "y": 728}, {"number": 5, "x": 839, "y": 451}, {"number": 6, "x": 304, "y": 320}, {"number": 7, "x": 563, "y": 725}, {"number": 8, "x": 245, "y": 697}],
        "10": [{"number": 1, "x": 2096, "y": 456}, {"number": 2, "x": 1527, "y": 264}, {"number": 3, "x": 1712, "y": 686}, {"number": 4, "x": 1306, "y": 697}, {"number": 5, "x": 1015, "y": 199}, {"number": 6, "x": 1041, "y": 621}, {"number": 7, "x": 776, "y": 456}, {"number": 8, "x": 560, "y": 235}, {"number": 9, "x": 577, "y": 646}, {"number": 10, "x": 290, "y": 437}],
        "11": [{"number": 1, "x": 1940, "y": 247}, {"number": 2, "x": 2054, "y": 680}, {"number": 3, "x": 1707, "y": 680}, {"number": 4, "x": 1260, "y": 394}, {"number": 5, "x": 927, "y": 468}, {"number": 6, "x": 646, "y": 459}, {"number": 7, "x": 219, "y": 465}],
        "12": [{"number": 1, "x": 1948, "y": 235}, {"number": 2, "x": 1971, "y": 646}, {"number": 3, "x": 1152, "y": 275}, {"number": 4, "x": 1496, "y": 737}, {"number": 5, "x": 1263, "y": 748}, {"number": 6, "x": 1018, "y": 728}, {"number": 7, "x": 734, "y": 731}, {"number": 8, "x": 324, "y": 267}, {"number": 9, "x": 321, "y": 598}],
        "13": [{"number": 1, "x": 2059, "y": 241}, {"number": 2, "x": 2076, "y": 609}, {"number": 3, "x": 1212, "y": 431}, {"number": 4, "x": 162, "y": 269}, {"number": 5, "x": 239, "y": 575}],
        "14": [{"number": 1, "x": 2096, "y": 264}, {"number": 2, "x": 2076, "y": 618}, {"number": 3, "x": 1465, "y": 451}, {"number": 4, "x": 850, "y": 165}, {"number": 5, "x": 674, "y": 539}, {"number": 6, "x": 683, "y": 170}, {"number": 7, "x": 407, "y": 201}, {"number": 8, "x": 247, "y": 584}, {"number": 9, "x": 168, "y": 201}],
        "15": [{"number": 1, "x": 1920, "y": 405}, {"number": 2, "x": 1340, "y": 193}, {"number": 3, "x": 1220, "y": 626}, {"number": 4, "x": 705, "y": 193}, {"number": 5, "x": 569, "y": 590}, {"number": 6, "x": 205, "y": 165}, {"number": 7, "x": 301, "y": 411}, {"number": 8, "x": 134, "y": 411}, {"number": 9, "x": 208, "y": 629}],
        "16": [{"number": 1, "x": 1664, "y": 439}, {"number": 2, "x": 848, "y": 199}, {"number": 3, "x": 270, "y": 179}, {"number": 4, "x": 412, "y": 598}],
        "17": [{"number": 1, "x": 1960, "y": 190}, {"number": 2, "x": 2057, "y": 442}, {"number": 3, "x": 1772, "y": 437}, {"number": 4, "x": 1985, "y": 652}, {"number": 5, "x": 1510, "y": 133}, {"number": 6, "x": 1237, "y": 153}, {"number": 7, "x": 1377, "y": 445}, {"number": 8, "x": 1525, "y": 731}, {"number": 9, "x": 1269, "y": 692}, {"number": 10, "x": 964, "y": 148}, {"number": 11, "x": 757, "y": 150}, {"number": 12, "x": 825, "y": 425}, {"number": 13, "x": 978, "y": 748}, {"number": 14, "x": 714, "y": 717}, {"number": 15, "x": 489, "y": 128}, {"number": 16, "x": 222, "y": 139}, {"number": 17, "x": 287, "y": 374}, {"number": 18, "x": 398, "y": 709}, {"number": 19, "x": 213, "y": 703}],
        "18": [{"number": 1, "x": 2130, "y": 425}, {"number": 2, "x": 1746, "y": 187}, {"number": 3, "x": 1653, "y": 590}, {"number": 4, "x": 1311, "y": 244}, {"number": 5, "x": 1308, "y": 652}, {"number": 6, "x": 950, "y": 159}, {"number": 7, "x": 1015, "y": 558}, {"number": 8, "x": 637, "y": 255}, {"number": 9, "x": 671, "y": 697}, {"number": 10, "x": 216, "y": 425}],
        "19": [{"number": 1, "x": 1897, "y": 286}, {"number": 2, "x": 2020, "y": 697}, {"number": 3, "x": 1678, "y": 683}, {"number": 4, "x": 1192, "y": 473}, {"number": 5, "x": 375, "y": 261}, {"number": 6, "x": 239, "y": 680}, {"number": 7, "x": 592, "y": 692}],
        "20": [{"number": 1, "x": 2054, "y": 159}, {"number": 2, "x": 2122, "y": 442}, {"number": 3, "x": 1940, "y": 417}, {"number": 4, "x": 2130, "y": 689}, {"number": 5, "x": 1766, "y": 692}, {"number": 6, "x": 1573, "y": 686}, {"number": 7, "x": 1277, "y": 703}, {"number": 8, "x": 1508, "y": 326}, {"number": 9, "x": 924, "y": 162}, {"number": 10, "x": 580, "y": 595}, {"number": 11, "x": 489, "y": 179}, {"number": 12, "x": 173, "y": 136}, {"number": 13, "x": 176, "y": 428}, {"number": 14, "x": 185, "y": 677}],
        "21": [{"number": 1, "x": 2031, "y": 139}, {"number": 2, "x": 2045, "y": 584}, {"number": 3, "x": 1647, "y": 272}, {"number": 4, "x": 1684, "y": 672}, {"number": 5, "x": 1291, "y": 133}, {"number": 6, "x": 1331, "y": 581}, {"number": 7, "x": 947, "y": 284}, {"number": 8, "x": 984, "y": 677}, {"number": 9, "x": 407, "y": 403}],
        "22": [{"number": 1, "x": 1926, "y": 252}, {"number": 2, "x": 2025, "y": 632}, {"number": 3, "x": 1490, "y": 136}, {"number": 4, "x": 1525, "y": 295}, {"number": 5, "x": 1419, "y": 575}, {"number": 6, "x": 1226, "y": 213}, {"number": 7, "x": 811, "y": 284}, {"number": 8, "x": 828, "y": 638}, {"number": 9, "x": 324, "y": 252}, {"number": 10, "x": 392, "y": 524}, {"number": 11, "x": 381, "y": 731}, {"number": 12, "x": 139, "y": 632}],
        "23": [{"number": 1, "x": 1815, "y": 400}, {"number": 2, "x": 1260, "y": 182}, {"number": 3, "x": 1220, "y": 442}, {"number": 4, "x": 1254, "y": 694}, {"number": 5, "x": 759, "y": 258}, {"number": 6, "x": 941, "y": 675}, {"number": 7, "x": 540, "y": 706}, {"number": 8, "x": 199, "y": 731}, {"number": 9, "x": 210, "y": 383}, {"number": 10, "x": 173, "y": 88}],
        "24": [{"number": 1, "x": 1900, "y": 363}, {"number": 2, "x": 1286, "y": 204}, {"number": 3, "x": 902, "y": 190}, {"number": 4, "x": 1488, "y": 442}, {"number": 5, "x": 1115, "y": 442}, {"number": 6, "x": 1655, "y": 697}, {"number": 7, "x": 1331, "y": 680}, {"number": 8, "x": 455, "y": 482}],
        "25": [{"number": 1, "x": 1946, "y": 386}, {"number": 2, "x": 1277, "y": 199}, {"number": 3, "x": 825, "y": 187}, {"number": 4, "x": 606, "y": 173}, {"number": 5, "x": 1422, "y": 420}, {"number": 6, "x": 1035, "y": 448}, {"number": 7, "x": 762, "y": 445}, {"number": 8, "x": 1567, "y": 689}, {"number": 9, "x": 1203, "y": 683}, {"number": 10, "x": 850, "y": 692}, {"number": 11, "x": 233, "y": 417}],
        "26": [{"number": 1, "x": 2074, "y": 122}, {"number": 2, "x": 1744, "y": 148}, {"number": 3, "x": 1886, "y": 380}, {"number": 4, "x": 2096, "y": 734}, {"number": 5, "x": 1775, "y": 734}, {"number": 6, "x": 1081, "y": 230}, {"number": 7, "x": 1479, "y": 717}, {"number": 8, "x": 1143, "y": 720}, {"number": 9, "x": 796, "y": 720}, {"number": 10, "x": 498, "y": 108}, {"number": 11, "x": 179, "y": 139}, {"number": 12, "x": 299, "y": 403}, {"number": 13, "x": 185, "y": 731}, {"number": 14, "x": 498, "y": 734}],
        "27": [{"number": 1, "x": 2085, "y": 182}, {"number": 2, "x": 1994, "y": 493}, {"number": 3, "x": 2122, "y": 757}, {"number": 4, "x": 1872, "y": 754}, {"number": 5, "x": 1601, "y": 442}, {"number": 6, "x": 1527, "y": 692}, {"number": 7, "x": 1479, "y": 207}, {"number": 8, "x": 592, "y": 278}, {"number": 9, "x": 1112, "y": 737}, {"number": 10, "x": 779, "y": 711}, {"number": 11, "x": 478, "y": 728}, {"number": 12, "x": 208, "y": 709}],
        "28": [{"number": 1, "x": 2091, "y": 697}, {"number": 2, "x": 1610, "y": 278}, {"number": 3, "x": 1761, "y": 723}, {"number": 4, "x": 1493, "y": 725}, {"number": 5, "x": 1203, "y": 737}, {"number": 6, "x": 998, "y": 728}, {"number": 7, "x": 612, "y": 306}, {"number": 8, "x": 745, "y": 737}, {"number": 9, "x": 498, "y": 748}, {"number": 10, "x": 236, "y": 711}],
        "29": [{"number": 1, "x": 1892, "y": 306}, {"number": 2, "x": 1303, "y": 213}, {"number": 3, "x": 964, "y": 196}, {"number": 4, "x": 367, "y": 241}, {"number": 5, "x": 947, "y": 411}, {"number": 6, "x": 1325, "y": 422}, {"number": 7, "x": 2039, "y": 697}, {"number": 8, "x": 1661, "y": 686}, {"number": 9, "x": 1306, "y": 683}, {"number": 10, "x": 967, "y": 669}, {"number": 11, "x": 586, "y": 672}, {"number": 12, "x": 307, "y": 677}],
        "30": [{"number": 1, "x": 1971, "y": 371}, {"number": 2, "x": 1112, "y": 420}, {"number": 3, "x": 319, "y": 431}]
    }
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מערכת מספור תמונות חתונה</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            direction: rtl;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 { font-size: 32px; margin-bottom: 10px; font-weight: 700; }
        .header p { font-size: 16px; opacity: 0.95; }
        .content { padding: 40px 30px; }
        .section { margin-bottom: 40px; }
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .design-option {
            padding: 20px;
            border: 3px solid #667eea;
            border-radius: 10px;
            text-align: center;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .design-option-number { font-size: 28px; font-weight: 700; color: #667eea; margin-bottom: 8px; }
        .file-upload-section {
            background: #f9f9f9;
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 40px 20px;
            text-align: center;
        }
        .file-input-wrapper input[type="file"] { display: none; }
        .upload-btn {
            display: inline-block;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px 0;
        }
        .upload-btn:hover { background: #5568d3; transform: translateY(-2px); }
        .upload-text { color: #666; font-size: 14px; margin-top: 10px; }
        .process-btn {
            padding: 15px 40px;
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
        }
        .process-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(72, 187, 120, 0.4); }
        .process-btn:disabled { background: #cbd5e0; cursor: not-allowed; }
        .progress { display: none; text-align: center; margin: 20px 0; }
        .progress.active { display: block; }
        .progress-bar { width: 100%; height: 6px; background: #e0e0e0; border-radius: 3px; margin-top: 10px; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #667eea 0%, #48bb78 100%); width: 0%; transition: width 0.3s; }
        .footer { background: #f9f9f9; padding: 20px 30px; text-align: center; color: #666; font-size: 13px; }
        .error-msg { color: #dc2626; padding: 10px; background: #fef2f2; border-radius: 6px; margin-bottom: 10px; display: none; }
        .error-msg.show { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📸 מערכת מספור תמונות חתונה</h1>
            <p>הוסף מספרים אוטומטיים לתמונות בהתאם לעיצוב הנבחר</p>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title">🎨 סוג עיצוב</div>
                <div class="design-option">
                    <div class="design-option-number">2</div>
                    <div>עיצוב מספר 2</div>
                </div>
            </div>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="section">
                    <div class="section-title">📁 העלה את ה-PDF</div>
                    <div class="error-msg" id="errorMsg"></div>
                    <div class="file-upload-section">
                        <div class="file-input-wrapper">
                            <input type="file" id="pdfFile" name="pdf" accept=".pdf" required>
                            <label for="pdfFile" class="upload-btn">📂 בחר קובץ PDF</label>
                        </div>
                        <div class="upload-text">או גרור קובץ PDF לכאן</div>
                    </div>
                </div>
                
                <input type="hidden" name="design" value="2">
                
                <div class="progress" id="progress">
                    <div>עיבוד...</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                </div>
                
                <button type="submit" class="process-btn" id="processBtn">
                    ✨ הוסף מספרים והורד PDF
                </button>
            </form>
        </div>
        
        <div class="footer">
            <p>💡 בחר עיצוב, העלה PDF, וקבל את התוצאה עם מספרים על כל תמונה</p>
        </div>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData();
            const file = document.getElementById('pdfFile').files[0];
            formData.append('pdf', file);
            formData.append('design', '2');
            
            document.getElementById('progress').classList.add('active');
            document.getElementById('processBtn').disabled = true;
            document.getElementById('errorMsg').classList.remove('show');
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'wedding_numbered.pdf';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                } else {
                    const error = await response.json();
                    showError(error.error || 'שגיאה בעיבוד PDF');
                }
            } catch (error) {
                showError('שגיאה בשרתון: ' + error.message);
            } finally {
                document.getElementById('progress').classList.remove('active');
                document.getElementById('processBtn').disabled = false;
            }
        });
        
        function showError(msg) {
            const errorEl = document.getElementById('errorMsg');
            errorEl.textContent = msg;
            errorEl.classList.add('show');
        }
        
        // Drag and drop
        const uploadSection = document.querySelector('.file-upload-section');
        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadSection.style.borderColor = '#48bb78';
            uploadSection.style.background = '#f0fdf4';
        });
        uploadSection.addEventListener('dragleave', () => {
            uploadSection.style.borderColor = '#667eea';
            uploadSection.style.background = '#f9f9f9';
        });
        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadSection.style.borderColor = '#667eea';
            uploadSection.style.background = '#f9f9f9';
            if (e.dataTransfer.files.length > 0) {
                document.getElementById('pdfFile').files = e.dataTransfer.files;
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['pdf']
        design = request.form.get('design', '2')
        
        if not file or file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Read PDF
        file_content = file.read()
        pdf_reader = PdfReader(io.BytesIO(file_content))
        pdf_writer = PdfWriter()
        
        coordinates = DESIGN_COORDINATES.get(design, {})
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_key = str(page_num + 1)
            
            # Add numbers to page if coordinates exist
            if page_key in coordinates:
                # Create overlay with numbers
                overlay_buffer = io.BytesIO()
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                c = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))
                
                for coord in coordinates[page_key]:
                    x = coord['x']
                    y = page_height - coord['y']
                    number = str(coord['number'])
                    
                    # Draw circle background
                    c.setLineWidth(0)
                    c.setFillColor(black)
                    c.circle(x, y, 25, fill=1)
                    
                    # Draw white number
                    c.setFillColor(white)
                    c.setFont("Helvetica-Bold", 20)
                    c.drawCentredString(x, y - 6, number)
                
                c.save()
                overlay_buffer.seek(0)
                
                # Merge overlay with page
                overlay_pdf = PdfReader(overlay_buffer)
                overlay_page = overlay_pdf.pages[0]
                page.merge_page(overlay_page)
            
            pdf_writer.add_page(page)
        
        # Return PDF
        output_buffer = io.BytesIO()
        pdf_writer.write(output_buffer)
        output_buffer.seek(0)
        
        return send_file(
            output_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='wedding_numbered.pdf'
        )
    
    except Exception as e:
        import traceback
        app.logger.error(f"Error processing PDF: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
