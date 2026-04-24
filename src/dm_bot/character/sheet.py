from pydantic import BaseModel, Field


class CharacterSheet(BaseModel):
    """COC 调查员角色卡"""

    character_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    age: int = 20
    occupation: str = ""

    # 基础属性
    strength: int = 50
    constitution: int = 50
    size: int = 50
    dexterity: int = 50
    appearance: int = 50
    intelligence: int = 50
    power: int = 50
    education: int = 50
    luck: int = 50

    # 衍生属性
    hit_points: int = 10
    magic_points: int = 10
    sanity: int = 50
    sanity_max: int = 99

    # 技能（技能名 -> 成功率）
    skills: dict[str, int] = Field(default_factory=dict)

    def get_skill_value(self, skill_name: str) -> int:
        """获取技能值，未设定则返回基础值"""
        return self.skills.get(skill_name, 0)
