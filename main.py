"""
╔══════════════════════════════════════════════════════╗
║         TELEGRAM NFT GIFT BOT — main.py              ║
║  Установка: pip install python-telegram-bot==20.7    ║
║  Запуск:    python main.py                           ║
╚══════════════════════════════════════════════════════╝
"""

import logging
import random
import json
from dataclasses import dataclass, field
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters,
)

# ── Настройки из config.py ──────────────────────────
from config import (
    BOT_TOKEN, ADMIN_ID, WEB_APP_URL,
    STARTING_BALANCE, UPGRADE_COST, UPGRADE_CHANCE,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════
#  МОДЕЛИ
# ════════════════════════════════════════════

@dataclass
class Gift:
    id: str; name: str; emoji: str; price: int
    supply: int; rarity: str; bg: str; desc: str
    author: str = ""

@dataclass
class OwnedGift:
    uid: int; gift_id: str
    level: int = 0
    upgrades: list = field(default_factory=list)


# ════════════════════════════════════════════
#  КАТАЛОГ ПОДАРКОВ
# ════════════════════════════════════════════

class GiftCatalog:
    """Все NFT-подарки Telegram (данные: giftsgram.ru)."""

    _DATA = [
        # ── LEGENDARY ──────────────────────────────────────────────────────
        ("heart_locket",   "Heart Locket",   "💝", 2000,   1973, "legendary", "Pure Gold",       "Самый редкий подарок Telegram"),
        ("plush_pepe",     "Plush Pepe",      "🐸", 1500,   2861, "legendary", "Emerald",         "Легендарный плюшевый Пепе"),
        ("heroic_helmet",  "Heroic Helmet",   "⚔️", 1200,   3794, "legendary", "Midnight Blue",   "Шлем героя"),
        ("mighty_arm",     "Mighty Arm",      "💪", 1000,   4123, "legendary", "Fire Engine",     "Могучая рука"),
        ("ion_gem",        "Ion Gem",         "💎",  900,   4692, "legendary", "Cyberpunk",       "Ионный кристалл"),
        ("durovs_cap",     "Durov's Cap",     "🧢",  850,   4774, "legendary", "Azure Blue",      "Кепка самого Дурова"),
        ("nail_bracelet",  "Nail Bracelet",   "📿",  800,   4818, "legendary", "Electric Indigo", "Браслет из гвоздей"),
        ("perfume_bottle", "Perfume Bottle",  "🌸",  750,   4848, "legendary", "Lavender",        "Флакон духов"),
        ("magic_potion",   "Magic Potion",    "🧪",  700,   4871, "legendary", "French Violet",   "Волшебное зелье"),
        ("mini_oscar",     "Mini Oscar",      "🏆",  650,   5614, "legendary", "Amber",           "Мини Оскар"),
        ("astral_shard",   "Astral Shard",    "🔮",  600,   6196, "legendary", "Electric Purple", "Астральный осколок"),
        ("artisan_brick",  "Artisan Brick",   "🧱",  550,   6852, "legendary", "Old Gold",        "Кирпич мастера"),
        ("gem_signet",     "Gem Signet",      "💍",  500,   6962, "legendary", "Sapphire",        "Перстень с бриллиантом"),
        ("precious_peach", "Precious Peach",  "🍑", 1800,   3160, "legendary", "Fandango",        "Драгоценный персик"),
        # ── EPIC ───────────────────────────────────────────────────────────
        ("sharp_tongue",   "Sharp Tongue",    "👅",  350,   8546, "epic", "Carmine",      "Острый язык"),
        ("loot_bag",       "Loot Bag",        "💰",  300,  14489, "epic", "Old Gold",     "Мешок с лутом"),
        ("electric_skull", "Electric Skull",  "💀",  380,   9407, "epic", "Cyberpunk",    "Электрический череп"),
        ("bonded_ring",    "Bonded Ring",     "💍",  420,   8130, "epic", "Neon Blue",    "Кольцо союза"),
        ("kissed_frog",    "Kissed Frog",     "🐸",  280,  14278, "epic", "Emerald",      "Целованная лягушка"),
        ("neko_helmet",    "Neko Helmet",     "🐱",  260,  16149, "epic", "Lavender",     "Шлем некомана"),
        ("scared_cat",     "Scared Cat",      "😱",  240,  19289, "epic", "Raspberry",    "Испуганный кот"),
        ("swiss_watch",    "Swiss Watch",     "⌚",  220,  29323, "epic", "Amber",        "Швейцарские часы"),
        ("crystal_ball",   "Crystal Ball",    "🔮",  200,  27732, "epic", "Grape",        "Хрустальный шар"),
        ("voodoo_doll",    "Voodoo Doll",     "🪆",  190,  27620, "epic", "Fire Engine",  "Кукла вуду"),
        ("diamond_ring",   "Diamond Ring",    "💎",  180,  32924, "epic", "Neon Blue",    "Бриллиантовое кольцо"),
        ("signet_ring",    "Signet Ring",     "💍",  170,  18499, "epic", "Cobalt Blue",  "Именная печатка"),
        # ── RARE ───────────────────────────────────────────────────────────
        ("skull_flower",   "Skull Flower",    "💀",   85,  24126, "rare", "Mystic Pearl", "Цветок с черепом"),
        ("cupid_charm",    "Cupid Charm",     "💘",   75,  33112, "rare", "Aquamarine",   "Амулет Купидона"),
        ("love_candle",    "Love Candle",     "🕯️",  70,  30296, "rare", "Fandango",     "Свеча любви"),
        ("love_potion",    "Love Potion",     "💜",   70,  30412, "rare", "Lavender",     "Зелье любви"),
        ("vintage_cigar",  "Vintage Cigar",   "🚬",   65,  31024, "rare", "Old Gold",     "Винтажная сигара"),
        ("eternal_rose",   "Eternal Rose",    "🌹",   60,  37640, "rare", "Carmine",      "Вечная роза"),
        ("top_hat",        "Top Hat",         "🎩",   65,  35099, "rare", "Midnight Blue","Цилиндр"),
        ("trapped_heart",  "Trapped Heart",   "💔",   80,  26407, "rare", "Fire Engine",  "Пойманное сердце"),
        ("ionic_dryer",    "Ionic Dryer",     "💨",   85,  25719, "rare", "Azure Blue",   "Ионный фен"),
        ("flying_broom",   "Flying Broom",    "🧹",   75,  25916, "rare", "Camo Green",   "Летающая метла"),
        ("mad_pumpkin",    "Mad Pumpkin",     "🎃",   90,  22199, "rare", "Tomato",       "Безумная тыква"),
        ("toy_bear",       "Toy Bear",        "🧸",   50,  57724, "rare", "Caramel",      "Плюшевый мишка"),
        ("moon_pendant",   "Moon Pendant",    "🌙",   40, 111080, "rare", "Midnight Blue","Лунный кулон"),
        ("eternal_candle", "Eternal Candle",  "🕯️",  55,  46590, "rare", "Old Gold",     "Вечная свеча"),
        # ── COMMON ─────────────────────────────────────────────────────────
        ("lol_pop",        "Lol Pop",         "🍭",   10, 468745, "common", "Electric Purple", "Карамельный леденец"),
        ("instant_ramen",  "Instant Ramen",   "🍜",   10, 457382, "common", "Amber",           "Быстрая лапша"),
        ("desk_calendar",  "Desk Calendar",   "📅",    8, 374077, "common", "Azure Blue",      "Настольный календарь"),
        ("xmas_stocking",  "Xmas Stocking",   "🧦",    9, 334632, "common", "Carmine",         "Рождественский носок"),
        ("candy_cane",     "Candy Cane",      "🍬",    8, 320622, "common", "Carmine",         "Леденцовая трость"),
        ("bday_candle",    "B-Day Candle",    "🎂",    8, 308639, "common", "Lavender",        "Свечи на торте"),
        ("pet_snake",      "Pet Snake",       "🐍",   15, 279106, "common", "Emerald",         "Домашняя змея"),
        ("cookie_heart",   "Cookie Heart",    "🍪",   10, 264486, "common", "Aquamarine",      "Печенье-сердечко"),
        ("jester_hat",     "Jester Hat",      "🎭",   12, 190222, "common", "Carmine",         "Шляпа шута"),
        ("witch_hat",      "Witch Hat",       "🧙",   18,  88480, "common", "Grape",           "Шляпа ведьмы"),
        ("santa_hat",      "Santa Hat",       "🎅",   18,  89034, "common", "Carmine",         "Шапка Санты"),
        ("faith_amulet",   "Faith Amulet",    "☯️",   12, 172784, "common", "Cobalt Blue",     "Амулет веры"),
        ("easter_egg",     "Easter Egg",      "🥚",   10, 173176, "common", "Fandango",        "Пасхальное яйцо"),
        ("jack_box",       "Jack-in-the-Box", "🎪",   15,  97345, "common", "Fire Engine",     "Чёртик из коробки"),
        ("clover_pin",     "Clover Pin",      "🍀",   12, 270970, "common", "Mint Green",      "Брошь-клевер"),
        ("snake_box",      "Snake Box",       "📦",   12, 273898, "common", "Jade Green",      "Коробка со змеёй"),
        ("mousse_cake",    "Mousse Cake",     "🍰",   12, 230505, "common", "Fandango",        "Торт-мусс"),
        ("spring_basket",  "Spring Basket",   "🧺",   12, 231311, "common", "Emerald",         "Весенняя корзинка"),
        ("fresh_socks",    "Fresh Socks",     "🧦",    8, 200509, "common", "Azure Blue",      "Свежие носки"),
        ("homemade_cake",  "Homemade Cake",   "🎂",   10, 199482, "common", "Lavender",        "Домашний торт"),
    ]

    _AUTHORS = [
        # (id, name, emoji, price, supply, rarity, bg, desc, author)
        ("snoop_dogg",     "Snoop Dogg",       "🎤",  50, 595358, "author", "Pacific Cyan", "Коллекционный Snoop Dogg",       "@snoopdogg"),
        ("swag_bag",       "Swag Bag",         "🛍️", 30, 239091, "author", "Pacific Cyan", "Сумка со свэгом",                "@snoopdogg"),
        ("snoop_cigar",    "Snoop Cigar",      "🚬",  60, 119806, "author", "Gunmetal",     "Сигара Snoop Dogg",              "@snoopdogg"),
        ("low_rider",      "Low Rider",        "🚗", 200,  23991, "author", "Cobalt Blue",  "Лоурайдер",                     "@snoopdogg"),
        ("westside_sign",  "Westside Sign",    "🤙", 400,  11995, "author", "Old Gold",     "Знак West Side — ультраредкий!", "@snoopdogg"),
        ("khabib_papakha", "Khabib's Papakha", "🧢", 150,  29000, "author", "Emerald",      "Папаха Хабиба",                  "@khabib_nurmagomedov"),
        ("ufc_strike",     "UFC Strike",       "🥊",  80,  60000, "author", "Carmine",      "Удар UFC",                      "@ufc"),
    ]

    RARITY_WEIGHT = {"legendary": 0, "epic": 1, "rare": 2, "common": 3, "author": 4}

    def __init__(self):
        self._cat: dict = {}
        for row in self._DATA:
            g = Gift(*row)
            self._cat[g.id] = g
        for row in self._AUTHORS:
            g = Gift(*row)
            self._cat[g.id] = g

    def get(self, gid: str) -> Optional[Gift]:
        return self._cat.get(gid)

    def all(self) -> list:
        return list(self._cat.values())

    def by_rarity(self, r: str) -> list:
        return [g for g in self._cat.values() if g.rarity == r]

    def search(self, q: str) -> list:
        q = q.lower()
        return [g for g in self._cat.values() if q in g.name.lower()]

    def sorted(self) -> list:
        return sorted(self._cat.values(),
                      key=lambda g: self.RARITY_WEIGHT.get(g.rarity, 9))


# ════════════════════════════════════════════
#  СИСТЕМА УЛУЧШЕНИЙ
# ════════════════════════════════════════════

class UpgradeSystem:
    """
    Рандомная система улучшений.

    Алгоритм:
      1. roll = random.random()  →  число от 0.0 до 1.0
      2. Если roll <= UPGRADE_CHANCE[level] → УСПЕХ → level + 1
      3. Иначе → НЕУДАЧА → level не меняется
      4. Стоимость списывается всегда (за попытку, не за результат)
    """

    MAX  = 5
    COST = UPGRADE_COST    # из config.py
    PROB = UPGRADE_CHANCE  # из config.py

    LV_NAME = {
        0: "Базовый",       1: "Улучшен I ⭐",
        2: "Улучшен II ⭐⭐", 3: "Улучшен III 🌟",
        4: "Элитный ✨",    5: "ЛЕГЕНДАРНЫЙ 🔥",
    }
    LV_STARS = {
        0: "", 1: "⭐", 2: "⭐⭐", 3: "🌟🌟🌟",
        4: "✨✨✨✨", 5: "🔥🔥🔥🔥🔥",
    }
    BONUSES = [
        "Усилен блеск", "Добавлена аура", "Золотая рамка",
        "Эффект частиц", "Анимированный фон", "Голографический слой",
        "Радужный отлив", "Огненный контур", "Звёздное свечение",
        "Алмазный блеск",
    ]

    def try_upgrade(self, owned: OwnedGift) -> dict:
        """Попытка улучшения. Возвращает результат dict."""
        lv = owned.level
        if lv >= self.MAX:
            return {"ok": False, "lv": lv, "msg": "👑 Уже максимальный уровень!"}

        prob = self.PROB[lv]
        roll = random.random()

        if roll <= prob:
            owned.level += 1
            bonus = random.choice(self.BONUSES)
            owned.upgrades.append(bonus)
            return {
                "ok": True, "lv": owned.level, "bonus": bonus,
                "msg": (
                    f"✅ *Успех!*\n"
                    f"Уровень: *{lv} → {owned.level}* {self.LV_STARS[owned.level]}\n"
                    f"Бонус: _{bonus}_\n"
                    f"Шанс: *{int(prob*100)}%* | Выпало: `{roll:.3f}`"
                ),
            }
        return {
            "ok": False, "lv": lv,
            "msg": (
                f"💨 *Неудача.*\n"
                f"Уровень остался: *{lv}*\n"
                f"Шанс: *{int(prob*100)}%* | Выпало: `{roll:.3f}`\n"
                f"_Попробуйте ещё раз!_"
            ),
        }

    def cost(self, lv: int) -> int:   return self.COST.get(lv, 0)
    def name(self, lv: int) -> str:   return self.LV_NAME.get(lv, f"Ур.{lv}")
    def stars(self, lv: int) -> str:  return self.LV_STARS.get(lv, "")


# ════════════════════════════════════════════
#  ИНВЕНТАРЬ
# ════════════════════════════════════════════

class Inventory:
    """Хранит данные пользователей в памяти."""

    def __init__(self):
        self._d: dict = {}

    def _init(self, uid: int):
        if uid not in self._d:
            self._d[uid] = {"bal": STARTING_BALANCE, "gifts": [], "bought": 0}

    def bal(self, uid: int) -> int:
        self._init(uid); return self._d[uid]["bal"]

    def add_bal(self, uid: int, n: int):
        self._init(uid); self._d[uid]["bal"] += n

    def spend(self, uid: int, n: int) -> bool:
        self._init(uid)
        if self._d[uid]["bal"] < n: return False
        self._d[uid]["bal"] -= n; return True

    def add_gift(self, uid: int, gid: str) -> OwnedGift:
        self._init(uid)
        og = OwnedGift(uid=random.randint(100000, 999999), gift_id=gid)
        self._d[uid]["gifts"].append(og)
        self._d[uid]["bought"] += 1
        return og

    def gifts(self, uid: int) -> list:
        self._init(uid); return self._d[uid]["gifts"]

    def find(self, uid: int, gift_uid: int) -> Optional[OwnedGift]:
        return next((g for g in self.gifts(uid) if g.uid == gift_uid), None)

    def stats(self, uid: int) -> dict:
        self._init(uid); d = self._d[uid]
        return {
            "bal": d["bal"], "total": len(d["gifts"]),
            "bought": d["bought"],
            "max_lv": max((g.level for g in d["gifts"]), default=0),
        }


# ════════════════════════════════════════════
#  ГЛОБАЛЬНЫЕ ОБЪЕКТЫ
# ════════════════════════════════════════════
cat = GiftCatalog()
up  = UpgradeSystem()
inv = Inventory()


# ════════════════════════════════════════════
#  УТИЛИТЫ
# ════════════════════════════════════════════
def N(n):  return f"{n:,}".replace(",", " ")
def RI(r): return {"legendary":"🟡","epic":"🟣","rare":"🔵","common":"⚪","author":"🟢"}.get(r,"⚪")

def gift_line(g: Gift) -> str:
    return f"{RI(g.rarity)} {g.emoji} *{g.name}* — ⭐{g.price} | {N(g.supply)} шт."

def owned_line(og: OwnedGift, g: Gift) -> str:
    return (f"{g.emoji} *{g.name}* {up.stars(og.level)}\n"
            f"   _{up.name(og.level)}_ · ID: `{og.uid}`")

def main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Открыть Mini App магазин",
                              web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton("🛍 Каталог",    callback_data="s_shop"),
         InlineKeyboardButton("🎀 Инвентарь",  callback_data="s_inv")],
        [InlineKeyboardButton("⬆️ Улучшить",   callback_data="s_up"),
         InlineKeyboardButton("💰 Баланс",      callback_data="s_bal")],
        [InlineKeyboardButton("🏆 Legendary",  callback_data="s_leg"),
         InlineKeyboardButton("⭐ Авторы",      callback_data="s_auth")],
    ])

