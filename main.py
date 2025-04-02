import logging
from astrbot.api.all import *
from astrbot.api.event.filter import command
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger("CS2BoxPlugin")

# 获取插件所在目录
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(PLUGIN_DIR, "user_data")
os.makedirs(USER_DATA_DIR, exist_ok=True)

# 武器箱数据结构
WEAPON_CASES = {
    "千瓦武器箱": {
        "保密": [
            {"name": "AK-47 | 传承", "price": 1280.59},
            {"name": "AWP | 镀铬大炮", "price": 712.61}
        ],
        "受限": [
            {"name": "USP 消音版 | 破颚者", "price": 123.01},
            {"name": "宙斯 X27 | 奥林匹斯", "price": 108.22},
            {"name": "M4A1 消音型 | 黑莲花", "price": 134.62}
        ],
        "军规级": [
            {"name": "截短霰弹枪 | 模拟输入", "price": 14.26},
            {"name": "MP7 | 笑一个", "price": 15.80},
            {"name": "FN57 | 混合体", "price": 15.19},
            {"name": "M4A4 | 蚀刻领主", "price": 16.45},
            {"name": "格洛克 18 型 | 崩络克-18", "price": 14.48}
        ],
        "工业级": [
            {"name": "XM1014 | 刺青", "price": 1.69},
            {"name": "UMP-45 | 机动化", "price": 1.83},
            {"name": "Tec-9 | 渣渣", "price": 2.05},
            {"name": "SSG 08 | 灾难", "price": 1.94},
            {"name": "新星 | 黑暗徽记", "price": 1.62},
            {"name": "MAC-10 | 灯箱", "price": 3.02},
            {"name": "双持贝瑞塔 | 藏身处", "price": 1.2}
        ]
    },
    "画廊武器箱": {
        "保密": [
            {"name": "M4A1 消音型 | 蒸汽波", "price": 1226.03},
            {"name": "格洛克 18 型 | 大金牙", "price": 279.75}
        ],
        "受限": [
            {"name": "AK-47 | 局外人", "price": 337.32}
        ],
        "军规级": [
            {"name": "UMP-45 | 黑色魅影", "price": 94.61},
            {"name": "P250 | 震中", "price": 96.54},
            {"name": "SSG 08 | 致命站点", "price": 20.98}
        ],
        "工业级": [
            {"name": "P90 | 兰迪快冲", "price": 21.16},
            {"name": "MAC-10 | 赛博恶魔", "price": 21.62},
            {"name": "双持贝瑞塔 | 水枪冲击", "price": 21.01},
            {"name": "M4A4 | 涡轮", "price": 26.65},
            {"name": "SCAR-20 | 开拓者", "price": 2.73},
            {"name": "R8 左轮手枪 | 探戈", "price": 3.38},
            {"name": "M249 | 催眠术", "price": 2.95},
            {"name": "AUG | 豪华装饰", "price": 3.52},
            {"name": "MP5-SD | 静态学", "price": 2.91},
            {"name": "沙漠之鹰 | 书法涂鸦", "price": 4.45},
            {"name": "USP 消音版 | 027", "price": 4.45}
        ]
    },
    "变革武器箱": {
        "保密": [
            {"name": "AK-47 | 一发入魂", "price": 251.02},
            {"name": "M4A4 | 反冲精英", "price": 608.67}
        ],
        "受限": [
            {"name": "AWP | 金粉肆蛇", "price": 59.05},
            {"name": "P2000 | 变态杀戮", "price": 57.72},
            {"name": "UMP-45 | 野孩子", "price": 59.34}
        ],
        "军规级": [
            {"name": "P90 | 元女王", "price": 8.55},
            {"name": "R8 左轮手枪 | 蕉农炮", "price": 9.99},
            {"name": "MAC-10 | 错觉", "price": 4.89},
            {"name": "格洛克 18 型 | 圆影玉兔", "price": 8.95},
            {"name": "M4A1 消音型 | 隐伏帝王龙", "price": 13.04}
        ],
        "工业级": [
            {"name": "Tec-9 | 叛逆", "price": 1.76},
            {"name": "SG 553 | 赛博之力", "price": 1.51},
            {"name": "MP5-SD | 液化", "price": 1.65},
            {"name": "P250 | 重构", "price": 1.58},
            {"name": "SCAR-20 | 碎片", "price": 1.51},
            {"name": "MP9 | 羽量级", "price": 1.65},
            {"name": "MAG-7 | 鱼长梦短", "price": 1.54}
        ]
    },
    "反冲武器箱": {
        "保密": [
            {"name": "USP 消音版 | 印花集", "price": 756.68},
            {"name": "AK-47 | 可燃冰", "price": 81.96}
        ],
        "受限": [
            {"name": "AWP | 迷人眼", "price": 102.69},
            {"name": "截短霰弹枪 | 么么", "price": 59.30},
            {"name": "P250 | 迷人幻象", "price": 56.46}
        ],
        "军规级": [
            {"name": "双持贝瑞塔 | 食人花", "price": 11.07},
            {"name": "P90 | 给爷冲", "price": 9.09},
            {"name": "SG 553 | 青龙", "price": 9.16},
            {"name": "R8 左轮手枪 | 疯狂老八", "price": 11.64},
            {"name": "M249 | 闹市区", "price": 8.77}
        ],
        "工业级": [
            {"name": "格洛克 18 型 | 冬季战术", "price": 1.73},
            {"name": "UMP-45 | 路障", "price": 1.51},
            {"name": "内格夫 | 丢把枪", "price": 1.51},
            {"name": "MAC-10 | 萌猴迷彩", "price": 1.51},
            {"name": "M4A4 | 透明弹匣", "price": 2.02},
            {"name": "加利尔 AR | 毁灭者", "price": 1.58},
            {"name": "法玛斯 | 喵喵36", "price": 1.66}
        ]
    },
    "梦魇武器箱": {
        "保密": [
            {"name": "AK-47 | 夜愿", "price": 257.74},
            {"name": "MP9 | 星使", "price": 81.42}
        ],
        "受限": [
            {"name": "MP7 | 幽幻深渊", "price": 42.35},
            {"name": "法玛斯 | 目皆转睛", "price": 39.65},
            {"name": "双持贝瑞塔 | 瓜瓜", "price": 43.75}
        ],
        "军规级": [
            {"name": "USP 消音版 | 地狱门票", "price": 9.88},
            {"name": "XM1014 | 行尸攻势", "price": 7.37},
            {"name": "M4A1 消音型 | 夜无眠", "price": 9.70},
            {"name": "G3SG1 | 梦之林地", "price": 8.37},
            {"name": "PP-野牛 | 太空猫", "price": 8.30}
        ],
        "工业级": [
            {"name": "截短霰弹枪 | 灵应牌", "price": 1.51},
            {"name": "SCAR-20 | 暗夜活死鸡", "price": 1.55},
            {"name": "P2000 | 升天", "price": 1.51},
            {"name": "MP5-SD | 小小噩梦", "price": 1.62},
            {"name": "MAG-7 | 先见之明", "price": 1.54},
            {"name": "MAC-10 | 坐牢", "price": 1.65},
            {"name": "FN57 | 涂鸦潦草", "price": 1.80}
        ]
    },
    "激流大行动武器箱": {
        "保密": [
            {"name": "沙漠之鹰 | 纵横波涛", "price": 642.18},
            {"name": "AK-47 | 抽象派 1337", "price": 588.02}
        ],
        "受限": [
            {"name": "SSG 08 | 速度激情", "price": 120.79},
            {"name": "格洛克 18 型 | 零食派对", "price": 122.80},
            {"name": "MAC-10 | 玩具盒子", "price": 108.15}
        ],
        "军规级": [
            {"name": "M4A4 | 彼岸花", "price": 126.82},
            {"name": "MP9 | 富士山", "price": 81.10},
            {"name": "FN57 | 同步力场", "price": 27.80},
            {"name": "法玛斯 | ZX81 彩色", "price": 43.89}
        ],
        "工业级": [
            {"name": "MAG-7 | 铋晶体", "price": 15.09},
            {"name": "XM1014 | 狻猊", "price": 27.48},
            {"name": "USP 消音版 | 黑莲花", "price": 46.73},
            {"name": "PP-野牛 | 战术手电", "price": 12.68},
            {"name": "MP7 | 游击队", "price": 13.00},
            {"name": "G3SG1 | 特训地图", "price": 11.64},
            {"name": "双持贝瑞塔 | 胶面花纹", "price": 11.46},
            {"name": "AUG | 瘟疫", "price": 10.78}
        ]
    },
    "蛇噬武器箱": {
        "保密": [
            {"name": "M4A4 | 活色生香", "price": 182.89},
            {"name": "USP 消音版 | 倒吊人", "price": 275.80}
        ],
        "受限": [
            {"name": "加利尔 AR | 迷人眼", "price": 58.04},
            {"name": "XM1014 | 要抱抱", "price": 45.72},
            {"name": "MP9 | 爆裂食物链", "price": 54.63},
            {"name": "AK-47 | 墨岩", "price": 73.92}
        ],
        "军规级": [
            {"name": "沙漠之鹰 | 后发制人", "price": 15.38},
            {"name": "MAC-10 | 战争手柄", "price": 8.12},
            {"name": "内格夫 | 橙灰之名", "price": 9.27},
            {"name": "P250 | 赛博先锋", "price": 8.15}
        ],
        "工业级": [
            {"name": "新星 | 随风", "price": 3.16},
            {"name": "R8 左轮手枪 | 废物王", "price": 3.45},
            {"name": "UMP-45 | 动摇", "price": 2.80},
            {"name": "CZ75 | 短趾雕", "price": 3.31},
            {"name": "M249 | O.S.I.P.R.", "price": 2.91},
            {"name": "格洛克 18 型 | 一目了然", "price": 7.15},
            {"name": "SG 553 | 重金属摇滚", "price": 3.30}
        ]
    },
    "狂牙大行动武器箱": {
        "保密": [
            {"name": "格洛克 18 型 | 黑色魅影", "price": 302.34},
            {"name": "M4A1 消音型 | 印花集", "price": 2926.62},
            {"name": "USP 消音版 | 小绿怪", "price": 322.53},
            {"name": "M4A4 | 赛博", "price": 342.50}
        ],
        "受限": [
            {"name": "FN57 | 童话城堡", "price": 431.71},
            {"name": "UMP-45 | 金铋辉煌", "price": 47.45},
            {"name": "SSG 08 | 抖枪", "price": 48.49},
            {"name": "新星 | 一见青心", "price": 46.80},
            {"name": "双持贝瑞塔 | 灾难", "price": 51.47},
            {"name": "AWP | 亡灵之主", "price": 61.89}
        ],
        "军规级": [
            {"name": "MP5-SD | 零点行动", "price": 9.49},
            {"name": "M249 | 等高线", "price": 8.44},
            {"name": "P250 | 污染物", "price": 7.80},
            {"name": "加利尔 AR | 破坏者", "price": 12.58},
            {"name": "G3SG1 | 血腥迷彩", "price": 7.80},
            {"name": "P90 | 大怪兽 RUSH", "price": 7.40},
            {"name": "CZ75 | 世仇", "price": 8.62}
        ]
    },
    "裂空武器箱": {
        "保密": [
            {"name": "AK-47 | 阿努比斯军团", "price": 91.01},
            {"name": "沙漠之鹰 | 印花集", "price": 580.98}
        ],
        "受限": [
            {"name": "XM1014 | 埋葬之影", "price": 48.52},
            {"name": "格洛克 18 型 | 摩登时代", "price": 73.06},
            {"name": "M4A4 | 齿仙", "price": 51.33}
        ],
        "军规级": [
            {"name": "MP5-SD | 猛烈冲锋", "price": 8.23},
            {"name": "加利尔 AR | 凤凰商号", "price": 8.19},
            {"name": "MAC-10 | 魅惑", "price": 8.69},
            {"name": "Tec-9 | 兄弟连", "price": 8.95},
            {"name": "MAG-7 | 北冥有鱼", "price": 9.52}
        ],
        "工业级": [
            {"name": "PP-野牛 | 神秘碑文", "price": 1.51},
            {"name": "P90 | 集装箱", "price": 1.51},
            {"name": "P250 | 卡带", "price": 1.51},
            {"name": "SSG 08 | 主机001", "price": 1.51},
            {"name": "SG 553 | 锈蚀之刃", "price": 1.40},
            {"name": "P2000 | 盘根错节", "price": 1.54},
            {"name": "内格夫 | 飞羽", "price": 1.51}
        ]
    },
    "棱彩2号武器箱": {
        "保密": [
            {"name": "格洛克 18 型 | 子弹皇后", "price": 184.18},
            {"name": "M4A1 消音型 | 二号玩家", "price": 623.68}
        ],
        "受限": [
            {"name": "MAG-7 | 正义", "price": 58.11},
            {"name": "MAC-10 | 渐变迪斯科", "price": 67.53},
            {"name": "AK-47 | 幻影破坏者", "price": 72.34}
        ],
        "军规级": [
            {"name": "SSG 08 | 浮生如梦", "price": 12.40},
            {"name": "SG 553 | 黯翼", "price": 10.78},
            {"name": "SCAR-20 | 执行者", "price": 9.20},
            {"name": "截短霰弹枪 | 启示录", "price": 10.53},
            {"name": "P2000 | 酸蚀", "price": 12.00}
        ],
        "工业级": [
            {"name": "R8 左轮手枪 | 骸骨锻造", "price": 1.58},
            {"name": "内格夫 | 原型机", "price": 1.55},
            {"name": "MP5-SD | 沙漠精英", "price": 2.12},
            {"name": "沙漠之鹰 | 蓝色层压板", "price": 8.12},
            {"name": "CZ75 | 做旧手艺", "price": 1.66},
            {"name": "AWP | 毛细血管", "price": 14.44},
            {"name": "AUG | 汤姆猫", "price": 1.73}
        ]
    }
    
}

