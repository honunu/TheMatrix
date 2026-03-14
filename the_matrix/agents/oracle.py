"""Oracle Agent - 先知"""
from ..core.base import BaseAgent, AgentConfig
from ..core.message import Message, MessageType


class OracleAgent(BaseAgent):
    """Oracle: 先知，负责风险评估和趋势预测"""

    SYSTEM_PROMPT = """你是Oracle，先知。
你的职责：
1. 预测风险和潜在问题
2. 识别趋势和模式
3. 提供前瞻性洞察
4. 评估行动的可行性

你就像黑客帝国中的Oracle，拥有预知能力。
你需要：
- 分析当前方案的潜在风险
- 预测可能的发展趋势
- 识别可能被忽视的问题
- 提供预防性建议"""

    def process(self, message: Message) -> Message:
        """处理预测请求"""
        task = message.content

        # 风险评估
        risk_assessment = self._assess_risks(task)

        # 趋势预测
        trend_prediction = self._predict_trends(task)

        # 模式识别
        patterns = self._identify_patterns(task)

        result = f"""## 预测分析

### 风险评估
{risk_assessment}

### 趋势预测
{trend_prediction}

### 模式识别
{patterns}

### 建议
基于以上分析，建议{'谨慎推进' if '高风险' in risk_assessment else '可以继续推进'}。"""

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=result,
            msg_type=MessageType.RESULT,
            reply_to=message.msg_id
        )

    def _assess_risks(self, task: str) -> str:
        """评估风险"""
        prompt = f"""评估以下任务的风险：

{task}

请分析：
1. 技术风险
2. 执行风险
3. 资源风险
4. 时间风险
5. 外部风险

返回风险等级（低/中/高）并说明原因。"""

        try:
            return self.think(prompt)
        except Exception:
            return "中风险：存在不确定性，需要监控。"

    def _predict_trends(self, task: str) -> str:
        """预测趋势"""
        prompt = f"""预测以下任务的发展趋势：

{task}

分析：
1. 可能的发展方向
2. 未来可能的变化
3. 需要关注的关键点"""

        try:
            return self.think(prompt)
        except Exception:
            return "趋势稳定，按照计划推进。"

    def _identify_patterns(self, task: str) -> str:
        """识别模式"""
        prompt = f"""识别以下任务中的模式和问题：

{task}

分析：
1. 重复出现的问题
2. 潜在的关联
3. 可复用的经验"""

        try:
            return self.think(prompt)
        except Exception:
            return "未发现明显异常模式。"
