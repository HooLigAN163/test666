import discord
from discord.ext import commands
import json
import os

# --- Настройки ---
TARGET = 30_000_000
DATA_FILE = 'savings.json'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- Форматирование ---
def format_num(n):
    return f"{n:,.0f}".replace(",", " ")

def make_progress_bar(percentage, width=20):
    filled = int(width * percentage)
    empty = width - filled
    return "▰" * filled + "▱" * empty

def make_embed(saved):
    percentage = min(saved / TARGET, 1.0)
    progress_bar = make_progress_bar(percentage)
    percent_str = f"{percentage * 100:.1f}%"
    color = discord.Color.green() if saved >= TARGET else discord.Color.blue()

    embed = discord.Embed(
        title="🚗 **Porsche 911**",
        description=f"Цель: **{format_num(TARGET)} ₽**",
        color=color
    )
    embed.add_field(
        name="💰 **Уже накоплено**",
        value=f"**{format_num(saved)} ₽**",
        inline=False
    )
    embed.add_field(
        name="📊 **Прогресс**",
        value=f"{progress_bar}\n{percent_str} завершено",
        inline=False
    )
    if saved < TARGET:
        needed = TARGET - saved
        embed.set_footer(text=f"**Осталось**: {format_num(needed)} ₽")
    else:
        embed.set_footer(text="🎉 **Цель достигнута! Пора покупать машину!**")
    return embed

# --- Работа с файлом ---
def load_savings():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("saved", 0)
    return 0

def save_savings(amount):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"saved": amount}, f, ensure_ascii=False, indent=4)

# --- События ---
@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} готов!')
    await bot.change_presence(activity=discord.Game(name="коплю на машину"))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    try:
        amount = float(message.content.replace(',', '.'))
        if amount <= 0:
            return
    except ValueError:
        await bot.process_commands(message)
        return

    saved = load_savings()
    saved += amount
    save_savings(saved)

    embed = make_embed(saved)
    await message.channel.send(f"✅ **+{format_num(amount)} ₽ добавлено!**", embed=embed)
    await bot.process_commands(message)

@bot.command()
async def balance(ctx):
    saved = load_savings()
    embed = make_embed(saved)
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()  # Только владелец бота может сбросить
async def reset(ctx):
    save_savings(0)
    embed = make_embed(0)
    await ctx.send("🔄 Копилка сброшена до 0.", embed=embed)

# --- Запуск ---
TOKEN = os.getenv("BOT_TOKEN")
if TOKEN is None:
    print("❌ ОШИБКА: BOT_TOKEN не найден! Проверь переменные окружения.")
else:
    bot.run(TOKEN)