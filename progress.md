# SoftWork — Project Progress & Engineering Changelog

> **Living Document:** This file records all built modules, architecture decisions, test results, execution guides, and roadmap milestones for **SoftWork**.

---

## 🗺️ Roadmap Reference in `SoftWork.md`

- **v0.1 — Foundation** *(✅ Completed)*: Desktop shell, 3D viewport, CAD backend, document model, primitive solids, STEP/STL export.
- **v0.2 — Parametric Part Modeling** *(✅ Completed)*: 2D sketches, datum planes (XY/XZ/YZ), closed profiles, extrusions, revolutions, patterns, chamfers, face picking, 2D constraint solver, viewport drawing.
- **v0.3 — AI CAD Copilot & Advanced Features** *(✅ Completed)*: Live cloud LLM providers (Gemini, Claude, OpenAI), visual AI ghost mesh preview & HUD volume delta, ISO Hole Wizard (M3-M16 Counterbore/Countersink), Shell/Hollow feature.
- **Modern IDE Architecture & UI Customization** *(✅ Completed)*: Vertical Activity Bar, **Draggable & Collapsible Floating AI Copilot HUD**, breadcrumb navigation, theme engine with 8 presets (OLED True Black, Charcoal, Studio Light, Nordic Frost, Cyberpunk Neon, Industrial Titanium, Forest Sage, Solarized Dark), persistent workspace settings (`~/.softwork/workspace_settings.json`).
- **PySide6 / Qt6 Modern CAD IDE Frontend (SolidWorks & PTC Creo Architecture)** *(✅ Completed)*:
  - **Pure Text Only Everywhere**: 100% clean industrial engineering aesthetic with zero icons, symbols, emojis, or cryptic glyphs anywhere in the interface (ribbons, trees, dialogs, viewport HUD, activity bar, floating copilot, or status bars).
  - **CommandManager Ribbon (Top)**: Tabbed toolbars (`Features`, `Sketch`, `Evaluate`, `Parametric Copilot`, `I/O & History`).
  - **FeatureManager Design Tree (Left)**: Real CAD hierarchy with standard datum planes (`Front Plane`, `Top Plane`, `Right Plane`, `Origin`), parametric features, material assignments, and sketch profiles.
  - **SolidWorks Studio Gradient Viewport**: Smooth vertical gradient, metallic diffuse shaded surfaces, crisp silhouette edges, high-contrast cyan face selection (`#00A8FF`), centered **Heads-Up View Toolbar** (`Zoom Fit`, `Isometric`, `Top View`, `Front View`, `Right View`, `Normal To`, `Section`), and bottom-left 3D coordinate triad with datum origin.
  - **Parametric Copilot HUD**: Clean engineering command prompt & NLP execution overlay with clear text badges (`GEMINI`, `HEURISTIC`), parameter log, and ghost geometry wireframes.
  - **Engineering Status Bar**: `Editing Part` | `Cursor: X, Y, Z` | `Units: MMGS` | `Rebuilt Clean`.
- **v0.4 — AI-Native Parametric Editing & Semantic References** *(✅ Completed)*:
  - **In-Place Parametric Mutation Engine (`ParametricModifier`)**: Translates NLP modification prompts (*"make the plate 15 mm thick"*, *"change holes from M8 to M10"*, *"increase fillet to 4 mm"*, *"change shell thickness to 3 mm"*) into deterministic parameter commands rather than re-creating duplicate shapes.
  - **Batch Multi-Parameter Transactions (`BatchSetParameterCommand`)**: Atomic simultaneous dimension resizing (*"resize width to 80 and length to 120"*) in a single undoable transaction.
  - **Semantic Topological Reference System (`SemanticTopologyMatcher`)**: Persistent topological entity naming (`face:top`, `face:bottom`, `face:hole_inner`, `face:fillet`) solving the CAD topological naming problem across DAG feature recomputations.
