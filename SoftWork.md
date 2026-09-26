# SoftWork — Product & Engineering Master Plan

> **Status:** Pre-alpha / Architecture Locked for Initial Build  
> **Project:** SoftWork  
> **Tagline:** AI-native parametric CAD  
> **Primary Goal:** Build a full desktop CAD application where engineers can create, understand, and modify real parametric 3D models through conventional CAD tools and natural-language AI.

---

# 1. Product Overview

## 1.1 What is SoftWork?

**SoftWork** is an open-source, desktop-first, AI-native parametric CAD application.

The core idea is:

> **Human intent → AI reasoning → structured engineering operations → parametric CAD → validated geometry → human review**

Instead of treating AI as a chatbot sitting beside a CAD program, SoftWork makes natural language a first-class interface to the CAD system.

A user should eventually be able to say:

> "Create a 100 × 60 × 10 mm mounting plate."

SoftWork should create a real parametric model.

Then:

> "Add four M8 holes, 10 mm from each corner."

SoftWork should modify the existing model.

Then:

> "Make the plate 15 mm thick."

SoftWork should change the relevant parameter in the existing feature history rather than regenerate an unrelated shape.

The resulting model must remain:

- editable
- parametric
- inspectable
- reproducible
- exportable
- compatible with conventional CAD workflows

---

# 2. Product Thesis

Traditional CAD gives engineers enormous control but requires users to understand the application's interaction model.

Generative AI can understand natural language but often produces geometry that lacks engineering structure.

SoftWork combines the two.

### SoftWork principle

> **AI understands what the engineer means. CAD determines what geometry actually exists.**

The AI should reason about:

- user intent
- design requirements
- feature selection
- parameters
- dependencies
- constraints
- engineering context

The CAD system should remain responsible for:

- exact geometry
- topology
- feature execution
- constraints
- document state
- validation
- deterministic results

The user remains the final authority.

---

# 3. Product Vision

SoftWork should eventually become a complete engineering design environment.

## Long-term capabilities

### Part design

- sketches
- constraints
- extrusions
- revolutions
- cuts
- unions
- fillets
- chamfers
- holes
- patterns
- mirrors
- lofts
- sweeps
- shells
- thickness
- drafts
- surface modeling

### Assemblies

- components
- mates
- constraints
- motion
- interference detection
- component libraries
- BOM
- assembly relationships

### Drawings

- orthographic views
- section views
- detail views
- dimensions
- annotations
- tolerances
- title blocks
- BOM
- PDF export
- DXF export

### Engineering workflows

- materials
- manufacturing methods
- tolerances
- standard fasteners
- mechanical interfaces
- design rules
- design alternatives
- manufacturability awareness

### Simulation

Eventually integrate appropriate external solvers for:

- structural analysis
- thermal analysis
- motion
- modal analysis
- fluid analysis

SoftWork should **not** attempt to build a complete simulation engine during early development.

---

# 4. What SoftWork Is

SoftWork is:

- a desktop CAD application
- a parametric modeling environment
- a mechanical design tool
- an AI-assisted engineering environment
- an AI-native CAD interface
- an open-source project
- a future engineering design platform

---

# 5. What SoftWork Is Not

SoftWork is not:

- an image generator
- a mesh-only 3D generator
- an AI chatbot with a 3D viewer
- a web wrapper around another CAD application
- a cloud-only CAD service
- a SolidWorks clone with a different logo
- a replacement for deterministic geometry
- a simulation engine in v0.x
- an unrestricted AI Python executor

The distinction is important.

The product is the **CAD system**, not the AI.

AI is one of the interfaces and reasoning layers of the CAD system.

---

# 6. Core Product Principles

These principles are non-negotiable.

## 6.1 AI is the reasoner, not the geometry authority

AI can decide:

> "The user probably wants a centered rectangular sketch."

But AI should not directly invent arbitrary geometry.

The CAD engine executes structured operations.

---

## 6.2 Parametric intent over visual imitation

SoftWork should prefer:

```text
Sketch
→ Constraint
→ Dimension
→ Extrude
→ Hole
→ Pattern
```

over:

```text
AI guesses what the shape looks like
→ generates mesh
→ user cannot edit it
```

---

## 6.3 Every AI change must be inspectable

If AI changes:

```text
Extrude001
10 mm → 15 mm
```

the user should be able to see exactly what changed.

---

## 6.4 Deterministic CAD is the source of truth

AI responses are not the source of truth.

The CAD document is.

The geometry kernel is authoritative about whether geometry is valid.

---

## 6.5 Provider independence

SoftWork should not be architecturally tied to one AI company.

Potential providers:

* OpenAI
* Anthropic
* Google
* local models
* open-weight models
* future providers

The AI provider should be replaceable.

---

## 6.6 Offline-capable CAD core

The CAD engine should function without internet access.

AI may require network access depending on the provider.

The core modeling workflow should not.

---

## 6.7 User ownership

Users should own their project files.

SoftWork should prioritize open formats and interoperability.

---

## 6.8 Traditional CAD remains first-class

A professional user must be able to use SoftWork without AI.

The application should support:

* mouse interaction
* keyboard shortcuts
* menus
* toolbars
* command palette
* property editing
* feature tree
* direct viewport interaction

AI is an additional interface, not a mandatory one.

---

# 7. The "AI Coding Agent for CAD" Analogy

One of the strongest product references is the modern AI coding agent.

A coding agent can:

1. understand intent
2. inspect a codebase
3. plan changes
4. call tools
5. modify files
6. run tests
7. inspect failures
8. fix problems
9. show the user what changed

SoftWork should apply the same pattern to engineering design.

### AI coding

```text
Intent
 ↓
Plan
 ↓
Tool calls
 ↓
Code changes
 ↓
Tests
 ↓
Validation
```

### SoftWork

```text
Engineering intent
 ↓
Design plan
 ↓
CAD operations
 ↓
Parametric feature changes
 ↓
Geometry validation
 ↓
Human review
```

This is the central interaction model.

---

# 8. Example User Experience

User:

> Create a 100 × 60 × 10 mm mounting plate.

SoftWork plans:

```text
1. Create sketch on XY plane
2. Create centered rectangle
3. Constrain width = 100 mm
4. Constrain height = 60 mm
5. Extrude = 10 mm
6. Validate solid
```

The resulting feature tree:

```text
Part
├── Sketch001
└── Extrude001
```

User:

> Add four M8 holes, 10 mm from each corner.

SoftWork:

```text
Sketch001
Extrude001
Hole001
Pattern001
```

User:

> Make it 15 mm thick.

SoftWork should recognize that the correct operation is probably:

```text
Extrude001.length:
10 mm → 15 mm
```

not:

```text
Delete everything
Generate another plate
Hope the holes survive
```

---

# 9. AI Change Preview

For a simple parameter modification:

```text
┌───────────────────────────────────────┐
│ AI CHANGE                             │
│                                       │
│ Extrude001                            │
│ 10 mm → 15 mm                         │
│                                       │
│ Affected:                             │
│ ✓ Base thickness                      │
│                                       │
│ Preserved:                            │
│ ✓ Width                               │
│ ✓ Length                              │
│ ✓ Hole pattern                        │
│ ✓ Fillets                             │
│                                       │
│ [Apply] [Undo] [Edit]                 │
└───────────────────────────────────────┘
```

For larger changes, SoftWork should eventually provide:

* before/after comparison
* affected features
* changed parameters
* validation result
* assumptions
* warnings

---

# 10. Product Architecture

High-level architecture:

```text
                           SOFTWORK
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
           UI Layer       AI Layer         Document Core
              │               │                │
              │               ▼                │
              │         Agent / Planner        │
              │               │                │
              │          Tool Calling          │
              │               │                │
              └───────────────┼────────────────┘
                              ▼
                       CAD Abstraction
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
             CadQuery       FreeCAD       OCP
                 │            │            │
                 └────────────┼────────────┘
                              ▼
                         OpenCascade
                              │
                              ▼
                        CAD Geometry
```

The architecture must keep the major concerns separate.

---

# 11. Technology Stack

## Primary language

```text
Python
```

Python is the initial language because:

* CadQuery is Python-native
* OCP exposes OpenCASCADE through Python
* AI integrations are easy
* rapid development is possible
* the ecosystem is large

Performance-critical components can later move to C++ or native libraries where necessary.

---

# 12. Desktop UI

Initial:

```text
Qt 6
PySide6
```

Reasons:

* mature desktop framework
* cross-platform
* native-feeling UI
* suitable for complex professional applications
* compatible with Python

Target platforms:

```text
Windows
Linux
macOS
```

