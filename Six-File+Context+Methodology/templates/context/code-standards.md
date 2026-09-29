### File 3: `code-standards.md`

```markdown
# Project Code Standards

## General Principles
- Maintain single-purpose functions and keep routing logic clean[cite: 4].
- Avoid absolute hardcoded file system paths; construct relative paths dynamically using `os.path.join()`[cite: 1, 4].
- Enforce standard exception handling around file I/O operations and model execution blocks[cite: 1].

## Python & Flask Conventions
- Enforce `secret_key` configuration on the Flask application instance for session encryption[cite: 1].
- Use `secure_filename` alongside `uuid.uuid4()` generation for safe handling of client uploads[cite: 1].
- Explicitly verify directory existence on app startup using `os.makedirs(path, exist_ok=True)`[cite: 1].

```python
# Example: Standard dynamic directory initialization pattern
UPLOAD_FOLDER = os.path.join('static', 'uploads')
RESULT_FOLDER = os.path.join('static', 'results')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)[cite: 1]
os.makedirs(RESULT_FOLDER, exist_ok=True)[cite: 1]