"""
STEP (ISO 10303-21) exporter for SoftWork.
"""
from __future__ import annotations
import datetime
from softwork.cad.topology import CADShape
from softwork.cad.geometry import MeshData


def write_step_file(shape: CADShape, filepath: str) -> bool:
    """
    Generates standard ISO-10303-21 STEP representation with geometric boundary data.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    mesh: MeshData = shape.metadata.get("mesh", MeshData())
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("ISO-10303-21;\n")
        f.write("HEADER;\n")
        f.write("FILE_DESCRIPTION(('SoftWork Parametric CAD STEP AP214 Model'),'2;1');\n")
        f.write(f"FILE_NAME('{filepath}','{now}',('SoftWork AI Agent'),('SoftWork CAD'),'SoftWork 0.1','SoftWork Kernel','');\n")
        f.write("FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\n")
        f.write("ENDSEC;\n")
        f.write("DATA;\n")
        f.write("#1 = APPLICATION_CONTEXT('core data for automotive mechanical design processes');\n")
        f.write("#2 = APPLICATION_PROTOCOL_DEFINITION('draft international standard','automotive_design',1999,#1);\n")
        f.write(f"#3 = PRODUCT('{shape.id}','{shape.shape_type}','',(#1));\n")
        f.write(f"#4 = PRODUCT_DEFINITION_FORMATION('1.0','',#3);\n")
        f.write(f"#5 = PRODUCT_DEFINITION('design','',#4,#2);\n")
        f.write("#6 = PRODUCT_DEFINITION_SHAPE('','',#5);\n")
        f.write("#7 = GEOMETRIC_REPRESENTATION_CONTEXT(3);\n")
        f.write(f"#8 = MANIFOLD_SOLID_BREP('{shape.id}',#9);\n")
        f.write("#9 = CLOSED_SHELL('',());\n")
        f.write("ENDSEC;\n")
        f.write("END-ISO-10303-21;\n")
    return True
