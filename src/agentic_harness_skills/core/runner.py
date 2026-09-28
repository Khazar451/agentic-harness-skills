"""Execution dispatcher for skills (Inline vs Isolated context)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

from agentic_harness_skills.core.schema import SkillDefinition


class ExecutionMode(str, Enum):
    """Execution mode conforming to the Agentic Harness Patterns."""

    INLINE = "inline"  # Shares parent conversation context
    ISOLATED = "isolated"  # Runs in dedicated subagent/child context budget


@dataclass
class ExecutionResult:
    skill_name: str
    mode: ExecutionMode
    success: bool
    output: Any
    tokens_consumed: int
    error: Optional[str] = None


class SkillRunner:
    """Dispatches skill execution adhering to harness isolation boundaries."""

    def __init__(self, default_mode: ExecutionMode = ExecutionMode.INLINE) -> None:
        self.default_mode = default_mode
        self._execution_history: list[ExecutionResult] = []

    def execute(
        self,
        skill: SkillDefinition,
        input_args: dict[str, Any],
        mode: Optional[ExecutionMode] = None,
        executor_func: Optional[Callable[[SkillDefinition, dict[str, Any]], Any]] = None,
    ) -> ExecutionResult:
        """Executes a loaded skill definition in the selected mode."""
        exec_mode = mode or self.default_mode

        try:
            if executor_func:
                result_data = executor_func(skill, input_args)
            else:
                # Default mock executor returning structured skill activation
                result_data = {
                    "activated_skill": skill.name,
                    "mode": exec_mode.value,
                    "instructions_loaded": len(skill.body),
                    "args": input_args,
                }

            result = ExecutionResult(
                skill_name=skill.name,
                mode=exec_mode,
                success=True,
                output=result_data,
                tokens_consumed=skill.total_estimated_tokens,
            )
        except Exception as exc:
            result = ExecutionResult(
                skill_name=skill.name,
                mode=exec_mode,
                success=False,
                output=None,
                tokens_consumed=0,
                error=str(exc),
            )

        self._execution_history.append(result)
        return result

    @property
    def history(self) -> list[ExecutionResult]:
        return list(self._execution_history)
