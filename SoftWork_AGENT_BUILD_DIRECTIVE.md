# SoftWork — Agent Build Directive
## Repository Correction, CAD-Core Refactor, and Forward Architecture

**Project:** SoftWork  
**Repository:** https://github.com/johnfaleke/SoftWork  
**Document type:** Engineering directive for the coding agent  
**Priority:** Correctness and architectural integrity over feature count or UI polish

---

# 0. Mission

You are working on **SoftWork**, an open-source, desktop-first, AI-native parametric CAD application.

SoftWork is not supposed to be:

- a chatbot attached to a 3D viewer;
- a mesh generator;
- a collection of hard-coded demo primitives;
- a UI imitation of SolidWorks;
- a custom toy CAD kernel hidden behind a professional interface;
- an AI system that deletes and recreates geometry while pretending to edit parameters.

SoftWork must become:

> A real parametric CAD application in which the user can create and modify editable engineering models through conventional CAD operations and natural-language AI commands.

The core product loop is:

```text
Human intent
    ↓
AI interpretation / planning
    ↓
Validated SoftWork commands
    ↓
Document + feature graph
    ↓
CadQuery / OCP
    ↓
OpenCASCADE geometry
    ↓
Validation
    ↓
Viewport + feature tree + properties
    ↓
Human review and undo
```

The user remains the designer.  
The AI is an operator/reasoner.  
The document model owns design intent.  
OpenCASCADE is the geometric authority.

---

# 1. Current state assessment

The repository already contains substantial prototype work:

- PySide6 desktop interface;
- feature tree and property panels;
- sketches and constraints;
- primitive and feature classes;
- commands;
- AI providers and tools;
- parameter mutation;
- serialization;
- tests;
- CadQuery integration;
- a custom direct geometry backend.

Do not delete the project or restart from zero.

However, the current code must be treated as a **prototype that needs architectural correction** before more feature expansion.

The following issues are the immediate priority:

1. The custom direct geometry backend must not silently impersonate a real CAD kernel.
2. CadQuery/OCP/OpenCASCADE must become the authoritative production geometry path.
3. Backend failures must be visible, typed, and recoverable.
4. The dependency graph must drive rebuild order.
5. Feature references must survive serialization and recomputation.
6. Convenience features must not replace the canonical parametric feature history.
7. AI must operate through the same command system as the GUI.
8. The UI must be frozen temporarily while the core is corrected.
9. Existing tests must be preserved, but new integration tests must test actual architectural guarantees.
10. Every change must be small, reviewable, and committed separately.

Do not add lofts, assemblies, drawings, simulation, more themes, or more AI providers until the core refactor is stable.

---

# 2. Non-negotiable engineering rules

## 2.1 No silent geometry fallback

Do not do this:

```python
try:
    return cadquery_operation()
except Exception:
    return direct_geometry_operation()
```

This is forbidden for the authoritative CAD path.

If CadQuery/OCP/OpenCASCADE fails:

```text
CAD_OPERATION_FAILED
```

must be returned as a structured failure.

The application must show:

- operation name;
- feature ID;
- input references;
- parameter values;
- backend error;
- whether the previous valid geometry was preserved;
- suggested corrective actions where possible.

The custom direct backend may remain temporarily for:

- isolated prototype tests;
- lightweight previews;
- development diagnostics;
- explicit experimental mode.

It must not be used silently for production geometry.

---

## 2.2 One authoritative geometry backend

The intended production path is:

```text
SoftWork feature/document system
        ↓
CADBackend abstraction
        ↓
CadQueryBackend
        ↓
OCP
        ↓
OpenCASCADE
        ↓
B-rep Shape
        ↓
tessellation for viewport
```

Do not maintain two competing CAD authorities.

The custom direct backend must be clearly marked as one of:

- `PrototypeGeometryBackend`;
- `PreviewGeometryBackend`;
- `LegacyGeometryBackend`.

It must never be selected by default for real CAD documents.

---

## 2.3 The document model must not depend on backend internals

SoftWork owns:

- document;
- part/body;
- feature;
- parameter;
- dependency;
- reference;
- transaction;
- validation result;
- provenance;
- serialization.

CadQuery owns the construction of geometric shapes.

Do not make the entire SoftWork document model equal to CadQuery's internal object graph.

A feature should store declarative information such as:

```python
{
    "id": "extrude_001",
    "type": "extrude",
    "profile_ref": "sketch_001",
    "distance": 10.0,
    "direction": "normal",
    "operation": "add"
}
```