def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="s_back")]])


# ════════════════════════════════════════════
#  КОМАНДЫ
# ════════════════════════════════════════════

async def cmd_start(u: Update, _):
    uid = u.effective_user.id
    await u.message.reply_text(
        f"👋 Привет, *{u.effective_user.first_name}*!\n\n"
        "🎁 *NFT Gift Bot* — покупай и улучшай\n"
        "настоящие Telegram NFT-подарки!\n\n"
        "🌟 *Каталог:* Plush Pepe, Durov's Cap,\n"
        "Snoop Dogg, Khabib's Papakha и 60+ других\n\n"
        "⬆️ *Улучшения:* 5 уровней с рандомными\n"
        "бонусами и разными шансами успеха!\n\n"
        f"💰 Баланс: *⭐ {N(inv.bal(uid))}*\n\n"
        "Выберите действие 👇",
        parse_mode="Markdown", reply_markup=main_kb()
    )

async def cmd_help(u: Update, _):
    await u.message.reply_text(
        "📖 *Команды*\n\n"
        "/start — главное меню\n"
        "/shop — каталог подарков\n"
        "/buy `<id>` — купить  _(пр: /buy plush\\_pepe)_\n"
        "/inventory — мои подарки\n"
        "/upgrade `<uid>` — улучшить подарок\n"
        "/balance — баланс\n\n"
        "🎲 *Шансы улучшений:*\n"
        "```\n"
        "0→1  95%   50 ⭐\n"
        "1→2  75%  120 ⭐\n"
        "2→3  50%  300 ⭐\n"
        "3→4  30%  800 ⭐\n"
        "4→5  15% 2000 ⭐\n"
        "```\n"
        "⚠️ _Звёзды — за попытку. Неудача не возвращает._",
        parse_mode="Markdown", reply_markup=back_kb()
    )

