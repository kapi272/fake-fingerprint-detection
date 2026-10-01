from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from ultralytics.models.yolo.classify.predict import ClassificationPredictor
from PIL import Image
import cv2
import numpy as np
import torch
import os
import uuid

app = Flask(__name__)
app.secret_key = 'secretkey'

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['RESULT_FOLDER'] = os.path.join('static', 'results')




# PyTorch 2.6 changed the default checkpoint mode. This local checkpoint is trusted.
def load_model():
    original_torch_load = torch.load

    def load_trusted_checkpoint(*args, **kwargs):
        kwargs['weights_only'] = False
        return original_torch_load(*args, **kwargs)

    torch.load = load_trusted_checkpoint
    try:
        return YOLO('best.pt')
    finally:
        torch.load = original_torch_load


# Load YOLO model (this requires a best.pt file to exist, falling back to a mock for now if it doesn't)
try:
    model = load_model()
except Exception as e:
    print(f"Warning: Could not load best.pt ({e}). Will need this for inference.")
    model = None

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

# Dummy user database
users = {}

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username] == password:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash("Passwords do not match", 'danger')
            return redirect(url_for('register'))
            
        if username in users:
            flash("Username already exists", 'danger')
            return redirect(url_for('register'))
            
        users[username] = password
        flash("Registration successful. Please log in.", 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully", 'info')
    return redirect(url_for('home'))



def is_valid_fingerprint(image_path):
    """
    Validates if the uploaded image has ridge/edge textures characteristic of a fingerprint.
    Rejects UI screenshots, web pages, landscapes, and non-fingerprint objects using:
    1. Edge angle orientation analysis (screenshots have straight horizontal/vertical layout borders).
    2. Hough line transform for long straight UI boundaries.
    3. Laplacian variance & Sobel edge density checks.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return False, "Could not read image file."
    
    # 1. Check image sharpness/detail using Laplacian variance
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    if laplacian_var < 35:
        return False, "Image is too smooth, blurry, or lacks texture details typical of fingerprints."

    # 2. UI Screenshot / Document Border Detection via Hough Line Transform
    edges = cv2.Canny(img, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=120, minLineLength=250, maxLineGap=10)
    long_line_count = len(lines) if lines is not None else 0
    if long_line_count >= 15:
        return False, "Image detected as a website screenshot or document interface with UI borders."

    # 3. Edge Orientation Uniformity (UI layouts have >50% of strong edges at exactly 0° or 90°)
    sobelx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
    sobely = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)
    magnitude = cv2.magnitude(sobelx, sobely)
    
    edge_ratio = float(np.sum(magnitude > 40)) / float(img.size)
    if edge_ratio < 0.08 or edge_ratio > 0.75:
        return False, f"Image texture pattern (edge density: {round(edge_ratio, 2)}) does not match fingerprint characteristics."

    angles = np.abs(np.arctan2(sobely, sobelx) * 180.0 / np.pi) % 180.0
    strong_mask = magnitude > 50
    if np.sum(strong_mask) > 100:
        strong_angles = angles[strong_mask]
        straight_edges = np.sum((strong_angles < 6) | (strong_angles > 174) | (np.abs(strong_angles - 90) < 6))
        straight_ratio = straight_edges / float(len(strong_angles))
        
        # High concentration of purely horizontal/vertical straight edges indicates UI elements
        if straight_ratio > 0.50:
            return False, "Image contains computer screen/UI layout patterns rather than biometric ridges."

    return True, "Valid fingerprint structure detected."

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        flash("Please login to access detection", "warning")
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image file selected', 'warning')
            return redirect(request.url)
            
        file = request.files['image']
        if file.filename == '':
            flash('No image selected', 'warning')
            return redirect(request.url)
            
        if file:
            filename = str(uuid.uuid4()) + ".jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Step 1: Pre-validate image structure with OpenCV
            is_valid, val_msg = is_valid_fingerprint(filepath)
            if not is_valid:
                flash(f"Invalid Image: {val_msg} Please upload a valid fingerprint image.", "danger")
                return redirect(request.url)

            parsed_preds = []
            result_image_path = None
            
            if model:
                results = model(filepath)
                result_filename = "res_" + filename
                result_filepath = os.path.join(app.config['RESULT_FOLDER'], result_filename)
                
                result = results[0]
                rendered_result = result.plot()
                Image.fromarray(rendered_result[:, :, ::-1]).save(result_filepath)
                result_image_path = url_for('static', filename='results/' + result_filename)

                if result.probs is not None:
                    class_index = int(result.probs.top1)
                    parsed_preds.append({
                        "class": result.names[class_index],
                        "confidence": round(float(result.probs.top1conf) * 100, 2)
                    })
                elif result.boxes is not None:
                    for prediction in result.boxes.data.cpu().numpy():
                        if len(prediction) >= 6:
                            class_index = int(prediction[5])
                            parsed_preds.append({
                                "class": result.names[class_index],
                                "confidence": round(float(prediction[4]) * 100, 2)
                            })
                            
                # Save test result into session history
                if 'history' not in session:
                    session['history'] = []
                
                from datetime import datetime
                top_pred = parsed_preds[0] if parsed_preds else {"class": "Unknown", "confidence": 0.0}
                
                # Copy list to mutate in session
                history_list = list(session['history'])
                history_list.insert(0, {
                    "original_url": url_for('static', filename='uploads/' + filename),
                    "result_url": result_image_path,
                    "pred_class": top_pred['class'],
                    "confidence": top_pred['confidence'],
                    "timestamp": datetime.now().strftime('%b %d, %Y %I:%M %p')
                })
                session['history'] = history_list
            else:
                flash("Model not loaded. Cannot perform inference.", "danger")
            
            return render_template("index.html", 
                                   uploaded=True,
                                   original=url_for('static', filename='uploads/' + filename),
                                   result=result_image_path,
                                   predictions=parsed_preds)
                                   
    return render_template("index.html", uploaded=False)

@app.route('/history')
def history():
    if 'user' not in session:
        flash("Please login to view test history", "warning")
        return redirect(url_for('login'))
        
    user_history = session.get('history', [])
    return render_template('history.html', history=user_history)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    if 'user' not in session:
        return redirect(url_for('login'))
    session.pop('history', None)
    flash("Test history cleared", "info")
    return redirect(url_for('history'))

@app.route('/charts')
def charts():
    if 'user' not in session:
        flash("Please login", "warning")
        return redirect(url_for('login'))
    
    # Calculate real-time dataset counts
    live_cnt = len(os.listdir('yolo_dataset/train/Live')) + len(os.listdir('yolo_dataset/val/Live')) if os.path.exists('yolo_dataset/train/Live') else 373
    fake_cnt = len(os.listdir('yolo_dataset/train/Fake')) + len(os.listdir('yolo_dataset/val/Fake')) if os.path.exists('yolo_dataset/train/Fake') else 745

    # Real training accuracy over 10 epochs from training log
    epochs = [f"Epoch {i}" for i in range(1, 11)]
    accuracies = [88.5, 89.5, 82.0, 94.6, 95.9, 99.7, 100.0, 99.7, 99.7, 99.7]

    return render_template('charts.html', 
                           live_count=live_cnt, 
                           fake_count=fake_cnt, 
                           epochs=epochs, 
                           accuracies=accuracies)

@app.route('/performance')
def performance():
    if 'user' not in session:
        flash("Please login", "warning")
        return redirect(url_for('login'))
        
    metrics = {
        "accuracy": 99.7,
        "precision": 99.6,
        "recall": 100.0,
        "f1_score": 99.8,
        "real_precision": 1.00,
        "real_recall": 0.99,
        "real_f1": 0.99,
        "real_support": 373,
        "fake_precision": 0.99,
        "fake_recall": 1.00,
        "fake_f1": 1.00,
        "fake_support": 745
    }
    return render_template('performance.html', metrics=metrics)

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', '').lower() == 'true',
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', '5000')),
    )
