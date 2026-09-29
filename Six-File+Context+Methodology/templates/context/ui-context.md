# UI/UX Context & Design System

## Visual Theme & Layout Architecture
The interface follows a modern, clean, cybersecurity-focused dashboard style. It uses high contrast for visual verification of fingerprint ridges, pores, and bounding box annotations[cite: 1].

### Design Tokens

| Role | CSS Variable / Token | Color Code / Value | Usage Context |
| :--- | :--- | :--- | :--- |
| **Page Background** | `--bg-main` | `#f8f9fa` | Main page body background |
| **Card Surface** | `--bg-surface` | `#ffffff` | Content containers, upload panels |
| **Primary Accent** | `--accent-primary` | `#0d6efd` | Primary buttons, active navigation links |
| **Success State** | `--state-success` | `#198754` | "Live" detection badges, login confirmation |
| **Danger / Alert** | `--state-danger` | `#dc3545` | "Spoof" detection badges, error messages |
| **Text Primary** | `--text-dark` | `#212529` | Headings, primary metric labels |
| **Text Muted** | `--text-muted` | `#6c757d` | Subtitles, file upload helper text |

## Key Page Views & Layout Patterns

### 1. Main Navigation Header
Present across all views; features system identity branding and contextual navigation links (`Home`, `Detection`, `Charts`, `Performance`, `Logout`/`Login`)[cite: 1].

### 2. Detection Dashboard (`index.html`)
- **Upload Form Panel:** Drag-and-drop file upload input accepting image files (PNG, JPG, JPEG)[cite: 1].
- **Results View (Post-Inference):** Split two-column grid layout displaying:
  - **Left Column:** Original raw input image from `static/uploads/`[cite: 1].
  - **Right Column:** Model annotated image from `static/results/` showing YOLO bounding box overlays[cite: 1].
- **Prediction Summary Card:** Displays parsed classification metrics including Class Tag (`Live` vs `Spoof`) and Confidence Percentage[cite: 1].

### 3. Analytics Views (`charts.html`, `performance.html`)
Presents statistical breakdowns of model evaluation metrics (Accuracy, Precision, Recall, Confusion Matrix) and execution charts[cite: 1].