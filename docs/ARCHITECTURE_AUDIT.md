# SoftWork — Comprehensive Architecture Audit
**Document:** `docs/ARCHITECTURE_AUDIT.md`  
**Date:** September 2026 (v0.5.0-dev)  
**Directive:** `SoftWork_AGENT_BUILD_DIRECTIVE.md`  
**Target Repository:** https://github.com/johnfaleke/SoftWork

---

## 1. Executive Summary

This architecture audit provides a full, unvarnished inspection of the entire **SoftWork** codebase. It evaluates the geometry execution pipeline, CAD kernel authority, dependency-driven rebuild engine, serialization, command transactions, undo/redo mechanisms, and AI copilot integrations against the production CAD requirements specified in `SoftWork_AGENT_BUILD_DIRECTIVE.md`.

SoftWork contains a functioning foundation (PySide6 CAD desktop shell, topological dependency graph, parameter system, 2D sketch constraint solver, ISO Hole Wizard, and AI tools). However, historically it suffered from:
1. Competing geometry backends where a custom polygonal CSG engine (`DirectGeometryBackend`) silently masqueraded as a CAD kernel.
2. Incomplete isolation of CadQuery/OpenCASCADE failures.
3. Live object reference coupling between features.
4. Redundant UI trees (`src/softwork/ui` [Tkinter] alongside `src/softwork/qt` [PySide6]).
5. Monolithic demo fixtures (`MountingPlateFeature`) bypassing canonical multi-feature parametric history.

---

## 2. Comprehensive Module Audit Table

