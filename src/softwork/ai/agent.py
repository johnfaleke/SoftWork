"""
AI CAD Agent orchestrator: Understand -> Plan -> Operate -> Validate -> Explain.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from softwork.ai.context import AIContextBuilder
from softwork.ai.provider import ModelProvider, HeuristicEngineProvider, ToolCall
from softwork.ai.tools import ToolRegistry
from softwork.cad.validation import ValidationReport
from softwork.core.document import Document
from softwork.core.transaction import AITransaction


@dataclass
class AgentPlanStep:
    description: str
    tool_name: str
    arguments: Dict[str, Any]
    status: str = "pending"  # "pending", "success", "failed"


@dataclass
class AgentExecutionResult:
    prompt: str
    explanation: str
    plan_steps: List[AgentPlanStep] = field(default_factory=list)
    validation: Optional[ValidationReport] = None
    transactions: List[AITransaction] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None
    created_feature_id: Optional[str] = None


@dataclass
class AgentPlan:
    prompt: str = ""
    explanation: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    predicted_delta_vol: float = 0.0
    ghost_mesh: Optional[Any] = None
    intent: Optional[str] = None
    target_feature_id: Optional[str] = None
    predicted_tool_calls: List[Dict[str, Any]] = field(default_factory=list)


class CADAgent:
    """
    Antigravity-native CAD Agent translating human intent to deterministic parametric operations.
    Supports in-place parametric modification and new feature synthesis.
    """

    def __init__(self, document: Document, provider: Optional[ModelProvider] = None) -> None:
        self.document = document
        self.provider = provider or HeuristicEngineProvider()
        self.tools = ToolRegistry(document)

    def set_provider(self, provider: ModelProvider) -> None:
        self.provider = provider

    def plan_prompt(self, user_prompt: str) -> AgentPlan:
        """
        Generates an AI execution plan with simulated ghost mesh preview before committing.
        """
        # 1. Check for in-place parametric modification
        from softwork.ai.modifier import ParametricModifier
        if ParametricModifier.is_modification_prompt(user_prompt):
            mod_plan = ParametricModifier.plan_modification(self.document, user_prompt)
            if mod_plan is not None:
                mod_plan.prompt = user_prompt
                return mod_plan

        # 2. General provider planning
        context = AIContextBuilder.build_context(self.document)
        schemas = self.tools.get_schemas()
        response = self.provider.generate(
            prompt=user_prompt,
            tools_schema=schemas,
            context=context,
        )

        cur_solid = self.document.active_part.active_solid
        cur_vol = cur_solid.volume if cur_solid else 0.0

        # Estimate proposed delta
        delta_v = 0.0
        for call in response.tool_calls:
            if "extrude" in call.tool_name:
                dist = float(call.arguments.get("distance", 25.0))
                delta_v += dist * 1000.0
            elif "create_box" in call.tool_name:
                w = float(call.arguments.get("width", 50.0))
                h = float(call.arguments.get("height", 50.0))
                d = float(call.arguments.get("depth", 10.0))
                delta_v += w * h * d
            elif "create_plate" in call.tool_name:
                l = float(call.arguments.get("length", 100.0))
                w = float(call.arguments.get("width", 60.0))
                t = float(call.arguments.get("thickness", 10.0))
                delta_v += l * w * t
            elif "hole_wizard" in call.tool_name or "shell" in call.tool_name:
                delta_v -= 1500.0

        ghost_mesh = self.document.backend.to_mesh(cur_solid) if cur_solid else None

        return AgentPlan(
            prompt=user_prompt,
            explanation=response.content,
            tool_calls=response.tool_calls,
            predicted_delta_vol=delta_v,
            ghost_mesh=ghost_mesh,
        )

    def execute_prompt(self, user_prompt: str) -> AgentExecutionResult:
        """
        Full interaction loop:
        1. In-place modification check (v0.4)
        2. Context extraction
        3. Intent reasoning & planning via Provider
        4. Deterministic tool execution via Command Layer
        5. Parametric recompute & Geometry Validation
        6. Explainability & Change Review
        """
        # 1. In-place modification check
        from softwork.ai.modifier import ParametricModifier
        if ParametricModifier.is_modification_prompt(user_prompt):
            mod_res = ParametricModifier.execute_modification(self.document, user_prompt)
            if mod_res is not None:
                mod_res.prompt = user_prompt
                return mod_res

        # 2. General provider execution
        context = AIContextBuilder.build_context(self.document)
        schemas = self.tools.get_schemas()

        response = self.provider.generate(
            prompt=user_prompt,
            tools_schema=schemas,
            context=context,
        )

        result = AgentExecutionResult(
            prompt=user_prompt,
            explanation=response.content,
        )

        for call in response.tool_calls:
            step = AgentPlanStep(
                description=f"Call {call.tool_name} with {call.arguments}",
                tool_name=call.tool_name,
                arguments=call.arguments,
            )
            result.plan_steps.append(step)

            try:
                tx = self.tools.execute(call.tool_name, call.arguments)
                tx.prompt = user_prompt
                result.transactions.append(tx)
                step.status = "success"
            except Exception as e:
                step.status = "failed"
                result.success = False
                result.error_message = f"Error executing '{call.tool_name}': {str(e)}"
                break

        # Recompute & Validate
        self.document.recompute()
        validator = self.document.backend.validator if hasattr(self.document.backend, "validator") else None
        if validator and self.document.active_part.active_solid:
            report = validator.validate(self.document.active_part.active_solid)
            result.validation = report
            self.document.latest_validation = report

        return result
