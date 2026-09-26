"""
Tests for Document persistence and STEP / STL file format export.
"""
import os
import tempfile
import unittest
from softwork.cad.backend import CADKernelError
from softwork.core.document import Document
from softwork.core.feature import MountingPlateFeature
from softwork.document.serializer import save_document, load_document
from tests.test_helpers import create_test_document, get_test_backend


class TestFormatsAndSerialization(unittest.TestCase):
    def test_document_save_and_load(self):
        backend = get_test_backend()
        doc = Document(name="SerializationTest", backend=backend)
        plate = MountingPlateFeature(length=120.0, width=80.0, thickness=12.0, hole_diameter=10.0, fillet_radius=3.0)
        doc.add_feature(plate)

        with tempfile.NamedTemporaryFile(suffix=".softwork", delete=False) as f:
            temp_path = f.name

        try:
            save_document(doc, temp_path)
            self.assertTrue(os.path.exists(temp_path))

            loaded_doc = load_document(temp_path, backend=backend)
            self.assertEqual(len(loaded_doc.active_part.features), 1)
            loaded_feat = loaded_doc.active_part.features[0]
            self.assertEqual(loaded_feat.get_parameter("length").value, 120.0)
            self.assertEqual(loaded_feat.get_parameter("thickness").value, 12.0)
            self.assertIsNotNone(loaded_doc.active_part.active_solid)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_step_and_stl_export(self):
        backend = get_test_backend()
        doc = Document(name="ExportTest", backend=backend)
        plate = MountingPlateFeature(length=100.0, width=60.0, thickness=10.0)
        doc.add_feature(plate)
        solid = doc.active_part.active_solid
        self.assertIsNotNone(solid)

        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as f_step, \
             tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f_stl:
            step_path = f_step.name
            stl_path = f_stl.name

        try:
            if solid.native_handle is None:
                # Prototype non-B-rep shape must explicitly fail STEP export
                with self.assertRaises(CADKernelError):
                    doc.backend.export_step(solid, step_path)
            else:
                ok_step = doc.backend.export_step(solid, step_path)
                self.assertTrue(ok_step)
                self.assertGreater(os.path.getsize(step_path), 0)

            ok_stl = doc.backend.export_stl(solid, stl_path, binary=True)
            self.assertTrue(ok_stl)
            self.assertGreater(os.path.getsize(stl_path), 84)  # 80 byte header + 4 byte count
        finally:
            if os.path.exists(step_path):
                os.remove(step_path)
            if os.path.exists(stl_path):
                os.remove(stl_path)


if __name__ == "__main__":
    unittest.main()