| File / Module | Current Responsibility | Action (Keep / Rewrite / Deprecate / Delete / Defer) | Technical Rationale | Risk & Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| `src/softwork/cad/backend.py` | Abstract `CADBackend` interface and `CADKernelError` exception. | **Keep & Expand** | Defines the core geometry kernel abstraction contract. | Low risk. Must be expanded to return typed `CADResult` objects rather than raw shapes. |
| `src/softwork/cad/cadquery_backend.py` | Authoritative OpenCASCADE & CadQuery B-rep kernel wrapper. | **Keep & Harden** | Produces true boundary representation solids (STEP export, exact analytical fillets, standard metric holes). | High risk if CadQuery/OCP is missing. Must provide explicit availability checks and diagnostic errors. |
| `src/softwork/cad/direct_backend.py` | Custom pure-Python polygonal CSG mesh generator. | **Deprecate / Rename to `PrototypeGeometryBackend`** | Does not produce true CAD B-rep geometry. Unsuitable for STEP export or production modeling. | Medium risk if tests depend on it. Must remain available strictly under an explicit prototype flag. |
| `src/softwork/cad/geometry.py` | 3D points, vectors, bounding boxes, and triangulated `MeshData`. | **Keep** | Essential tessellation and spatial data structures for viewport rendering. | Low risk. Viewport display representation only. |
| `src/softwork/cad/topology.py` | `CADShape` metadata container and entity handles. | **Rewrite** | Bridges kernel B-rep handles with document feature IDs. Needs stronger shape state and B-rep face/edge tagging. | Low risk. |
| `src/softwork/cad/validation.py` | `GeometryValidator` (volume, manifold, boundary checks). | **Keep & Expand** | Checks volume positivity, valid B-rep topology, and fillet bounds. | Low risk. |
| `src/softwork/core/document.py` | Root `Document` holding parts, parameters, history, and `recompute()`. | **Keep & Harden** | Owns design intent and orchestrates topological recomputation. Must default strictly to `CadQueryBackend`. | High risk. Central hub of application. |
| `src/softwork/core/dependency.py` | DAG graph data structure (`networkx` or adjacency-based) with topological sort. | **Keep & Harden** | Provides topological ordering and cycle detection for feature rebuilds. | Low risk. Needs dirty-subgraph pruning. |
| `src/softwork/core/feature.py` | Feature definitions (`Sketch`, `Extrude`, `Revolve`, `HoleWizard`, `Pattern`, `Fillet`, `Chamfer`, `Shell`). | **Keep & Decouple** | Declares CAD operations and parameters. Must strictly decouple live object references into semantic IDs. | Medium risk. |
| `src/softwork/core/parameter.py` | Parametric dimension container with unit conversion (`mm`, `in`, `deg`). | **Keep** | Handles value storage, canonical units, and expression evaluation. | Low risk. |
| `src/softwork/core/part.py` | `Part` entity holding feature list and `active_solid`. | **Keep** | Organizes feature sequences into discrete solid bodies. | Low risk. |
| `src/softwork/core/material.py` | Material library (Steel, Aluminum, Titanium, Polymer) and mass physics. | **Keep** | Evaluates volume, mass, density, and center of gravity. | Low risk. |
| `src/softwork/core/selection.py` | Selection context for picked features, faces, and datum planes. | **Keep** | Mediates user/AI selection state in the UI. | Low risk. |
| `src/softwork/core/semantic.py` | Semantic topological reference naming (`face:top`, `face:bottom`). | **Keep & Integrate** | Mitigates CAD topological naming problem across rebuilds. | Medium risk. Needs kernel face binding. |
| `src/softwork/core/transaction.py` | `HistoryManager`, `AITransaction`, and `TransactionChange`. | **Keep & Harden** | Manages undo/redo stacks and atomic rollback of multi-step operations. | Low risk. |
| `src/softwork/sketch/sketch.py` | 2D Sketch container managing elements, constraints, and profiles. | **Keep** | First-class 2D parametric geometry holder. | Low risk. |
| `src/softwork/sketch/elements.py` | 2D primitives (`Line2D`, `Circle2D`, `Rectangle2D`, `Polygon2D`). | **Keep** | 2D sketch geometry definition. | Low risk. |
| `src/softwork/sketch/plane.py` | Datum planes (`XY`, `XZ`, `YZ`) and 2D-to-3D projection matrices. | **Keep** | Positions sketches in 3D world space. | Low risk. |
| `src/softwork/sketch/profile.py` | Closed profile loop detection and Shoelace polygon area calculation. | **Keep** | Extracts closed wire loops for extrusion and revolution. | Low risk. |
| `src/softwork/sketch/constraints.py` | 2D geometric constraints (`Coincident`, `Horizontal`, `Vertical`, `Distance`). | **Keep** | Parametric geometric relationships in 2D. | Low risk. |
| `src/softwork/sketch/solver.py` | Numerical constraint solver (Gauss-Newton / Levenberg-Marquardt). | **Keep** | Resolves 2D sketch degrees of freedom. | Low risk. |
| `src/softwork/commands/base.py` | Abstract `Command` interface returning `AITransaction`. | **Keep** | Enforces transactional mutation across UI and AI. | Low risk. |
| `src/softwork/commands/feature_commands.py` | Feature creation commands (`ExtrudeSketch`, `AddHole`, `AddFillet`). | **Keep & Hardwire** | Deterministic command handlers for adding features to the document. | Low risk. |
| `src/softwork/commands/parameter_commands.py` | `SetParameterCommand`, `BatchSetParameterCommand`. | **Keep** | Atomic single and multi-parameter mutation commands. | Low risk. |
| `src/softwork/document/serializer.py` | JSON document format (`.softwork`) serialization / deserialization. | **Keep & Hardwire** | Serializes declarative document structure, sketches, and feature parameters. | Medium risk. Must not serialize live Python objects. |
| `src/softwork/formats/step.py` | ISO-10303 STEP AP214 export wrapper. | **Keep** | Produces production STEP exchange files via OpenCASCADE. | Medium risk if non-B-rep shape is exported. |
| `src/softwork/formats/stl.py` | Binary and ASCII STL mesh export wrapper. | **Keep** | Exports triangulated solid meshes for 3D printing. | Low risk. |
| `src/softwork/ai/agent.py` | `CADAgent` orchestrator (Understand → Plan → Operate → Validate → Explain). | **Keep & Harden** | Directs natural language to validated command transactions. | Medium risk. |
| `src/softwork/ai/modifier.py` | `ParametricModifier` in-place NLP parameter mutation engine. | **Keep** | Parses NLP edits (*"make plate 15 mm thick"*) to `SetParameterCommand`. | Low risk. |
| `src/softwork/ai/tools.py` | Typed AI tool registry (`sketch.create`, `feature.extrude`, etc.). | **Keep & Hardwire** | Routes LLM tool calls through the command layer. | Low risk. |
| `src/softwork/ai/provider.py` | Cloud LLMs (Gemini, Claude, OpenAI) + deterministic Heuristic Engine. | **Keep** | Multi-provider LLM interface. | Low risk. |
| `src/softwork/ai/context.py` | Document context compressor for LLM prompt context. | **Keep** | Injects part, parameter, and selection states into AI prompts. | Low risk. |
| `src/softwork/qt/main_window.py` | PySide6 / Qt6 SolidWorks & PTC Creo CAD IDE window. | **Keep (Frozen)** | Production CAD IDE UI. Visual features frozen during core refactor. | High UI risk if modified prematurely. Freeze visual changes. |
| `src/softwork/qt/viewport.py` | OpenGL / Software 3D Viewport with metallic shading and coordinate triad. | **Keep** | Real-time interactive CAD viewport. | Low risk. |
| `src/softwork/qt/floating_copilot.py` | Floating draggable AI Copilot command prompt and HUD. | **Keep** | AI interaction surface. | Low risk. |
| `src/softwork/qt/activity_bar.py` | Clean vertical Activity Bar navigation strip. | **Keep** | IDE sidebar navigation. | Low risk. |
| `src/softwork/qt/styles.py` | Industrial SolidWorks/Creo QSS stylesheet and design tokens. | **Keep** | Pure-text dark industrial CAD aesthetic. | Low risk. |
| `src/softwork/ui/*` | Legacy Tkinter UI implementation (`MainWindow`, `theme.py`, etc.). | **Deprecate / Delete** | Redundant prototype interface obsolete since PySide6 implementation. | Low risk. Safe to isolate and remove. |
| `src/softwork/app/main.py` | Application bootstrap entry point. | **Keep** | Boots `CADMainWindow` by default. Remove Tkinter fallback. | Low risk. |
| `pyproject.toml` | Build metadata, dependencies, and entry points. | **Keep & Update** | Package configuration. Move optional desktop/cad dependencies to core where needed. | Low risk. |

