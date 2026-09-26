"""
Tests for CADAgent, AI tools, and natural language command execution pipeline.
"""
import unittest
from softwork.core.document import Document
from softwork.ai.agent import CADAgent
from tests.test_helpers import create_test_document


class TestAIAgentAndTools(unittest.TestCase):
    def test_ai_agent_mounting_plate_workflow(self):
        doc = create_test_document(name="AgentTestDoc")
        agent = CADAgent(doc)

        # 1. Natural language: Create a 100 x 60 x 10 mm mounting plate
        res1 = agent.execute_prompt("Create a 100 x 60 x 10 mm mounting plate")
        self.assertTrue(res1.success)
        self.assertEqual(len(doc.active_part.features), 1)
        plate_feat = doc.active_part.features[0]
        self.assertEqual(plate_feat.get_parameter("length").value, 100.0)
        self.assertEqual(plate_feat.get_parameter("width").value, 60.0)
        self.assertEqual(plate_feat.get_parameter("thickness").value, 10.0)

        # 2. Add 4 M8 holes 10 mm from corner
        res2 = agent.execute_prompt("Add four M8 holes, 10 mm from each corner")
        self.assertTrue(res2.success)
        self.assertEqual(plate_feat.get_parameter("hole_diameter").value, 8.0)
        self.assertEqual(plate_feat.get_parameter("hole_offset").value, 10.0)

        # 3. Fillet outer edges by 2 mm
        res3 = agent.execute_prompt("Fillet the outer edges by 2 mm")
        self.assertTrue(res3.success)
        self.assertEqual(plate_feat.get_parameter("fillet_radius").value, 2.0)

        # 4. Make it 15 mm thick (parameter update preserving all other features)
        res4 = agent.execute_prompt("Make it 15 mm thick")
        self.assertTrue(res4.success)
        self.assertEqual(plate_feat.get_parameter("thickness").value, 15.0)
        self.assertEqual(plate_feat.get_parameter("hole_diameter").value, 8.0)
        self.assertEqual(plate_feat.get_parameter("fillet_radius").value, 2.0)
        self.assertTrue(doc.latest_validation.is_valid)


if __name__ == "__main__":
    unittest.main()
