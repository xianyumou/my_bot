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
            "两仪化形": {
                "type": "主动招式",
                "招式类型": "内功招式",
                "招式": self.两仪化形
            },
            "紫气东来": {
                "type": "主动招式",
                "招式类型": "内功招式",
                "招式": self.紫气东来
            },
            "吸星大法": {
                "type": "主动招式",
                "招式类型": "内功招式",
                "招式": self.吸星大法
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
            },
            "怖畏暗刑": {
                "type": "主动招式",
                "招式类型": "外功招式",
                "招式": self.怖畏暗刑
            },
            "剑心通明": {
                "type": "主动招式",
                "招式类型": "内功招式",
                "招式": self.剑心通明
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
             穿透: float = 0,
             是否记录: bool = True) -> bool:
        """造成伤害"""
        伤害数值, 重伤信息 = self.触发被动(守方.基础属性["武学"], 伤害类型, 伤害数值,守方, 攻方)
        if 重伤信息:
            return 重伤信息, 伤害数值
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
        伤害 = int(伤害数值 * (3000 / (3000 + 防御)))
        if 守方.当前气血 < 伤害:
            伤害 = 守方.当前气血
        if 是否记录:
            攻方.本次伤害 += 伤害
        守方.气血变化(-伤害)
        self.战斗记录(
            f"<strong>{攻方.名称}</strong> {技能名称}[{伤害类型[:2]}](-<span class='text-danger'>{伤害}</span>) > <strong>{守方.名称}</strong>({守方.当前气血}/{守方.当前状态['气血上限']})"
        )
        # 重伤状态 = 守方.当前气血 <= 0
        return 守方.重伤状态, 伤害

    def 三清剑法(self, 自己: UserInfo, 目标: UserInfo):
        """
三清剑法
【触发类型】主动招式
【招式类型】外功招式
根据自身速度与对方速度差进行多次普通攻击，每次攻击伤害递增。
攻击次数：(自身速度 - 对方速度) / 800 取整) + 3。
伤害：普通攻击 * 伤害系数
伤害系数：第一击 0.7，第二击 0. 8，第三击 0.9，每次递增 0.1，以此类推
穿透：自身外功穿透
        """
        伤害类型, 伤害数值, 穿透 = 自己.普通攻击()
        速度差 = 自己.当前状态['速度'] - 目标.当前状态['速度']
        if 速度差 < 0:
            速度差 = 0
        攻击次数 = (速度差 // 800) + 3
        伤害增幅 = 0.1
        伤害系数 = 0.7
        for _ in range(攻击次数):
            重伤状态, _ = self.造成伤害("三清剑法", 自己, 目标, 伤害类型, 伤害数值 * 伤害系数, 穿透)
            伤害系数 += 伤害增幅
            if 重伤状态:
                break
        return 重伤状态

    def 两仪化形(self, 自己: UserInfo, 目标: UserInfo):
        """
两仪化形
【触发类型】主动招式
【招式类型】内功招式
根据自身内攻攻击对敌方造成随机伤害。并对减少目标当前速度。
伤害 = 内攻攻击 * (1 ~ 7随机数)
穿透 = 自身内功穿透
减速 = 目标当前速度 * 0.13
内力消耗 = 100
        """
        内功穿透 = 自己.当前状态["内功穿透"]
        伤害数值 = 自己.当前状态["内功攻击"] * randint(1, 7)
        消耗内力 = 100
        if not self.计算内力("两仪化形", 自己, 目标, 消耗内力):
            return ""
        减速 = int(目标.当前状态['速度'] * 0.13)
        self.战斗记录(
            f"<strong>{目标.名称}</strong> 速度-{减速}"
        )
        目标.改变当前状态({"速度": -减速})
        重伤状态, _ = self.造成伤害("两仪化形", 自己, 目标, "内功伤害", 伤害数值, 内功穿透)
        return 重伤状态

    def 紫气东来(self, 自己: UserInfo, 目标: UserInfo):
        """
紫气东来
【触发类型】主动招式
【招式类型】内功招式
造成内攻伤害的同时恢复内力值。
消耗当前 元气 * 0.3 的内力。对敌方造成 内功攻击 * 1.7 的内功伤害。
若当前内力低于 元气 * 0.3，则对敌方造成 内功攻击 * 0.7 的内功伤害。
伤害结算完成后自己恢复 造成伤害 / 2 的内力值。
        """
        内功穿透 = 自己.当前状态["内功穿透"]
        消耗内力 = int(自己.基础属性["元气"] * 0.3)
        if self.计算内力("紫气东来", 自己, 目标, 消耗内力, 是否普通攻击=False):
            伤害数值 = int(自己.当前状态["内功攻击"] * 1.7)
        else:
            伤害数值 = int(自己.当前状态["内功攻击"] * 0.7)
        重伤状态, 实际伤害 = self.造成伤害("紫气东来", 自己, 目标, "内功伤害", 伤害数值, 内功穿透)
        恢复内力 = 实际伤害 // 2
        if 恢复内力 > (自己.当前状态["内力上限"] - 自己.当前内力):
            恢复内力 = 自己.当前状态["内力上限"] - 自己.当前内力
        自己.内力变化(恢复内力)
        self.战斗记录(
            f"<strong>{自己.名称}</strong> 紫气东来 恢复内力 +<span class='text-primary'>{恢复内力}</span> ({自己.当前内力}/{自己.当前状态['内力上限']})"
        )
        return 重伤状态

    def 吸星大法(self, 自己: UserInfo, 目标: UserInfo):
        """
吸星大法
【触发类型】主动招式
【招式类型】内功招式
根据敌方当前气血与自己放内功攻击对敌方造成内功伤害, 并根据此伤害恢复气血
消耗当前 元气 * 0.3 的内力。对敌方造成 内功攻击 * 2.5 + 目标当前气血 * 0.05 的内功伤害
伤害结算完成后自己恢复 造成伤害 / 2 的气血值。
        """
        内功穿透 = 自己.当前状态["内功穿透"]
        消耗内力 = int(自己.基础属性["元气"] * 0.3)
        if not self.计算内力("吸星大法", 自己, 目标, 消耗内力):
            return
        if 目标.基础属性.get("类型") == "首领":
            伤害数值 = int(自己.当前状态["内功攻击"] * 2.75)
        else:
            伤害数值 = int(自己.当前状态["内功攻击"] * 2.5 + 目标.当前气血 * 0.05)

        重伤状态, 实际伤害 = self.造成伤害("吸星大法", 自己, 目标, "内功伤害", 伤害数值, 内功穿透)
        恢复气血 = 实际伤害 // 2
        self.治疗("吸星大法", 自己, 目标, 恢复气血)
        return 重伤状态

    def 剑若惊鸿(self, 自己: UserInfo, 目标: UserInfo):
        """
剑若惊鸿
【触发类型】主动招式
【招式类型】外功招式
根据自身的内功攻击与外功攻击对敌方造成混合伤害。
伤害=(内功攻击+外功攻击)*(2-|内功攻击-外功攻击|/(内功攻击 + 外功攻击))*2。
穿透=内功穿透+外功穿透。
内功攻击与内公共攻击总和越高，数值越接近，伤害越高。
最高为内功攻击与外功攻击总和的4倍，最低为内功攻击与外功攻击总和的2倍。
        """
        内功穿透 = 自己.当前状态["内功穿透"]
        外功穿透 = 自己.当前状态["外功穿透"]
        内功攻击 = 自己.当前状态["内功攻击"]
        外功攻击 = 自己.当前状态["外功攻击"]
        伤害数值 = int((内功攻击 + 外功攻击) * (2 - abs(内功攻击 - 外功攻击) / (内功攻击 + 外功攻击)) * 2)
        重伤状态, _ = self.造成伤害("剑若惊鸿", 自己, 目标, "混合伤害", 伤害数值, 内功穿透+外功穿透)
        return 重伤状态

    def 斗转星移(self, 自己: UserInfo, 目标: UserInfo, 数值: int):
        """
斗转星移
【触发类型】被动招式
【触发条件】受到外功伤害
【招式类型】外功招式
遭受攻击时将受到的伤害返还给对方。
反击伤害=对方普通攻击伤害 * 100% 的混合伤害。
穿透=0
        """
        if randint(1, 100) < 自己.基础属性["身法"]:
            _, 伤害数值, _ = 目标.普通攻击()
            重伤状态, _ = self.造成伤害("斗转星移", 自己, 目标, "混合伤害", 伤害数值, 0)
            return 数值, 重伤状态
        return 数值, False

    def 北冥神功(self, 自己: UserInfo, 目标: UserInfo, 数值: int):
        """
北冥神功
【触发类型】被动招式
【触发条件】受到内功伤害
【招式类型】内功招式
吸取对方元气，吸取对方内力，降低受到的内功伤害。
吸取对方元气：对方元气*10%
降低伤害：自身元气*1
吸取内力：对方当前内力*20%
        """
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
十方鬼道
【触发类型】主动招式
【招式类型】内功招式
【招式说明】
消耗自身气血对目标造成内功伤害。
当自己当前气血高于气血上限的20%时，自身减少当前气血的15%，对目标造成 当前气血 * 15% + 自己内功攻击 * 50% 的 内功伤害。
当自己当前气血低于气血上限的20%时，对目标造成 气血上限 * 10% + 自己内功攻击 * 50% 的 内功伤害。
        """
        if 自己.当前气血 >= 自己.当前状态["气血上限"] * 0.2:
            伤害 = int(自己.当前气血 * 0.15)
            self.造成伤害("十方鬼道(消耗)", 自己, 自己, "内功伤害", 伤害, 是否记录=False)
        else:
            伤害 = int(自己.当前状态["气血上限"] * 0.1)
        重伤状态, _ = self.造成伤害("十方鬼道", 自己, 目标, "内功伤害",
                            伤害 + int(自己.当前状态["内功攻击"] * 0.8), 自己.当前状态["内功穿透"])
        return 重伤状态

    def 推气过宫(self, 自己: UserInfo, 对方: UserInfo):
        """
推气过宫
【触发类型】主动招式
【招式类型】内功招式
【招式说明】
为自己回复当前气血，并提高自身元气。
内力消耗 = 根骨 * 0.4
恢复气血 = 恢复自己 元气 *  4
增加元气 = 根骨 * 0.4
        """
        消耗内力 = int(自己.基础属性["根骨"] * 0.4)
        if not self.计算内力("推气过宫", 自己, 对方, 消耗内力):
            return ""
        self.治疗("推气过宫", 自己, 对方, int(自己.基础属性["元气"] * 4))
        自己.改变当前状态({"元气": 消耗内力})
        return ""

    def 摧山坼地(self, 自己: UserInfo, 目标: UserInfo):
        """
摧山坼地
【触发类型】主动招式
【招式类型】外功招式
【招式说明】
消耗 20% 当前内力，造成对方气血上限 17% + 消耗内力值 的穿透伤害。
内力低于 50% 时无法施放。
        """
        消耗内力 = int(自己.当前内力 * 0.2)
        需要内力 = 自己.当前状态["内力上限"] * 0.5
        if not self.计算内力("摧山坼地", 自己, 目标, 消耗内力, 需要内力):
            return ""
        伤害 = int(目标.当前状态["气血上限"] * 0.17) + 消耗内力 // 2
        if 目标.基础属性.get("类型") == "首领":
            伤害 = 自己.当前状态["外功攻击"] * 1.7 + 消耗内力
        重伤状态, _ = self.造成伤害("摧山坼地", 自己, 目标, "穿透伤害", 伤害)
        return 重伤状态

    def 怖畏暗刑(self, 自己: UserInfo, 目标: UserInfo):
        """
怖畏暗刑
【触发类型】主动招式
【招式类型】外功招式
【招式说明】
对目标施展缴械并附带少量外功伤害。
消耗内力：100
成功率：100%-((100 + 目标状态抗性)/(200 + 己方速度))%
缴械回合：3 - 目标状态抗性 /700取整，若小于1则生效1回合
伤害：己方外功攻击 * 1
        """
        if not self.计算内力("怖畏暗刑", 自己, 目标, 100):
            return
        目标状态抗性 = 目标.当前状态["状态抗性"]
        己方速度 = 自己.当前状态["速度"]
        if randint(1, 200 + 己方速度) < 目标状态抗性 + 100:
            self.战斗记录("怖畏暗刑施放失败")
            return
        有效回合 = 3 - 目标状态抗性 // 700
        if 有效回合 < 1:
            有效回合 = 1
        self.战斗记录(f"怖畏暗刑施放成功，{目标.名称}缴械{有效回合}回合")
        目标.debuff.append({"名称": "怖畏暗刑", "type": "缴械", "剩余回合": 有效回合})
        伤害 = 自己.当前状态["外功攻击"]
        重伤状态, _ = self.造成伤害("怖畏暗刑", 自己, 目标, "外功伤害", 伤害, 自己.当前状态["外功穿透"])
        return 重伤状态

    def 剑心通明(self, 自己: UserInfo, 目标: UserInfo):
        """
剑心通明（临时）
【触发类型】主动招式
【招式类型】内功招式
【招式说明】
对目标施展封内并附带少量内功伤害。
消耗内力：100
成功率：100%-((100 + 目标状态抗性)/(200 + 己方速度))%
缴械回合：3 - 目标状态抗性 /700取整，若小于1则生效1回合
伤害：己方内功攻击 * 1
        """
        if not self.计算内力("剑心通明", 自己, 目标, 100):
            return
        目标状态抗性 = 目标.当前状态["状态抗性"]
        己方速度 = 自己.当前状态["速度"]
        if randint(1, 200 + 己方速度) < 目标状态抗性 + 100:
            self.战斗记录("剑心通明施放失败")
            return
        有效回合 = 3 - 目标状态抗性 // 700
        if 有效回合 < 1:
            有效回合 = 1
        self.战斗记录(f"剑心通明施放成功，{目标.名称}封内{有效回合}回合")
        目标.debuff.append({"名称": "剑心通明", "type": "封内", "剩余回合": 有效回合})
        伤害 = 自己.当前状态["内功攻击"]
        重伤状态, _ = self.造成伤害("剑心通明", 自己, 目标, "内功伤害", 伤害, 自己.当前状态["内功穿透"])
        return 重伤状态