async def cmd_balance(u: Update, _):
    s = inv.stats(u.effective_user.id)
    await u.message.reply_text(
        f"💰 *Ваш аккаунт*\n\n"
        f"⭐ Баланс: *{N(s['bal'])}*\n"
        f"🎁 В инвентаре: *{s['total']}*\n"
        f"🛍 Куплено всего: *{s['bought']}*\n"
        f"🔝 Макс. уровень: *{s['max_lv']}*",
        parse_mode="Markdown", reply_markup=back_kb()
    )

async def cmd_shop(u: Update, _):
    gifts = cat.sorted()[:14]
    lines = ["🛍 *Каталог NFT подарков*\n"] + [gift_line(g) for g in gifts]
    lines += ["", "_/buy <id> — купить_", "_Пр: /buy plush\\_pepe_"]
    await u.message.reply_text(
        "\n".join(lines), parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Полный каталог в Mini App",
                                  web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton("◀️ Назад", callback_data="s_back")],
        ])
    )

async def cmd_buy(u: Update, ctx):
    uid = u.effective_user.id
    if not ctx.args:
        await u.message.reply_text(
            "❗ Укажите ID.\nПример: `/buy plush_pepe`\nКаталог: /shop",
            parse_mode="Markdown"); return

    gid = ctx.args[0].lower()
    g   = cat.get(gid)
    if not g:
        found = cat.search(gid)
        if found:
            lines = ["🔍 *Возможно имели в виду:*\n"]
            for x in found[:5]:
                lines.append(f"• `{x.id}` — {x.emoji} {x.name} ⭐{x.price}")
            await u.message.reply_text("\n".join(lines), parse_mode="Markdown")
        else:
            await u.message.reply_text(f"❌ `{gid}` не найден. Каталог: /shop",
                                       parse_mode="Markdown")
        return

    if not inv.spend(uid, g.price):
        await u.message.reply_text(
            f"⭐ Недостаточно звёзд!\nНужно: *{g.price}* | У вас: *{inv.bal(uid)}*",
            parse_mode="Markdown"); return

    og  = inv.add_gift(uid, g.id)
    await u.message.reply_text(
        f"✅ *Куплено!*\n\n"
        f"{g.emoji} *{g.name}*\n"
        f"{RI(g.rarity)} {g.rarity.capitalize()}\n"
        f"_{up.name(0)}_  |  ID: `{og.uid}`\n\n"
        f"💰 Остаток: ⭐ *{N(inv.bal(uid))}*\n\n"
        f"_Улучшить: /upgrade {og.uid}_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"⬆️ Улучшить ({up.cost(0)}⭐)",
                                  callback_data=f"u_{uid}_{og.uid}")],
            [InlineKeyboardButton("🎀 Инвентарь", callback_data="s_inv")],
        ])
    )