- **v0.5 — Core Architectural Overhaul & Advanced Modeling (v0.5.0-dev)** *(✅ Core Real DAG Recomputation Complete)*:
  - **Authoritative CAD Kernel Integration**: Eliminated all silent fallbacks in `CadQueryBackend`; strict `CADKernelError` failure bubbling.
  - **Strict Topological DAG Recomputation Engine**: `Document.recompute()` evaluates in topological sort order, cascades `FeatureStatus.FAILED` to downstream dependents upon broken parameters or geometry errors, and restores healthy state upon recovery.
  - **Semantic Feature Decoupling**: Features reference parent entities via semantic string IDs and dynamically resolve geometry from evaluated dependency shapes.
  - **Canonical Parametric Feature Chain Integration**: Validated end-to-end multi-feature lifecycle (`Sketch` -> `Extrude` -> `Hole` -> `Pattern` -> `Fillet`) under mutations, invalid states, recovery, and serialization.
- **v0.6 — Assemblies**: Components, mates, interference detection, BOM.
- **v0.7 — Drawings**: Orthographic views, dimensions, annotations, PDF/DXF export.
- **v0.8 — AI Engineering Agent**: Multi-step design plans, multimodal inputs, design alternatives, manufacturing awareness.
- **v0.9 — Collaboration & Ecosystem**: Plugins, Git-friendly projects, community workbenches.
- **v1.0 — SoftWork CAD**: Enterprise stability, deterministic geometry, verified engineering workflows.

---

## 🏗️ Completed Implementation

### 1. 2D Sketching, Constraints & Profile Subsystem (`softwork.sketch`) — *v0.2*
| Module / File | Description | Status |
| :--- | :--- | :--- |
| [`sketch/plane.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/sketch/plane.py) | Datum planes (`XY`, `XZ`, `YZ`) and 2D-to-3D coordinate projection | ✅ Complete |
| [`sketch/elements.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/sketch/elements.py) | 2D geometric entities (`Line2D`, `Circle2D`, `Rectangle2D`, `Polygon2D`) | ✅ Complete |
| [`sketch/profile.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/sketch/profile.py) | Closed boundary loop detection & Shoelace polygon area calculation | ✅ Complete |
| [`sketch/constraints.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/sketch/constraints.py) | 2D geometric constraints (`Coincident`, `Horizontal`, `Vertical`, `Distance`, `Length`, `Radius`, `Fixed`) | ✅ Complete |
| [`sketch/solver.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/sketch/solver.py) | Gauss-Newton / Levenberg-Marquardt numerical constraint solver with DOF estimation | ✅ Complete |
| [`sketch/sketch.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/sketch/sketch.py) | 2D Sketch container managing plane, elements, constraints, profiles, and JSON serialization | ✅ Complete |

### 2. Parametric Features (`softwork.core.feature`) — *v0.1 - v0.5*
| Feature Class | Description | Status |
| :--- | :--- | :--- |
| `SketchFeature` | First-class 2D sketch entity holding 2D profile wires | ✅ Complete |
| `ExtrudeFeature` | Extrudes 2D sketch profile by parametric `distance` (semantic ID reference) | ✅ Complete |
| `RevolveFeature` | Revolves 2D sketch profile around axis by parametric `angle` | ✅ Complete |
| `HoleWizardFeature` | Standard ISO metric holes (M3 to M16) with simple, counterbore, and countersink geometry | ✅ Complete |
| `ShellFeature` | Uniform wall thickness shelling & hollow cavity generation | ✅ Complete |
| `PatternFeature` | Linear array repetition of 3D solid features | ✅ Complete |
| `ChamferFeature` | Edge chamfering with parametric `distance` | ✅ Complete |
| `FilletFeature` | Edge rounding with parametric `radius` | ✅ Complete |
| `BoxFeature` & `CylinderFeature` | Parametric primitive solids | ✅ Complete |
| `MountingPlateFeature` | Legacy monolithic test fixture (retired from canonical workflow) | ✅ Complete |

### 3. CAD Kernel & Geometry Engine (`softwork.cad`)
| Module / File | Description | Status |
| :--- | :--- | :--- |
| [`cad/geometry.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/geometry.py) | 3D points, vectors, bounding boxes, and triangulated `MeshData` | ✅ Complete |
| [`cad/topology.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/topology.py) | Topology entity structures and `CADShape` representation | ✅ Complete |
| [`cad/backend.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/backend.py) | Abstract geometric kernel interface (`CADBackend`) & `CADKernelError` | ✅ Complete |
| [`cad/direct_backend.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/direct_backend.py) | Solid kernel with CSG, hole tools, shell cavities, profile extrusions, revolutions, and tessellation | ✅ Complete |
| [`cad/cadquery_backend.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/cadquery_backend.py) | Strict CadQuery & OpenCASCADE adapter raising `CADKernelError` on failure (no silent fallbacks) | ✅ Complete |
| [`cad/validation.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/validation.py) | `GeometryValidator` (volume, manifold, and boundary checks) | ✅ Complete |

