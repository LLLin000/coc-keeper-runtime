from dm_bot.character.sheet import CharacterSheet


class CharacterBuilder:
    """对话式角色创建器"""

    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}  # user_id -> 创建会话状态

    def begin_creation(self, user_id: str) -> str:
        """开始创建流程，返回第一句话"""
        self._sessions[user_id] = {"step": "name", "data": {}}
        return "你好，我是你的守秘人。我们要创建一个调查员角色。首先，你叫什么名字？"

    def handle_response(self, user_id: str, text: str) -> str:
        """处理玩家回复，返回下一步提示"""
        session = self._sessions.get(user_id)
        if not session:
            return self.begin_creation(user_id)

        step = session["step"]
        data = session["data"]

        if step == "name":
            data["name"] = text
            session["step"] = "age"
            return f"好的，{text}。你今年多少岁？"

        elif step == "age":
            try:
                data["age"] = int(text)
            except ValueError:
                return "请输入数字。你今年多少岁？"
            session["step"] = "occupation"
            return "你的职业是什么？（例如：考古学家、记者、医生）"

        elif step == "occupation":
            data["occupation"] = text
            # 生成基础属性
            import random
            stats = {
                "strength": random.randint(30, 80),
                "constitution": random.randint(30, 80),
                "size": random.randint(40, 90),
                "dexterity": random.randint(30, 80),
                "appearance": random.randint(30, 80),
                "intelligence": random.randint(40, 90),
                "power": random.randint(30, 80),
                "education": random.randint(40, 90),
                "luck": random.randint(30, 80),
            }
            data.update(stats)
            data["hit_points"] = (stats["constitution"] + stats["size"]) // 10
            data["magic_points"] = stats["power"] // 5
            data["sanity"] = stats["power"]
            data["sanity_max"] = 99 - data["skills_bonus"] if "skills_bonus" in data else 99
            session["step"] = "done"
            return (
                f"角色创建完成！\n"
                f"姓名：{data['name']}\n"
                f"年龄：{data['age']}\n"
                f"职业：{data['occupation']}\n"
                f"HP：{data['hit_points']} | MP：{data['magic_points']} | SAN：{data['sanity']}\n"
                f"STR:{stats['strength']} CON:{stats['constitution']} SIZ:{stats['size']} "
                f"DEX:{stats['dexterity']} APP:{stats['appearance']} INT:{stats['intelligence']} "
                f"POW:{stats['power']} EDU:{stats['education']} LUCK:{stats['luck']}"
            )

        else:
            return "你的角色已经创建完成。输入 /sheet 查看角色卡。"

    def get_sheet(self, user_id: str) -> CharacterSheet | None:
        """获取已创建的角色卡"""
        session = self._sessions.get(user_id)
        if not session or session["step"] != "done":
            return None
        data = session["data"]
        return CharacterSheet(
            character_id=user_id,
            name=data["name"],
            age=data["age"],
            occupation=data["occupation"],
            strength=data["strength"],
            constitution=data["constitution"],
            size=data["size"],
            dexterity=data["dexterity"],
            appearance=data["appearance"],
            intelligence=data["intelligence"],
            power=data["power"],
            education=data["education"],
            luck=data["luck"],
            hit_points=data["hit_points"],
            magic_points=data["magic_points"],
            sanity=data["sanity"],
            sanity_max=data.get("sanity_max", 99),
        )
