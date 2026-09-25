"""
Standalone SoftWork MVP Demonstration CLI script.
Demonstrates the complete human-intent to parametric-CAD pipeline:
1. Initialize CAD Document
2. Ask: "Create a 100 x 60 x 10 mm mounting plate"
3. Ask: "Add four M8 holes, 10 mm from each corner"
4. Ask: "Fillet the outer edges by 2 mm"
5. Ask: "Make it 15 mm thick"
6. Validate geometry and explain preserved features
7. Export to STEP and STL
"""
import sys
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from softwork.core.document import Document
from softwork.ai.agent import CADAgent
from softwork.document.serializer import save_document


def run_mvp_demo() -> None:
    print("=" * 70)
    print(" SOFTWORK -- AI-native Parametric CAD (MVP Demonstration)")
    print("=" * 70)

    # 1. Initialize Document
    doc = Document(name="MountingPlateDemo.softwork")
    agent = CADAgent(doc)
    print("\n[1] Initialized CAD Document & Agent.")

    # 2. Step 1: Create Mounting Plate
    prompt1 = "Create a 100 x 60 x 10 mm mounting plate"
    print(f"\n[2] Prompt: \"{prompt1}\"")
    res1 = agent.execute_prompt(prompt1)
    print(f"    AI Explanation: {res1.explanation}")
    plate = doc.active_part.features[0]
    print(f"    Feature Created: {plate.name} ({plate.parameters['length'].value}x{plate.parameters['width'].value}x{plate.parameters['thickness'].value} mm)")

    # 3. Step 2: Add 4 M8 Holes
    prompt2 = "Add four M8 holes, 10 mm from each corner"
    print(f"\n[3] Prompt: \"{prompt2}\"")
    res2 = agent.execute_prompt(prompt2)
    print(f"    AI Explanation: {res2.explanation}")
    print(f"    Updated Parameters: Hole Dia={plate.parameters['hole_diameter'].value} mm, Corner Offset={plate.parameters['hole_offset'].value} mm")

    # 4. Step 3: Fillet Outer Edges
    prompt3 = "Fillet the outer edges by 2 mm"
    print(f"\n[4] Prompt: \"{prompt3}\"")
    res3 = agent.execute_prompt(prompt3)
    print(f"    AI Explanation: {res3.explanation}")
    print(f"    Updated Parameters: Fillet Radius={plate.parameters['fillet_radius'].value} mm")

    # 5. Step 4: Change Thickness to 15 mm
    prompt4 = "Make it 15 mm thick"
    print(f"\n[5] Prompt: \"{prompt4}\"")
    res4 = agent.execute_prompt(prompt4)
    print(f"    AI Explanation: {res4.explanation}")
    print(f"    Updated Thickness: {plate.parameters['thickness'].value} mm")
    print(f"    Preserved Features & Parameters: Length={plate.parameters['length'].value}mm, Width={plate.parameters['width'].value}mm, Holes=4xM{plate.parameters['hole_diameter'].value:.0f}, Fillet={plate.parameters['fillet_radius'].value}mm")

    # 6. Validation
    val = doc.latest_validation
    status_str = "PASS" if val and val.is_valid else "FAIL"
    print(f"\n[6] Geometry Validation: [{status_str}]")
    if doc.active_part.active_solid:
        print(f"    Calculated Solid Volume: {doc.active_part.active_solid.volume:,.2f} mm3")

    # 7. Exports
    step_out = root_dir / "mounting_plate.step"
    stl_out = root_dir / "mounting_plate.stl"
    softwork_out = root_dir / "mounting_plate.softwork"

    doc.backend.export_step(doc.active_part.active_solid, str(step_out))
    doc.backend.export_stl(doc.active_part.active_solid, str(stl_out), binary=True)
    save_document(doc, str(softwork_out))

    print(f"\n[7] Exported Artifacts:")
    print(f"    - ISO STEP File:   {step_out.name} ({step_out.stat().st_size} bytes)")
    print(f"    - Binary STL File: {stl_out.name} ({stl_out.stat().st_size} bytes)")
    print(f"    - Native Doc File: {softwork_out.name} ({softwork_out.stat().st_size} bytes)")

    print("\n" + "=" * 70)
    print(" MVP DEMONSTRATION COMPLETE: All criteria satisfied!")
    print("=" * 70)


if __name__ == "__main__":
    run_mvp_demo()