Primary development platform:

```text
Windows
```

Platform-specific code should remain isolated.

---

# 13. CAD Stack

Initial CAD stack:

```text
SoftWork
   ↓
CAD Abstraction
   ↓
CadQuery
   ↓
OCP
   ↓
OpenCASCADE
```

---

# 14. OpenCASCADE

OpenCASCADE Technology (OCCT) is the geometric foundation.

It is responsible for concepts such as:

* B-rep geometry
* solids
* shells
* faces
* edges
* vertices
* boolean operations
* geometric algorithms
* topology

SoftWork should not attempt to create its own CAD kernel.

---

# 15. OCP

OCP provides Python bindings around OpenCASCADE.

It gives the Python ecosystem access to OCCT functionality.

SoftWork should use it where lower-level geometry access is required.

---

# 16. CadQuery

CadQuery provides a high-level Python-based parametric CAD interface.

It is useful for:

* programmatic geometry
* feature operations
* parametric construction
* rapid prototyping
* AI-generated structured modeling operations

CadQuery should be the initial high-level CAD backend.

---

# 17. FreeCAD

FreeCAD is a mature open-source parametric CAD application.

It provides useful concepts and infrastructure around:

* document objects
* feature trees
* sketches
* constraints
* workbenches
* Python scripting
* GUI architecture
* file formats
* OCCT

However:

> **FreeCAD should not automatically become the foundation of SoftWork.**

Initially, SoftWork should study and integrate with the ecosystem where useful.

A FreeCAD backend may be introduced later.

Potential architecture:

```text
SoftWork CAD Abstraction
        │
        ├── CadQueryBackend
        │
        ├── FreeCADBackend
        │
        └── DirectOCCTBackend
```

This prevents the entire product from being coupled to one implementation.

---

# 18. Repository Strategy

Primary repository:

```text
github.com/<you>/softwork
```

Potential forks:

```text
github.com/<you>/cadquery
github.com/<you>/FreeCAD
```

However:

> Forking does not mean immediately modifying them.

Fork only when there is a concrete reason.

---

# 19. Git Remote Strategy

For an active fork:

```text
origin   → your fork
upstream → original project
```

Example:

```bash
git remote -v
```

Expected:

```text
origin    git@github.com:<you>/cadquery.git
upstream  https://github.com/CadQuery/cadquery.git
```

This allows SoftWork-specific work while retaining the ability to pull upstream improvements.

---

# 20. Main SoftWork Repository

Initial structure:

```text
softwork/
├── src/
│   └── softwork/
│       ├── __init__.py
│       │
│       ├── app/
│       │   ├── __init__.py
│       │   └── main.py
│       │
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   ├── viewport.py
│       │   ├── panels/
│       │   └── widgets/
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── document.py
│       │   ├── part.py
│       │   ├── feature.py
│       │   ├── parameter.py
│       │   ├── dependency.py
│       │   ├── constraint.py
│       │   ├── selection.py
│       │   └── history.py
│       │
│       ├── cad/
│       │   ├── __init__.py
│       │   ├── backend.py
│       │   ├── cadquery_backend.py
│       │   ├── geometry.py
│       │   ├── topology.py
│       │   └── validation.py
│       │
│       ├── ai/
│       │   ├── __init__.py
│       │   ├── provider.py
│       │   ├── agent.py
│       │   ├── planner.py
│       │   ├── context.py
│       │   ├── tools.py
│       │   ├── validation.py
│       │   ├── memory.py
│       │   └── providers/
│       │
│       ├── document/
│       │   ├── __init__.py
│       │   ├── serializer.py
│       │   ├── loader.py
│       │   └── schema.py
│       │
│       ├── formats/
│       │   ├── __init__.py
│       │   ├── step.py
│       │   ├── stl.py
│       │   ├── dxf.py
│       │   └── iges.py
│       │
│       └── services/
│           ├── __init__.py
│           ├── workers.py
│           ├── settings.py
│           └── logging.py
│
├── tests/
│   ├── unit/
│   ├── cad/
│   ├── document/
│   ├── ai/
│   └── integration/
│
├── examples/
│
├── docs/
│
├── assets/
│
├── scripts/
│
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── THIRD_PARTY_NOTICES
└── .gitignore
```

---

# 21. CAD Abstraction

SoftWork must not make CadQuery's internal objects the entire application model.

The product should own its own abstraction.

Example:

```python
class CADBackend:
    def create_box(self, width, height, depth):
        ...

    def create_cylinder(self, radius, height):
        ...

    def extrude(self, profile, distance):
        ...

    def cut(self, base, tool):
        ...

    def union(self, a, b):
        ...

    def intersect(self, a, b):
        ...

    def fillet(self, shape, radius):
        ...

    def chamfer(self, shape, distance):
        ...

    def export_step(self, shape, path):
        ...
```

The exact API will evolve.

The purpose is architectural separation.

---

# 22. Document Core

SoftWork's document model should represent engineering intent rather than simply storing geometry.

Conceptually:

```text
Document
├── Metadata
├── Parameters
├── Bodies
├── Sketches
├── Features
├── Assemblies
├── Materials
├── References
├── Constraints
└── History
```

---

# 23. Feature Model

Each feature should contain information such as:

* ID
* type
* inputs
* parameters
* references
* dependencies
* generated geometry
* validation state
* provenance
* design intent

Example:

```yaml
feature:
  id: extrude_001
  type: extrude
  profile: sketch_001
  length: 10mm
  direction: normal
  operation: add
```

---

# 24. Dependency Graph

Internally, SoftWork should maintain a dependency graph.

Example:

```text
Sketch001
    │
    ▼
Extrude001
    │
    ▼
HolePattern001
    │
    ▼
Fillet001
```

The UI can display this as a traditional feature tree.

The underlying representation should support dependency-aware updates.

---

# 25. Parameters

Parameters should be typed.

Do not represent every dimension as an arbitrary string.

Example:

```python
Parameter(
    name="thickness",
    value=10,
    unit="mm"
)
```

Future parameters may support expressions:

```text
thickness = plate_width / 10
```

Parameters should eventually support:

* values
* units
* expressions
* references
* constraints
* metadata
* provenance

---

# 26. Units

Initial supported units:

```text
mm
cm
m
in
ft
deg
rad
```

Internally use canonical units.

Users should be able to enter:

```text
10mm
1cm
0.5in
10 deg
```

The system should normalize them consistently.

---

# 27. Feature History

Feature history should behave similarly to established parametric CAD systems.

Example:

```text
Part
├── Sketch001
├── Extrude001
├── Hole001
├── Pattern001
└── Fillet001
```

Changing `Extrude001` should cause dependent features to regenerate where possible.

---

# 28. Parametric Operations

Initial operations:

```text
Primitive
Sketch
Extrude
Cut
Union
Intersect
Revolve
Hole
Fillet
Chamfer
Pattern
Mirror
```

Later:

```text
Loft
Sweep
Shell
Draft
Offset
Thickness
Advanced Patterns
Surface Features
```

---

# 29. Sketch System

The sketch system will eventually support:

### Geometry

* line
* arc
* circle
* rectangle
* spline
* construction geometry

### Constraints

* coincident
* horizontal
* vertical
* tangent
* parallel
* perpendicular
* equal
* symmetric
* concentric
* distance
* angle
* radius
* diameter

AI should eventually be able to create and modify sketches.

---

# 30. AI Architecture

The AI subsystem:

```text
ai/
├── providers/
├── agent/
├── planner/
├── tools/
├── context/
├── validation/
├── memory/
└── prompts/
```

---

# 31. AI Provider Abstraction

SoftWork should not call one AI vendor directly throughout the codebase.

Create an abstraction:

```python
class ModelProvider:
    def generate(self, messages, **kwargs):
        ...

    def stream(self, messages, **kwargs):
        ...

    def tool_call(self, messages, tools, **kwargs):
        ...
```

Provider implementations can later include:

```text
OpenAIProvider
AnthropicProvider
GoogleProvider
LocalProvider
```

The actual API details must stay inside provider implementations.

---

# 32. AI Agent Pipeline

Default pipeline:

```text
UNDERSTAND
     ↓
PLAN
     ↓
EXECUTE
     ↓
VALIDATE
```

For simple requests, the stages can be hidden.

For complex requests, the plan should be visible.

Example:

```text
User:
Create a bracket for a 20 mm shaft.

AI:
I will:
1. Create the base plate.
2. Create the mounting holes.
3. Create the shaft interface.
4. Add the required fillets.
5. Validate the resulting solid.
```

---

# 33. AI Tool Calling

