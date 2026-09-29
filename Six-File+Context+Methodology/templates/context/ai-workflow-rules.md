# AI Workflow & Development Execution Rules

## Development Strategy
Execute project modifications incrementally, adhering strictly to the architecture defined in `architecture.md` and code guidelines in `code-standards.md`[cite: 2, 3, 4]. Every implementation step must focus on one isolated system layer before moving forward[cite: 2].

## Scoping & Boundary Rules
- Implement work in single feature units (e.g., authentication system separate from inference execution)[cite: 2].
- Do not make speculative alterations to deep learning parameter extraction logic without updating specifications[cite: 2].
- Do not mix file system logic with front-end template markup changes in a single step[cite: 2].

## Modification Guardrails
- **Protected Files:** Do not modify model weights (`best.pt`) or context standards unless explicitly requested[cite: 1, 2].
- **Dependency Isolation:** Ensure new library requirements are compatible with `ultralytics`, `flask`, and `werkzeug`[cite: 1].

## Verification Checklist Before Closing a Stage
1. `app.py` executes without import or syntax errors[cite: 1, 2].
2. File uploads are successfully ingested, renamed via UUID, and saved to `static/uploads/`[cite: 1, 2].
3. YOLOv8 model processes saved images and writes outputs to `static/results/`[cite: 1, 2].
4. Parsed predictions correctly populate class names and rounded confidence values[cite: 1, 2].
5. All `.md` context documentation files accurately reflect any updated routes or data contracts[cite: 2].