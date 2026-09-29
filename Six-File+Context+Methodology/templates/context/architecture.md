# System Architecture Context

## Technical Stack

| Layer | Technology | Version / Tool | Role in Project |
| :--- | :--- | :--- | :--- |
| **Web Framework** | Python / Flask | Flask 3.x | HTTP route handling, session authentication, request parsing, Jinja2 template rendering[cite: 1]. |
| **Deep Learning Engine** | Ultralytics YOLO | YOLOv8n (`best.pt`) | Object detection backbone, feature extraction, decoupled head liveness classification[cite: 1]. |
| **Numeric & Vision Operations** | NumPy / OpenCV | PyTorch / Python | Coordinate array transformation, confidence score calculation, tensor manipulation[cite: 1]. |
| **Front-End Interface** | HTML5 / CSS3 / Jinja2 | Standard CSS | Web user interface rendering, side-by-side image comparison, dynamic result display[cite: 1]. |
| **Artifact Storage** | File System Storage | Native Operating System | Local disk storage for raw user uploads and model output result images[cite: 1]. |

## Directory & Subsystem Boundaries

fingerprint-liveness/
│
├── app.py
├── requirements.txt
├── best.pt
│
├── models/
│   └── model.py
│
├── preprocessing/
│   └── preprocess.py
│
├── detection/
│   └── detector.py
│
├── evaluation/
│   └── metrics.py
│
├── static/
│   ├── css/
│   ├── js/
│   ├── uploads/
│   └── results/
│
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── detection.html
│   ├── charts.html
│   └── performance.html
│
├── dataset/
│   ├── train/
│   ├── val/
│   └── test/
│
└── README.md