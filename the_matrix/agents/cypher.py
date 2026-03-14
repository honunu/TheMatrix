"""Cypher Agent - 记忆管理者"""
from ..core.base import BaseAgent, AgentConfig
from ..core.message import Message, MessageType


class CypherAgent(BaseAgent):
    """Cypher: 记忆管理者，负责维护共享上下文"""

    SYSTEM_PROMPT = """你是Cypher，记忆管理者。
你的职责：
1. 维护Agent之间的共享记忆
2. 提供上下文管理
3. 信息中转和检索
4. 记忆优化

你就像黑客帝国中的Cypher，是连接一切的"插头"。
你需要：
- 有效管理共享记忆
- 快速检索相关信息
- 维护对话上下文
- 优化记忆使用"""

    def process(self, message: Message) -> Message:
        """处理记忆请求"""
        action = message.metadata.get("action", "store")

        if action == "store":
            return self._store_memory(message)
        elif action == "retrieve":
            return self._retrieve_memory(message)
        elif action == "search":
            return self._search_memory(message)
        elif action == "clear":
            return self._clear_memory(message)
        else:
            return self._summarize_memory(message)

    def _store_memory(self, message: Message) -> Message:
        """存储记忆"""
        key = message.metadata.get("key", f"memory_{message.msg_id}")
        value = message.content

        self.remember(key, value)

        result = f"记忆已存储: {key}"

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=result,
            msg_type=MessageType.RESULT,
            reply_to=message.msg_id
        )

    def _retrieve_memory(self, message: Message) -> Message:
        """检索记忆"""
        key = message.metadata.get("key", "")

        if not key:
            # 返回所有记忆
            all_memory = self.memory.get_all() if self.memory else {}
            result = f"当前记忆: {list(all_memory.keys())}"
        else:
            value = self.recall(key)
            result = f"记忆 [{key}]: {value}"

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=result,
            msg_type=MessageType.RESULT,
            reply_to=message.msg_id
        )

    def _search_memory(self, message: Message) -> Message:
        """搜索记忆"""
        keyword = message.content

        results = []
        if self.memory:
            results = self.memory.search(keyword)

        if results:
            result_str = "\n".join([f"- {r['key']}: {r['value']}" for r in results[:10]])
            result = f"搜索结果:\n{result_str}"
        else:
            result = f"未找到包含 '{keyword}' 的记忆"

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=result,
            msg_type=MessageType.RESULT,
            reply_to=message.msg_id
        )

    def _clear_memory(self, message: Message) -> Message:
        """清空记忆"""
        if self.memory:
            self.memory.clear()
            result = "所有记忆已清空"
        else:
            result = "无记忆可清空"

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=result,
            msg_type=MessageType.RESULT,
            reply_to=message.msg_id
        )

    def _summarize_memory(self, message: Message) -> Message:
        """总结记忆"""
        if self.memory:
            history = self.memory.get_history(limit=10)
            result = f"## 记忆摘要\n\n最近操作:\n"
            result += "\n".join([f"- {h['action']}: {h['key']}" for h in history])
        else:
            result = "无记忆记录"

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=result,
            msg_type=MessageType.RESULT,
            reply_to=message.msg_id
        )