### 4. Unified Command System (`softwork.commands`)
| Module / File | Description | Status |
| :--- | :--- | :--- |
| [`commands/base.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/commands/base.py) | Abstract `Command` interface | ✅ Complete |
| [`commands/feature_commands.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/commands/feature_commands.py) | `CreateSketchCommand`, `ExtrudeSketchCommand`, `RevolveSketchCommand`, `AddHoleWizardCommand`, `AddShellCommand`, `AddPatternCommand`, `AddChamferCommand`, `CreateBoxCommand`, `CreateMountingPlateCommand`, `AddFilletCommand` | ✅ Complete |
| [`commands/parameter_commands.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/commands/parameter_commands.py) | `SetParameterCommand` & `BatchSetParameterCommand` with cascading DAG recalculation | ✅ Complete |

### 5. AI Subsystem (`softwork.ai`) — *v0.3 & v0.4*
| Module / File | Description | Status |
| :--- | :--- | :--- |
| [`ai/provider.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/ai/provider.py) | Cloud LLM providers (`GeminiProvider`, `OpenAIProvider`, `AnthropicProvider`) and deterministic Heuristic engine | ✅ Complete |
| [`ai/modifier.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/ai/modifier.py) | **Parametric Modifier Engine**: In-place feature parameter mutations, batch edits, and ghost plan generation | ✅ Complete |
| [`ai/tools.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/ai/tools.py) | Strict typed tool registry (`sketch.create`, `sketch.add_rectangle`, `sketch.add_circle`, `feature.extrude`, `feature.revolve`, `feature.hole_wizard`, `feature.shell`, `feature.pattern`, `feature.chamfer`, `parameter.set`, `parameter.batch_set`) | ✅ Complete |
| [`ai/context.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/ai/context.py) | Selection & dependency-aware compressed context builder | ✅ Complete |
| [`ai/agent.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/ai/agent.py) | `CADAgent` (Understand → In-Place Modify / Plan with Ghost Simulation → Operate → Validate → Explain) | ✅ Complete |