async def cmd_inventory(u: Update, _):
    uid   = u.effective_user.id
    gifts = inv.gifts(uid)
    if not gifts:
        await u.message.reply_text(
            "🎀 *Инвентарь пуст.*\n\nКупите подарки: /shop",
            parse_mode="Markdown"); return
    lines = [f"🎀 *Инвентарь* ({len(gifts)} шт.)\n"]
    for og in gifts[-10:]:
        g = cat.get(og.gift_id)
        if g: lines.append(owned_line(og, g))
    if len(gifts) > 10:
        lines.append(f"\n_...ещё {len(gifts)-10}_")
    lines.append("\n_/upgrade <ID> — улучшить_")
    await u.message.reply_text("\n".join(lines),
                               parse_mode="Markdown", reply_markup=back_kb())

async def cmd_upgrade(u: Update, ctx):
    uid = u.effective_user.id
    if not ctx.args:
        await u.message.reply_text(
            "❗ Укажите ID.\nПример: `/upgrade 123456`\nID смотрите в /inventory",
            parse_mode="Markdown"); return
    try:    gid = int(ctx.args[0])
    except: await u.message.reply_text("❗ ID должен быть числом."); return

    og = inv.find(uid, gid)
    if not og:
        await u.message.reply_text(f"❌ ID `{gid}` не найден. /inventory",
                                   parse_mode="Markdown"); return
    g = cat.get(og.gift_id)
    if not g: return

    if og.level >= up.MAX:
        await u.message.reply_text(
            f"👑 *{g.name}* уже максимальный!\n{up.stars(5)}",
            parse_mode="Markdown"); return

    if not inv.spend(uid, up.cost(og.level)):
        await u.message.reply_text(
            f"⭐ Нужно *{up.cost(og.level)}*, у вас *{inv.bal(uid)}*",
            parse_mode="Markdown"); return

    res = up.try_upgrade(og)
    btns = []
    if og.level < up.MAX:
        btns.append([InlineKeyboardButton(
            f"{'⬆️ Ещё раз' if not res['ok'] else '⬆️ Улучшить ещё'} ({up.cost(og.level)}⭐)",
            callback_data=f"u_{uid}_{og.uid}")])
    else:
        btns.append([InlineKeyboardButton("👑 МАКСИМУМ!", callback_data="noop")])
    btns.append([InlineKeyboardButton("🎀 Инвентарь", callback_data="s_inv")])

    await u.message.reply_text(
        f"{g.emoji} *{g.name}*\n\n{res['msg']}\n\n💰 Остаток: ⭐ *{N(inv.bal(uid))}*",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(btns)
    )

