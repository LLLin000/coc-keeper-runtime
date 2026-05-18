import json
from pathlib import Path

from dm_bot.adventure.models import Adventure, Scene


class AdventureLoader:
    """加载模组数据（当前为内存实现，后续可扩展为 JSON/YAML 加载）"""

    def load_module(self, module_name: str) -> Adventure:
        path = Path(module_name)
        if path.suffix == ".json":
            try:
                with open(path) as f:
                    data = json.load(f)
                return Adventure.model_validate(data)
            except FileNotFoundError:
                raise
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON in adventure file {module_name}: {e}"
                )
        return Adventure(adventure_id=module_name, name=module_name)

    def get_scene(self, adventure: Adventure, scene_id: str) -> Scene | None:
        """获取场景"""
        return adventure.scenes.get(scene_id)
