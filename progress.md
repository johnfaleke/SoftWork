# SoftWork — Project Progress & Engineering Changelog

> **Living Document:** This file records all built modules, architecture decisions, test results, execution guides, and roadmap milestones for **SoftWork**.

---

## 🗺️ Roadmap Reference in `SoftWork.md`

- **v0.1 — Foundation** *(✅ Completed)*: Desktop shell, 3D viewport, CAD backend, document model, primitive solids, STEP/STL export.
- **v0.2 — Parametric Part Modeling** *(✅ Completed)*: 2D sketches, datum planes (XY/XZ/YZ), closed profiles, extrusions, revolutions, patterns, chamfers, face picking.
- **v0.3 — AI CAD Copilot** *(In Progress)*: Live cloud LLM providers (Gemini, Claude, OpenAI), visual AI change preview modal, diff inspector.
- **v0.4 — AI-Native Parametric Editing**: Semantic references, design-intent metadata, dependency-aware preservation.
- **v0.5 — Advanced Part Modeling**: Loft, sweep, shell, draft, advanced pattern topologies.
- **v0.6 — Assemblies**: Components, mates, interference detection, BOM.
- **v0.7 — Drawings**: Orthographic views, dimensions, annotations, PDF/DXF export.
- **v0.8 — AI Engineering Agent**: Multi-step design plans, multimodal inputs, design alternatives, manufacturing awareness.
- **v0.9 — Collaboration & Ecosystem**: Plugins, Git-friendly projects, community workbenches.
- **v1.0 — SoftWork CAD**: Enterprise stability, deterministic geometry, verified engineering workflows.

---

## 🏗️ Completed Implementation

### 1. 2D Sketching & Profile Subsystem (`softwork.sketch`) — *v0.2*
| Module / File | Description | Status |
| :--- | :--- | :--- |
| [`sketch/plane.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/sketch/plane.py) | Datum planes (`XY`, `XZ`, `YZ`) and 2D-to-3D coordinate projection | ✅ Complete |
| [`sketch/elements.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/sketch/elements.py) | 2D geometric entities (`Line2D`, `Circle2D`, `Rectangle2D`, `Polygon2D`) | ✅ Complete |
| [`sketch/profile.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/sketch/profile.py) | Closed boundary loop detection & Shoelace polygon area calculation | ✅ Complete |
| [`sketch/sketch.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/sketch/sketch.py) | 2D Sketch container managing plane, elements, and profiles | ✅ Complete |

### 2. Parametric Features (`softwork.core.feature`) — *v0.1 & v0.2*
| Feature Class | Description | Status |
| :--- | :--- | :--- |
| `SketchFeature` | First-class 2D sketch entity in the feature tree | ✅ Complete |
| `ExtrudeFeature` | Extrudes 2D sketch profile by parametric `distance` | ✅ Complete |
| `RevolveFeature` | Revolves 2D sketch profile around axis by parametric `angle` | ✅ Complete |
| `PatternFeature` | Linear array repetition of 3D solid features | ✅ Complete |
| `ChamferFeature` | Edge chamfering with parametric `distance` | ✅ Complete |
| `MountingPlateFeature` | Multi-hole parametric mounting plate with corner fillets | ✅ Complete |
| `BoxFeature` & `CylinderFeature` | Parametric primitive solids | ✅ Complete |
| `FilletFeature` | Outer edge rounding with parametric `radius` | ✅ Complete |

### 3. CAD Kernel & Geometry Engine (`softwork.cad`)
| Module / File | Description | Status |
| :--- | :--- | :--- |
| [`cad/geometry.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/geometry.py) | 3D points, vectors, bounding boxes, and triangulated `MeshData` | ✅ Complete |
| [`cad/topology.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/topology.py) | Topology entity structures and `CADShape` representation | ✅ Complete |
| [`cad/backend.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/backend.py) | Abstract geometric kernel interface (`CADBackend`) | ✅ Complete |
| [`cad/direct_backend.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/direct_backend.py) | Solid kernel with CSG, profile extrusions, revolutions, and tessellation | ✅ Complete |
| [`cad/cadquery_backend.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/cadquery_backend.py) | OpenCASCADE & CadQuery adapter with automatic fallback | ✅ Complete |
| [`cad/validation.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/validation.py) | `GeometryValidator` (volume, manifold, and boundary checks) | ✅ Complete |