---

## 3. Deep-Dive Answers to Core Audit Questions

### Q1: What is the actual default geometry backend?
**Finding:** Currently, `Document.__init__` defaults to `DirectGeometryBackend()` unless an explicit backend is supplied:
```python
self.backend: CADBackend = backend or DirectGeometryBackend()
```
`CadQueryBackend` exists and implements all modeling operations, but is only instantiated when explicitly requested or during tests.  
**Required Action:** Change the authoritative default to `CadQueryBackend()`. If `cadquery` is not installed, it must fail explicitly or enter an explicit `PrototypeGeometryBackend` mode with a clear user-facing warning.

### Q2: Where can geometry silently fall back?
**Finding:**
1. In `CadQueryBackend`, inner try-except blocks that fell back to `DirectGeometryBackend` were removed in v0.5.0-dev, now raising `CADKernelError`.
2. However, at initialization, if a user does not pass a backend, `Document` silently defaults to `DirectGeometryBackend`.
3. In `STEP` export (`src/softwork/formats/step.py`), if `shape.native_handle` is missing (i.e. shape came from `DirectGeometryBackend`), it attempts a fallback or writes empty mock files.  
**Required Action:** Disallow any silent instantiation of `DirectGeometryBackend`. Fail with `CADKernelError` and prevent STEP export on non-B-rep shapes.

### Q3: Which features produce real OpenCASCADE shapes?
**Finding:**
When `CadQueryBackend` is active, the following features create genuine OpenCASCADE B-rep solids via CadQuery Workplanes and OCP topology:
- `BoxFeature`: `cq.Workplane("XY").box(...)`
- `CylinderFeature`: `cq.Workplane("XY").circle(...).extrude(...)`
- `ExtrudeFeature`: `cq.Workplane(plane).polyline(loop).close().extrude(...)`
- `RevolveFeature`: `cq.Workplane(plane).polyline(loop).close().revolve(...)`
- `HoleWizardFeature`: Standard ISO metric counterbore/countersink cut via `backend.cut(base, hole_tool)`.
- `PatternFeature`: 2D linear array repetition via repeated `backend.union`.
- `FilletFeature`: `shape.native_handle.edges().fillet(radius)`
- `ChamferFeature`: `shape.native_handle.edges().chamfer(distance)`
- `ShellFeature`: `shape.native_handle.faces("+Z").shell(-wall_thickness)`

### Q4: Which features only produce custom mesh-like geometry?
**Finding:**
When running on `DirectGeometryBackend`, **all** features (including `MountingPlateFeature`, `ExtrudeFeature`, etc.) generate approximate triangulated `MeshData` through procedural polyhedral CSG rather than analytical B-rep geometry (surfaces, NURBS, exact curves).

