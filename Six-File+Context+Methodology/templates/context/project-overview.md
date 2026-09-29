# Lightweight Deep Learning Framework for Fingerprint Liveness Detection

## Overview
This project delivers a software-based Fingerprint Liveness Detection (FLD) system designed to protect biometric authentication infrastructure from presentation attacks. Artificial fingerprints fabricated from materials such as silicone, gelatin, and latex pose significant security risks to optical and capacitive sensors. Traditional detection solutions often require specialized hardware or complex multimodal biometric sensors. 

This framework addresses these limitations by using a single static image pipeline. It leverages **YOLOv8n**—a lightweight object detection model featuring a decoupled detection head and multi-scale feature aggregation—to evaluate ridge-level characteristics (pore distribution, minutiae, ridge distortions) alongside global texture cues (perspiration patterns, surface irregularities). The deep learning core is paired with a **Flask** web application that handles user authentication, file ingestion, real-time inference execution, and dynamic output visualization.

## Primary Objectives
1. **High-Accuracy Spoof Identification:** Differentiate between live human fingerprints and synthetic presentation attack copies (silicone, gelatin, latex) using single static images.
2. **Real-Time Efficiency:** Maintain low parameter counts and swift inference speeds to support resource-constrained environments and embedded biometric devices.
3. **Hardware Independence:** Operate strictly through software image processing without requiring auxiliary physical sensors, secondary cameras, or iris/face biometric fusion.
4. **End-to-End Operational Workflow:** Provide a full-stack deployment pipeline with secure user session handling, unique file naming, dynamic bounding-box rendering, and confidence score parsing[cite: 1].

## Core User Workflow
1. **Access Control & Session Creation:** User registers an account (`/register`) or logs in (`/login`) via the Flask application session management system[cite: 1].
2. **Sample Ingestion:** User navigates to the detection interface (`/index`) and uploads a fingerprint sample image (JPEG/PNG)[cite: 1].
3. **Server Ingestion & Renaming:** The Flask backend validates the file payload and assigns a unique `UUIDv4` filename to prevent collision before saving to `static/uploads/`[cite: 1].
4. **YOLOv8n Inference Execution:** The image path is passed to the pre-loaded `best.pt` model, executing multi-scale feature extraction across the backbone and decoupled head[cite: 1].
5. **Post-Processing & Rendering:** Bounding boxes, assigned class labels (`Live` or `Spoof`), and confidence percentages are saved to `static/results/` and rendered on `index.html`[cite: 1].
6. **System Analytics Review:** Authenticated users inspect detection history, performance metrics, and charts via `/performance` and `/charts`[cite: 1].

## Functional Scope

### In Scope
- Single-sensor static image fingerprint liveness detection[cite: 1].
- Pretrained YOLOv8n deep learning inference pipeline[cite: 1].
- Flask web backend with secure routing, file handling, and session tracking[cite: 1].
- UI dashboard displaying side-by-side original and annotated detection outputs[cite: 1].
- Metric routes for evaluating model classification results[cite: 1].

### Out of Scope
- Hardware-level physical sensor drivers or direct USB optical scanner integration[cite: 1].
- Multimodal biometric fusion (e.g., combining facial, iris, or voice traits)[cite: 1].
- Real-time video frame streaming input pipelines[cite: 1].