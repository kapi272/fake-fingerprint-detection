# Fingerprint Liveness Detection

Fingerprint Liveness Detection is a Flask web application for identifying whether an uploaded fingerprint image is **Live** (genuine) or a presentation attack (**Fake** / spoofed). The project utilizes Ultralytics YOLOv8 classification models combined with OpenCV Computer Vision pre-validation filter rules, providing a complete web interface for authentication, image evaluation, test history, dynamic analytics, and performance metrics.

---

## Features

- **OpenCV Fingerprint Pre-Validation**: Automatically inspects images before AI model inference. Rejects non-fingerprint uploads, blurry photos, and UI/browser screenshots using Laplacian variance, Hough line transform, and edge orientation angle analysis.
- **YOLOv8 AI Classifier**: Real-time classification (`Live` vs `Fake`) with confidence scoring.
- **Interactive History Dashboard**: Tracks all valid fingerprint test runs with timestamped original uploads, annotated YOLO outputs, predicted labels, and confidence metrics.
- **Dynamic Analytics & Charts**: Real-time dataset distribution breakdown (Pie chart) and epoch-by-epoch accuracy curve (Line chart) rendered via Chart.js.
- **Performance Evaluation**: Displays actual model accuracy (99.7%), precision, recall, F1-score, and per-class evaluation metrics.
- **User Authentication**: Flask session management with login, registration, and session logout capabilities.

---

## Technology Stack

### Backend & Machine Learning
- **Python**: Core development language.
- **Flask 3.0.0**: Web framework for routing, templates, sessions, and alerts.
- **Ultralytics 8.0.200**: YOLOv8 nano classification model loader, trainer, and predictor.
- **OpenCV (opencv-python-headless)**: Edge density, Hough line transform, and gradient orientation analysis.
- **PyTorch**: Deep learning backend framework.
- **Pandas & NumPy**: Data processing and statistical analysis.

### Frontend
- **Jinja2**: Dynamic HTML templating.
- **Bootstrap 5.3.2**: Dark-themed responsive UI design.
- **Chart.js**: Frontend chart visualizations.
- **Google Fonts (Inter)**: Clean modern typography.

---

## Project Structure

```text
fingerprint-liveness/
├── app.py                         # Flask application, OpenCV filter & routes
├── prepare_dataset.py             # Prepares & merges datasets into YOLO layout
├── requirements.txt               # Updated project dependencies
├── best.pt                        # Trained YOLO model weights used by Flask
├── yolov8n-cls.pt                 # Pretrained YOLOv8 classification model
├── yolo_dataset/
│   ├── train/
│   │   ├── Live/                  # Genuine fingerprint training images
│   │   └── Fake/                  # Spoofed fingerprint training images
│   └── val/
│       ├── Live/                  # Validation genuine fingerprints
│       └── Fake/                  # Validation spoofed fingerprints
├── runs/classify/train_new/       # Latest Ultralytics training logs & weights
├── static/
│   ├── css/style.css              # Custom styling tokens
│   ├── uploads/                   # Temporary user uploaded images
│   └── results/                   # Model annotated outputs
└── templates/
    ├── base.html                  # Main navigation layout
    ├── home.html                  # Landing page
    ├── index.html                 # Fingerprint detection interface
    ├── history.html               # Session test history timeline
    ├── charts.html                # Dataset & training accuracy charts
    ├── performance.html           # Model metrics & evaluation table
    ├── login.html                 # User login page
    └── register.html              # User registration page
```

---

## Application Routes

| Route | Purpose | Access |
|---|---|---|
| `/` or `/home` | Welcome & landing page | Public |
| `/register` | Register a user session | Public |
| `/login` | Authenticate user session | Public |
| `/logout` | End active session | Logged-in Users |
| `/index` | Upload and analyze fingerprint images | Logged-in Users |
| `/history` | View history of tested fingerprint runs | Logged-in Users |
| `/clear_history` | Clear test session history | Logged-in Users |
| `/charts` | View dynamic dataset & training curves | Logged-in Users |
| `/performance` | View model evaluation metrics | Logged-in Users |

---

## Requirements & Installation

### Requirements
- macOS, Linux, or Windows.
- Python 3.9+ installed.

### Clone and Setup Virtual Environment

```bash
git clone https://github.com/kapi272/fake-fingerprint-detection.git
cd fake-fingerprint-detection/fingerprint-liveness
```

Create and activate virtual environment:

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows PowerShell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install updated requirements:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

---

## Run the Application

```bash
python app.py
```

Open <http://127.0.0.1:5000> or <http://127.0.0.1:5001> in your browser, register/login, and start analyzing fingerprints!

---

## Dataset Preparation & Model Training

### Prepare Dataset
To process and split raw image directories into YOLO classification format (80% train / 20% validation):

```bash
python prepare_dataset.py
```

### Train YOLO Classifier Model
To retrain the model checkpoint:

```bash
python -c "
import torch
orig_load = torch.load
torch.load = lambda *a, **k: orig_load(*a, **{**k, 'weights_only': False})

from ultralytics import YOLO
model = YOLO('yolov8n-cls.pt')
model.train(data='yolo_dataset', epochs=10, imgsz=256, batch=16, project='runs/classify', name='train_new')
"
```

After training completes, update `best.pt`:

```bash
cp runs/classify/train_new/weights/best.pt best.pt
```