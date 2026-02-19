# 🎁 Telegram NFT Gift Bot

Бот для покупки и улучшения настоящих NFT-подарков Telegram с Mini App интерфейсом.

## 📦 Файлы проекта

| Файл | Описание |
|------|----------|
| `main.py` | Основной код бота |
| `config.py` | Настройки (токен, ID, URL) |
| `index.html` | Mini App (загружается на Vercel) |
| `requirements.txt` | Зависимости Python |

## 🚀 Запуск

### 1. Установить зависимости
```bash
pip install -r requirements.txt
```

### 2. Запустить бота
```bash
python main.py
```

## 🎮 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню |
| `/shop` | Каталог подарков |
| `/buy <id>` | Купить подарок (пр: `/buy plush_pepe`) |
| `/inventory` | Ваши подарки |
| `/upgrade <uid>` | Улучшить подарок |
| `/balance` | Баланс и статистика |

## 🎁 Подарки в каталоге

**Legendary:** Heart Locket, Plush Pepe, Durov's Cap, Ion Gem и др.  
**Epic:** Crystal Ball, Diamond Ring, Swiss Watch и др.  
**Rare:** Eternal Rose, Top Hat, Love Candle и др.  
**Common:** Lol Pop, Pet Snake, Santa Hat и др.  
**Авторы:** Snoop Dogg, Snoop Cigar, Khabib's Papakha, UFC Strike

## ⬆️ Система улучшений

| Уровень | Шанс | Стоимость |
|---------|------|-----------|
| 0 → 1 ⭐ | 95% | 50 ⭐ |
| 1 → 2 ⭐⭐ | 75% | 120 ⭐ |
| 2 → 3 🌟 | 50% | 300 ⭐ |
| 3 → 4 ✨ | 30% | 800 ⭐ |
| 4 → 5 🔥 | 15% | 2000 ⭐ |

## ⚙️ Настройки (config.py)

```python
BOT_TOKEN   = "ваш_токен"
ADMIN_ID    = ваш_telegram_id
WEB_APP_URL = "https://ваш-сайт.vercel.app"
```

## 🌐 Деплой Mini App (Vercel)

1. Загрузите `index.html` в репозиторий GitHub
2. Подключите репозиторий к [vercel.com](https://vercel.com)
3. Vercel автоматически опубликует сайт
4. Скопируйте URL в `config.py`

---
*GiftBot 2026*