async def cmd_admin(u: Update, _):
    if u.effective_user.id != ADMIN_ID:
        await u.message.reply_text("❌ Нет доступа."); return
    tu = len(inv._d)
    tg = sum(len(d["gifts"]) for d in inv._d.values())
    tb = sum(d["bought"]     for d in inv._d.values())
    await u.message.reply_text(
        f"🔑 *Админ-панель*\n\n"
        f"👥 Пользователей: *{tu}*\n"
        f"🎁 В инвентарях: *{tg}*\n"
        f"🛍 Покупок: *{tb}*\n"
        f"📋 В каталоге: *{len(cat.all())}*\n\n"
        f"Пополнить: `/addbal <uid> <сумма>`",
        parse_mode="Markdown"
    )

async def cmd_addbal(u: Update, ctx):
    if u.effective_user.id != ADMIN_ID: return
    try:
        tid = int(ctx.args[0]); amt = int(ctx.args[1])
    except:
        await u.message.reply_text("Формат: /addbal <uid> <сумма>"); return
    inv.add_bal(tid, amt)
    await u.message.reply_text(f"✅ +{amt}⭐ → `{tid}`", parse_mode="Markdown")


# ════════════════════════════════════════════
#  INLINE КНОПКИ
# ════════════════════════════════════════════

