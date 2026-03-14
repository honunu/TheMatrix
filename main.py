"""The Matrix - 多智能体系统入口"""
import sys
import yaml
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from the_matrix.core.base import AgentConfig
from the_matrix.core.memory import Memory
from the_matrix.core.message import Message, MessageType
from the_matrix.services.llm_client import LLMClient
from the_matrix.services.prompt_manager import PromptManager


class TheMatrix:
    """The Matrix 多智能体系统"""

    def __init__(self, config_path: str = None):
        # 加载配置
        if config_path is None:
            config_path = project_root / "config" / "settings.yaml"

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # 初始化LLM客户端
        self.llm = LLMClient(self.config["llm"])

        # 初始化共享记忆
        memory_config = self.config.get("memory", {})
        self.memory = Memory(max_history=memory_config.get("max_history", 100))

        # 初始化Prompt管理器
        self.prompt_manager = PromptManager()

        # 直接创建agents字典
        self.agents = {}

        # 延迟导入和创建agents
        self._init_agents_simple()

    def _init_agents_simple(self):
        """简化初始化"""
        from the_matrix.agents.architect import ArchitectAgent
        from the_matrix.agents.morpheus import MorpheusAgent
        from the_matrix.agents.trinity import TrinityAgent
        from the_matrix.agents.oracle import OracleAgent
        from the_matrix.agents.neo import NeoAgent
        from the_matrix.agents.smith import SmithAgent
        from the_matrix.agents.cypher import CypherAgent

        agent_configs = self.config.get("agents", {})

        # 创建所有agents
        all_agents = [
            ("Cypher", CypherAgent, agent_configs.get("cypher", {})),
            ("Smith", SmithAgent, agent_configs.get("smith", {})),
            ("Morpheus", MorpheusAgent, agent_configs.get("morpheus", {})),
            ("Oracle", OracleAgent, agent_configs.get("oracle", {})),
            ("Trinity", TrinityAgent, agent_configs.get("trinity", {})),
            ("Neo", NeoAgent, agent_configs.get("neo", {})),
            ("Architect", ArchitectAgent, agent_configs.get("architect", {})),
        ]

        for name, cls, cfg in all_agents:
            agent_config = AgentConfig(
                name=cfg.get("name", name),
                description=cfg.get("description", "")
            )
            self.agents[name] = cls(
                config=agent_config,
                llm_client=self.llm,
                memory=self.memory,
                agents=self.agents
            )

    def run(self, task: str) -> str:
        """运行任务"""
        print(f"\n{'='*60}")
        print(f"The Matrix System")
        print(f"{'='*60}")
        print(f"\n任务: {task}\n")

        # 创建初始消息
        initial_message = Message(
            sender="user",
            receiver="Architect",
            content=task,
            msg_type=MessageType.TASK
        )

        # 通过Architect处理
        result = self.agents["Architect"].process(initial_message)

        print(f"\n{'='*60}")
        print(f"执行完成")
        print(f"{'='*60}\n")

        return result.content

    def interactive(self):
        """交互模式"""
        print("\n欢迎进入 The Matrix!")
        print("输入您的任务，按回车执行")
        print("输入 'quit' 或 'exit' 退出\n")

        while True:
            try:
                task = input("> ").strip()

                if task.lower() in ["quit", "exit", "q"]:
                    print("\n离开Matrix... 后会有期!")
                    break

                if not task:
                    continue

                result = self.run(task)
                print(f"\n{result}\n")

            except KeyboardInterrupt:
                print("\n\n离开Matrix... 后会有期!")
                break
            except Exception as e:
                print(f"\n错误: {str(e)}\n")


def main():
    """主入口"""
    matrix = TheMatrix()

    # 检查命令行参数
    if len(sys.argv) > 1:
        # 命令行模式
        task = " ".join(sys.argv[1:])
        result = matrix.run(task)
        print(result)
    else:
        # 交互模式
        matrix.interactive()


if __name__ == "__main__":
    main()
