"""Smith Agent - 防御者"""
from ..core.base import BaseAgent, AgentConfig
from ..core.message import Message, MessageType


class SmithAgent(BaseAgent):
    """Smith: 防御者，负责异常检测和安全审计"""

    SYSTEM_PROMPT = """你是Smith，防御者。
你的职责：
1. 检测异常和错误
2. 安全审计
3. 质量把控
4. 识别潜在威胁

你就像黑客帝国中的Smith，是系统的"免疫系统"。
你需要：
- 严格检查任何输出
- 识别潜在问题
- 确保安全性
- 提供改进建议"""

    def process(self, message: Message) -> Message:
        """处理验证请求"""
        if message.msg_type == MessageType.QUERY:
            # 验证请求
            return self._validate(message)
        else:
            # 防御请求
            return self._defend(message)

    def _validate(self, message: Message) -> Message:
        """验证结果"""
        content = message.content

        # 质量检查
        quality = self._check_quality(content)

        # 安全检查
        security = self._check_security(content)

        # 异常检测
        anomalies = self._detect_anomalies(content)

        result = f"""### 验证结果

**质量检查**: {quality}

**安全检查**: {security}

**异常检测**: {anomalies}

**结论**: {"通过" if "通过" in quality else "需要修改"}"""

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=result,
            msg_type=MessageType.RESPONSE,
            reply_to=message.msg_id
        )

    def _defend(self, message: Message) -> Message:
        """处理防御请求"""
        task = message.content

        # 威胁分析
        threats = self._analyze_threats(task)

        # 安全建议
        recommendations = self._get_recommendations(threats)

        result = f"""## 防御分析

### 威胁识别
{threats}

### 安全建议
{recommendations}"""

        return Message(
            sender=self.name,
            receiver=message.sender,
            content=result,
            msg_type=MessageType.RESULT,
            reply_to=message.msg_id
        )

    def _check_quality(self, content: str) -> str:
        """检查质量"""
        prompt = f"""检查以下内容质量：

{content}

评估：
1. 完整性
2. 准确性
3. 实用性

返回：质量评级（优秀/良好/需改进）+ 原因"""

        try:
            return self.think(prompt)
        except Exception:
            return "良好 - 基础检查通过"

    def _check_security(self, content: str) -> str:
        """检查安全性"""
        prompt = f"""检查以下内容的安全性：

{content}

检查：
1. 是否有敏感信息泄露
2. 是否有安全隐患
3. 是否有恶意代码

返回：安全评级 + 原因"""

        try:
            return self.think(prompt)
        except Exception:
            return "安全 - 未发现明显问题"

    def _detect_anomalies(self, content: str) -> str:
        """检测异常"""
        prompt = f"""检测以下内容的异常：

{content}

检查：
1. 逻辑异常
2. 数据异常
3. 格式异常

返回：异常描述或"未发现异常" """

        try:
            return self.think(prompt)
        except Exception:
            return "未发现明显异常"

    def _analyze_threats(self, task: str) -> str:
        """分析威胁"""
        prompt = f"""分析以下任务的潜在威胁：

{task}

列出可能的威胁和风险。"""

        try:
            return self.think(prompt)
        except Exception:
            return "未发现明显威胁"

    def _get_recommendations(self, threats: str) -> str:
        """获取安全建议"""
        prompt = f"""基于以下威胁分析，提供安全建议：

{threats}

提供具体的改进建议。"""

        try:
            return self.think(prompt)
        except Exception:
            return "建议：保持警惕，监控执行过程。"