The AI should not directly manipulate the CAD engine.

It should call controlled tools.

Initial tools:

```text
document.create
document.open
document.save

selection.inspect
geometry.measure

sketch.create
sketch.add_line
sketch.add_circle
sketch.add_rectangle

constraint.add

parameter.set

feature.extrude
feature.cut
feature.revolve
feature.hole
feature.fillet
feature.chamfer
feature.pattern
feature.mirror

history.undo
history.redo

model.validate

export.step
export.stl
export.dxf
```

---

# 34. Tool Schema Requirements

Every AI tool should have:

* strict input schema
* typed parameters
* validation
* permission level
* preview behavior
* undo information
* error handling

Example conceptual schema:

```json
{
  "name": "feature.extrude",
  "description": "Create an extrusion from an existing sketch",
  "parameters": {
    "profile_id": "string",
    "distance": "length",
    "operation": "add|cut"
  }
}
```

---

# 35. No Unrestricted AI Execution

The first versions must not allow:

```text
LLM → arbitrary Python → filesystem → shell → network
```

Instead:

```text
LLM
 ↓
Typed tool call
 ↓
SoftWork command layer
 ↓
Validated CAD operation
```

If arbitrary scripting is eventually introduced, it must be sandboxed.

---

# 36. AI Context

Do not send the entire model history to the AI on every request.

Use structured context.

Possible context levels:

```text
Level 1 — Current selection
Level 2 — Current feature
Level 3 — Local dependency graph
Level 4 — Current body
Level 5 — Entire document
Level 6 — Project history
```

For example, if the user selects:

```text
Extrude001
```

and asks:

> "Make this 15 mm."

The AI may only need:

```text
Selected feature: Extrude001
Type: Extrude
Current length: 10 mm
Profile: Sketch001
Dependents: HolePattern001
```

---

# 37. Selection-Aware AI

Selection should become a major AI context mechanism.

User selects:

```text
HolePattern001
```

and asks:

> "Make the holes 10 mm larger."

SoftWork should know what "the holes" refers to.

The user should not need to repeatedly describe the object.

---

# 38. Design Intent System

One of SoftWork's most important long-term differentiators is structured design intent.

Instead of only storing:

```text
hole diameter = 8mm
```

SoftWork can eventually understand:

```yaml
mounting_pattern:
  count: 4
  diameter: 8mm
  edge_offset: 10mm
  symmetry: center
```

Possible semantic concepts:

```text
mounting_hole_pattern
shaft_interface
minimum_wall_thickness
symmetry
clearance
centered
equal_spacing
fixed_dimension
reference_dimension
manufacturing_constraint
```

The exact schema will evolve.

The key principle:

> CAD should preserve why something exists, not merely what geometry happened to be generated.

---

# 39. AI Design Intent

Suppose the user says:

> "These holes are for mounting."

SoftWork should eventually be able to associate semantic meaning with the feature:

```text
Purpose:
Mounting interface

Pattern:
4 holes

Diameter:
8 mm

Symmetry:
Centered

Edge offset:
10 mm
```

Then the user can say:

> "Move the mounting pattern 5 mm inward."

The AI can reason about the semantic feature rather than guessing from geometry.

---

# 40. Validation

Every AI-generated or AI-modified operation should be validated.

Potential checks:

* valid solid
* manifoldness
* self-intersections
* failed booleans
* missing references
* broken dependencies
* invalid constraints
* zero-thickness geometry
* unsupported operation
* export failure

---

# 41. Validation Philosophy

AI should never say:

> "Done!"

if the CAD engine reports failure.

Instead:

```text
Operation failed.

Fillet001 could not be generated.

Reason:
The requested 8 mm radius exceeds the available edge geometry.

Suggested options:
- reduce radius to 4 mm
- modify adjacent geometry
- select a different edge
```

Engineering errors must remain explicit.

---

# 42. AI Transactions

Every AI mutation should happen inside a transaction.

Conceptually:

```text
AI Transaction #42

Before document state
        ↓
Tool calls
        ↓
Result
        ↓
Validation
        ↓
After document state
```

This makes:

* undo
* debugging
* auditing
* recovery
* reproducibility

possible.

---

# 43. Undo / Redo

Every AI operation must be undoable.

Example:

```text
User:
Make the plate 15 mm thick.

SoftWork:
Extrude001
10 mm → 15 mm

[Apply]
```

After applying:

```text
Undo
```

should restore the previous state.

Eventually, SoftWork should prefer reversible operations over giant full-document snapshots for performance.

---

# 44. AI History

SoftWork should eventually maintain:

```text
AI Session
├── User request
├── Interpretation
├── Plan
├── Tool calls
├── Validation
├── Result
└── User decision
```

This can support:

* undo
* debugging
* reproducibility
* auditability
* collaboration
* future training/evaluation
* explanation

---

# 45. AI Assumptions

AI must distinguish:

```text
Confirmed
Assumed
Inferred
Unknown
```

Example:

```text
I assumed the holes should be symmetric about the plate center.

[Accept]
[Change assumption]
```

This becomes especially important for engineering design.

---

# 46. UI Architecture

Initial interface:

```text
┌──────────────────────────────────────────────────────────────┐
│ SoftWork   File Edit View Design Assembly AI Help            │
├─────────────┬───────────────────────────────┬────────────────┤
│ MODEL TREE  │          3D VIEWPORT          │  PROPERTIES    │
│             │                               │                │
│ Part        │                               │ Width 100mm    │
│ ├ Sketch    │                               │ Height 60mm    │
│ ├ Extrude   │                               │ Depth 10mm     │
│ ├ Hole      │                               │                │
│ └ Fillet    │                               │                │
├─────────────┴───────────────────────────────┴────────────────┤
│ ✨ Ask SoftWork...                              [Send]        │
└──────────────────────────────────────────────────────────────┘
```

---

# 47. UI Philosophy

SoftWork should feel like a serious CAD application first.

Not:

```text
AI chatbot
+
3D viewer
```

Instead:

```text
CAD application
+
AI-native interaction layer
```

---

# 48. Viewport Requirements

Initial viewport capabilities:

* orbit
* pan
* zoom
* fit
* orthographic view
* perspective view
* standard views
* object selection

Later:

* face selection
* edge selection
* vertex selection
* section view
* measurement
* transparency
* clipping
* display modes
* visual comparison

Selection should synchronize with:

* model tree
* properties
* AI context

---

# 49. Properties Panel

Selecting a feature should display relevant information.

Example:

```text
Extrude001

Length:
10 mm

Direction:
Normal

Operation:
Add

Profile:
Sketch001

Status:
Valid
```

Editing a property should update the parametric model.

---

# 50. Command Palette

SoftWork should eventually support a command palette.

Example:

```text
> extrude
> fillet
> create sketch
> measure
> export STEP
> show dependencies
> ask AI
```

This provides a bridge between traditional CAD and AI interaction.

---

# 51. Natural Language Interface

The AI input should eventually support:

```text
Create a plate 100 x 60 x 10 mm.
```

and:

```text
Make the selected fillet 1 mm smaller.
```

and:

```text
Why did this feature fail?
```

and:

```text
Show me what depends on this sketch.
```

and:

```text
What is the distance between these holes?
```

AI should be able to answer questions as well as mutate the model.

---

# 52. File Architecture

SoftWork should eventually have a native project format.

Possible:

```text
project.softwork/
├── manifest.json
├── document.json
├── features/
├── geometry/
├── assets/
├── ai/
│   ├── conversations/
│   ├── plans/
│   └── changes/
└── previews/
```

The exact format can change.

The principles should not:

* readable where practical
* versioned
* recoverable
* portable
* extensible
* deterministic
* user-owned

---

# 53. Native Document Contents

A native document may eventually store:

```text
Document metadata
Parameters
Feature graph
Constraints
References
Geometry
Materials
Assemblies
AI history
Prompts
Plans
Changes
Validation results
Provenance
```

---

# 54. Interoperability

Priority formats:

```text
STEP
STL
DXF
IGES
3MF
```

Later:

```text
OBJ
BREP
FCStd
additional industry formats
```

SoftWork should never intentionally trap users inside its native format.

---

# 55. STEP

STEP should become one of the most important interchange formats.

Initial target:

```text
SoftWork model
        ↓
STEP export
        ↓
External CAD system
```

Eventually:

```text
External STEP
        ↓
SoftWork import
        ↓
Recognized / reconstructed feature structure where possible
```

Importing arbitrary STEP files into a clean parametric history is a difficult problem and should not be treated as an early trivial feature.

---

# 56. Assemblies

Assemblies come after the core part workflow is reliable.

