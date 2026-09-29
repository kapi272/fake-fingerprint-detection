from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from ultralytics.models.yolo.classify.predict import ClassificationPredictor
from PIL import Image
import torch
import os
import uuid

app = Flask(__name__)
app.secret_key = 'secretkey'

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['RESULT_FOLDER'] = os.path.join('static', 'results')


# Ultralytics 8.0.200 supplies NumPy arrays to a torchvision transform that now
# expects PIL images. Convert the classifier's BGR arrays at that boundary.
original_classification_preprocess = ClassificationPredictor.preprocess


def preprocess_classification(self, images):
    if not isinstance(images, torch.Tensor):
        images = [
            Image.fromarray(image[:, :, ::-1].copy())
            for image in images
        ]
    return original_classification_preprocess(self, images)


ClassificationPredictor.preprocess = preprocess_classification

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
            else:
                flash("Model not loaded. Cannot perform inference.", "danger")
            
            return render_template("index.html", 
                                   uploaded=True,
                                   original=url_for('static', filename='uploads/' + filename),
                                   result=result_image_path,
                                   predictions=parsed_preds)
                                   
    return render_template("index.html", uploaded=False)

@app.route('/charts')
def charts():
    if 'user' not in session:
        flash("Please login", "warning")
        return redirect(url_for('login'))
    return render_template('charts.html')

@app.route('/performance')
def performance():
    if 'user' not in session:
        flash("Please login", "warning")
        return redirect(url_for('login'))
    return render_template('performance.html')

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', '').lower() == 'true',
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', '5000')),
    )