async def on_btn(u: Update, _):
    q   = u.callback_query
    await q.answer()
    d   = q.data
    uid = q.from_user.id

    # ── Меню ────────────────────────────────
    if d == "s_back":
        await q.message.edit_text(
            f"💰 Баланс: ⭐ *{N(inv.bal(uid))}*\n\nВыберите действие 👇",
            parse_mode="Markdown", reply_markup=main_kb()
        )

    elif d == "s_bal":
        s = inv.stats(uid)
        await q.message.edit_text(
            f"💰 *Аккаунт*\n\n⭐ *{N(s['bal'])}*\n"
            f"🎁 {s['total']} подарков\n"
            f"🛍 {s['bought']} куплено\n"
            f"🔝 Макс. уровень: {s['max_lv']}",
            parse_mode="Markdown", reply_markup=back_kb()
        )

    elif d == "s_shop":
        gifts = cat.sorted()[:12]
        lines = ["🛍 *Каталог* (топ-12)\n"] + [gift_line(g) for g in gifts]
        lines.append("\n_/buy <id>_")
        await q.message.edit_text(
            "\n".join(lines), parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎁 Mini App", web_app=WebAppInfo(url=WEB_APP_URL))],
                [InlineKeyboardButton("◀️ Назад", callback_data="s_back")],
            ])
        )

    elif d == "s_inv":
        gifts = inv.gifts(uid)
        if not gifts:
            await q.message.edit_text(
                "🎀 *Инвентарь пуст.*\n\n/shop — купить",
                parse_mode="Markdown", reply_markup=back_kb()); return
        lines = [f"🎀 *Инвентарь* ({len(gifts)} шт.)\n"]
        for og in gifts[-8:]:
            g = cat.get(og.gift_id)
            if g: lines.append(owned_line(og, g))
        if len(gifts) > 8: lines.append(f"\n_...ещё {len(gifts)-8}_")
        lines.append("\n_/upgrade <ID>_")
        await q.message.edit_text("\n".join(lines),
                                  parse_mode="Markdown", reply_markup=back_kb())

    elif d == "s_up":
        avail = [og for og in inv.gifts(uid) if og.level < up.MAX]
        if not avail:
            msg = "👑 Все на максимуме!" if inv.gifts(uid) else "🎀 Нет подарков."
            await q.message.edit_text(msg, reply_markup=back_kb()); return
        lines = ["⬆️ *Доступно для улучшения*\n"]
        for og in avail[-6:]:
            g = cat.get(og.gift_id)
            if g:
                lines.append(
                    f"{g.emoji} *{g.name}* [{up.name(og.level)}]\n"
                    f"   ⭐{up.cost(og.level)} | шанс {int(up.PROB.get(og.level,0)*100)}%"
                    f" · `/upgrade {og.uid}`\n"
                )
        await q.message.edit_text("\n".join(lines),
                                  parse_mode="Markdown", reply_markup=back_kb())

    elif d == "s_leg":
        gifts = cat.by_rarity("legendary")[:8]
        lines = ["🏆 *Legendary подарки*\n"] + [gift_line(g) for g in gifts]
        await q.message.edit_text(
            "\n".join(lines), parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎁 Купить в Mini App",
                                      web_app=WebAppInfo(url=WEB_APP_URL+"?tab=top"))],
                [InlineKeyboardButton("◀️ Назад", callback_data="s_back")],
            ])
        )

    elif d == "s_auth":
        gifts = cat.by_rarity("author")
        lines = ["⭐ *Авторские подарки*\n"]
        for g in gifts:
            lines.append(gift_line(g) + (f" · {g.author}" if g.author else ""))
        await q.message.edit_text(
            "\n".join(lines), parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎁 Mini App",
                                      web_app=WebAppInfo(url=WEB_APP_URL+"?tab=auth"))],
                [InlineKeyboardButton("◀️ Назад", callback_data="s_back")],
            ])
        )

    # ── Кнопка "Улучшить" ───────────────────
    elif d.startswith("u_"):
        try:
            _, oid, ouid = d.split("_")
            oid = int(oid); ouid = int(ouid)
        except: return
        if oid != uid:
            await q.answer("❌ Не ваш подарок!", show_alert=True); return
        og = inv.find(uid, ouid)
        if not og:
            await q.answer("❌ Подарок не найден!", show_alert=True); return
        g = cat.get(og.gift_id)
        if not g: return
        if og.level >= up.MAX:
            await q.answer("👑 Максимальный уровень!", show_alert=True); return
        if not inv.spend(uid, up.cost(og.level)):
            await q.answer(f"❌ Нужно {up.cost(og.level)}⭐!", show_alert=True); return

        res = up.try_upgrade(og)
        btns = []
        if og.level < up.MAX:
            btns.append([InlineKeyboardButton(
                f"⬆️ Ещё раз ({up.cost(og.level)}⭐)",
                callback_data=f"u_{uid}_{og.uid}")])
        else:
            btns.append([InlineKeyboardButton("👑 МАКСИМУМ!", callback_data="noop")])
        btns.append([InlineKeyboardButton("🎀 Инвентарь", callback_data="s_inv")])

        await q.message.edit_text(
            f"{g.emoji} *{g.name}*\n\n{res['msg']}\n\n💰 ⭐ *{N(inv.bal(uid))}*",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(btns)
        )

    elif d == "noop":
        await q.answer("👑 Максимальный уровень!")


