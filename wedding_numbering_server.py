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
        "1": [{"number": 1, "x": 2602.67, "y": 493.67}, {"number": 2, "x": 829.67, "y": 514.67}],
        "2": [{"number": 1, "x": 2988, "y": 779}, {"number": 2, "x": 2335, "y": 358}, {"number": 3, "x": 2349, "y": 788}, {"number": 4, "x": 2353, "y": 1107}, {"number": 5, "x": 1916, "y": 179}, {"number": 6, "x": 1916, "y": 494}, {"number": 7, "x": 1903, "y": 991}, {"number": 8, "x": 1480.33, "y": 207}, {"number": 9, "x": 1468.33, "y": 600}, {"number": 10, "x": 628, "y": 555}],
        "3": [{"number": 1, "x": 2995, "y": 602}, {"number": 2, "x": 2205, "y": 258}, {"number": 3, "x": 2229, "y": 680}, {"number": 4, "x": 2195, "y": 1050}, {"number": 5, "x": 1575, "y": 652}, {"number": 6, "x": 995, "y": 236}, {"number": 7, "x": 983, "y": 638}, {"number": 8, "x": 995, "y": 1044}, {"number": 9, "x": 371, "y": 608}],
        "4": [{"number": 1, "x": 2943, "y": 562}, {"number": 2, "x": 2081, "y": 396}, {"number": 3, "x": 2109, "y": 924}, {"number": 4, "x": 1199, "y": 606}, {"number": 5, "x": 299, "y": 242}, {"number": 6, "x": 337, "y": 1030}, {"number": 7, "x": 341, "y": 622}],
        "5": [{"number": 1, "x": 2619, "y": 614}, {"number": 2, "x": 1437, "y": 230}, {"number": 3, "x": 963, "y": 208}, {"number": 4, "x": 1139, "y": 618}, {"number": 5, "x": 1411, "y": 1078}, {"number": 6, "x": 971, "y": 1106}, {"number": 7, "x": 403, "y": 624}],
        "6": [{"number": 1, "x": 3093, "y": 632}, {"number": 2, "x": 2513, "y": 620}, {"number": 3, "x": 1949, "y": 640}, {"number": 4, "x": 1443, "y": 638}, {"number": 5, "x": 909, "y": 646}, {"number": 6, "x": 339, "y": 632}],
        "7": [{"number": 1, "x": 3195, "y": 304}, {"number": 2, "x": 3189, "y": 902}, {"number": 3, "x": 2717, "y": 636}, {"number": 4, "x": 2075, "y": 476}, {"number": 5, "x": 2079, "y": 928}, {"number": 6, "x": 1471, "y": 646}, {"number": 7, "x": 563, "y": 674}],
        "8": [{"number": 1, "x": 3033, "y": 614}, {"number": 2, "x": 2533, "y": 214}, {"number": 3, "x": 2535, "y": 1064}, {"number": 4, "x": 1135, "y": 652}, {"number": 5, "x": 283, "y": 656}],
        "9": [{"number": 1, "x": 2541, "y": 404}, {"number": 2, "x": 3057, "y": 1028}, {"number": 3, "x": 2473, "y": 1080}, {"number": 4, "x": 1311, "y": 666}, {"number": 5, "x": 585, "y": 432}, {"number": 6, "x": 863, "y": 1036}, {"number": 7, "x": 289, "y": 1056}, {"number": 8, "x": 1973, "y": 1088}],
        "10": [{"number": 1, "x": 3077, "y": 598}, {"number": 2, "x": 2381, "y": 420}, {"number": 3, "x": 2529, "y": 1024}, {"number": 4, "x": 2041, "y": 1056}, {"number": 5, "x": 1559, "y": 924}, {"number": 6, "x": 1193, "y": 626}, {"number": 7, "x": 835, "y": 414}, {"number": 8, "x": 779, "y": 932}, {"number": 9, "x": 385, "y": 586}],
        "11": [{"number": 1, "x": 2901, "y": 342}, {"number": 2, "x": 3051, "y": 958}, {"number": 3, "x": 1983, "y": 686}, {"number": 4, "x": 1481, "y": 702}, {"number": 5, "x": 959, "y": 690}, {"number": 6, "x": 345, "y": 702}],
        "12": [{"number": 1, "x": 2935, "y": 326}, {"number": 2, "x": 3001, "y": 952}, {"number": 3, "x": 1951, "y": 494}, {"number": 4, "x": 2275, "y": 1110}, {"number": 5, "x": 1931, "y": 1126}, {"number": 6, "x": 1577, "y": 1108}, {"number": 7, "x": 1067, "y": 1110}, {"number": 8, "x": 483, "y": 406}, {"number": 9, "x": 463, "y": 1000}],
        "13": [{"number": 1, "x": 3107, "y": 356}, {"number": 2, "x": 3119, "y": 876}, {"number": 3, "x": 1613, "y": 676}, {"number": 4, "x": 315, "y": 356}, {"number": 5, "x": 299, "y": 864}],
        "14": [{"number": 1, "x": 3155, "y": 312}, {"number": 2, "x": 3155, "y": 858}, {"number": 3, "x": 1317, "y": 290}, {"number": 4, "x": 1277, "y": 732}, {"number": 5, "x": 977, "y": 1090}, {"number": 6, "x": 1015, "y": 434}, {"number": 7, "x": 655, "y": 970}, {"number": 8, "x": 299, "y": 508}, {"number": 9, "x": 583, "y": 208}],
        "15": [{"number": 1, "x": 3091, "y": 354}, {"number": 2, "x": 2907, "y": 928}, {"number": 3, "x": 2369, "y": 646}, {"number": 4, "x": 1611, "y": 672}, {"number": 5, "x": 1031, "y": 372}, {"number": 6, "x": 1045, "y": 996}, {"number": 7, "x": 325, "y": 660}, {"number": 8, "x": 593, "y": 382}, {"number": 9, "x": 613, "y": 1012}],
        "16": [{"number": 1, "x": 1629, "y": 622}, {"number": 2, "x": 1075, "y": 652}, {"number": 3, "x": 563, "y": 286}, {"number": 4, "x": 567, "y": 1030}],
        "17": [{"number": 1, "x": 3185, "y": 258}, {"number": 2, "x": 3201, "y": 732}, {"number": 3, "x": 3193, "y": 1100}, {"number": 4, "x": 2649, "y": 304}, {"number": 5, "x": 2665, "y": 892}, {"number": 6, "x": 2709, "y": 1082}, {"number": 7, "x": 2073, "y": 404}, {"number": 8, "x": 2055, "y": 964}, {"number": 9, "x": 2103, "y": 1104}, {"number": 10, "x": 1471, "y": 214}, {"number": 11, "x": 1463, "y": 860}, {"number": 12, "x": 1461, "y": 1080}, {"number": 13, "x": 879, "y": 314}, {"number": 14, "x": 877, "y": 968}, {"number": 15, "x": 875, "y": 1102}, {"number": 16, "x": 425, "y": 210}, {"number": 17, "x": 415, "y": 858}, {"number": 18, "x": 423, "y": 1072}, {"number": 19, "x": 1473, "y": 636}],
        "18": [{"number": 1, "x": 3109, "y": 402}, {"number": 2, "x": 3119, "y": 932}, {"number": 3, "x": 2357, "y": 428}, {"number": 4, "x": 2341, "y": 1040}, {"number": 5, "x": 1733, "y": 636}, {"number": 6, "x": 1099, "y": 402}, {"number": 7, "x": 1087, "y": 996}, {"number": 8, "x": 379, "y": 422}, {"number": 9, "x": 369, "y": 996}, {"number": 10, "x": 793, "y": 626}],
        "19": [{"number": 1, "x": 2851, "y": 524}, {"number": 2, "x": 3029, "y": 992}, {"number": 3, "x": 2373, "y": 400}, {"number": 4, "x": 2373, "y": 1056}, {"number": 5, "x": 1767, "y": 650}, {"number": 6, "x": 1113, "y": 424}, {"number": 7, "x": 1113, "y": 1050}],
        "20": [{"number": 1, "x": 2847, "y": 680}, {"number": 2, "x": 2963, "y": 374}, {"number": 3, "x": 2979, "y": 1014}, {"number": 4, "x": 2111, "y": 598}, {"number": 5, "x": 1659, "y": 676}, {"number": 6, "x": 1283, "y": 350}, {"number": 7, "x": 1161, "y": 816}, {"number": 8, "x": 1139, "y": 1080}, {"number": 9, "x": 613, "y": 674}, {"number": 10, "x": 619, "y": 1020}, {"number": 11, "x": 477, "y": 330}, {"number": 12, "x": 477, "y": 948}, {"number": 13, "x": 549, "y": 498}, {"number": 14, "x": 333, "y": 668}],
        "21": [{"number": 1, "x": 2917, "y": 398}, {"number": 2, "x": 3021, "y": 962}, {"number": 3, "x": 2329, "y": 254}, {"number": 4, "x": 2501, "y": 1004}, {"number": 5, "x": 1983, "y": 262}, {"number": 6, "x": 1975, "y": 834}, {"number": 7, "x": 1539, "y": 500}, {"number": 8, "x": 1417, "y": 1008}, {"number": 9, "x": 849, "y": 602}],
        "22": [{"number": 1, "x": 2887, "y": 346}, {"number": 2, "x": 3049, "y": 952}, {"number": 3, "x": 2265, "y": 220}, {"number": 4, "x": 2293, "y": 500}, {"number": 5, "x": 2259, "y": 816}, {"number": 6, "x": 1897, "y": 310}, {"number": 7, "x": 1233, "y": 394}, {"number": 8, "x": 1219, "y": 872}, {"number": 9, "x": 485, "y": 292}, {"number": 10, "x": 583, "y": 794}, {"number": 11, "x": 595, "y": 1108}, {"number": 12, "x": 261, "y": 926}],
        "23": [{"number": 1, "x": 2775, "y": 512}, {"number": 2, "x": 1859, "y": 214}, {"number": 3, "x": 1833, "y": 612}, {"number": 4, "x": 1831, "y": 964}, {"number": 5, "x": 1361, "y": 438}, {"number": 6, "x": 1399, "y": 1062}, {"number": 7, "x": 955, "y": 1046}, {"number": 8, "x": 345, "y": 258}, {"number": 9, "x": 325, "y": 630}],
        "24": [{"number": 1, "x": 2955, "y": 474}, {"number": 2, "x": 1405, "y": 228}, {"number": 3, "x": 1923, "y": 276}, {"number": 4, "x": 1669, "y": 664}, {"number": 5, "x": 2285, "y": 674}, {"number": 6, "x": 2483, "y": 1016}, {"number": 7, "x": 1997, "y": 1010}, {"number": 8, "x": 835, "y": 588}],
        "25": [{"number": 1, "x": 2835, "y": 562}, {"number": 2, "x": 1907, "y": 252}, {"number": 3, "x": 1355, "y": 226}, {"number": 4, "x": 941, "y": 236}, {"number": 5, "x": 1007, "y": 552}, {"number": 6, "x": 1607, "y": 618}, {"number": 7, "x": 2303, "y": 628}, {"number": 8, "x": 2413, "y": 1004}, {"number": 9, "x": 1799, "y": 1014}, {"number": 10, "x": 1277, "y": 1026}, {"number": 11, "x": 393, "y": 630}],
        "26": [{"number": 1, "x": 3049, "y": 208}, {"number": 2, "x": 3043, "y": 666}, {"number": 3, "x": 2751, "y": 1126}, {"number": 4, "x": 2669, "y": 228}, {"number": 5, "x": 1803, "y": 382}, {"number": 6, "x": 753, "y": 250}, {"number": 7, "x": 2181, "y": 1088}, {"number": 8, "x": 1715, "y": 1088}, {"number": 9, "x": 1223, "y": 1104}, {"number": 10, "x": 3111, "y": 1086}, {"number": 11, "x": 283, "y": 210}, {"number": 12, "x": 503, "y": 656}, {"number": 13, "x": 705, "y": 1100}, {"number": 14, "x": 249, "y": 1116}],
        "27": [{"number": 1, "x": 3145, "y": 256}, {"number": 2, "x": 2905, "y": 744}, {"number": 3, "x": 3167, "y": 1086}, {"number": 4, "x": 2805, "y": 1122}, {"number": 5, "x": 2425, "y": 652}, {"number": 6, "x": 2323, "y": 1002}, {"number": 7, "x": 2251, "y": 280}, {"number": 8, "x": 1105, "y": 444}, {"number": 9, "x": 1713, "y": 1052}, {"number": 10, "x": 1247, "y": 1096}, {"number": 11, "x": 759, "y": 1064}, {"number": 12, "x": 295, "y": 1082}],
        "28": [{"number": 1, "x": 1469, "y": 394}, {"number": 2, "x": 3097, "y": 1050}, {"number": 3, "x": 2625, "y": 1116}, {"number": 4, "x": 2249, "y": 1132}, {"number": 5, "x": 1887, "y": 1102}, {"number": 6, "x": 1503, "y": 1090}, {"number": 7, "x": 1151, "y": 1104}, {"number": 8, "x": 823, "y": 1116}, {"number": 9, "x": 335, "y": 1076}],
        "29": [{"number": 1, "x": 2727, "y": 490}, {"number": 2, "x": 3069, "y": 962}, {"number": 3, "x": 2547, "y": 1048}, {"number": 4, "x": 1971, "y": 262}, {"number": 5, "x": 1981, "y": 576}, {"number": 6, "x": 1975, "y": 908}, {"number": 7, "x": 1391, "y": 262}, {"number": 8, "x": 1483, "y": 626}, {"number": 9, "x": 1435, "y": 984}, {"number": 10, "x": 593, "y": 428}, {"number": 11, "x": 883, "y": 1016}, {"number": 12, "x": 377, "y": 1030}],
        "30": [{"number": 1, "x": 2803, "y": 488}, {"number": 2, "x": 1691, "y": 590}, {"number": 3, "x": 497, "y": 554}]
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