### 4. Unified Command System (`softwork.commands`)
| Module / File | Description | Status |
| :--- | :--- | :--- |
| [`commands/base.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/commands/base.py) | Abstract `Command` interface | ✅ Complete |
| [`commands/feature_commands.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/commands/feature_commands.py) | `CreateSketchCommand`, `ExtrudeSketchCommand`, `RevolveSketchCommand`, `AddPatternCommand`, `AddChamferCommand`, `CreateBoxCommand`, `CreateMountingPlateCommand`, `AddFilletCommand` | ✅ Complete |
| [`commands/parameter_commands.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/commands/parameter_commands.py) | `SetParameterCommand` with cascading dependency recalculation | ✅ Complete |

### 5. AI Subsystem (`softwork.ai`)
| Module / File | Description | Status |
| :--- | :--- | :--- |
| [`ai/provider.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/ai/provider.py) | Heuristic engine recognizing sketch creation, rectangle/circle profiles, extrusions, revolutions, patterns, and chamfers | ✅ Complete |
| [`ai/tools.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/ai/tools.py) | Strict typed tool registry (`sketch.create`, `sketch.add_rectangle`, `sketch.add_circle`, `feature.extrude`, `feature.revolve`, `feature.pattern`, `feature.chamfer`, `parameter.set`) | ✅ Complete |
| [`ai/context.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/ai/context.py) | Selection & dependency-aware compressed context builder | ✅ Complete |
| [`ai/agent.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/ai/agent.py) | `CADAgent` (Understand → Plan → Operate → Validate → Explain) | ✅ Complete |

### 6. Desktop User Interface (`softwork.ui`)
| Module / File | Description | Status |
| :--- | :--- | :--- |
| [`ui/viewport.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/ui/viewport.py) | 3D Canvas with Orbit, Pan, Zoom, Lighting, and **Interactive Face Raycasting Picking** | ✅ Complete |
| [`ui/main_window.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/ui/main_window.py) | Menubar, Design Toolbar (`Sketch`, `Extrude`, `Revolve`, `Pattern`, `Chamfer`), Tree, Properties, AI Bar | ✅ Complete |
| [`app/main.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/app/main.py) | Application bootstrap and CLI entry point | ✅ Complete |

---

## 🧪 Testing Protocol & Results

### How to Run Tests
```bash
py run_tests.py
```

### Test Suites Summary (16 Tests)
| Test File | Covered Functionality | Result |
| :--- | :--- | :--- |
| [`tests/test_sketch_and_profiles.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_sketch_and_profiles.py) | Sketch plane transforms, rectangle/circle 2D profiles, Shoelace area, and loop detection | ✅ Passed |
| [`tests/test_v02_parametric_features.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_v02_parametric_features.py) | Sketch extrusion, revolution, linear pattern, chamfer, and AI agent sketch-to-extrude flow | ✅ Passed |
| [`tests/test_geometry_and_backend.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_geometry_and_backend.py) | Box creation, mounting plate with holes, tessellation, bounds, volume, and fillet validation | ✅ Passed |
| [`tests/test_core_document.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_core_document.py) | Parameter unit conversions (`in`, `mm`, `deg`), DAG recomputation, and undo/redo history | ✅ Passed |
| [`tests/test_ai_agent_and_tools.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_ai_agent_and_tools.py) | CAD agent natural-language creation, hole additions, filleting, and thickness update | ✅ Passed |
| [`tests/test_formats_and_serialization.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_formats_and_serialization.py) | Save/load `.softwork` document files, STEP AP214 export, and binary STL exports | ✅ Passed |

**Result:** 16 tests ran in 2.170s — **100% OK**.

---

## 🚀 How to Run SoftWork

### 1. Launch the Desktop GUI (v0.2)
```bash
py src/softwork/app/main.py
```
- **3D Face Picking:** Click on any surface in the 3D viewport to highlight it in gold and view normal/index in the status bar.
- **2D Sketch & Extrude:** Click `✏️ New Sketch` or type `"Create sketch on XY plane"` then `"Add a 100 x 60 mm rectangle"` and `"Extrude by 25 mm"`.
- **Revolve:** Click `🔁 Revolve` or type `"Revolve the sketch by 360 degrees"`.
- **Linear Pattern & Chamfer:** Duplicate parts into array patterns and apply edge chamfers.

---

## 📅 Next Development Tasks (v0.3 AI Copilot)

- [ ] **Task 3.1: Live Cloud LLM Provider Integration**
  - Connect `GeminiProvider`, `AnthropicProvider`, and `OpenAIProvider` with streaming function calling.
  - Add API key configuration dialog in the GUI.
- [ ] **Task 3.2: Visual AI Change Preview & Ghost Overlay**
  - Display before/after diff summary and volume delta before committing AI changes.
