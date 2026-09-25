# SoftWork

> **AI-native parametric CAD.**

SoftWork is an open-source, desktop-first, AI-native parametric CAD application.

```text
Human intent → AI reasoning → structured engineering operations → parametric CAD → validated geometry → human review
```

---

## Core Philosophy

1. **AI is the Reasoner, not the Geometry Authority:** AI reasons about intent, requirements, parameters, and constraints. The CAD kernel is the sole authority on geometric truth.
2. **Parametric Intent over Visual Imitation:** Features are structured operations (Sketches, Extrusions, Holes, Fillets, Patterns) rather than unconstrained mesh approximations.
3. **Deterministic Command Layer:** Every AI action routes through the same validated command system that drives manual GUI interactions.
4. **Inspectable & Reversible:** Every modification occurs within a transactional history supporting undo, redo, validation, and change explanations.
5. **Offline-Capable & Open:** The core CAD system runs entirely offline with open document standards and industry-standard export formats (STEP, STL, DXF).

---

## Architecture Overview

```text
                 ┌─────────────┐
                 │  User / UI  │
                 └──────┬──────┘
                        │
                 ┌──────▼──────┐
                 │   Commands  │
                 └──────┬──────┘
                        │
             ┌──────────▼──────────┐
             │    Document Core    │
             └──────────┬──────────┘
                        │
                 ┌──────▼──────┐
                 │ CAD Backend │
                 └─────────────┘
                        ▲
                        │
                 ┌──────┴──────┐
                 │ AI Tooling  │
                 └─────────────┘
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- (Optional) PySide6 for full Qt6 GUI
- (Optional) CadQuery / OCP for OpenCASCADE kernel integration

### Installation
```bash
# Clone the repository
git clone https://github.com/SoftWork-CAD/softwork.git
cd softwork

# Install in editable mode
pip install -e .
```

### Running SoftWork
```bash
# Launch the desktop application
softwork
```

---

## License

SoftWork is licensed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.