Potential features:

```text
Components
Mates
Coincident
Concentric
Distance
Angle
Rigid
Motion
Interference
BOM
```

AI example:

> Insert this motor into the bracket and align the shaft with the central hole.

SoftWork should convert this into explicit assembly relationships.

---

# 57. Drawings

Drawing workflow eventually:

```text
3D model
 ↓
Drawing
 ↓
Orthographic views
 ↓
Dimensions
 ↓
Annotations
 ↓
Tolerances
 ↓
PDF / DXF
```

AI example:

> Create a manufacturing drawing for this part.

SoftWork should create a drawing that remains editable.

---

# 58. Manufacturing Awareness

Long-term support:

### 3D printing

* wall thickness
* overhangs
* supports
* print orientation

### CNC

* tool access
* internal radii
* pocket geometry
* machining constraints

### Laser cutting

* sheet thickness
* kerf considerations
* 2D geometry

### Injection molding

* draft
* wall thickness
* ribs
* bosses

AI should surface relevant constraints rather than pretend to provide certification.

---

# 59. Materials

Eventually:

```text
Material
├── Name
├── Density
├── Young's modulus
├── Poisson ratio
├── Yield strength
├── Thermal properties
└── Manufacturing information
```

This can support:

* mass estimation
* engineering calculations
* simulation preparation
* manufacturing reasoning

---

# 60. AI Design Alternatives

SoftWork should eventually support requests like:

> Create three bracket designs while keeping the mounting interface unchanged.

The system should create:

```text
Variant A
Variant B
Variant C
```

Each variant should remain independently editable.

The system can report:

```text
Variant
Mass
Dimensions
Features
Material
Manufacturing assumptions
Constraints
```

The user decides which design to keep.

---

# 61. Design Comparison

SoftWork should eventually compare models.

Example:

```text
Compare Version A and Version B.
```

Possible output:

```text
Changed:
- plate thickness
- fillet radius
- hole diameter

Preserved:
- mounting interface
- overall footprint
- hole locations

Geometry:
Valid

Mass:
A → ...
B → ...
```

AI explains the differences.

The user makes the engineering decision.

---

# 62. Engineering Knowledge Layer

Eventually support structured engineering knowledge around:

* standard fasteners
* materials
* tolerances
* manufacturing methods
* mechanical interfaces
* common components
* design rules

Prefer structured data over hiding everything inside prompts.

---

# 63. Plugin System

Long-term plugin architecture:

```text
softwork-plugin/
├── manifest
├── commands
├── ui
├── cad
└── ai_tools
```

Possible plugins:

* robotics
* electronics enclosure design
* automotive
* aerospace
* manufacturing
* 3D printing
* simulation
* component libraries
* custom AI providers

---

# 64. Open-Source Strategy

SoftWork should be developed transparently.

Important infrastructure:

* GitHub repository
* issues
* pull requests
* architecture documentation
* contribution guidelines
* automated testing
* release notes
* examples
* reproducible builds

The AI provider should not be mandatory for the core CAD system.

---

# 65. Licensing

Dependencies have different licenses and requirements.

Known ecosystem considerations include:

```text
CadQuery → Apache 2.0
OCP → Apache 2.0
FreeCAD → LGPL-based
OpenCASCADE → its own licensing terms
```

Before public binary distribution:

* audit dependencies
* inspect bundled components
* maintain license notices
* maintain third-party notices
* understand dynamic/static linking implications
* document attribution requirements

Do not blindly copy upstream source code.

Do not choose a final SoftWork license solely based on convenience before the dependency architecture is settled.

---

# 66. Dependency Policy

Do not blindly follow upstream `main`.

Maintain tested combinations of:

```text
SoftWork version
Python version
Qt/PySide version
CadQuery version
OCP version
OCCT version
Operating system
```

Pin known-working versions.

Upgrade intentionally.

---

# 67. Performance Architecture

CAD operations can be expensive.

The UI must remain responsive.

Long-running operations should run in worker threads/processes as appropriate.

Potential background operations:

* geometry generation
* STEP import/export
* validation
* AI requests
* heavy calculations
* mesh generation

The main UI thread should not be blocked unnecessarily.

---

# 68. Error Handling

Errors should be engineering states.

Example:

```text
Fillet001 FAILED

Reason:
Requested radius exceeds available geometry.

Current radius:
8 mm

Maximum valid radius:
approximately 4.2 mm

Suggested action:
Reduce radius.
```

Avoid:

```text
Something went wrong 😕
```

for engineering failures.

---

# 69. Security

AI-powered CAD creates a security risk if arbitrary code execution is allowed.

Rules:

1. No unrestricted shell access.
2. No unrestricted filesystem access.
3. No unrestricted network access from CAD tools.
4. Explicit tool permissions.
5. Sandbox arbitrary Python if introduced.
6. Confirm destructive operations.
7. Never expose API secrets to generated code.
8. Treat imported files as untrusted.
9. Log important AI actions.
10. Make external operations auditable.

---

# 70. Reproducibility

The same structured CAD operation should ideally produce the same result under the same environment.

AI is probabilistic.

CAD execution should be as deterministic as possible.

Therefore:

```text
AI output
    ↓
Structured command
    ↓
Deterministic CAD operation
```

rather than:

```text
AI directly generates geometry
```

---

# 71. AI Benchmarking

AI quality should not be evaluated primarily by conversation quality.

Measure the resulting engineering state.

Metrics:

### Geometry correctness

Did the resulting model have the requested dimensions?

### Intent preservation

Did unrelated features remain unchanged?

### Parameter correctness

Were the right parameters modified?

### Tool efficiency

How many operations were required?

### Recovery

Could the agent recover from failed geometry?

### Explainability

Can the user understand what changed?

### Determinism

Do equivalent requests produce structurally equivalent documents?

---

# 72. Test Architecture

Tests should exist at multiple levels.

## Unit tests

Test:

* parameters
* units
* document operations
* dependencies
* feature schemas
* tool schemas
* serialization

## CAD tests

Test:

* box
* cylinder
* boolean
* fillet
* chamfer
* extrusion
* holes
* patterns
* topology
* validation
* export

## Integration tests

Test:

```text
User request
 ↓
AI tool call
 ↓
SoftWork command
 ↓
Document update
 ↓
CAD operation
 ↓
Validation
```

---

# 73. AI Evaluation Dataset

Create benchmark prompts such as:

```text
Create a 100 × 60 × 10 mm plate.
```

```text
Add four 8 mm holes centered 10 mm from each corner.
```

```text
Change the thickness to 15 mm.
```

```text
Make the hole diameter 10 mm.
```

```text
Add a 2 mm fillet to the outside edges.
```

Evaluate the actual resulting document.

---

# 74. First Vertical Slice

Do not attempt to build all of SoftWork at once.

The first vertical slice should be:

```text
Desktop window
        ↓
3D viewport
        ↓
CAD backend
        ↓
Create real parametric solid
        ↓
Display solid
```

The first objective is NOT:

> "Build an AI CAD platform."

The first objective is:

> **"Make SoftWork open a desktop window and render one real parametric CAD solid."**

---

# 75. Version Roadmap

## v0.1 — Foundation

Goal:

> Get the CAD application alive.

Features:

* desktop shell
* 3D viewport
* CadQuery/OCP integration
* OCCT-backed geometry
* basic document
* primitive solids
* save/load prototype

Success criterion:

> SoftWork can display and manipulate a real parametric CAD solid.

---

# 76. v0.2 — Parametric Part Modeling

Features:

* feature tree
* parameters
* sketches
* extrude
* cut
* revolve
* hole
* fillet
* chamfer
* pattern
* mirror
* undo/redo
* STEP export
* STL export

Success criterion:

> A useful simple mechanical part can be created without AI.

---

# 77. v0.3 — AI CAD Copilot

Features:

* AI command bar
* provider abstraction
* CAD tools
* natural-language creation
* natural-language editing
* operation preview
* AI undo
* validation
* error reporting

Success criterion:

> A user can describe a simple part, create it, and iteratively modify it using natural language.

---

# 78. v0.4 — AI-Native Parametric Editing

Features:

* semantic feature references
* design-intent metadata
* dependency-aware editing
* selection-aware prompts
* model inspection
* context-aware AI
* change explanations
* improved transaction system

Success criterion:

> AI can modify existing designs without unnecessarily destroying or recreating their structure.

---

# 79. v0.5 — Advanced Part Modeling

Features:

* loft
* sweep
* shell
* advanced patterns
* better constraints
* complex sketches
* surface features

Success criterion:

> SoftWork can handle significantly more realistic mechanical parts.

