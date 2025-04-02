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

# 武器箱数据结构（此处省略，保留原有WEAPON_CASES定义）
WEAPON_CASES = {}  # 保留原有武器箱数据

# 品质概率分布（此处省略，保留原有RARITY_PROBS定义）
RARITY_PROBS = []  # 保留原有概率数据

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

@register("CS2BoxPlugin", "Kimi", "CS2开箱模拟系统", "1.0.0")
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