It should not rely on a live Python object reference as the only way to identify its input.

---

## 2.4 No fake parametric editing

This is invalid:

```text
delete old object
create new object with similar dimensions
```

when the user asked:

```text
make the existing extrusion 15 mm thick
```

The expected operation is:

```text
Extrude001.distance = 15 mm
```

followed by dependency-aware recomputation.

Convenience features such as `MountingPlateFeature` may remain, but the canonical demonstration must use a real feature chain:

```text
Sketch001
    ↓
Extrude001
    ↓
Hole001 / HoleWizard001
    ↓
Pattern001
    ↓
Fillet001
```

---

# 3. Required first phase: repository audit

Before changing behavior, inspect the repository and produce:

```text
docs/ARCHITECTURE_AUDIT.md
```

The audit must include a table with:

| File/module | Current responsibility | Keep / Rewrite / Deprecate / Delete / Defer | Reason | Risk |
|---|---|---|---|---|

Inspect at minimum:

```text
src/softwork/core/
src/softwork/cad/
src/softwork/commands/
src/softwork/ai/
src/softwork/qt/
src/softwork/sketch/
tests/
pyproject.toml
README.md
SoftWork.md
```

The audit must answer:

1. What is the actual default geometry backend?
2. Where can geometry silently fall back?
3. Which features produce real OpenCASCADE shapes?
4. Which features only produce custom mesh-like geometry?
5. Does `Document.recompute()` use the dependency graph?
6. Which features store live object references?
7. Which features serialize only IDs?
8. How are failed rebuilds represented?
9. How does undo/redo restore geometry?
10. Which AI commands bypass the command layer?
11. Which tests verify actual geometry and which only verify metadata?
12. What is the current package/version mismatch?
13. Which dependencies are optional versus required?
14. What is the current behavior when CadQuery/OCP is unavailable?

Do not make broad changes before this audit is complete.

---

# 4. Target architecture

## 4.1 Target package layout

Move toward this structure without performing a reckless all-at-once rewrite:

```text
src/softwork/
├── app/
│   ├── main.py
│   └── bootstrap.py
├── core/
│   ├── document.py
│   ├── part.py
│   ├── body.py
│   ├── feature.py
│   ├── parameter.py
│   ├── dependency.py
│   ├── reference.py
│   ├── transaction.py
│   ├── errors.py
│   ├── validation.py
│   └── provenance.py
├── cad/
│   ├── backend.py
│   ├── cadquery_backend.py
│   ├── shape.py
│   ├── tessellation.py
│   ├── topology.py
│   └── capabilities.py
├── features/
│   ├── base.py
│   ├── sketch.py
│   ├── extrude.py
│   ├── revolve.py
│   ├── hole.py
│   ├── pattern.py
│   ├── fillet.py
│   ├── chamfer.py
│   └── shell.py
├── commands/
│   ├── base.py
│   ├── feature_commands.py
│   ├── parameter_commands.py
│   ├── transaction_commands.py
│   └── registry.py
├── ai/
│   ├── provider.py
│   ├── agent.py
│   ├── planner.py
│   ├── tools.py
│   ├── context.py
│   ├── validation.py
│   └── modifier.py
├── formats/
│   ├── softwork_format.py
│   ├── step.py
│   ├── stl.py
│   └── dxf.py
└── qt/
    ├── main_window.py
    ├── viewport.py
    ├── feature_tree.py
    ├── property_manager.py
    └── copilot.py
```

Do not move files merely for aesthetics. Move them when it improves ownership, dependency direction, testing, or maintainability.

---

## 4.2 Dependency direction

Enforce this dependency direction:

```text
UI
 ↓
Commands / Application Services
 ↓
Document Core
 ↓
Feature Definitions
 ↓
CAD Backend Interface
 ↓
CadQuery/OCP/OpenCASCADE
```

AI may call commands and application services.

AI must not directly mutate arbitrary feature internals.

The UI must not directly construct OpenCASCADE shapes.

The document core must not import PySide6.

The CAD backend must not import the Qt UI.

---

# 5. CAD backend correction

## 5.1 Backend interface

Define a clear backend interface with typed results.

Example:

```python
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class CADOperationError:
    code: str
    message: str
    operation: str
    feature_id: Optional[str] = None
    details: dict[str, Any] | None = None

@dataclass
class CADResult:
    success: bool
    shape: Any | None = None
    error: CADOperationError | None = None
```

The exact implementation may differ, but the behavior must be equivalent.

Required operations should include:

