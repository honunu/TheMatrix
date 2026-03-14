"""共享记忆模块"""
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional
import threading


class Memory:
    """Agent共享记忆"""

    def __init__(self, max_history: int = 100):
        self._store = {}
        self._history = []
        self._max_history = max_history
        self._lock = threading.Lock()

    def set(self, key: str, value: Any) -> None:
        """设置记忆"""
        with self._lock:
            self._store[key] = {
                "value": value,
                "timestamp": datetime.now()
            }
            self._history.append({
                "action": "set",
                "key": key,
                "timestamp": datetime.now()
            })
            self._trim_history()

    def get(self, key: str) -> Optional[Any]:
        """获取记忆"""
        with self._lock:
            item = self._store.get(key)
            return item["value"] if item else None

    def delete(self, key: str) -> bool:
        """删除记忆"""
        with self._lock:
            if key in self._store:
                del self._store[key]
                self._history.append({
                    "action": "delete",
                    "key": key,
                    "timestamp": datetime.now()
                })
                return True
            return False

    def get_all(self) -> dict:
        """获取所有记忆"""
        with self._lock:
            return {k: v["value"] for k, v in self._store.items()}

    def search(self, keyword: str) -> list:
        """搜索记忆"""
        results = []
        with self._lock:
            for key, item in self._store.items():
                if keyword.lower() in str(item["value"]).lower():
                    results.append({"key": key, **item})
        return results

    def _trim_history(self) -> None:
        """修剪历史记录"""
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def get_history(self, limit: int = 20) -> list:
        """获取历史记录"""
        with self._lock:
            return self._history[-limit:]

    def clear(self) -> None:
        """清空所有记忆"""
        with self._lock:
            self._store.clear()
            self._history.clear()
