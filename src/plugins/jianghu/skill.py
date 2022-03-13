import os
from datetime import datetime
from random import choice, randint
from src.plugins.jianghu.user_info import UserInfo
from src.utils.db import db
"""技能:
  - 主动技能
    - 主动攻击
    - 主动辅助
  - 被动技能
  - 状态加持"""


class 战斗计数():

    def __init__(self) -> None:
        self.伤害 = 0
        self.治疗 = 0


data_dir = os.path.realpath(__file__ + "/../../../../data/战斗记录/")


class Skill():

    def __init__(self) -> None:
        self.战斗记录目录 = os.path.join(data_dir, datetime.now().strftime("%Y%m%d"))
        if not os.path.isdir(self.战斗记录目录):
            os.makedirs(self.战斗记录目录)
        self.战斗编号 = str(len(os.listdir(self.战斗记录目录)))
        self.skill = {
            "三清剑法": {
                "type": "主动招式",
                "招式类型": "外功招式",
                "招式": self.三清剑法
            },
            "紫气东来": {
                "type": "主动招式",
                "招式类型": "内功招式",
                "招式": self.紫气东来
            },
            "斗转星移": {
                "type": "被动招式",
                "招式类型": "外功招式",
                "触发": "外功伤害",
                "招式": self.斗转星移
            },
            "十方鬼道": {
                "type": "主动招式",
                "招式类型": "内功招式",
                "招式": self.十方鬼道
            },
            "推气过宫": {
                "type": "主动招式",
                "招式类型": "内功招式",
                "招式": self.推气过宫
            },
            "摧山坼地": {
                "type": "主动招式",
                "招式类型": "外功招式",
                "招式": self.摧山坼地
            },
            "北冥神功": {
                "type": "被动招式",
                "招式类型": "内功招式",
                "触发": "内功伤害",
                "招式": self.北冥神功
            },
            "剑若惊鸿": {
                "type": "主动招式",
                "招式类型": "外功招式",
                "招式": self.剑若惊鸿
            }
        }

    def 战斗记录(self, 战斗记录):
        战斗记录文件 = os.path.join(self.战斗记录目录, self.战斗编号)
        with open(战斗记录文件, "a", encoding="utf-8") as f:
            f.write(战斗记录 + "\n")

    def 触发被动(self, 武学: list, 事件: str, 数值: int, 自己: UserInfo, 目标: UserInfo):
        if not any(武学):
            return 数值, ""
        招式 = choice([i for i in 武学 if i])
        招式 = self.skill.get(招式, {})
        if 招式.get("type") == "被动招式" and 招式.get("触发") == 事件:
            return 招式["招式"](自己, 目标, 数值)
        return 数值, False

    def 计算内力(self,
             技能名称: str,
             自己: UserInfo,
             对方: UserInfo,
             消耗内力: int,
             需要内力: int = None,
             是否普通攻击: bool = True):
        if not 需要内力:
            需要内力 = 消耗内力
        if 自己.当前内力 < 需要内力:
            if 是否普通攻击:
                self.造成伤害(f"{技能名称}(<span class='text-primary'>内力不足</span>)",
                          自己, 对方, *自己.普通攻击())
            return False
        自己.内力变化(-消耗内力)
        self.战斗记录(
            f"<strong>{自己.名称}</strong> {技能名称} 内力-<span class='text-primary'>{消耗内力}</span>({自己.当前内力}/{自己.当前状态['内力上限']})"
        )
        return True

    def 治疗(self, 技能名称: str, 自己: UserInfo, 对方: UserInfo, 治疗量: int):
        治疗量, _ = self.触发被动(自己.基础属性["武学"], "治疗", 治疗量, 自己, 对方)
        损失气血 = 自己.当前状态['气血上限'] - 自己.当前气血
        if 治疗量 > 损失气血:
            治疗量 = 损失气血
        自己.本次治疗 += 治疗量
        自己.气血变化(治疗量)
        self.战斗记录(
            f"<strong>{自己.名称}</strong> < {技能名称}[治疗](+<span class='text-success'>{治疗量}</span>) 生命({自己.当前气血}/{自己.当前状态['气血上限']})"
        )

    def 造成伤害(self,
             技能名称: str,
             攻方: UserInfo,
             守方: UserInfo,
             伤害类型: str,
             伤害数值: float,
             穿透: float = 0) -> bool:
        """造成伤害"""
        伤害数值, 重伤信息 = self.触发被动(守方.基础属性["武学"], 伤害类型, 伤害数值,守方, 攻方)
        if 重伤信息:
            return 重伤信息
        if 伤害类型 == "外功伤害":
            防御 = 守方.当前状态["外功防御"] - 穿透
        elif 伤害类型 == "内功伤害":
            防御 = 守方.当前状态["内功防御"] - 穿透
        elif 伤害类型 == "混合伤害":
            防御 = 守方.当前状态["外功防御"] + 守方.当前状态["内功防御"] - 穿透
        elif 伤害类型 == "穿透伤害":
            防御 = 0
        if 防御 < 0:
            防御 = 0
        伤害 = int(伤害数值 * (1000 / (1000 + 防御)))
        if 守方.当前气血 < 伤害:
            伤害 = 守方.当前气血
        攻方.本次伤害 += 伤害
        守方.气血变化(-伤害)
        self.战斗记录(
            f"<strong>{攻方.名称}</strong> {技能名称}[{伤害类型[:2]}](-<span class='text-danger'>{伤害}</span>) > <strong>{守方.名称}</strong>({守方.当前气血}/{守方.当前状态['气血上限']})"
        )
        重伤状态 = 守方.当前气血 <= 0
        return 重伤状态, 伤害

    def 三清剑法(self, 自己: UserInfo, 目标: UserInfo):
        """对目标攻击三次, 伤害逐渐提高"""
        伤害类型, 伤害数值, 穿透 = 自己.普通攻击()
        重伤状态, _ = self.造成伤害("三清剑法", 自己, 目标, 伤害类型, 伤害数值 * 0.3, 穿透)
        if not 重伤状态:
            重伤状态, _ = self.造成伤害("三清剑法", 自己, 目标, 伤害类型, 伤害数值 * 0.7, 穿透)
            if not 重伤状态:
                重伤状态, _ = self.造成伤害("三清剑法", 自己, 目标, 伤害类型, 伤害数值 * 1.1, 穿透)
        return 重伤状态

    def 紫气东来(self, 自己: UserInfo, 目标: UserInfo):
        """造成伤害的同时恢复内力值"""
        内功穿透 = 自己.当前状态["内功穿透"]
        消耗内力 = 自己.基础属性["元气"]
        if self.计算内力("紫气东来", 自己, 目标, 消耗内力, 是否普通攻击=False):
            伤害数值 = int(自己.当前状态["内功攻击"] * 1.5)
        else:
            伤害数值 = int(自己.当前状态["内功攻击"] * 0.5)
        重伤状态, 实际伤害 = self.造成伤害("紫气东来", 自己, 目标, "内功伤害", 伤害数值, 内功穿透)
        恢复内力 = 实际伤害 // 2
        if 恢复内力 > (自己.当前状态["内力上限"] - 自己.当前内力):
            恢复内力 = 自己.当前状态["内力上限"] - 自己.当前内力
        自己.内力变化(恢复内力)
        self.战斗记录(
            f"<strong>{自己.名称}</strong> 紫气东来 恢复内力 +<span class='text-primary'>{恢复内力}</span> ({自己.当前内力}/{自己.当前状态['内力上限']})"
        )
        return 重伤状态

    def 剑若惊鸿(self, 自己: UserInfo, 目标: UserInfo):
        """根据内功攻击与外功攻击对目标造成混合伤害"""
        内功穿透 = 自己.当前状态["内功穿透"]
        外功穿透 = 自己.当前状态["外功穿透"]
        内功攻击 = 自己.当前状态["内功攻击"]
        外功攻击 = 自己.当前状态["外功攻击"]
        伤害数值 = int((内功攻击 + 外功攻击) * (2 - abs(内功攻击 - 外功攻击) / (内功攻击 + 外功攻击)))
        重伤状态, _ = self.造成伤害("剑若惊鸿", 自己, 目标, "混合伤害", 伤害数值, 内功穿透+外功穿透)
        return 重伤状态

    def 斗转星移(self, 自己: UserInfo, 目标: UserInfo, 数值: int):
        """遭受外功伤害时, 使用对方的攻击反击对方"""
        if randint(1, 100) < 自己.基础属性["身法"]:
            _, 伤害数值, _ = 目标.普通攻击()
            重伤状态, _ = self.造成伤害("斗转星移", 自己, 目标, "混合伤害", 伤害数值, 0)
            return 数值, 重伤状态
        return 数值, False

    def 北冥神功(self, 自己: UserInfo, 目标: UserInfo, 数值: int):
        """遭受内功伤害时, 吸取对方的内力, 并减少对方元气"""
        吸取内力 = 目标.当前内力 // 5
        自己.内力变化(吸取内力)
        目标.内力变化(-吸取内力)
        改变元气 = 目标.基础属性["元气"] // 10
        数值 -= 自己.基础属性["元气"]
        目标.改变当前状态({"元气": -改变元气})
        自己.改变当前状态({"元气": 改变元气})
        self.战斗记录(f"<strong>{自己.名称}</strong> 北冥神功 吸取内力 +<span class='text-primary'>{吸取内力}</span> ({自己.当前内力}/{自己.当前状态['内力上限']}) {目标.名称} 内力-<span class='text-primary'>{吸取内力}</span> 元气-{改变元气}")
        return 数值, False

    def 十方鬼道(self, 自己: UserInfo, 目标: UserInfo):
        """
        当气血高于20%时, 造成当前血量 * 15% + 内功攻击 * 50% 的伤害
        当气血低于20%时, 造成血量上限 * 10% + 内功攻击 * 50% 的伤害
        """
        if 自己.当前气血 >= 自己.当前状态["气血上限"] * 0.2:
            伤害 = int(自己.当前气血 * 0.15)
            self.造成伤害("十方鬼道(消耗)", 自己, 自己, "穿透伤害", 伤害)
        else:
            伤害 = int(自己.当前状态["气血上限"] * 0.1)
        重伤状态, _ = self.造成伤害("十方鬼道", 自己, 目标, "内功伤害",
                            伤害 + int(自己.当前状态["内功攻击"] * 0.5))
        return 重伤状态

    def 推气过宫(self, 自己: UserInfo, 对方: UserInfo):
        """
        恢复 元气 * 5 的气血, 并增加 0.3 * 根骨的元气
        """
        消耗内力 = int(自己.基础属性["根骨"] * 0.3)
        if not self.计算内力("推气过宫", 自己, 对方, 消耗内力):
            return ""
        self.治疗("推气过宫", 自己, 对方, int(自己.基础属性["元气"] * 4))
        自己.改变当前状态({"元气": 消耗内力})
        return ""

    def 摧山坼地(self, 自己: UserInfo, 目标: UserInfo):
        """
        消耗 20% 当前内力，造成敌方气血上限 15% + 消耗内力值 的穿透伤害。
        内力低于 50% 时无法释放。
        """
        消耗内力 = int(自己.当前内力 * 0.2)
        需要内力 = 自己.当前状态["内力上限"] * 0.5
        if not self.计算内力("摧山坼地", 自己, 目标, 消耗内力, 需要内力):
            return ""
        伤害 = int(目标.当前状态["气血上限"] * 0.15) + 消耗内力 // 2
        if 目标.基础属性.get("类型") == "首领":
            伤害 = 伤害 // 100
        重伤状态, _ = self.造成伤害("摧山坼地", 自己, 目标, "穿透伤害", 伤害)
        return 重伤状态


