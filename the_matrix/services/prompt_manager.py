"""Prompt管理器"""
from pathlib import Path
from typing import Dict


class PromptManager:
    """管理和加载Agent的Prompt模板"""

    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent.parent / "prompts"
        self.prompts_dir = Path(prompts_dir)
        self._templates = {}
        self._load_prompts()

    def _load_prompts(self):
        """加载所有prompt模板"""
        if not self.prompts_dir.exists():
            return

        for file in self.prompts_dir.glob("*.txt"):
            agent_name = file.stem
            with open(file, "r", encoding="utf-8") as f:
                self._templates[agent_name] = f.read()

    def get(self, agent_name: str, **kwargs) -> str:
        """获取prompt模板并填充变量"""
        template = self._templates.get(agent_name, "")
        if not template:
            return self._get_default_prompt(agent_name)

        try:
            return template.format(**kwargs)
        except KeyError:
            return template

    def _get_default_prompt(self, agent_name: str) -> str:
        """获取默认prompt"""
        defaults = {
            "architect": "你是Architect，系统架构师。负责任务分解、资源分配和工作流编排。",
            "morpheus": "你是Morpheus，导航者。负责理解用户意图并制定研究策略。",
            "oracle": "你是Oracle，先知。负责风险评估和趋势预测。",
            "neo": "你是Neo，救世主。负责复杂问题决策和创新突破。",
            "trinity": "你是Trinity，执行者。负责高效执行任务并产出结果。",
            "smith": "你是Smith，防御者。负责异常检测和安全审计。",
            "cypher": "你是Cypher，记忆管理者。负责维护共享上下文。"
        }
        return defaults.get(agent_name.lower(), f"你是{agent_name}。")

    def register(self, agent_name: str, template: str):
        """注册新的prompt模板"""
        self._templates[agent_name] = template

    def list_prompts(self) -> Dict[str, str]:
        """列出所有prompt模板"""
        return self._templates.copy()