---

# 80. v0.6 — Assemblies

Features:

* components
* mates
* assembly tree
* interference detection
* basic motion
* BOM

Success criterion:

> Users can construct and inspect multi-component mechanical assemblies.

---

# 81. v0.7 — Drawings

Features:

* drawing sheets
* orthographic views
* dimensions
* annotations
* sections
* PDF
* DXF

Success criterion:

> A finished part can produce a usable engineering drawing.

---

# 82. v0.8 — AI Engineering Agent

Features:

* multi-step plans
* multimodal input
* design alternatives
* engineering constraints
* manufacturing-aware reasoning
* model comparison
* richer design intent

Success criterion:

> AI can assist with engineering design tasks rather than merely executing isolated CAD commands.

---

# 83. v0.9 — Collaboration & Ecosystem

Features:

* plugin API
* shared projects
* Git-friendly workflows
* AI provider ecosystem
* community workbenches
* component libraries

Success criterion:

> SoftWork becomes a platform rather than only an application.

---

# 84. v1.0 — SoftWork CAD

v1.0 is not defined by a huge feature checklist.

It is defined by:

* stability
* reliability
* interoperability
* predictable geometry
* strong parametric behavior
* usable UI
* trustworthy AI operations
* recoverable failures
* professional workflows

---

# 85. First MVP Demo

The first meaningful demonstration should be:

```text
1. Open SoftWork
2. Create blank document
3. Ask:
   "Create a 100 × 60 × 10 mm mounting plate."

4. Ask:
   "Add four M8 holes 10 mm from each corner."

5. Ask:
   "Fillet the outer edges by 2 mm."

6. Ask:
   "Make it 15 mm thick."

7. Show AI change summary.

8. Export STEP.
```

If this works reliably, the core product thesis has been demonstrated.

---

# 86. MVP Pipeline

```text
User
 ↓
Natural language
 ↓
LLM provider
 ↓
Structured tool calls
 ↓
SoftWork command layer
 ↓
Document model
 ↓
CadQuery / OCP
 ↓
OpenCASCADE
 ↓
Geometry validation
 ↓
Viewport
 ↓
User
```

---

# 87. Development Phases

## Phase 0 — Environment

Install/configure:

* Git
* Python
* virtual environment
* CadQuery
* OCP
* Qt/PySide
* testing framework

Create:

```text
softwork/
```

---

## Phase 1 — CAD Kernel Proof

Build:

```text
Create box
Create cylinder
Boolean cut
Fillet
Display
Select
Export STEP
```

---

## Phase 2 — Document Model

Implement:

```text
Document
Part
Feature
Parameter
Dependency
History
```

---

## Phase 3 — Feature Tree

Build the UI representation:

```text
Part
├── Sketch
├── Extrude
├── Hole
└── Fillet
```

---

## Phase 4 — Manual Editing

Allow users to modify:

```text
dimensions
features
parameters
```

without AI.

This proves the parametric foundation.

---

## Phase 5 — AI Tool Layer

Introduce:

```text
feature.extrude
feature.cut
feature.fillet
parameter.set
model.validate
```

---

## Phase 6 — AI Agent

Implement:

```text
Understand
Plan
Execute
Validate
```

---

## Phase 7 — UX Polish

Improve:

* selection
* viewport
* properties
* AI panel
* change previews
* error messages
* undo
* keyboard shortcuts

---

# 88. Initial Repository Checklist

## GitHub

* [ ] Create `softwork`
* [ ] Fork CadQuery
* [ ] Fork FreeCAD
* [ ] Clone SoftWork
* [ ] Configure remotes
* [ ] Create README
* [ ] Create contribution guidelines
* [ ] Create initial documentation
* [ ] Decide provisional license
* [ ] Add third-party notices

---

# 89. Initial Environment Checklist

* [ ] Install Git
* [ ] Install supported Python
* [ ] Create virtual environment
* [ ] Install CadQuery
* [ ] Verify OCP import
* [ ] Install PySide6
* [ ] Create first Qt application
* [ ] Verify CAD geometry generation
* [ ] Verify geometry display

---

# 90. Initial CAD Checklist

* [ ] Create box
* [ ] Create cylinder
* [ ] Boolean cut
* [ ] Boolean union
* [ ] Fillet
* [ ] Display shape
* [ ] Select shape
* [ ] Measure basic dimensions
* [ ] Export STEP
* [ ] Export STL

---

# 91. Initial Document Checklist

* [ ] Document
* [ ] Part
* [ ] Feature
* [ ] Parameter
* [ ] Dependency
* [ ] History
* [ ] Serialization
* [ ] Deserialization
* [ ] Validation state

---

# 92. Initial AI Checklist

* [ ] Provider interface
* [ ] Provider configuration
* [ ] Tool schema
* [ ] Tool execution
* [ ] CAD operation tools
* [ ] Validation
* [ ] AI transaction
* [ ] Undo
* [ ] Error handling
* [ ] Context generation

---

# 93. First Git Milestones

The first five meaningful commits should be:

```text
chore: initialize SoftWork project
```

```text
feat: add desktop application shell
```

```text
feat: render first CadQuery solid
```

```text
feat: add basic CAD document model
```

```text
feat: add parametric feature operations
```

AI should not become the main focus until the CAD foundation is working.

---

# 94. Git Branching

Main branch:

```text
main
```

Feature branches:

```text
feat/document-model
feat/viewport
feat/cad-backend
feat/feature-tree
feat/ai-tools
feat/ai-agent
feat/validation
```

---

# 95. Commit Convention

Use:

```text
feat:
fix:
refactor:
test:
docs:
chore:
```

Examples:

```text
feat: add CadQuery backend
```

```text
fix: preserve feature dependency on parameter update
```

```text
test: add fillet validation cases
```

Avoid enormous commits that introduce half the application at once.

---

# 96. Development Rules

1. Do not prematurely build the entire application.
2. Every abstraction must have a reason.
3. CAD operations must remain deterministic.
4. AI must operate through controlled interfaces.
5. AI mutations must be reversible.
6. Geometry failures must remain visible.
7. Provider-specific code must remain isolated.
8. Do not fork upstream without a demonstrated need.
9. Build small vertical slices.
10. Test critical CAD operations.
11. Keep the UI responsive.
12. Prefer explicit engineering states over magic behavior.
13. Preserve user control.
14. Do not let AI silently rewrite unrelated design intent.
15. Build the CAD foundation before making the AI impressive.

---

# 97. Things We Should NOT Build Yet

Do not start with:

* full assemblies
* simulation
* CAM
* cloud collaboration
* mobile app
* marketplace
* custom CAD kernel
* custom rendering engine
* foundation model training
* complex agent memory
* dozens of AI providers
* advanced surface modeling
* massive plugin ecosystem

These can come later.

---

# 98. Why Not Build Everything at Once?

Because SoftWork contains several difficult engineering problems:

```text
CAD kernel
+
parametric modeling
+
document architecture
+
desktop UI
+
AI reasoning
+
tool calling
+
geometry validation
+
file interoperability
```

Trying to solve all of them simultaneously will make failures impossible to isolate.

Instead:

```text
Geometry
 ↓
Document
 ↓
Features
 ↓
UI
 ↓
AI tools
 ↓
AI agent
```

Each layer should become reliable before the next becomes complex.

---

# 99. Architecture Evolution

The architecture is expected to evolve.

The following should be treated as stable principles:

```text
SoftWork owns product architecture.
CAD kernel owns geometry.
Document model owns design intent.
AI owns reasoning.
Tools control AI actions.
Validation verifies results.
User owns final decisions.
```

Specific class names, folder structures, and backend implementations can change.

---

# 100. Future Direct OCCT Backend

A future backend may bypass CadQuery when necessary:

```text
SoftWork
 ↓
CAD Abstraction
 ↓
DirectOCCTBackend
 ↓
OpenCASCADE
```

This should only happen if concrete requirements justify it.

Potential reasons:

* performance
* unavailable CadQuery operations
* deeper topology control
* specialized geometry operations
* feature implementation requirements

Do not build this early.

---

# 101. Future FreeCAD Integration

Possible future model:

```text
SoftWork
       │
       ├── Native SoftWork Document
       │
       ├── CadQuery Backend
       │
       └── FreeCAD Integration
```

FreeCAD could provide:

* compatibility
* mature feature concepts
* existing workbenches
* import/export capabilities
* engineering ecosystem integration

But SoftWork should avoid becoming dependent on FreeCAD internals before the product requirements are known.

---

# 102. Multimodal CAD

Long-term AI input should support:

### Images

