# Fingerprint Liveness Detection

Fingerprint Liveness Detection is a Flask web application for identifying whether an uploaded fingerprint image is **Live** or a presentation attack (**Fake**). The project uses Ultralytics YOLO models for computer-vision inference and provides a browser interface for registration, login, image upload, result visualization, analytics, and model-performance pages.

> This README describes the implementation currently present in this repository. It also documents the changes recommended before using a much larger benchmark such as LivDet 2021 in production or in a published experiment.

## Contents

- [Features](#features)
- [Technology stack](#technology-stack)
- [Project structure](#project-structure)
- [How the application works](#how-the-application-works)
- [Requirements](#requirements)
- [Clone and install](#clone-and-install)
- [Run the application](#run-the-application)
- [Run with Docker](#run-with-docker)
- [Prepare a dataset](#prepare-a-dataset)
- [Train a model](#train-a-model)
- [Large datasets and LivDet 2021](#large-datasets-and-livdet-2021)
- [Model and inference compatibility](#model-and-inference-compatibility)
- [Configuration and security notes](#configuration-and-security-notes)
- [Troubleshooting](#troubleshooting)
- [Future improvements](#future-improvements)

## Features

- Flask web interface with Bootstrap 5 styling.
- In-memory user registration, login, session handling, and logout.
- Upload of JPG, JPEG, and PNG fingerprint images.
- YOLO inference using a local `best.pt` model.
- Saving of uploaded files under `static/uploads/`.
- Saving of annotated inference output under `static/results/`.
- Display of the original image, processed image, predicted class, and confidence.
- Analytics and performance pages for presenting dataset and evaluation information.
- Dataset preparation script that maps:
  - `Real` to `Live`
  - `Print` and `Replay` to `Fake`

## Technology stack

### Backend and machine learning

- **Python**: application and dataset-preparation language.
- **Flask 3.0.0**: web server, routing, templates, sessions, and form handling.
- **Werkzeug 3.0.0**: Flask's request and file-upload support.
- **Ultralytics 8.0.200**: YOLO model loading, training, and inference.
- **OpenCV Headless 4.8.1.78**: computer-vision dependency used by the Ultralytics stack without requiring desktop GUI libraries.
- **PyTorch**: installed as part of the Ultralytics dependency chain and used to execute the neural network.

### Frontend

- **Jinja2 templates** through Flask.
- **Bootstrap 5.3.2** loaded from jsDelivr.
- **Chart.js** loaded from jsDelivr for charts.
- **Google Fonts Inter** loaded by the base template.
- Custom CSS in `static/css/style.css`.

### Models and training artifacts

- `yolov8n-cls.pt`: pretrained YOLOv8 nano classification checkpoint.
- `yolov8n.pt`: YOLOv8 nano checkpoint included in the project.
- `best.pt`: model loaded by the Flask application at startup.
- `runs/classify/train/`: recorded Ultralytics classification training output, including `args.yaml`, `results.csv`, and saved weights.

## Project structure

```text
fingerprint-liveness/
├── app.py                         # Flask application and inference route
├── prepare_dataset.py             # Converts phone-folder data to YOLO classification layout
├── requirements.txt               # Python dependencies
├── best.pt                        # Runtime model expected by app.py
├── yolov8n-cls.pt                 # Pretrained classification model
├── yolov8n.pt                     # YOLOv8 nano model
├── yolo_dataset/
│   ├── train/Live/                # Live training images
│   ├── train/Fake/                # Fake training images
│   ├── val/Live/                  # Live validation images
│   └── val/Fake/                  # Fake validation images
├── runs/classify/train/           # Training logs, plots, and weights
├── static/
│   ├── css/style.css
│   ├── uploads/                   # Uploaded input images
│   └── results/                   # Annotated model outputs
└── templates/                     # Flask/Jinja HTML pages
```

Large datasets should generally stay outside the Git repository. Keep only a small sample or an empty directory marker in `yolo_dataset/`, and document the dataset location in a manifest.

## How the application works

1. A user opens the home page and registers or logs in.
2. The protected Detection page accepts an image upload.
3. The server generates a UUID filename and stores the image in `static/uploads/`.
4. At startup, Flask attempts to load `best.pt` with Ultralytics.
5. The uploaded image is passed to the model.
6. The result image is written to `static/results/`.
7. The template displays the source image, annotated result, predicted class, and confidence.

The main routes are:

| Route | Purpose | Access |
|---|---|---|
| `/` or `/home` | Home page | Public |
| `/register` | Create an in-memory user | Public |
| `/login` | Start a session | Public |
| `/logout` | End a session | Logged-in users |
| `/index` | Upload and analyze a fingerprint | Logged-in users |
| `/charts` | Dataset and accuracy charts | Logged-in users |
| `/performance` | Model metrics page | Logged-in users |

## Requirements

- macOS, Linux, or Windows.
- Python 3.9 or newer recommended.
- `pip` and `venv`.
- Enough disk space for Python packages, model checkpoints, uploaded images, and training data.
- Optional: an NVIDIA GPU with a compatible CUDA/PyTorch installation for faster training and inference.

The exact pinned application dependencies are listed in [`requirements.txt`](requirements.txt).

## Clone and install

The current workspace does not contain a configured Git remote. Replace `<repository-url>` with the URL of the repository that contains this project.

```bash
git clone <repository-url>
cd fingerprint-liveness
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, use:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Upgrade packaging tools and install dependencies:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

Verify the installation:

```bash
python -c "import flask, cv2, ultralytics; print('Dependencies loaded successfully')"
```

## Run the application

From the `fingerprint-liveness` directory, with the virtual environment active:

```bash
python app.py
```

Open <http://127.0.0.1:5000> in a browser. Register a temporary user, log in, and upload a fingerprint image.

The app listens on port `5000` by default. Set `FLASK_DEBUG=true` only for local development; do not expose debug mode directly to the internet.

## Run with Docker

Docker packages the application and the dependencies in `requirements.txt` so it can be run on Windows, macOS, or Linux. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) on Windows or macOS, or install Docker Engine and Docker Compose on Linux.

From the `fingerprint-liveness` directory, build the image:

```bash
docker build -t fingerprint-liveness .
```

Start the application:

```bash
docker run --name fingerprint-liveness \
  -p 5000:5000 \
  -v "$(pwd)/static/uploads:/app/static/uploads" \
  -v "$(pwd)/static/results:/app/static/results" \
  fingerprint-liveness
```

Open <http://localhost:5000> in a browser. The volume mounts keep uploaded and processed images on the host after the container stops.

### Windows PowerShell

Run these commands from the project directory:

```powershell
docker build -t fingerprint-liveness .
docker run --name fingerprint-liveness `
  -p 5000:5000 `
  -v "${PWD}/static/uploads:/app/static/uploads" `
  -v "${PWD}/static/results:/app/static/results" `
  fingerprint-liveness
```

### Windows Command Prompt

```bat
docker build -t fingerprint-liveness .
docker run --name fingerprint-liveness -p 5000:5000 -v "%cd%\static\uploads:/app/static/uploads" -v "%cd%\static\results:/app/static/results" fingerprint-liveness
```

### macOS and Linux

Use the first `docker build` and `docker run` commands in this section. On Linux, if Docker requires it, add your user to the `docker` group or run Docker commands with the permissions configured by your distribution.

Useful commands:

```bash
docker ps
docker logs -f fingerprint-liveness
docker stop fingerprint-liveness
docker rm fingerprint-liveness
```

To run it again after stopping, use the same `docker run` command after removing the old container. The image includes `best.pt`; do not omit that file when copying the project to another computer.

## Prepare a dataset

The included `prepare_dataset.py` expects the source data to be arranged by device and capture type:

```text
archive_finger_prints/
├── iPhone 15 Pro/
│   ├── Print/
│   ├── Real/
│   └── Replay/
├── OPPO A18/
│   ├── Print/
│   ├── Real/
│   └── Replay/
└── Samsung Galaxy A53 5G/
    ├── Print/
    ├── Real/
    └── Replay/
```

Run it from the project directory:

```bash
python prepare_dataset.py
```

The script currently uses the absolute source path defined near the bottom of the file. Update `SOURCE_DIRECTORY` for another machine before running it. It shuffles each class, uses an 80/20 train/validation split, renames files to avoid collisions, and copies them into:

```text
yolo_dataset/
├── train/
│   ├── Live/
│   └── Fake/
└── val/
    ├── Live/
    └── Fake/
```

This is the directory format expected by YOLO classification training.

## Train a model

The recorded training run used `yolov8n-cls.pt`, 50 epochs, batch size 16, and 256px images. A comparable command is:

```bash
yolo classify train \
  model=yolov8n-cls.pt \
  data=yolo_dataset \
  epochs=50 \
  imgsz=256 \
  batch=16 \
  project=runs/classify \
  name=train
```

Ultralytics writes weights and metrics under the run directory. Copy the desired trained checkpoint to the location expected by the web app:

```bash
cp runs/classify/train/weights/best.pt best.pt
```

On Windows, copy the file with File Explorer or use `copy` in Command Prompt.

For a reproducible experiment, also record the dataset version, class counts, train/validation/test split, model version, image size, seed, hardware, and evaluation metrics.

## Large datasets and LivDet 2021

LivDet datasets are biometric research datasets with their own access, licensing, and usage conditions. Obtain the data through the authorized source, follow its license, and do not commit or redistribute the images in this repository without permission.

### Recommended workflow

1. **Keep raw data immutable.** Store the extracted LivDet data outside the Git repository, for example under `/data/livdet-2021/raw/`.
2. **Create a manifest.** Store relative path, sensor/device, subject or identity group, live/spoof label, spoof material or attack type, and dataset split in CSV or Parquet format.
3. **Normalize labels.** Map genuine/live samples to `Live` and every presentation-attack sample to `Fake` for this binary application. Keep the original attack subtype in the manifest for later analysis.
4. **Split by identity and acquisition group.** Do not randomly place images from the same finger, subject, sensor session, or near-duplicate sequence into both train and validation sets. This prevents identity and session leakage.
5. **Create an independent test set.** Prefer a held-out sensor, material, subject group, or acquisition session when the benchmark protocol permits it. A validation score alone is not evidence of generalization.
6. **Use a staging dataset.** Materialize only the YOLO directory needed for the current run using hard links, symbolic links, or a controlled copy. Avoid keeping multiple full copies of a very large dataset.
7. **Train with a streaming-friendly pipeline.** Use an appropriate batch size, multiple workers, local SSD storage, and GPU acceleration when available. Start with a small verified subset before launching a long run.
8. **Track experiments.** Save the exact manifest version, class balance, random seed, Ultralytics arguments, checkpoint, and hardware information for every run.
9. **Evaluate beyond accuracy.** Report confusion matrix, precision, recall, F1, ROC-AUC where appropriate, APCER/BPCER or equivalent biometric error rates, and results by sensor and attack type.

### Example large-dataset layout

```text
/data/livdet-2021/
├── raw/                         # Licensed source data; never committed
├── manifests/
│   ├── train.csv
│   ├── val.csv
│   └── test.csv
├── yolo_dataset_v1/             # Materialized training view
│   ├── train/Live/
│   ├── train/Fake/
│   ├── val/Live/
│   ├── val/Fake/
│   ├── test/Live/
│   └── test/Fake/
└── experiments/
    └── yolo8n-classification-v1/
```

For millions of images, the current `prepare_dataset.py` should be replaced or extended with a manifest-driven preparation job. The current script gathers all paths into Python lists and copies every selected image; that is convenient for a small dataset but creates unnecessary I/O and storage pressure at LivDet scale. Add resumability, logging, duplicate detection, integrity checks, and deterministic group-based splits before using it for a large benchmark.

### Avoiding misleading results

- Never let augmented versions of one source image cross a split boundary.
- Check class balance separately for every sensor and attack type.
- Do not use the test set to select a threshold or tune hyperparameters.
- Compare performance on unseen devices or spoof materials when possible.
- Treat the confidence score as a model score, not a calibrated probability, until calibration has been evaluated.

## Model and inference compatibility

The recorded training configuration uses `yolov8n-cls.pt`, which is a **classification** model. Classification results normally expose class probabilities through `result.probs`.

The application now reads `result.probs` for the classification checkpoint and also retains a detection-box fallback for detection checkpoints:

- If `best.pt` is a detection model, ensure its classes and annotations match the application logic.
- If `best.pt` is the classification checkpoint trained from `yolov8n-cls.pt`, the top class and confidence are read from `result.probs`.
- Test both `Live` and `Fake` images after changing the checkpoint or inference code.

This distinction is essential: a classification dataset with `Live/` and `Fake/` folders does not produce bounding boxes.

The project pins an older Ultralytics release. With PyTorch 2.6 or newer, `app.py` uses a scoped full-checkpoint load for the trusted local `best.pt` file. It also adapts the classifier preprocessing for newer torchvision versions that expect PIL images.

## Configuration and security notes

The current code is suitable for a local prototype, but it needs hardening before deployment:

- Replace the hard-coded Flask secret key with an environment variable such as `FLASK_SECRET_KEY`.
- Replace the in-memory `users` dictionary with a persistent database and securely hashed passwords.
- Validate file type and content, enforce a maximum upload size, and generate safe server-side filenames.
- Add authorization checks to every protected route and configure secure session cookies.
- Remove `debug=True` in production and serve Flask behind a production WSGI server such as Gunicorn.
- Add retention and cleanup policies for `static/uploads/` and `static/results/`, especially for biometric data.
- Keep raw biometric data private, encrypted where appropriate, and governed by the applicable privacy requirements.
- Move hard-coded chart and performance values to metrics generated from an evaluated model.

## Troubleshooting

### `Model not loaded`

Confirm that `best.pt` exists in the directory from which `python app.py` is started, or change the model path in `app.py` to an explicit path. Check the startup warning for the original loading error.

### `No features detected` or `Model processing failed`

Restart the Flask process after changing `app.py`, confirm that `best.pt` is in the project directory, and check the terminal startup or request traceback. The application supports the included classification checkpoint and reads its class probability from `result.probs`.

### Out-of-memory during training

Reduce `batch`, reduce `imgsz`, use a smaller model, enable a GPU with sufficient memory, or split the training job. Do not silently discard validation or test data to make training fit.

### Dataset preparation is slow or fills the disk

The preparation script copies files and currently uses an 80/20 random split. For a large dataset, use a manifest-driven, resumable staging process and links where the filesystem and data policy permit it.

## Future improvements

- Add a real training/evaluation script with deterministic, group-aware splits.
- Correctly support YOLO classification inference in the Flask route.
- Add automated tests for authentication, uploads, model failures, and prediction rendering.
- Add persistent user storage and secure password hashing.
- Add configurable model paths, upload limits, retention settings, and secret keys.
- Replace static analytics values with metrics generated from `results.csv` and held-out evaluation data.
- Add batch inference and an asynchronous job queue for large image collections.
- Add experiment tracking and dataset versioning for LivDet-scale research.