```text
create_box
create_cylinder
create_sketch_profile
extrude
revolve
cut
union
intersect
hole
pattern
fillet
chamfer
shell
tessellate
validate
export_step
export_stl
```

Every operation must:

- validate inputs;
- return a typed result;
- preserve the original shape on failure;
- expose backend errors;
- avoid silently switching geometry engines.

---

## 5.2 CadQuery backend policy

The CadQuery backend must:

1. be the default production backend;
2. explicitly verify that CadQuery/OCP is installed;
3. expose a clear unavailable state if dependencies are missing;
4. convert CadQuery/OCP shapes into a stable SoftWork shape wrapper;
5. provide tessellation separately from geometric truth;
6. validate solids before committing them to the document;
7. preserve backend exceptions for diagnostics;
8. avoid leaking CadQuery objects throughout the UI and document layers.

The viewport may receive mesh data generated from the authoritative B-rep shape.

The mesh is a display representation, not the design truth.

---

## 5.3 Direct backend policy

Do not immediately delete the current direct backend if it is useful for tests.

Instead:

1. rename or mark it clearly as prototype/preview;
2. remove it as the default;
3. add warnings when it is explicitly selected;
4. prevent it from being used for STEP export;
5. prevent it from being presented as validated engineering geometry;
6. add tests proving it cannot silently replace CadQuery.

Eventually decide whether to delete it.

---

# 6. Rebuild engine

## 6.1 Required behavior

The dependency graph must become the actual rebuild engine.

The correct conceptual flow is:

```text
parameter/reference change
        ↓
find affected features
        ↓
topologically sort affected features
        ↓
evaluate each feature
        ↓
validate result
        ↓
commit successful results
        ↓
preserve previous valid state on failure
```

Do not rely only on the order in which features happen to be stored in a list.

---

## 6.2 Feature dependencies

Every feature must declare:

```text
feature_id
feature_type
input_references
parameter_values
dependency_ids
generated_shape
validation_state
provenance
```

Example:

```python
@dataclass
class FeatureDefinition:
    id: str
    type: str
    inputs: dict[str, str]
    parameters: dict[str, Any]
    dependencies: list[str]
```

The document resolves IDs to features during evaluation.

Do not rely on object identity as the primary reference mechanism.

---

## 6.3 Rebuild states

Every feature should have explicit states:

```text
UNBUILT
BUILDING
VALID
FAILED
SUPPRESSED
OUT_OF_DATE
```

A failed feature must expose:

- failure code;
- human-readable message;
- backend details;
- affected descendants;
- previous valid shape if available.

A failed rebuild must not destroy the last valid model.

---

## 6.4 Transactional rebuild

A rebuild must be transactional:

```text
capture previous state
        ↓
apply requested parameter changes
        ↓
recompute affected graph
        ↓
validate all affected features
        ↓
if all succeed:
    commit
else:
    restore previous valid state
    expose failure
```

For a multi-parameter change:

```text
resize width to 80
resize length to 120
```

the operation must be atomic.

Do not leave half-applied parameter changes if the second operation fails.

---

# 7. Canonical feature chain

Build and test the following canonical model without using `MountingPlateFeature`:

```text
Sketch001
    └── centered rectangle: 100 × 60 mm

Extrude001
    └── distance: 10 mm

Hole001
    └── M8 hole or cylindrical cut

Pattern001
    └── four instances positioned from the corners

Fillet001
    └── radius: 2 mm
```

The exact internal feature names may differ, but the model must have separate feature nodes and dependencies.

The following actions must work:

```text
1. Create the sketch.
2. Extrude it.
3. Add a hole.
4. Pattern the hole.
5. Fillet appropriate edges.
6. Change extrusion thickness from 10 mm to 15 mm.
7. Change hole size from M8 to M10.
8. Change fillet radius from 2 mm to 4 mm.
9. Save.
10. Close.
11. Reopen.
12. Rebuild.
13. Export STEP.
```

The final model must remain editable.

---

# 8. AI architecture correction

## 8.1 AI must call commands

The AI flow must be:

```text
user prompt
    ↓
context builder
    ↓
provider
    ↓
structured plan/tool calls
    ↓
tool schema validation
    ↓
SoftWork command registry
    ↓
transaction
    ↓
rebuild
    ↓
validation
    ↓
result/explanation
```

The AI must not:

- directly edit arbitrary Python objects;
- directly call random backend methods without command validation;
- execute unrestricted Python;
- silently create replacement geometry;
- claim success when the transaction failed.

