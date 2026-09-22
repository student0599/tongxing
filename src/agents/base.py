"""子智能体基类。

参考 Claude Agent SDK 的子智能体（subagent）设计思想：
每个子智能体拥有独立的角色定位（system prompt）、职责与输入输出契约，
通过统一的 AgentResult 返回结果，便于编排器解耦调度与错误隔离。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from src.llm_client import ZhipuClient


@dataclass
class AgentResult:
    """子智能体统一返回结构。"""

    ok: bool
    data: Any = None
    error: str = ""

    @classmethod
    def success(cls, data: Any) -> "AgentResult":
        return cls(ok=True, data=data)

    @classmethod
    def failure(cls, error: str) -> "AgentResult":
        return cls(ok=False, error=error)


class BaseAgent(ABC):
    """所有子智能体的基类。"""

    name: str = "base"
    description: str = ""

    def __init__(self, client: Optional[ZhipuClient] = None) -> None:
        self.client = client

    @abstractmethod
    def run(self, **kwargs: Any) -> AgentResult:
        """执行该子智能体的核心任务。"""

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} name={self.name}>"