### Q5: Does `Document.recompute()` truly use the dependency graph?
**Finding:**
**Yes.** In v0.5.0-dev, `Document.recompute()` was refactored to:
1. Populate all feature nodes and dependency edges into `DependencyGraph`.
2. Compute `DependencyGraph.topological_sort()`.
3. Sequentially evaluate features in strict topological DAG order.
4. Track any failed upstream feature IDs in `failed_nodes` and cascade `FeatureStatus.FAILED` with `code="DEPENDENCY_FAILED"` down to all dependent children.
5. Restore healthy status and regenerate geometry when parameters are repaired.

### Q6: Which features store live object references vs IDs?
**Finding:**
- `ExtrudeFeature` & `RevolveFeature`: Accept `SketchFeature | str`, but store `sketch_feature_id: str`. In `evaluate()`, they look up the parent sketch dynamically from `context_shapes[self.sketch_feature_id]`.
- `HoleWizardFeature`, `FilletFeature`, `ChamferFeature`, `PatternFeature`, `ShellFeature`: Store only `target_feature_id: str`.
- `MountingPlateFeature`: Monolithic feature with no external feature references.

### Q7: Which features serialize only IDs?
**Finding:**
All feature serializers in `src/softwork/document/serializer.py` serialize declarative IDs, parameter dictionaries, and string dependency arrays (`dependencies: list[str]`). Live Python object handles (`native_handle`, `CADShape`) are not saved to disk; geometry is deterministically regenerated on file load via `doc.recompute()`.

### Q8: How are failed rebuilds represented?
**Finding:**
- Features store `status: FeatureStatus` (`DIRTY`, `VALID`, `FAILED`, `SUPPRESSED`) and `error_message: Optional[str]`.
- `Document.recompute()` returns a structured `ValidationReport` containing issue codes (`INVALID_PARAMETER`, `CAD_OPERATION_FAILED`, `DEPENDENCY_FAILED`, `CYCLIC_DEPENDENCY`).
- *Weakness Identified:* When a feature fails, `feat.generated_shape` is currently set to `None` rather than preserving the `previous_valid_shape` for viewport preview.

### Q9: How does undo/redo restore geometry?
**Finding:**
- `Command` executions create `AITransaction` records pushed onto `HistoryManager`.
- `SetParameterCommand.undo()` and `BatchSetParameterCommand.undo()` restore previous parameter float/string values and trigger `document.recompute()`.
- `CreateFeatureCommand.undo()` removes the feature from `part.features` and `dependency_graph` and recomputes the document.
- *Weakness Identified:* If an operation fails midway, rollback must automatically revert all partially applied parameters without leaving the document in a dirty state.

### Q10: Which AI commands bypass the command layer?
**Finding:**
- `ParametricModifier` routes NLP dimension mutations through `SetParameterCommand` and `BatchSetParameterCommand`.
- In `src/softwork/ai/tools.py`, tool handlers instantiate commands (`CreateSketchCommand`, `ExtrudeSketchCommand`, `AddHoleWizardCommand`, etc.) and call `.execute(document)`.
- *Weakness Identified:* In `_handle_sketch_add_rectangle` and `_handle_sketch_add_circle`, entities were added directly to `sketch.elements` without wrapping them in an undoable `AddSketchEntityCommand`.

### Q11: Which tests verify actual geometry vs metadata?
**Finding:**
- `tests/test_real_parametric_chain.py`: Verifies actual geometry volume changes, DAG failure cascade, recovery, and serialization round-trip.
- `tests/test_geometry_and_backend.py`: Verifies mesh vertex counts, face counts, and bounding volumes.
- `tests/test_sketch_and_profiles.py`: Verifies Shoelace polygon areas and profile loop vertex coordinates.
- `tests/test_v04_ai_parametric_editing.py`: Verifies mass, volume, and parameter mutations from NLP prompts.
- `tests/test_qt_ide_components.py` & `test_ui_theme_and_workspace_settings.py`: Verify UI tokens and settings persistence.

### Q12: What is the current package/version mismatch?
**Finding:**
`pyproject.toml` was updated to `version = "0.5.0-dev"`. However, legacy references in docstrings or comments across `src/softwork/ai/tools.py` still reference "v0.2" or "v0.3".

