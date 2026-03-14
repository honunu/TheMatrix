"""Trinity Agent - 执行者"""
from ..core.base import BaseAgent, AgentConfig
from ..core.message import Message, MessageType


class TrinityAgent(BaseAgent):
    """Trinity: 执行者，负责高效执行任务"""

    SYSTEM_PROMPT = """你是Trinity，执行者。
你的职责：
1. 高效执行分配的任务
2. 快速检索和处理信息
3. 产出实际结果
4. 突破限制达成目标

你就像黑客帝国中的Trinity，是最优秀的执行者。
你需要：
- 快速理解任务要求
- 高效执行
- 提供可用的结果
- 突破困难达成目标"""

    def process(self, message: Message) -> Message:
        """处理执行请求"""
        task = message.content

        # 获取上下文
        context = self._get_context(message.msg_id)

        # 执行任务
        result = self._execute_task(task, context)

        # 让Smith验证
        smith = self.agents.get("Smith")
        validation = ""
        if smith:
            validation_msg = Message(
                sender=self.name,
                receiver="Smith",
                content=result,
                msg_type=MessageType.QUERY
            )
            validation = smith.process(validation_msg).content

        validation_section = ""
        if validation:
            validation_section = f"### 验证结果\n{validation}"

        final_result = f"""## 执行结果

### 产出
{result}

{validation_section}"""

        # 存储结果
        self.remember(f"result_{message.msg_id}", result)

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=final_result,
            msg_type=MessageType.RESULT,
            reply_to=message.msg_id
        )

    def _get_context(self, msg_id: str) -> dict:
        """获取执行上下文"""
        context = {}

        intent = self.recall(f"intent_{msg_id}")
        if intent:
            context["intent"] = intent

        strategy = self.recall(f"strategy_{msg_id}")
        if strategy:
            context["strategy"] = strategy

        return context

    def _execute_task(self, task: str, context: dict) -> str:
        """执行任务"""
        prompt = f"""执行以下任务：

任务: {task}

上下文:
{context}

请高效执行任务，提供实际可用的结果。
根据任务类型（代码开发/分析/研究），提供相应格式的结果。"""

        try:
            return self.think(prompt, context)
        except Exception as e:
            return f"执行出错: {str(e)}"