> Recreate this enclosure.

### Hand sketches

> Turn this sketch into a parametric part.

### Engineering drawings

> Create a 3D model from this drawing.

### Existing CAD

> Change the mounting interface.

### Photos + dimensions

> Create an approximate parametric model of this bracket.

The objective remains:

> **Editable engineering geometry, not merely visual similarity.**

---

# 103. AI + Existing CAD

A powerful long-term workflow:

```text
Import existing model
        ↓
Inspect feature/geometry structure
        ↓
User describes desired change
        ↓
AI identifies relevant features
        ↓
AI proposes structured edits
        ↓
CAD system executes
        ↓
Validate
        ↓
Preview
        ↓
Apply
```

This is more valuable than simply generating new parts.

---

# 104. AI Engineering Agent

The long-term agent should eventually be able to:

```text
Inspect
Reason
Plan
Modify
Measure
Validate
Compare
Explain
Recover
```

Example:

> "Make this bracket lighter without changing the mounting interface."

Possible plan:

```text
1. Inspect current mass.
2. Identify non-interface material.
3. Generate candidate geometry changes.
4. Preserve mounting holes.
5. Check minimum wall thickness.
6. Compare mass reduction.
7. Present alternatives.
```

The AI should not silently decide what engineering tradeoff the user accepts.

---

# 105. Human-in-the-Loop Design

SoftWork should encourage a workflow where AI proposes and humans approve important changes.

Possible levels:

```text
Automatic
Preview
Confirm
Restricted
```

For example:

### Safe read operation

```text
"Measure this distance."
```

Can execute immediately.

### Simple parameter change

```text
"Make the thickness 15 mm."
```

Can preview and apply.

### Destructive operation

```text
"Delete all unused features."
```

Should require explicit confirmation.

---

# 106. AI Permission Model

Potential future permission categories:

```text
READ
CREATE
MODIFY
DELETE
EXPORT
EXECUTE
NETWORK
```

The default should be conservative.

---

# 107. Model Provenance

Every AI-created feature may eventually contain provenance:

```yaml
provenance:
  source: ai
  provider: ...
  model: ...
  request_id: ...
  user_prompt: ...
  timestamp: ...
  confidence: ...
```

For manually created features:

```yaml
provenance:
  source: user
```

For imported geometry:

```yaml
provenance:
  source: imported
  format: step
```

This can become valuable for auditing and debugging.

---

# 108. AI Memory

Do not build complex long-term agent memory early.

Start with:

```text
Current document
Current selection
Recent operations
Current conversation
Relevant design intent
```

Long-term project memory can come later.

---

# 109. Context Compression

As models become complex, SoftWork should summarize relevant context instead of dumping everything into the prompt.

Example:

```text
Document:
1 body
18 features
4 sketches

Selected:
HolePattern001

Relevant dependencies:
Sketch002
Hole001
Extrude001

Parameters:
Hole diameter = 8 mm
Pattern count = 4
Edge offset = 10 mm

Validation:
Valid
```

This is much more useful than sending thousands of raw geometry values.

---

# 110. Deterministic Command Layer

The command layer should be usable without AI.

For example:

```python
document.create()

sketch = document.create_sketch("Sketch001")

sketch.add_rectangle(
    width=100,
    height=60,
    centered=True,
)

extrude = document.extrude(
    sketch,
    length=10,
)
```

AI should ultimately produce equivalent structured operations.

This means:

```text
AI interface
```

and:

```text
Traditional interface
```

can share the same underlying command system.

This is extremely important.

---

# 111. One Command System

Avoid having:

```text
Manual CAD engine
```

and separately:

```text
AI CAD engine
```

Instead:

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

This is one of the most important architectural decisions.

---

# 112. Example Command Flow

Manual:

```text
User clicks Extrude
 ↓
UI collects length
 ↓
Command
 ↓
Document
 ↓
CAD backend
```

AI:

```text
User says:
"Extrude this 10 mm"

 ↓

AI tool call

 ↓

Same command

 ↓

Document

 ↓

CAD backend
```

Therefore AI does not create a parallel CAD implementation.

---

# 113. Design Intent vs Feature History

SoftWork should eventually maintain both:

```text
Feature history
```

and:

```text
Design intent
```

Example:

```text
Feature history:

Sketch001
Extrude001
Hole001
Pattern001
```

Semantic layer:

```text
Base plate
Mounting interface
Four symmetric mounting holes
Primary thickness
```

This combination is powerful.

---

# 114. Geometry vs Semantics

The CAD kernel knows:

```text
Face #182
Edge #91
Cylinder radius 4 mm
```

The semantic layer can know:

```text
Mounting hole
```

The AI can reason:

```text
"The user means the mounting holes."
```

The system can then map that intent back to actual CAD entities.

---

# 115. Topology Naming Problem

CAD topology can be unstable after feature changes.

For example:

```text
Face5
```

may not remain the same logical face after regeneration.

SoftWork should eventually avoid relying purely on raw topology IDs for semantic references.

Potential mechanisms:

* persistent references
* geometric signatures
* feature references
* semantic labels
* dependency-aware references

This is a major future engineering problem.

Do not pretend it is solved in v0.1.

---

# 116. AI Failure Recovery

If a command fails:

```text
AI
 ↓
Tool call
 ↓
CAD failure
```

the agent should receive structured error information.

Example:

```json
{
  "status": "failed",
  "operation": "fillet",
  "reason": "radius_exceeds_geometry",
  "max_estimated_radius": 4.2,
  "requested_radius": 8.0
}
```

The AI can then reason about recovery.

---

# 117. AI Recovery Example

User:

> Add an 8 mm fillet.

CAD:

```text
Failed.
Maximum valid radius approximately 4.2 mm.
```

AI:

> The 8 mm fillet is too large for the selected geometry. I can reduce it to 4 mm or try a different edge.

The AI should not silently choose 4 mm unless the user has granted that behavior.

---

# 118. Engineering Safety

SoftWork is engineering software.

Incorrect geometry can lead to real-world consequences.

Therefore SoftWork should clearly distinguish:

```text
Geometric validity
```

from:

```text
Engineering correctness
```

A model can be geometrically valid while being mechanically unsafe.

AI should not claim:

> "This part is safe."

unless appropriate validated analysis supports such a claim.

---

# 119. Simulation Boundary

SoftWork should eventually integrate simulation tools.

But:

```text
CAD geometry
≠
validated physical performance
```

Simulation outputs should be clearly separated from AI speculation.

---

# 120. Manufacturing Boundary

Similarly:

```text
AI suggestion
≠
manufacturing certification
```

Manufacturing-aware AI should surface considerations and calculations where supported.

---

# 121. User Ownership

The user should always be able to:

* inspect features
* edit parameters
* undo AI actions
* reject AI proposals
* export geometry
* save locally
* work without AI
* choose an AI provider

---

# 122. No AI Lock-In

SoftWork should not require:

```text
SoftWork Cloud
```

to function as a CAD application.

Potential future cloud services may exist, but local CAD should remain meaningful.

---

# 123. Packaging

Early development:

```text
Python virtual environment
```

Prototype distribution:

```text
PyInstaller
```

or an equivalent packaging approach.

Later:

### Windows

* installer
* signed releases

### macOS

* application bundle
* signed/notarized distribution where appropriate

### Linux

Potential:

* AppImage
* Flatpak
* distro packages

Packaging strategy should evolve after the application stabilizes.

---

# 124. Configuration

User settings may eventually include:

```text
AI provider
AI model
API key
Default units
Theme
Viewport preferences
CAD preferences
Autosave
Permissions
```

API keys should be stored securely where possible.

---

# 125. Logging

SoftWork should have structured logging.

Potential categories:

```text
UI
CAD
DOCUMENT
AI
TOOL
VALIDATION
IMPORT
EXPORT
PERFORMANCE
```

Example:

```text
[CAD] Extrude001 generated successfully
[VALIDATION] Solid valid
[AI] Tool call feature.extrude
```

Logs should help developers debug failures without exposing secrets.

---

# 126. Autosave

Eventually support:

* autosave
* recovery files
* crash recovery
* version history

Engineering work should not disappear because the application crashed.

---

# 127. Performance Targets

Early target:

* application opens reliably
* viewport remains responsive
* simple parts regenerate quickly
* AI requests do not freeze the UI
* document operations remain predictable

Exact numeric performance targets should be established after real profiling.

Do not optimize based on guesses.

---

# 128. Telemetry

The open-source core should not silently collect user design data.

If telemetry is ever introduced:

* make it explicit
* document it
* provide opt-out
* never upload private CAD models without consent

---