### Q13: Which dependencies are optional versus required?
**Finding:**
- Core: `numpy` (required).
- Desktop GUI: `PySide6` (listed under `[project.optional-dependencies]`, but is the primary CAD IDE frontend).
- CAD Kernel: `cadquery` (listed under optional `cad`).
- AI: `openai`, `anthropic`, `google-generativeai` (optional, falling back to local deterministic `HeuristicEngineProvider`).

### Q14: What is the current behavior when CadQuery/OCP is unavailable?
**Finding:**
`CadQueryBackend(require_installed=False)` sets `_has_cadquery = False`. When any geometric method is invoked, it raises a structured `CADKernelError("CadQuery/OpenCASCADE kernel is unavailable. Ensure CadQuery is installed...")`.

---

## 4. Geometry Execution Path Map

```
[User UI Action / AI Prompt]
         │
         ▼
[Command Layer (SetParameterCommand / ExtrudeSketchCommand)]
         │
         ▼
[Document Model (src/softwork/core/document.py)]
         │  (Parameter modified or Feature added)
         ▼
[DependencyGraph (src/softwork/core/dependency.py)]
         │  (topological_sort() resolves execution order)
         ▼
[Feature Chain Execution Loop (for feat_id in topo_order)]
         │
         ├── Check upstream dependencies in failed_nodes
         │     ├── If upstream failed ──► Mark FeatureStatus.FAILED (DEPENDENCY_FAILED)
         │     └── If upstream healthy ──► Proceed to evaluate()
         ▼
[Feature.evaluate(backend, context_shapes)]
         │
         ▼
[Authoritative CADBackend (CadQueryBackend)]
         │
         ├── OpenCASCADE / OCP B-rep Kernel
         │     ├── Success ──► Return CADShape (native_handle: cq.Workplane, exact volume, surface area)
         │     └── Failure ──► Raise CADKernelError(operation, message)
         ▼
[GeometryValidator.validate_shape(shape)]
         │
         ├── Valid ──► FeatureStatus.VALID ──► context_shapes[feat_id] = shape
         └── Invalid ──► FeatureStatus.FAILED ──► Add to failed_nodes & report issues
         ▼
[Tessellation Engine (backend.to_mesh)]
         │
         ▼
[PySide6 Viewport (CADViewport3D) & FeatureManager Tree Updates]
```

---

## 5. First Implementation Step Proposal

Following the completion of this architecture audit, here is the proposal for the first focused implementation step under `SoftWork_AGENT_BUILD_DIRECTIVE.md`:

### Step 1: CAD Backend Authority, Explicit Prototype Mode, and Typed CAD Result Envelope

1. **Files to change:**
   - [`src/softwork/cad/backend.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/backend.py)
   - [`src/softwork/cad/cadquery_backend.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/cadquery_backend.py)
   - [`src/softwork/cad/direct_backend.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/direct_backend.py)
   - [`src/softwork/core/document.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/core/document.py)
   - [`src/softwork/cad/capabilities.py`](file:///c:/Users/BLVCK/Desktop/SoftWork/src/softwork/cad/capabilities.py) *(new)*

2. **Exact reason:**
   - Define a structured `CADResult` envelope containing `(success: bool, shape: Optional[CADShape], error: Optional[CADOperationError])`.
   - Explicitly designate `CadQueryBackend` as the default authoritative backend in `Document`.
   - Formally rename/mark `DirectGeometryBackend` as `PrototypeGeometryBackend` (with explicit non-production warnings) so it cannot silently impersonate a CAD kernel.
   - Provide runtime backend diagnostic capabilities (`BackendCapabilities`).

3. **Risks & Mitigation:**
   - *Risk:* Environments without CadQuery installed need clear diagnostic messaging rather than crashes during unit testing.
   - *Mitigation:* `CadQueryBackend` cleanly reports capability availability and surfaces actionable install instructions; tests explicitly test both `CadQueryBackend` availability and `PrototypeGeometryBackend` isolation.

4. **Tests to add:**
   - `tests/test_backend_authority.py`:
     - Verifies `CadQueryBackend` behaves as the primary kernel and raises structured `CADOperationError` on failure.
     - Verifies `PrototypeGeometryBackend` cannot export STEP or claim OpenCASCADE compliance.
     - Verifies `Document` reports kernel capability state accurately.

5. **Expected result:**
   - Complete architectural clarity: zero silent fallbacks, typed error diagnostics, and single authoritative B-rep geometry pipeline.
