"""消息传递机制"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class MessageType(Enum):
    """消息类型"""
    TASK = "task"           # 任务分配
    RESULT = "result"       # 结果返回
    QUERY = "query"         # 询问
    RESPONSE = "response"   # 响应
    BROADCAST = "broadcast" # 广播
    ALERT = "alert"         # 警告
    APPROVAL = "approval"   # 审批


@dataclass
class Message:
    """Agent间传递的消息"""
    sender: str
    receiver: str
    content: Any
    msg_type: MessageType = MessageType.TASK
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    reply_to: Optional[str] = None  # 关联的消息ID

    def to_dict(self) -> dict:
        return {
            "msg_id": self.msg_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "type": self.msg_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "reply_to": self.reply_to
        }

    def __str__(self) -> str:
        return f"[{self.msg_type.value.upper()}] {self.sender} -> {self.receiver}: {self.content[:100]}..."