# 129. Privacy

CAD models may contain proprietary engineering information.

SoftWork should treat model data as sensitive by default.

AI providers may receive:

* prompts
* selected geometry metadata
* document context

depending on the user's configuration.

The application should make this understandable.

---

# 130. AI Provider UI

Potential interface:

```text
AI Provider

Provider:
[ OpenAI ▼ ]

Model:
[ ... ]

API Key:
[ *************** ]

Context:
[ Selected feature only ▼ ]

Permissions:
[x] Read model
[x] Create features
[x] Modify parameters
[ ] Delete features
```

This can evolve later.

---

# 131. Future Local AI

SoftWork should eventually support local models where practical.

Potential architecture:

```text
SoftWork
   ↓
ModelProvider
   ├── CloudProvider
   └── LocalProvider
```

This can support:

* privacy
* offline AI
* experimentation
* custom engineering models

Local AI should not be a v0.1 requirement.

---

# 132. AI Prompt Engineering

Do not hard-code the entire product into a giant system prompt.

Prefer:

```text
Structured context
+
Tool schemas
+
Small task-specific instructions
+
Validation feedback
```

This makes the system easier to maintain.

---

# 133. AI Tool Discipline

The AI should not have 200 tools on day one.

Start with a small high-value tool set.

Example:

```text
document.create
selection.inspect
parameter.set
feature.extrude
feature.cut
feature.fillet
model.validate
history.undo
```

Expand based on actual user workflows.

---

# 134. AI Tool Naming

Tool names should be predictable.

Examples:

```text
feature.extrude
feature.fillet
feature.hole
feature.pattern
parameter.set
geometry.measure
model.validate
```

This allows the AI to reason about capabilities more easily.

---

# 135. AI Plan Representation

A plan may eventually look like:

```yaml
plan:
  goal: create_mounting_plate

  steps:
    - operation: sketch.create
      plane: XY

    - operation: sketch.add_rectangle
      width: 100mm
      height: 60mm
      centered: true

    - operation: feature.extrude
      distance: 10mm

    - operation: feature.hole
      diameter: 8mm
      count: 4

    - operation: feature.fillet
      radius: 2mm

  validation:
    - valid_solid
    - dimensions
```

This is more reliable than free-form text execution.

---

# 136. Plan Approval

For simple operations:

```text
"Create a 10 mm cube."
```

SoftWork may execute directly.

For complex operations:

```text
"Redesign this bracket to reduce mass while preserving all interfaces."
```

SoftWork should show a plan first.

---

# 137. AI Confidence

Confidence should not be treated as a magical scalar.

More useful:

```text
Certain:
Selected object is HolePattern001.

Assumed:
User intends all four holes.

Ambiguous:
"Near the edge" has no exact dimension.
```

Ask only when necessary.

---

# 138. Clarification Strategy

AI should avoid asking unnecessary questions.

Bad:

> What unit system are you using?

when the user already said:

> 10 mm

Good:

> You said "near the edge." What offset should I use?

The AI should infer safely where possible and ask when ambiguity affects engineering intent.

---

# 139. AI Conversational State

Conversation should map to document state.

Example:

```text
User:
Create a 100 mm plate.

AI:
Created.

User:
Make it thicker.

AI:
How thick?

User:
15 mm.

AI:
Updated Extrude001 from 10 mm to 15 mm.
```

The system should know what "it" refers to through document context.

---

# 140. Multi-Object Context

Eventually:

```text
User:
Move this hole pattern 5 mm inward.
```

Selection and semantic references should make this possible.

AI should not require object IDs in normal conversation.

---

# 141. Explainability

AI should explain important operations at the right level.

Not:

```text
I called tool feature.extrude with JSON...
```

unless developer/debug mode is enabled.

Normal user:

> I changed the base extrusion from 10 mm to 15 mm. The hole pattern and fillets were preserved.

Developer mode:

```text
feature.parameter.set(
    feature_id="Extrude001",
    parameter="length",
    value=15mm
)
```

---

# 142. Developer Mode

Future developer mode may show:

* AI messages
* tool calls
* tool arguments
* validation results
* CAD backend logs
* execution time
* dependency changes

This will be extremely useful while building SoftWork.

---

# 143. Debugging AI

When a model behaves incorrectly, developers should be able to reproduce:

```text
Prompt
+
Document
+
Selection
+
AI provider/model
+
Tool calls
```

and inspect the resulting failure.

---

# 144. AI Regression Tests

Every important AI workflow should become a regression test.

Example:

```text
Prompt:
Make the plate 15 mm thick.

Expected:
Extrude001.length == 15mm

Expected preserved:
HolePattern001
Fillet001
```

This prevents future agent changes from breaking existing behavior.

---

# 145. Geometry Regression Tests

Maintain known models.

Example:

```text
fixtures/
├── plate
├── bracket
├── shaft
├── enclosure
└── mounting_plate
```

Test regeneration after changes.

---

# 146. Native Model Versioning

The `.softwork` format should have explicit schema versions.

Example:

```json
{
  "schema_version": "0.1"
}
```

When the document schema changes:

```text
v0.1
 ↓
migration
 ↓
v0.2
```

Do not silently break old project files.

---

# 147. Backward Compatibility

Eventually:

```text
Old SoftWork document
        ↓
Migration layer
        ↓
Current document
```

Users should not lose projects simply because the application upgraded.

---

# 148. Crash Recovery

Potential architecture:

```text
project.softwork
project.softwork.autosave
project.softwork.recovery
```

Exact implementation comes later.

---

# 149. Documentation

Documentation should eventually include:

```text
docs/
├── architecture/
├── getting-started/
├── CAD/
├── AI/
├── document-format/
├── plugins/
├── contributing/
└── development/
```

---

# 150. Example Projects

Create example models that demonstrate the system.

Initial:

```text
100 × 60 mounting plate
shaft
bracket
simple enclosure
wheel
coupling
```

Later:

```text
robot arm joint
motor mount
gearbox housing
drone frame
```

Examples are useful for:

* demos
* tests
* onboarding
* AI benchmarks
* documentation

---

# 151. Demo Philosophy

A demo should show actual engineering work.

Avoid:

```text
"Look how cool this AI animation is."
```

Prefer:

```text
"Watch the AI create a real parametric mounting plate,
modify its thickness,
preserve its hole pattern,
validate the geometry,
and export a STEP file."
```

---

# 152. The First Killer Demo

The first public demo should ideally show:

```text
Blank document
      ↓
"Create a 100 × 60 × 10 mm mounting plate."
      ↓
Real model appears
      ↓
"Add four M8 holes 10 mm from each corner."
      ↓
Real parametric hole pattern
      ↓
"Fillet the outer edges by 2 mm."
      ↓
Fillets appear
      ↓
"Make it 15 mm thick."
      ↓
Only thickness changes
      ↓
AI explains preserved features
      ↓
Export STEP
```

This communicates the product immediately.

---

# 153. What Makes This Different?

SoftWork should not compete merely by saying:

> "We have AI."

Many CAD products will eventually have AI.

The deeper differentiation should be:

```text
AI
+
parametric structure
+
design intent
+
transparent operations
+
dependency-aware editing
+
engineering context
```

---

# 154. Long-Term Product Direction

Eventually the interaction could look like:

```text
Human:
"I need a bracket for this motor."

SoftWork:
"What are the motor mounting dimensions?"

Human:
"Here's the datasheet."

SoftWork:
"Understood. I'll use the mounting-hole dimensions
and preserve a 5 mm clearance around the housing."

        ↓

Generate design

        ↓

Validate

        ↓

Compare alternatives

        ↓

Human chooses

        ↓

Create drawing

        ↓

Export manufacturing files
```

The goal is not simply faster CAD commands.

It is reducing the distance between:

```text
Engineering intent
```

and:

```text
Engineering artifact
```

---

# 155. SoftWork as an Engineering Interface

The long-term product may become less about individual commands and more about engineering intent.

Instead of:

```text
Click Sketch
Click Rectangle
Enter Dimension
Click Extrude
Enter Dimension
Click Hole
...
```

the user can say:

> "I need a mounting plate for four M8 bolts, centered on the shaft, with 10 mm edge clearance."

SoftWork translates this into explicit engineering structure.

The conventional UI remains available.

---

# 156. Human + AI + CAD

The intended relationship:

```text
                 HUMAN
                   │
             Engineering intent
                   │
                   ▼
                  AI
          Reasoning / planning
                   │
            Structured tools
                   │
                   ▼
            SOFTWORK CORE
         Document / commands
                   │
                   ▼
             CAD BACKEND
                   │
                   ▼
             OPEN CASCADE
                   │
                   ▼
               GEOMETRY
                   │
                   ▼
              VALIDATION
                   │
                   ▼
                 HUMAN
             Review / decision
```

