import os
from flask import Flask, render_template, request, send_file, url_for
import qrcode
import cv2
from pyzbar.pyzbar import decode
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/qr_codes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    qr_path = None
    scanned_data = None
    qr_generated = False

    if request.method == 'POST':
        if 'generate' in request.form:
            data = request.form['data']
            qr_type = request.form['type']
            final_data = generate_qr_data(data, qr_type)

            img = qrcode.make(final_data)
            filename = "generated_qr.png"
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img.save(path)

            qr_path = url_for('static', filename=f'qr_codes/{filename}')
            qr_generated = True

        elif 'scan' in request.form:
            file = request.files['qr_image']
            if file:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
                file.save(filepath)
                scanned_data = scan_qr(filepath)

        elif 'scan_generated' in request.form:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], "generated_qr.png")
            scanned_data = scan_qr(filepath)
            qr_path = url_for('static', filename='qr_codes/generated_qr.png')
            qr_generated = True

    return render_template('index.html', qr_path=qr_path, scanned_data=scanned_data, qr_generated=qr_generated)

def scan_qr(filepath):
    try:
        img = cv2.imread(filepath)
        decoded = decode(img)
        if decoded:
            return decoded[0].data.decode('utf-8')
        return "No QR code detected."
    except Exception as e:
        return f"Error: {str(e)}"

def generate_qr_data(data, qr_type):
    if qr_type == "url":
        return data if data.startswith("http") else f"http://{data}"
    elif qr_type == "email":
        return f"mailto:{data}"
    elif qr_type == "phone":
        return f"tel:{data}"
    elif qr_type == "wifi":
        try:
            ssid, password = data.split(',')
            return f"WIFI:T:WPA;S:{ssid};P:{password};;"
        except ValueError:
            return data
    else:
        return data

@app.route('/download_qr')
def download_qr():
    path = os.path.join(app.config['UPLOAD_FOLDER'], "generated_qr.png")
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
