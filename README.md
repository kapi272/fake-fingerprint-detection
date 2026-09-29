# Fake Fingerprint Detection

Flask web application for classifying fingerprint images as **Live** or **Fake**. The project uses Ultralytics YOLO models to detect presentation attacks such as printed and replayed fingerprints.

## Features

- Upload fingerprint images through a browser interface.
- Classify images as `Live` or `Fake` with confidence scores.
- Display original and processed inference results.
- Provide authentication, analytics, and model-performance pages.
- Prepare source images arranged as `Real`, `Print`, and `Replay` folders for training.

## Repository Structure

```text
.
├── fingerprint-liveness/          # Flask application, models, and dataset
├── archive_finger_prints/         # Original fingerprint image archive
└── Six-File+Context+Methodology/  # AI development methodology and templates
```

The application documentation is available in [fingerprint-liveness/README.md](fingerprint-liveness/README.md).

## Quick Start

### 1. Create a virtual environment

```bash
cd fingerprint-liveness
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the application

```bash
python app.py
```

Open the local URL printed by Flask in your browser.

## Dataset Preparation

The source archive uses `Real`, `Print`, and `Replay` categories. To create the YOLO classification layout used by the application:

```bash
python prepare_dataset.py
```

This maps `Real` images to `Live` and both `Print` and `Replay` images to `Fake`.

## Docker

Build and run the application from the application directory:

```bash
docker build -t fake-fingerprint-detection .
docker run --rm -p 5000:5000 fake-fingerprint-detection
```

## Models

The repository includes the runtime model and YOLO checkpoints used for inference and training. See the application README for training commands, configuration details, and troubleshooting guidance.

## License

No license has been specified for this repository.
