"""基础Agent类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
import yaml
from pathlib import Path

from .message import Message
from .memory import Memory


@dataclass
class AgentConfig:
    """Agent配置"""
    name: str
    description: str
    system_prompt: str = ""


class BaseAgent(ABC):
    """所有Agent的基类"""

    def __init__(
        self,
        config: AgentConfig,
        llm_client,
        memory: Optional[Memory] = None,
        agents: Optional[dict] = None
    ):
        self.config = config
        self.name = config.name
        self.description = config.description
        self.llm = llm_client
        self.memory = memory
        self.agents = agents or {}

    @abstractmethod
    def process(self, message: Message) -> Message:
        """处理消息的抽象方法"""
        pass

    def think(self, prompt: str, context: dict = None) -> str:
        """调用LLM进行思考"""
        return self.llm.chat(
            system_prompt=self.config.system_prompt,
            user_prompt=prompt,
            context=context or {}
        )

    def send_to(self, agent_name: str, content: Any) -> Message:
        """发送消息给另一个Agent"""
        target_agent = self.agents.get(agent_name)
        if target_agent:
            message = Message(
                sender=self.name,
                receiver=agent_name,
                content=content,
                msg_type=MessageType.TASK
            )
            return target_agent.process(message)
        raise ValueError(f"Agent {agent_name} not found")

    def broadcast(self, content: Any) -> None:
        """广播消息给所有Agent"""
        for agent_name, agent in self.agents.items():
            if agent_name != self.name:
                message = Message(
                    sender=self.name,
                    receiver=agent_name,
                    content=content,
                    msg_type=MessageType.BROADCAST
                )
                agent.process(message)

    def remember(self, key: str, value: Any) -> None:
        """存储到共享记忆"""
        if self.memory:
            self.memory.set(key, value)

    def recall(self, key: str) -> Any:
        """从共享记忆读取"""
        if self.memory:
            return self.memory.get(key)
        return None

    @classmethod
    def load_config(cls, config_path: str = None) -> dict:
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