---

# 157. Responsibility Boundaries

### Human

Responsible for:

* requirements
* engineering judgment
* acceptance
* tradeoffs
* final design decisions

### AI

Responsible for:

* interpretation
* planning
* assistance
* tool selection
* explanation
* alternative generation

### SoftWork document core

Responsible for:

* design structure
* dependencies
* parameters
* history
* provenance

### CAD backend / kernel

Responsible for:

* geometry
* topology
* deterministic operations
* geometric validity

This separation should remain clear throughout the project.

---

# 158. First Technical Goal

The immediate technical objective is:

```text
Open SoftWork
        ↓
Show desktop UI
        ↓
Create a CAD document
        ↓
Generate a box
        ↓
Display the box
```

Nothing more is required for the first milestone.

---

# 159. Second Technical Goal

Then:

```text
Box
 ↓
Parameter
 ↓
Edit parameter
 ↓
Regenerate
 ↓
Display updated geometry
```

This proves parametric behavior.

---

# 160. Third Technical Goal

Then:

```text
Feature
 ↓
Feature tree
 ↓
Dependency
 ↓
Modify upstream feature
 ↓
Regenerate downstream features
```

This proves the document model.

---

# 161. Fourth Technical Goal

Then:

```text
User
 ↓
AI
 ↓
Structured tool
 ↓
Same CAD command system
 ↓
Document
 ↓
Geometry
```

This proves AI integration.

---

# 162. Fifth Technical Goal

Then:

```text
AI modification
 ↓
Validation
 ↓
Change preview
 ↓
User approval
 ↓
Transaction
 ↓
Undo
```

This proves the AI-native interaction loop.

---

# 163. Build Order

The recommended order is:

```text
1. Repository
2. Environment
3. Desktop shell
4. CAD backend
5. Viewport
6. Document
7. Feature system
8. Parameters
9. Feature tree
10. Manual editing
11. Validation
12. Export
13. AI provider
14. AI tools
15. AI agent
16. Change preview
17. AI transactions
18. Design intent
```

---

# 164. Why AI Comes Later

This is intentional.

If SoftWork starts with AI first, the project risks becoming:

```text
LLM
 ↓
Generated Python
 ↓
Some CAD geometry
```

That is not enough.

SoftWork needs a real underlying application so that AI has something meaningful to operate.

The correct order is:

```text
Build the machine
 ↓
Expose the machine through commands
 ↓
Teach AI to operate those commands
```

---

# 165. First Architecture Lock

For the initial build, lock:

```text
Language:
Python

Desktop:
Qt 6 / PySide6

CAD:
CadQuery + OCP + OpenCASCADE

AI:
Provider abstraction

Document:
SoftWork-owned model

Architecture:
Command-driven

Validation:
Mandatory for AI mutations
```

Everything else can evolve.

---

# 166. Architecture That Must Not Happen

Avoid:

```text
AI
 ↓
Generate random Python
 ↓
Run Python
 ↓
Hope geometry works
```

Avoid:

```text
AI
 ↓
Generate mesh
 ↓
Call it CAD
```

Avoid:

```text
SoftWork
 ↓
Fork FreeCAD
 ↓
Rewrite everything
```

Avoid:

```text
SoftWork
 ↓
Hard-code OpenAI everywhere
```

Avoid:

```text
UI
 ↓
Directly manipulate CadQuery objects everywhere
```

---

# 167. Preferred Architecture

```text
                 UI
                  │
                  ▼
             Command Layer
             ▲          ▲
             │          │
           User         AI
             │          │
             └────┬─────┘
                  ▼
            Document Core
                  │
                  ▼
            CAD Abstraction
                  │
          ┌───────┼────────┐
          ▼       ▼        ▼
      CadQuery  FreeCAD   OCCT
          │       │        │
          └───────┴────────┘
                  │
                  ▼
              Geometry
```

---

# 168. Product North Star

The North Star is:

> **Make engineering intent directly executable without sacrificing the structure, transparency, and determinism of professional CAD.**

---

# 169. Product Statement

SoftWork is:

> **An open-source, desktop-first, AI-native parametric CAD application that lets engineers create and modify real engineering models through both conventional CAD tools and natural language.**

---

# 170. Core Interaction Loop

```text
INTENT
  ↓
UNDERSTAND
  ↓
PLAN
  ↓
OPERATE
  ↓
VALIDATE
  ↓
EXPLAIN
  ↓
REVIEW
  ↓
CONTINUE
```

---

# 171. Final Architecture Principle

The product should always preserve this relationship:

```text
Human
  ↓
Intent

AI
  ↓
Reasoning

SoftWork
  ↓
Commands + document structure

CAD Kernel
  ↓
Geometry

Validation
  ↓
Evidence

Human
  ↓
Decision
```

---

# 172. Build Directive

> **Start small. Build vertically. Validate every layer.**

Do not measure progress by how many folders exist.

Measure progress by how much real engineering workflow works.

---

# 173. Immediate Task List

## Task 1

Create:

```text
softwork
```

GitHub repository.

---

## Task 2

Create local project:

```text
softwork/
```

with Python packaging.

---

## Task 3

Create environment.

Verify:

```python
import cadquery
import OCP
```

---

## Task 4

Create PySide6 application.

Expected result:

```text
SoftWork
┌────────────────────────────┐
│                            │
│        Empty viewport      │
│                            │
└────────────────────────────┘
```

---

## Task 5

Generate a box.

Example conceptual operation:

```python
result = cq.Workplane("XY").box(
    100,
    60,
    10
)
```

---

## Task 6

Display the resulting solid in the viewport.

---

## Task 7

Create:

```python
Document
Part
Feature
Parameter
```

---

## Task 8

Connect the generated box to the document.

---

## Task 9

Allow the parameter to change.

Example:

```text
Width:
100 mm → 120 mm
```

---

## Task 10

Regenerate and display the updated geometry.

---

# 174. First Definition of "Working"

SoftWork v0.1 is working when:

```text
Application launches
        ↓
Document exists
        ↓
Parametric solid exists
        ↓
Viewport displays it
        ↓
Parameter can change
        ↓
Geometry regenerates
        ↓
Document can be saved
```

That is the first real milestone.

---

# 175. Final Product Vision

SoftWork begins as:

```text
A box.
```

Then becomes:

```text
A parametric part.
```

Then:

```text
A CAD document.
```

Then:

```text
A CAD application.
```

Then:

```text
An AI-native CAD application.
```

Eventually:

```text
An engineering design environment.
```

The sequence matters.

Do not skip the foundations.

---

# 176. Final Statement

SoftWork should make engineering design more expressive without making it less rigorous.

The ultimate workflow is:

```text
Human intent
      ↓
AI reasoning
      ↓
Structured engineering operations
      ↓
Parametric CAD
      ↓
Validated geometry
      ↓
Human review
```

The human remains the designer.

The AI is the assistant/operator.

The document model preserves design intent.

The CAD system executes deterministic operations.

The geometry kernel is the geometric authority.

Validation provides evidence.

And SoftWork ties all of them together into one desktop engineering environment.

---

# 177. Current Build Status

```text
Product vision          ████████████████████  LOCKED
Architecture            ████████████████████  INITIAL LOCK
Technology direction    ████████████████████  CHOSEN
Repository               ████████████████████  COMPLETE
Environment              ████████████████████  COMPLETE
Desktop shell            ████████████████████  COMPLETE
CAD backend              ████████████████████  COMPLETE
Document model           ████████████████████  COMPLETE
AI layer                 ████████████████████  COMPLETE
Design intent             ████████████████████  COMPLETE
Assemblies                ░░░░░░░░░░░░░░░░░░░░  FUTURE
Drawings                  ░░░░░░░░░░░░░░░░░░░░  FUTURE
Engineering agent         ░░░░░░░░░░░░░░░░░░░░  FUTURE
```

---

# 178. One-Sentence Build Rule

> **Never make SoftWork smarter before making SoftWork more structurally correct.**

---

# 179. The First Commit

The first commit should be boring.

That is good.

```text
chore: initialize SoftWork project
```

Then build the machine.

AI comes after the machine exists.

---

# 180. END

**SoftWork**

> **AI-native parametric CAD.**

```text
Human intent
      ↓
AI reasoning
      ↓
CAD operations
      ↓
Parametric model
      ↓
Validated geometry
      ↓
Engineering artifact
```

**SoftWork begins with a box.**
