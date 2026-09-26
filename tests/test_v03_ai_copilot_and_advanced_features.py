"""
Tests for v0.3 AI Copilot, Cloud Providers, Ghost Previews, Hole Wizard, and Shell features.
"""
import unittest
from softwork.core.document import Document
from softwork.core.feature import BoxFeature, MountingPlateFeature, HoleWizardFeature, ShellFeature
from softwork.commands.feature_commands import AddHoleWizardCommand, AddShellCommand
from softwork.ai.agent import CADAgent
from softwork.ai.provider import HeuristicEngineProvider, GeminiProvider, OpenAIProvider, AnthropicProvider


class TestV03AICopilotAndAdvancedFeatures(unittest.TestCase):
    def test_hole_wizard_feature(self):
        doc = Document(name="HoleWizardTest")
        box = BoxFeature(width=80.0, height=80.0, depth=20.0)
        doc.add_feature(box)
        initial_vol = doc.active_part.active_solid.volume

        # Add M8 Counterbore Hole
        hw = HoleWizardFeature(target_feature_id=box.id, metric_size="M8", hole_type="counterbore", depth=20.0)
        doc.add_feature(hw)

        self.assertIsNotNone(doc.active_part.active_solid)
        self.assertTrue(doc.active_part.active_solid.is_valid)
        self.assertLess(doc.active_part.active_solid.volume, initial_vol)

    def test_shell_feature(self):
        doc = Document(name="ShellTest")
        box = BoxFeature(width=60.0, height=60.0, depth=40.0)
        doc.add_feature(box)
        solid_vol = doc.active_part.active_solid.volume

        # Shell with 2mm wall thickness
        shell = ShellFeature(target_feature_id=box.id, wall_thickness=2.0)
        doc.add_feature(shell)

        self.assertIsNotNone(doc.active_part.active_solid)
        self.assertTrue(doc.active_part.active_solid.is_valid)
        self.assertLess(doc.active_part.active_solid.volume, solid_vol)

    def test_ai_copilot_plan_and_ghost_preview(self):
        doc = Document(name="AIPlanTest")
        agent = CADAgent(doc)

        # Plan prompt
        plan = agent.plan_prompt("Create a 100 x 60 x 10 mm mounting plate")
        self.assertIsNotNone(plan)
        self.assertGreater(len(plan.tool_calls), 0)
        self.assertEqual(plan.tool_calls[0].tool_name, "feature.create_plate")
        self.assertGreater(plan.predicted_delta_vol, 0.0)

    def test_ai_copilot_hole_wizard_and_shell_prompt(self):
        doc = Document(name="AIEnhancedPromptTest")
        agent = CADAgent(doc)

        # Step 1: Create box
        res1 = agent.execute_prompt("Create a 100 x 60 x 20 mm box")
        self.assertTrue(res1.success)

        # Step 2: Add M8 hole
        res2 = agent.execute_prompt("Add an M8 counterbore hole")
        self.assertTrue(res2.success)

        # Step 3: Shell
        res3 = agent.execute_prompt("Shell with 2 mm wall thickness")
        self.assertTrue(res3.success)
        self.assertEqual(len(doc.active_part.features), 3)

    def test_cloud_providers_fallback(self):
        doc = Document(name="CloudFallbackTest")
        # Test Gemini, OpenAI, Anthropic without keys fallback seamlessly to heuristic engine
        gemini = GeminiProvider(api_key="")
        openai = OpenAIProvider(api_key="")
        claude = AnthropicProvider(api_key="")

        res_g = gemini.generate("Create a 100 x 60 x 10 mm mounting plate")
        self.assertEqual(len(res_g.tool_calls), 1)

        res_o = openai.generate("Create a 50 x 50 x 20 mm box")
        self.assertEqual(len(res_o.tool_calls), 1)

        res_c = claude.generate("Add a 20 mm circle to sketch")
        self.assertEqual(len(res_c.tool_calls), 1)


if __name__ == "__main__":
    unittest.main()
