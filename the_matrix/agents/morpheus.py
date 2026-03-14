"""Morpheus Agent - 导航者"""
from ..core.base import BaseAgent, AgentConfig
from ..core.message import Message, MessageType


class MorpheusAgent(BaseAgent):
    """Morpheus: 导航者，负责理解用户意图并制定策略"""

    SYSTEM_PROMPT = """你是Morpheus，导航者。
你的职责：
1. 理解用户的真实意图
2. 制定研究和执行策略
3. 引导任务的方向
4. 为其他Agent提供上下文

你就像黑客帝国中的Morpheus，是用户的"引导者"。
你需要：
- 深入理解用户想要什么
- 将模糊的需求清晰化
- 制定合适的探索策略
- 帮助Neo和其他Agent理解任务背景"""

    def process(self, message: Message) -> Message:
        """处理导航请求"""
        user_request = message.content

        # 深入理解用户意图
        insight = self._understand_intent(user_request)

        # 制定策略
        strategy = self._formulate_strategy(insight)

        # 存储理解结果
        self.remember(f"intent_{message.msg_id}", insight)
        self.remember(f"strategy_{message.msg_id}", strategy)

        result = f"""## 任务理解

**原始需求**: {user_request}

**深入理解**: 
{insight.get('understanding', '')}

**执行策略**:
{strategy}

**推荐Agent**: {insight.get('recommended_agents', [])}"""

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=result,
            msg_type=MessageType.RESULT,
            reply_to=message.msg_id
        )

    def _understand_intent(self, request: str) -> dict:
        """理解用户意图"""
        prompt = f"""深入分析用户需求：

"{request}"

请分析：
1. 用户真正想要什么？（表面需求 vs 深层需求）
2. 任务的背景是什么？
3. 成功的标准是什么？
4. 有哪些约束条件？

返回JSON格式：
{{
    "understanding": "详细理解",
    "surface_need": "表面需求",
    "deep_need": "深层需求",
    "success_criteria": ["标准1", "标准2"],
    "constraints": ["约束1"],
    "recommended_agents": ["Oracle", "Neo", "Trinity"]
}}"""

        try:
            result = self.think(prompt)
            return {"understanding": result, "request": request}
        except Exception as e:
            return {"understanding": str(e), "request": request}

    def _formulate_strategy(self, insight: dict) -> str:
        """制定策略"""
        prompt = f"""基于以下理解，制定执行策略：

{insight.get('understanding', '')}

请制定：
1. 探索路径（如何一步步接近目标）
2. 需要收集哪些信息
3. 可能的挑战和应对方案

直接返回策略描述。"""

        try:
            return self.think(prompt)
        except Exception as e:
            return f"标准执行策略：按照直接、高效的方式完成任务。"