---

## 8.2 Tool schemas

Every AI tool must define:

```text
name
description
input schema
required fields
units
allowed references
permission level
preview support
undo behavior
failure behavior
```

Example:

```json
{
  "name": "parameter.set",
  "description": "Change one existing feature parameter",
  "input": {
    "feature_id": "Extrude001",
    "parameter": "distance",
    "value": 15,
    "unit": "mm"
  }
}
```

The agent must resolve natural language to existing feature IDs and parameters.

It must not depend on special-case names such as `MountingPlateFeature`.

---

## 8.3 AI response contract

Every AI operation should return:

```text
Interpretation
Plan
Commands
Affected features
Validation result
Changes applied
Warnings
Undo availability
```

For example:

```text
Interpretation:
Increase the existing extrusion thickness.

Change:
Extrude001.distance: 10 mm → 15 mm

Affected:
Extrude001
Hole001
Pattern001
Fillet001

Result:
Valid rebuild

[Undo]
```

If the operation fails:

```text
Result:
Rebuild failed

Reason:
Fillet radius exceeds available geometry.

State:
Previous valid model preserved.
```

---

# 9. Serialization requirements

The `.softwork` format must store declarative document data, not live Python objects.

At minimum store:

```text
document metadata
units
parts/bodies
feature definitions
feature IDs
input references
dependencies
parameters
constraints
semantic references
validation state
history/provenance
materials
AI operation history where appropriate
```

A saved file must be rebuildable after restarting the application.

Required test:

```text
create model
save
close process
open file in fresh process
rebuild from definitions
compare:
    feature IDs
    feature types
    parameters
    dependencies
    bounding box
    volume within tolerance
    exportability
```

Do not serialize raw backend objects as the primary source of truth.

---

# 10. Validation requirements

Create structured validation results.

Validation should distinguish:

```text
VALID
WARNING
FAILED
```

Check as applicable:

- shape exists;
- shape is a solid;
- volume is positive;
- no invalid topology;
- no failed boolean;
- no missing references;
- no broken dependencies;
- no zero-thickness result;
- no invalid parameter;
- export succeeds;
- tessellation succeeds.

Do not claim “rebuild clean” if validation has not actually run.

---

# 11. Undo and redo

Every command must be undoable.

Every AI request that mutates the document must be one user-level transaction.

Example:

```text
AI Transaction #42
    before state
    interpreted request
    commands
    affected features
    validation
    after state
```

Undo must restore:

- parameter values;
- feature states;
- dependency state;
- geometry;
- validation state;
- selection where practical.

Redo must reapply the same validated operation.

Do not implement undo as merely “create another replacement object.”

---

# 12. Testing plan

Add tests in layers.

## 12.1 Backend tests

- CadQuery availability;
- box shape;
- cylinder shape;
- extrusion;
- cut;
- union;
- fillet;
- chamfer;
- shell;
- tessellation;
- STEP export;
- invalid operation behavior;
- no silent fallback.

## 12.2 Document tests

- feature insertion;
- ID resolution;
- dependency registration;
- topological rebuild order;
- affected-descendant detection;
- failed rebuild preservation;
- serialization;
- unit conversion;
- transactions;
- undo/redo.

## 12.3 Integration test

Create:

```text
Sketch → Extrude → Hole → Pattern → Fillet
```

Then test:

```text
Extrude 10 → 15
M8 → M10
Fillet 2 → 4
```

Then deliberately test:

```text
Fillet radius → 1000
```

Expected:

```text
operation fails
previous valid state remains
feature marked FAILED
error visible
undo available
```

Then recover:

```text
Fillet radius → 2
```

Expected:

```text
model becomes valid again
```

Then save, restart, reopen, rebuild, and export.

## 12.4 AI tests

Test prompts such as:

```text
Make the existing extrusion 15 mm thick.
Change the holes from M8 to M10.
Increase the fillet radius to 4 mm.
Resize the width to 80 mm and length to 120 mm.
What feature is selected?
Why did the fillet fail?
```

Judge the resulting document state, not the quality of the prose.

---

# 13. UI requirements during this phase

Freeze visual expansion.

Do not add:

- new themes;
- new ribbon tabs;
- decorative HUD elements;
- more icons;
- more visual effects;
- more fake status indicators.

Only change UI when needed to expose real core behavior:

- feature state;
- rebuild progress;
- validation errors;
- backend availability;
- transaction preview;
- affected features;
- undo/redo;
- parameter references.

The UI must never display:

