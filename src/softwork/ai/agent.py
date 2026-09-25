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


class CADAgent:
    """
    Antigravity-native CAD Agent translating human intent to deterministic parametric operations.
    """

    def __init__(self, document: Document, provider: Optional[ModelProvider] = None) -> None:
        self.document = document
        self.provider = provider or HeuristicEngineProvider()
        self.tools = ToolRegistry(document)

    def execute_prompt(self, user_prompt: str) -> AgentExecutionResult:
        """
        Full interaction loop:
        1. Context extraction (selection + dependencies)
        2. Intent reasoning & planning via Provider
        3. Deterministic tool execution via Command Layer
        4. Parametric recompute & Geometry Validation
        5. Explainability & Change Review
        """
        # Step 1: Context Extraction
        context = AIContextBuilder.build_context(self.document)
        schemas = self.tools.get_schemas()

        # Step 2: Intent Reasoning & Planning
        response = self.provider.generate(
            prompt=user_prompt,
            tools_schema=schemas,
            context=context,
        )

        result = AgentExecutionResult(
            prompt=user_prompt,
            explanation=response.content,
        )

        # Step 3: Tool Execution through Command Layer
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

        # Step 4: Validate Geometry
        val_report = self.document.recompute()
        result.validation = val_report

        return result