# ════════════════════════════════════════════
#  MINI APP ДАННЫЕ
# ════════════════════════════════════════════

async def on_webapp(u: Update, _):
    """Получает JSON от index.html."""
    try: p = json.loads(u.message.web_app_data.data)
    except: return
    action = p.get("action",""); name = p.get("gift","?"); lv = int(p.get("level",0))
    if action == "bought":
        await u.message.reply_text(
            f"✅ *Куплено!*\n🎁 *{name}*\n_{up.name(lv)}_",
            parse_mode="Markdown")
    elif action == "upgraded":
        await u.message.reply_text(
            f"✨ *Улучшено!*\n🎁 *{name}* {up.stars(lv)}\n"
            f"*{up.name(lv)}*{'  👑 МАКСИМУМ!' if lv==5 else ''}",
            parse_mode="Markdown")


# ════════════════════════════════════════════
#  ЗАПУСК
# ════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════╗")
    print("║    NFT GIFT BOT — запускается    ║")
    print(f"║  Mini App: {WEB_APP_URL[:22]}  ║")
    print("╚══════════════════════════════════╝\n")

    app = Application.builder().token(BOT_TOKEN).build()

    for cmd, fn in [
        ("start",     cmd_start),
        ("help",      cmd_help),
        ("shop",      cmd_shop),
        ("buy",       cmd_buy),
        ("inventory", cmd_inventory),
        ("upgrade",   cmd_upgrade),
        ("balance",   cmd_balance),
        ("admin",     cmd_admin),
        ("addbal",    cmd_addbal),
    ]:
        app.add_handler(CommandHandler(cmd, fn))

    app.add_handler(CallbackQueryHandler(on_btn))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, on_webapp))

    print("✅ Бот запущен! Ctrl+C — остановить.\n")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