### 6. Clean Desktop CAD IDE Architecture (`softwork.qt`) — *SolidWorks & PTC Creo Standard*
| Module / File | Description | Status |
| :--- | :--- | :--- |
| [`core/material.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/core/material.py) | Standard CAD material library (Steel, Aluminum, Titanium, Polymers) with mass, density, and physical properties | ✅ Complete |
| [`core/semantic.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/core/semantic.py) | **Semantic Reference System**: Persistent topology tags (`face:top`, `face:bottom`, `face:hole_inner`) | ✅ Complete |
| [`qt/styles.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/qt/styles.py) | SolidWorks & PTC Creo dark slate QSS stylesheet with `#00A8FF` CAD blue accents and precision controls | ✅ Complete |
| [`qt/activity_bar.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/qt/activity_bar.py) | Clean CAD vertical icon strip (`Tree`, `Feat`, `Prop`, `AI`, `Cfg`) without emojis | ✅ Complete |
| [`qt/floating_copilot.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/qt/floating_copilot.py) | **Engineering HUD Parametric Copilot Command Prompt** with ghost preview overlay | ✅ Complete |
| [`qt/viewport.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/qt/viewport.py) | SolidWorks slate studio gradient canvas, ground drop shadow, in-viewport contextual mini-toolbar, diffuse metallic shading, silhouette edges, and 3D coordinate triad | ✅ Complete |
| [`qt/main_window.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/qt/main_window.py) | CommandManager ribbon with tabs, top-bar universal CAD/AI prompt box, FeatureManager tree with datums & materials, PropertyManager mass evaluation, and MMGS status bar | ✅ Complete |
| [`app/main_qt.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/app/main_qt.py) | PySide6 application bootstrap entry point | ✅ Complete |

---

## 🧪 Testing Protocol & Results

### How to Run Tests
```bash
py run_tests.py
```

### Test Suites Summary (46 Tests Passing)
| Test File | Covered Functionality | Result |
| :--- | :--- | :--- |
| [`tests/test_backend_authority.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_backend_authority.py) | Document CadQuery default authority, absence of silent fallback, PrototypeGeometryBackend isolation, STEP export safety (blocking non-B-rep export), rebuild failure safety & `previous_valid_shape` retention, atomic transaction rollback, and AI sketch entity undoability | ✅ Passed |
| [`tests/test_real_parametric_chain.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_real_parametric_chain.py) | Canonical parametric feature chain (`Sketch` -> `Extrude` -> `Hole` -> `Pattern` -> `Fillet`), parameter mutation, DAG failure cascade, model recovery, and round-trip serialization | ✅ Passed |
| [`tests/test_v04_ai_parametric_editing.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_v04_ai_parametric_editing.py) | In-place parametric thickness/hole/fillet modification, multi-parameter batch dimension edits, and semantic topological reference tagging | ✅ Passed |
| [`tests/test_core_document.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_core_document.py) | Parameter unit conversions (`in`, `mm`, `deg`), DAG recomputation, history undo/redo, Material densities, and mass evaluation | ✅ Passed |
| [`tests/test_qt_ide_components.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_qt_ide_components.py) | PySide6 SolidWorks/Creo QSS tokens, document and CAD agent bindings | ✅ Passed |
| [`tests/test_ui_theme_and_workspace_settings.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_ui_theme_and_workspace_settings.py) | Floating AI Copilot widget lifecycle, Activity Bar navigation, 8 theme palettes, True Black OLED mode, Charcoal grey contrast, theme registration, and workspace settings persistence | ✅ Passed |
| [`tests/test_v03_ai_copilot_and_advanced_features.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_v03_ai_copilot_and_advanced_features.py) | ISO Metric Hole Wizard, Shell hollowing, Cloud Provider fallback, and AI Ghost preview generation | ✅ Passed |
| [`tests/test_constraint_solver.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_constraint_solver.py) | 2D Geometric constraint solver: Coincident, Fixed, Horizontal, Vertical, Radius, and DOF diagnostics | ✅ Passed |
| [`tests/test_sketch_and_profiles.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_sketch_and_profiles.py) | Sketch plane transforms, rectangle/circle 2D profiles, Shoelace area, and loop detection | ✅ Passed |
| [`tests/test_v02_parametric_features.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_v02_parametric_features.py) | Sketch extrusion, multi-solid boolean join on mounting plate, revolution, linear pattern, chamfer, and AI agent sketch-to-extrude flow | ✅ Passed |
| [`tests/test_geometry_and_backend.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_geometry_and_backend.py) | Box creation, mounting plate with holes, tessellation, bounds, volume, and fillet validation | ✅ Passed |
| [`tests/test_ai_agent_and_tools.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_ai_agent_and_tools.py) | CAD agent natural-language creation, hole additions, filleting, and thickness update | ✅ Passed |
| [`tests/test_formats_and_serialization.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/tests/test_formats_and_serialization.py) | Save/load `.softwork` document files, STEP AP214 export, and binary STL exports | ✅ Passed |

---

## 💻 Manual Verification Checklist

1. **Launch Desktop CAD IDE:**
   ```bash
   py src/softwork/app/main.py
   ```
2. **In-Place Parametric AI Editing:**
   - In the top command box or floating Copilot HUD, enter *"Make the plate 15 mm thick"*.
   - Verify that the existing mounting plate's thickness increases in-place without duplicating features.
   - Enter *"Change the holes to M10"*, then *"Increase fillet to 4 mm"*.
   - Enter *"Resize width to 80 and length to 120"*.
3. **Direct In-Viewport 3D Actions:** Click any 3D face to bring up the contextual action capsule (`[Sketch]`, `[Extrude]`, `[Hole]`, `[Fillet]`, `[Normal To]`).
4. **Physical Mass Properties:** Inspect the PropertyManager for live Mass ($g$), Density ($g/cm^3$), and Volume ($mm^3$).


