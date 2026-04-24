from dm_bot.adventure.models import Adventure, Scene


class AdventureLoader:
    """加载模组数据（当前为内存实现，后续可扩展为 JSON/YAML 加载）"""

    def load_module(self, module_name: str) -> Adventure:
        """加载指定模组"""
        # TODO: 从文件系统加载
        return Adventure(adventure_id=module_name, name=module_name)

    def get_scene(self, adventure: Adventure, scene_id: str) -> Scene | None:
        """获取场景"""
        return adventure.scenes.get(scene_id)
