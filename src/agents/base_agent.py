"""
Base Agent Definition and Communication Protocol
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time


@dataclass
class AgentMessage:
    sender: str
    receiver: str
    content: str
    step_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "step_name": self.step_name,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class BaseAgent:
    """
    Base Agent class providing logging, execution telemetry, and lifecycle hooks.
    """

    def __init__(self, name: str, role_description: str):
        self.name = name
        self.role_description = role_description
        self.execution_log: List[AgentMessage] = []

    def log_step(
        self,
        receiver: str,
        step_name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        msg = AgentMessage(
            sender=self.name,
            receiver=receiver,
            step_name=step_name,
            content=content,
            metadata=metadata or {}
        )
        self.execution_log.append(msg)
        return msg