```text
Rebuilt: Clean
```

unless the document actually completed a successful validated rebuild.

---

# 14. Version plan

## v0.4.1 — Architecture audit

Deliver:

- architecture audit;
- backend call-path map;
- list of silent fallbacks;
- dependency/rebuild analysis;
- test gap report.

## v0.4.2 — Backend authority

Deliver:

- CadQuery backend as default;
- no silent fallback;
- typed CAD errors;
- explicit prototype backend mode;
- backend availability diagnostics.

## v0.4.3 — Rebuild engine

Deliver:

- dependency graph-driven evaluation;
- explicit feature states;
- affected-descendant recomputation;
- failed rebuild preservation.

## v0.4.4 — Stable references and serialization

Deliver:

- ID-based feature references;
- declarative serialization;
- fresh-process reload;
- rebuild after reopening.

## v0.4.5 — Canonical parametric chain

Deliver:

- Sketch → Extrude → Hole → Pattern → Fillet;
- parameter editing;
- geometry validation;
- STEP export;
- undo/redo.

## v0.4.6 — AI command integrity

Deliver:

- AI through command registry;
- typed tool schemas;
- transaction boundaries;
- clear plans and change summaries;
- no special-case mounting plate dependence.

## v0.5 — Advanced part modeling

Only begin after the above is stable:

- loft;
- sweep;
- draft;
- shell improvements;
- advanced patterns;
- better sketch constraints;
- more robust topology references.

## v0.6 — Assemblies

- components;
- mates;
- interference;
- assembly tree;
- BOM.

## v0.7 — Drawings

- orthographic views;
- dimensions;
- annotations;
- sections;
- PDF/DXF.

## v0.8 — AI engineering agent

- multi-step design plans;
- design alternatives;
- multimodal input;
- manufacturing-aware suggestions;
- constraint reasoning;
- model comparison.

## v1.0

Do not define v1.0 by the number of features.

Define it by:

- reliable rebuilds;
- deterministic geometry;
- inspectable history;
- stable file format;
- predictable undo/redo;
- usable manual CAD;
- AI that cannot silently corrupt the model.

---

# 15. Git workflow

Use small commits:

```text
docs: add architecture audit
refactor: make CadQuery backend authoritative
fix: remove silent geometry fallback
refactor: make rebuild graph-driven
feat: add explicit feature build states
refactor: replace live feature references with IDs
test: add failed rebuild preservation coverage
test: add fresh-process serialization integration test
refactor: route AI mutations through command registry
```

Do not mix:

```text
core refactor + UI redesign + new feature + theme changes
```

in one commit.

Before each commit:

```text
run full test suite
run targeted integration tests
inspect git diff
update changelog
```

---

# 16. Definition of done for this directive

This directive is complete only when:

- CadQuery/OCP/OpenCASCADE is the default authoritative geometry path;
- no backend failure silently falls back;
- direct geometry is clearly prototype-only or removed;
- dependency graph drives rebuild order;
- feature references are ID-based;
- failed rebuilds preserve the last valid model;
- the canonical feature chain works;
- parameter edits mutate existing features;
- save/restart/reopen/rebuild works;
- STEP export uses authoritative geometry;
- AI uses typed commands and transactions;
- tests cover valid and invalid operations;
- UI status reflects real system state;
- architecture documentation matches implementation.

---

# 17. Agent behavior

When implementing this directive:

1. Inspect before editing.
2. Explain the current behavior with file and function names.
3. Make one coherent change at a time.
4. Do not invent successful behavior.
5. Do not hide failures.
6. Do not add features to avoid fixing architecture.
7. Preserve working functionality where possible.
8. Add tests before or alongside risky changes.
9. Prefer explicit errors over silent fallback.
10. Keep the user informed of:
   - what changed;
   - why it changed;
   - which tests passed;
   - which limitations remain;
   - what should be built next.

The agent must not declare a milestone complete merely because the UI looks correct.

The milestone is complete only when the underlying document, dependency, geometry, validation, serialization, and transaction behavior are correct.

---

# Final directive

Do not make SoftWork look more like CAD.

Make SoftWork **behave more like CAD**.

The immediate goal is not another feature.

The immediate goal is:

> Build one honest, editable, validated, restartable parametric model through a real CadQuery/OCP/OpenCASCADE pipeline, with dependency-aware rebuilds and reversible AI commands.

Start with the audit.

Then correct the geometry authority.

Then correct the rebuild engine.

Then prove the canonical feature chain.

Only after that should SoftWork expand.
