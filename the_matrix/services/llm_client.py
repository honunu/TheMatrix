"""LLM客户端 - 支持多种LLM供应商"""
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import requests


class LLMProvider(ABC):
    """LLM供应商抽象类"""

    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str, context: Dict = None) -> str:
        pass


class QwenProvider(LLMProvider):
    """阿里千问LLM供应商"""

    def __init__(self, api_key: str, base_url: str, model: str, **kwargs):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 4096)

    def chat(self, system_prompt: str, user_prompt: str, context: Dict = None) -> str:
        """调用千问API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 构建上下文
        messages = [{"role": "system", "content": system_prompt}]
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            messages.append({"role": "user", "content": f"{context_str}\n\n{user_prompt}"})
        else:
            messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")


class OpenAIProvider(LLMProvider):
    """OpenAI LLM供应商"""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", model: str = "gpt-4", **kwargs):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 4096)

    def chat(self, system_prompt: str, user_prompt: str, context: Dict = None) -> str:
        """调用OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_prompt}]
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            messages.append({"role": "user", "content": f"{context_str}\n\n{user_prompt}"})
        else:
            messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")


class LLMClient:
    """LLM客户端工厂"""

    PROVIDERS = {
        "qwen": QwenProvider,
        "openai": OpenAIProvider,
    }

    def __init__(self, config: dict):
        self.config = config
        provider_name = config.get("provider", "qwen").lower()
        provider_class = self.PROVIDERS.get(provider_name)

        if not provider_class:
            raise ValueError(f"Unsupported provider: {provider_name}")

        self.provider = provider_class(
            api_key=config["api_key"],
            base_url=config.get("base_url", ""),
            model=config.get("model", "qwen-plus"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 4096)
        )

    def chat(self, system_prompt: str, user_prompt: str, context: dict = None) -> str:
        """通用聊天接口"""
        return self.provider.chat(system_prompt, user_prompt, context)
