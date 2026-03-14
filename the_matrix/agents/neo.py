"""Neo Agent - 救世主"""
from ..core.base import BaseAgent, AgentConfig
from ..core.message import Message, MessageType


class NeoAgent(BaseAgent):
    """Neo: 救世主，负责复杂问题决策和创新突破"""

    SYSTEM_PROMPT = """你是Neo，救世主。
你的职责：
1. 处理复杂和未知的问题
2. 突破常规思维，找到创新解决方案
3. 做出关键决策
4. 在困境中找到出路

你就像黑客帝国中的Neo，拥有突破一切限制的能力。
当其他Agent无法解决问题时，你会介入。
你需要：
- 跳出常规思维
- 综合各种信息做出判断
- 找到创新的解决方案
- 敢于打破常规"""

    def process(self, message: Message) -> Message:
        """处理复杂决策"""
        task = message.content

        # 获取上下文
        context = self._get_context(message.msg_id)

        # 分析问题本质
        analysis = self._analyze_problem(task, context)

        # 制定解决方案
        solution = self._develop_solution(analysis, context)

        # 如果需要，调用Trinity执行
        execution_result = None
        if solution.get("needs_execution"):
            trinity = self.agents.get("Trinity")
            if trinity:
                exec_msg = Message(
                    sender=self.name,
                    receiver="Trinity",
                    content=solution["execution_plan"],
                    msg_type=MessageType.TASK
                )
                execution_result = trinity.process(exec_msg).content

        exec_section = ""
        if execution_result:
            exec_section = f"### 执行结果\n{execution_result}"

        result = f"""## 复杂问题分析

### 问题本质
{analysis.get('essence', '')}

### 创新解决方案
{solution.get('description', '')}

### 决策依据
{solution.get('rationale', '')}

### 执行计划
{solution.get('execution_plan', '')}

{exec_section}"""

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=result,
            msg_type=MessageType.RESULT,
            reply_to=message.msg_id
        )

    def _get_context(self, msg_id: str) -> dict:
        """获取相关上下文"""
        context = {}

        # 从记忆中获取
        intent = self.recall(f"intent_{msg_id}")
        if intent:
            context["intent"] = intent

        strategy = self.recall(f"strategy_{msg_id}")
        if strategy:
            context["strategy"] = strategy

        oracle_assessment = self.recall(f"oracle_assessment_{msg_id}")
        if oracle_assessment:
            context["risk_assessment"] = oracle_assessment

        return context

    def _analyze_problem(self, task: str, context: dict) -> dict:
        """分析问题本质"""
        prompt = f"""深入分析这个复杂问题：

任务: {task}

上下文:
{context}

请分析：
1. 问题的本质是什么？
2. 真正的难点在哪里？
3. 常规方法为什么可能失败？
4. 需要什么突破？"""

        try:
            result = self.think(prompt)
            return {"essence": result, "task": task}
        except Exception as e:
            return {"essence": str(e), "task": task}

    def _develop_solution(self, analysis: dict, context: dict) -> dict:
        """制定解决方案"""
        prompt = f"""基于问题分析，制定创新解决方案：

问题分析: {analysis.get('essence', '')}

请提供：
1. 创新方案描述
2. 决策依据
3. 执行计划
4. 是否需要执行（needs_execution: true/false）

返回JSON格式：
{{
    "description": "方案描述",
    "rationale": "决策依据",
    "execution_plan": "执行计划",
    "needs_execution": true/false
}}"""

        try:
            result = self.think(prompt)
            return {
                "description": result,
                "rationale": "基于深度分析",
                "execution_plan": "交由Trinity执行",
                "needs_execution": True
            }
        except Exception:
            return {
                "description": "标准解决方案",
                "rationale": "常规判断",
                "execution_plan": "交由Trinity执行",
                "needs_execution": True
            }