# 品质概率分布（工业级、军规级、受限、保密、特殊物品）
RARITY_PROBS = [
    ("工业级", 79.923),
    ("军规级", 15.985),
    ("受限", 3.197),
    ("保密", 0.639),
    ("特殊物品", 0.256)
]

def get_today():
    """获取上海时区当日日期"""
    utc_now = datetime.utcnow()
    shanghai_time = utc_now + timedelta(hours=8)
    return shanghai_time.date().isoformat()

def _get_group_id(event: AstrMessageEvent) -> str:
    """获取有效的群组标识"""
    group_id = event.get_group_id()
    return group_id if group_id else "private"  # 私聊场景使用"private"

def _load_user_data(event: AstrMessageEvent) -> Dict:
    """加载群组隔离的用户数据"""
    user_id = event.get_sender_id()
    group_id = _get_group_id(event)
    group_dir = os.path.join(USER_DATA_DIR, f"group_{group_id}")
    os.makedirs(group_dir, exist_ok=True)
    
    user_file = os.path.join(group_dir, f"{user_id}.json")
    default_data = {
        "gold": 0,
        "inventory": {},
        "pending_items": [],
        "last_checkin": "",
        "username": event.get_sender_name(),
        "group_id": group_id
    }
    
    try:
        if not os.path.exists(user_file):
            return default_data
        
        with open(user_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 数据迁移兼容
            data["username"] = data.get("username", event.get_sender_name())
            data["group_id"] = data.get("group_id", group_id)
            return data
    except Exception as e:
        logger.error(f"加载用户数据失败: {str(e)}")
        return default_data

def _save_user_data(event: AstrMessageEvent, data: Dict):
    """保存群组隔离的用户数据"""
    user_id = event.get_sender_id()
    group_id = _get_group_id(event)
    group_dir = os.path.join(USER_DATA_DIR, f"group_{group_id}")
    os.makedirs(group_dir, exist_ok=True)
    
    user_file = os.path.join(group_dir, f"{user_id}.json")
    try:
        # 始终更新最新用户名和群组ID
        data["username"] = event.get_sender_name()
        data["group_id"] = group_id
        
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存用户数据失败: {str(e)}")

def _format_pending_items(items: List[Dict]) -> str:
    """格式化待处理物品列表（包含品质）"""
    return "\n".join(
        f"{idx}. {item['name']} ({item.get('rarity', '未知')}) 价值：￥{item['price']:.2f}"
        for idx, item in enumerate(items, 1)
    ) if items else "无物品"

def _add_gold_info(message: str, gold: int) -> str:
    """在消息末尾添加金币信息"""
    return f"{message}\n当前金币：{gold}"

@register("CS2BoxPlugin", "bvzrays", "CS2开箱模拟系统", "1.0.0")
class CS2BoxPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("CS2开箱插件已加载")

    @command("签到")
    async def check_in(self, event: AstrMessageEvent):
        """每日签到"""
        user_data = _load_user_data(event)
        
        today = get_today()
        if user_data["last_checkin"] == today:
            yield event.plain_result(_add_gold_info("⚠️ 今天已经签到过了，请明天再来", user_data["gold"]))
            return
        
        user_data["gold"] += 100
        user_data["last_checkin"] = today
        _save_user_data(event, user_data)
        yield event.plain_result(_add_gold_info("🎉 签到成功！获得100金币", user_data["gold"]))

    @command("开箱")
    async def open_case(self, event: AstrMessageEvent, case_name: str = None, count: int = 1):
        """开箱功能"""
        if case_name is None:
            case_list = "当前箱子：\n" + "\n".join(
                f"{idx}. {case}" for idx, case in enumerate(WEAPON_CASES.keys(), 1)
            )
            help_msg = f"{case_list}\n\n请输入【开箱 箱子名称 数量】开箱\n示例：开箱 梦魇武器箱 1"
            yield event.plain_result(_add_gold_info(help_msg, _load_user_data(event)["gold"]))
            return

        matched_case = next(
            (case for case in WEAPON_CASES if case_name.lower() == case.lower()),
            None
        )
        if not matched_case:
            user_data = _load_user_data(event)
            yield event.plain_result(_add_gold_info("❌ 不存在的武器箱", user_data["gold"]))
            return

        user_data = _load_user_data(event)
        cost = 17 * count
        
        if user_data["gold"] < cost:
            yield event.plain_result(_add_gold_info(f"❌ 金币不足，需要{cost}金币", user_data["gold"]))
            return

        user_data["gold"] -= cost
        results = []
        
        for _ in range(count):
            rand = random.uniform(0, 100)
            cumulative = 0
            selected_rarity = "工业级"

            for rarity, prob in RARITY_PROBS:
                cumulative += prob
                if rand <= cumulative:
                    selected_rarity = rarity
                    break

            if selected_rarity == "特殊物品":
                results.append({"name": "大金", "price": 4000, "rarity": "特殊物品"})
            else:
                weapons = WEAPON_CASES[matched_case].get(selected_rarity, [])
                if weapons:
                    weapon = random.choice(weapons).copy()
                    weapon["rarity"] = selected_rarity
                    results.append(weapon)

        user_data["pending_items"] = results
        _save_user_data(event, user_data)

        result_msg = f"🎁 开箱结果：\n{_format_pending_items(results)}\n\n"
        result_msg += "回复【出售 全部】或【保留全部】处理物品\n或使用【出售 编号】处理单个物品（例：出售 1 3）"
        
        yield event.plain_result(_add_gold_info(result_msg, user_data["gold"]))

    @command("出售")
    async def sell_pending_items(self, event: AstrMessageEvent):
        """出售待处理物品"""
        user_data = _load_user_data(event)
        items = user_data["pending_items"]
        
        if not items:
            yield event.plain_result(_add_gold_info("⚠️ 没有待处理的物品", user_data["gold"]))
            return

        args = event.message_str.strip().split()[1:]  # 获取出售后面的参数
        
        if "全部" in args:
            total = sum(item["price"] for item in items)
            user_data["gold"] += total
            user_data["pending_items"] = []
            _save_user_data(event, user_data)
            yield event.plain_result(_add_gold_info(f"💰 出售全部获得 ￥{total:.2f}金币", user_data["gold"]))
            return

        try:
            indexes = {int(arg)-1 for arg in args if arg.isdigit()}
            valid_indexes = {i for i in indexes if 0 <= i < len(items)}
            
            if not valid_indexes:
                yield event.plain_result(_add_gold_info("❌ 请输入有效的物品编号", user_data["gold"]))
                return

            total = sum(items[i]["price"] for i in valid_indexes)
            remaining_items = [item for i, item in enumerate(items) if i not in valid_indexes]
            
            user_data["gold"] += total
            user_data["pending_items"] = remaining_items
            _save_user_data(event, user_data)
            
            msg = f"💰 出售成功！获得 ￥{total:.2f}金币\n\n"
            msg += f"剩余物品：\n{_format_pending_items(remaining_items)}\n\n"
            msg += "可以继续选择出售或回复【保留全部】"
            yield event.plain_result(_add_gold_info(msg, user_data["gold"]))
            
        except Exception as e:
            logger.error(f"出售物品出错: {str(e)}")
            yield event.plain_result(_add_gold_info("❌ 参数错误，请使用数字编号", user_data["gold"]))

    @command("保留全部")
    async def keep_all(self, event: AstrMessageEvent):
        """保留全部物品"""
        user_data = _load_user_data(event)
        
        if not user_data["pending_items"]:
            yield event.plain_result(_add_gold_info("⚠️ 没有待处理的物品", user_data["gold"]))
            return

        for item in user_data["pending_items"]:
            name = item["name"]
            user_data["inventory"][name] = user_data["inventory"].get(name, 0) + 1
        
        user_data["pending_items"] = []
        _save_user_data(event, user_data)
        yield event.plain_result(_add_gold_info("📦 所有物品已存入背包", user_data["gold"]))

    @command("背包")
    async def show_inventory(self, event: AstrMessageEvent):
        """查看背包"""
        user_data = _load_user_data(event)
        
        if not user_data["inventory"]:
            yield event.plain_result(_add_gold_info("🎒 背包为空", user_data["gold"]))
            return

        # 获取物品价格信息
        inventory_items = []
        for name, count in user_data["inventory"].items():
            price = 0
            for case in WEAPON_CASES.values():
                for items in case.values():
                    for item in items:
                        if item["name"] == name:
                            price = item["price"]
                            break
                    if price > 0:
                        break
                if price > 0:
                    break
            
            inventory_items.append({
                "name": name,
                "count": count,
                "price": price
            })

        # 按价格排序
        inventory_items.sort(key=lambda x: x["price"], reverse=True)
        
        msg = "🎒 背包物品：\n"
        msg += "\n".join(
            f"{idx}. {item['name']} x{item['count']} 价值：￥{item['price']:.2f}"
            for idx, item in enumerate(inventory_items, 1)
        )
        msg += "\n\n使用【背包出售 全部】出售所有物品\n或【背包出售 编号】出售指定物品"
        yield event.plain_result(_add_gold_info(msg, user_data["gold"]))

    @command("背包出售")
    async def sell_inventory_items(self, event: AstrMessageEvent):
        """出售背包物品"""
        user_data = _load_user_data(event)
        
        if not user_data["inventory"]:
            yield event.plain_result(_add_gold_info("🎒 背包为空", user_data["gold"]))
            return

        args = event.message_str.strip().split()[1:]  # 获取背包出售后面的参数
        inventory = user_data["inventory"]
        
        # 获取物品价格
        item_prices = {}
        for name in inventory:
            for case in WEAPON_CASES.values():
                for items in case.values():
                    for item in items:
                        if item["name"] == name:
                            item_prices[name] = item["price"]
                            break
                    if name in item_prices:
                        break
                if name in item_prices:
                    break

        if "全部" in args:
            total = sum(
                item_prices.get(name, 0) * count 
                for name, count in inventory.items()
            )
            user_data["gold"] += total
            user_data["inventory"] = {}
            _save_user_data(event, user_data)
            yield event.plain_result(_add_gold_info(f"💰 出售全部背包物品获得 ￥{total:.2f}金币", user_data["gold"]))
            return

        try:
            inventory_list = list(inventory.items())
            indexes = {int(arg)-1 for arg in args if arg.isdigit()}
            valid_indexes = {i for i in indexes if 0 <= i < len(inventory_list)}
            
            if not valid_indexes:
                yield event.plain_result(_add_gold_info("❌ 请输入有效的物品编号", user_data["gold"]))
                return

            total = 0
            # 需要从后往前删除避免索引变化
            for i in sorted(valid_indexes, reverse=True):
                name, count = inventory_list[i]
                total += item_prices.get(name, 0) * count
                del inventory[name]
            
            user_data["gold"] += total
            _save_user_data(event, user_data)
            yield event.plain_result(_add_gold_info(f"💰 出售成功！获得 ￥{total:.2f}金币", user_data["gold"]))
            
        except Exception as e:
            logger.error(f"出售背包物品出错: {str(e)}")
            yield event.plain_result(_add_gold_info("❌ 参数错误，请使用数字编号", user_data["gold"]))

    @command("排行")
    async def show_rank(self, event: AstrMessageEvent, page: int = 1):
        """显示当前群组的金币排行榜"""
        current_group = _get_group_id(event)
        group_dir = os.path.join(USER_DATA_DIR, f"group_{current_group}")
        
        if not os.path.exists(group_dir):
            yield event.plain_result(_add_gold_info("当前群组还没有任何开箱数据哦~", _load_user_data(event)["gold"]))
            return

        user_files = [f for f in os.listdir(group_dir) if f.endswith('.json')]
        user_list = []
        
        for user_file in user_files:
            try:
                with open(os.path.join(group_dir, user_file), "r", encoding="utf-8") as f:
                    user_data = json.load(f)
                    # 过滤无效数据
                    if user_data.get("gold", 0) <= 0:
                        continue
                    user_list.append({
                        "gold": user_data["gold"],
                        "username": user_data["username"],
                        "user_id": os.path.splitext(user_file)[0]
                    })
            except Exception as e:
                logger.error(f"读取用户文件 {user_file} 失败: {str(e)}")
                continue
        
        # 按金币排序（降序）
        sorted_users = sorted(user_list, key=lambda x: x["gold"], reverse=True)
        
        # 分页处理
        per_page = 10
        total_users = len(sorted_users)
        total_pages = max((total_users + per_page - 1) // per_page, 1)
        
        # 校验页码有效性
        page = max(min(page, total_pages), 1)
        
        # 生成排行榜内容
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paged_users = sorted_users[start_idx:end_idx]
        
        rank_msg = [
            f"🏆 金币排行榜（第 {page}/{total_pages} 页）",
            f"👥 当前群组：{current_group}",
            "================================="
        ]
        
        for idx, user in enumerate(paged_users, start=1):
            rank_msg.append(
                f"{start_idx + idx}. {user['username']} (ID: {user['user_id']}) - {user['gold']}金币"
            )
        
        rank_msg.append("=================================")
        rank_msg.append(f"使用【排行 页码】查看其他页面")
        
        # 获取当前用户金币信息
        current_user_data = _load_user_data(event)
        return_msg = _add_gold_info("\n".join(rank_msg), current_user_data["gold"])
        
        yield event.plain_result(return_msg)
