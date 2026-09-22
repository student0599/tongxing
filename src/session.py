"""导航会话管理：维护「连续导航模式」的多轮上下文。

视障用户出行是一个连续过程，系统需要记住已提醒过什么、当前走到哪一步，
从而生成连贯、不重复的语音指引。本模块提供与框架无关的纯数据模型，
在 Streamlit 中挂载到 st.session_state 即可跨交互持久化。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Turn:
    """单轮导航记录。"""

    step: int
    environment: Dict[str, Any]
    guidance: str


@dataclass
class NavigationSession:
    """一次完整出行的会话状态。"""

    goal: str = ""                 # 用户目的地
    destination: str = ""          # 目的地别名（与 goal 等价，保留扩展）
    turns: List[Turn] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # 状态操作
    # ------------------------------------------------------------------ #
    @property
    def step_count(self) -> int:
        return len(self.turns)

    def set_goal(self, goal: str) -> None:
        self.goal = goal.strip()
        self.destination = self.goal

    def add_turn(self, environment: Dict[str, Any], guidance: str) -> Turn:
        turn = Turn(step=self.step_count + 1, environment=environment, guidance=guidance)
        self.turns.append(turn)
        return turn

    def reset(self) -> None:
        """清空会话，开始一次新导航。"""
        self.goal = ""
        self.destination = ""
        self.turns.clear()

    # ------------------------------------------------------------------ #
    # 上下文构造（供指引智能体使用）
    # ------------------------------------------------------------------ #
    def history(self, n: int = 3) -> List[Dict[str, Any]]:
        """最近 n 轮历史，供指引智能体避免重复。"""
        return [
            {"step": t.step, "guidance": t.guidance, "environment": t.environment}
            for t in self.turns[-n:]
        ]

    def last_guidance(self) -> Optional[str]:
        return self.turns[-1].guidance if self.turns else None

    def summary(self) -> str:
        """会话摘要（界面展示）。"""
        if not self.turns:
            return "尚未开始导航"
        lines = [f"目的地：{self.goal or '未设定'}", f"已指引 {self.step_count} 步："]
        for t in self.turns:
            lines.append(f"  · 第{t.step}步：{t.guidance}")
        return "\n".join(lines)
