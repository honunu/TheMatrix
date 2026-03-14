"""Architect Agent - 系统架构师"""
from typing import Any

from ..core.base import BaseAgent, AgentConfig
from ..core.message import Message, MessageType


class ArchitectAgent(BaseAgent):
    """Architect: 系统架构师，负责任务分解与资源分配"""

    SYSTEM_PROMPT = """你是Architect，系统架构师。
你的职责：
1. 将复杂任务分解为可执行的子任务
2. 协调各Agent之间的工作
3. 优化资源分配和负载均衡
4. 监控整个系统的工作流程

当收到任务时，你应该：
- 分析任务的复杂度
- 确定需要哪些Agent协作
- 制定执行计划
- 分配任务给合适的Agent

记住：你不是执行者，而是协调者。"""

    def __init__(self, config: AgentConfig, llm_client, memory=None, agents=None):
        config.system_prompt = self.SYSTEM_PROMPT
        super().__init__(config, llm_client, memory, agents)

    def process(self, message: Message) -> Message:
        """处理任务分配请求"""
        task = message.content

        # 分析任务并制定计划
        plan = self._create_plan(task)

        # 存储计划到记忆
        self.remember(f"plan_{message.msg_id}", plan)

        # 根据计划分配任务
        results = self._execute_plan(plan, message)

        # 汇总结果
        final_result = self._aggregate_results(results)

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=final_result,
            msg_type=MessageType.RESULT,
            metadata={"plan": plan},
            reply_to=message.msg_id
        )

    def _create_plan(self, task: Any) -> dict:
        """创建执行计划"""
        prompt = f"""分析以下任务，制定执行计划：

任务：{task}

请分析：
1. 任务类型（代码开发/系统分析/金融研究等）
2. 需要哪些Agent协作
3. 执行顺序
4. 潜在风险

以JSON格式返回：
{{
    "task_type": "类型",
    "required_agents": ["Morpheus", "Neo", "Trinity"],
    "execution_order": ["步骤1", "步骤2"],
    "risks": ["风险1"]
}}"""

        try:
            result = self.think(prompt)
            # 简单解析（实际可用JSON解析）
            return {"raw": result, "task": task}
        except Exception as e:
            return {"task": task, "error": str(e)}

    def _execute_plan(self, plan: dict, original_message: Message) -> dict:
        """执行计划"""
        results = {}

        # 直接执行，不再调用sub-agents（避免超时）
        # 1. 简单分析任务
        task_analysis = self.think(f"分析以下任务：{plan['task']}")
        results["analysis"] = task_analysis

        # 2. 直接生成结果
        final_result = self.think(f"根据以下分析完成任务：{task_analysis}")
        results["execution"] = final_result

        # 3. 复杂任务交给Neo处理
        neo = self.agents.get("Neo")
        if neo and self._is_complex_task(plan["task"]):
            neo_msg = Message(
                sender=self.name,
                receiver="Neo",
                content=plan["task"],
                msg_type=MessageType.TASK
            )
            neo_result = neo.process(neo_msg)
            results["neo"] = neo_result.content
        else:
            # 简单任务交给Trinity执行
            trinity = self.agents.get("Trinity")
            if trinity:
                trinity_msg = Message(
                    sender=self.name,
                    receiver="Trinity",
                    content=plan["task"],
                    msg_type=MessageType.TASK
                )
                trinity_result = trinity.process(trinity_msg)
                results["trinity"] = trinity_result.content

        return results

    def _is_complex_task(self, task: Any) -> bool:
        """判断任务是否复杂"""
        task_str = str(task).lower()
        complex_keywords = ["复杂", "系统", "架构", "设计", "困难", "挑战", "创新"]
        return any(kw in task_str for kw in complex_keywords)

    def _aggregate_results(self, results: dict) -> str:
        """汇总各Agent的结果"""
        if not results:
            return "任务执行完成，无结果返回。"

        summary_parts = []
        for agent_name, result in results.items():
            summary_parts.append(f"### {agent_name.upper()} 的贡献:\n{result}\n")

        return "\n".join(summary_parts)
