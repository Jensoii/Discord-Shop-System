import discord
from discord.ext import commands
import sqlite3

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

shop_items = {
    'Discord Welcome Message': {
        'name': 'Discord Welcome Message',
        'price': 10,
        'description': 'Damit könnt ihr easy eine bessere welcome message haben auf euren Discord Community Server!',
        'emoji': ':call_me:'
    },
    'Ban & Kick Command': {
        'name': 'Ban & Kick Command',
        'price': 20,
        'description': 'Damit könnt ihr leute von euren discord kicken/bannen',
        'emoji': ':pizza:'
    },
    'Niklas Seine Nudes': {
        'name': 'Niklas Seine Nudes',
        'price': 30,
        'description': 'Niklas seine Geilen nudes',
        'emoji': ':sweat_drops:'
    }
}

conn = sqlite3.connect('credits.db')
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS credits (
                    user_id INTEGER PRIMARY KEY,
                    credits INTEGER DEFAULT 0
                )''')

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user.name}')

@bot.command()
async def give_credits(ctx, user: discord.Member, amount: int):
    if ctx.author.guild_permissions.administrator:
        cursor.execute("INSERT OR REPLACE INTO credits (user_id, credits) VALUES (?, ?)", (user.id, amount))
        conn.commit()
        await ctx.send(f"{amount} Credits wurden erfolgreich an {user.mention} vergeben.")
    else:
        await ctx.send("Nur Administratoren können Credits vergeben.")

@bot.command()
async def check_credits(ctx):
    user_credits = cursor.execute("SELECT credits FROM credits WHERE user_id=?", (ctx.author.id,)).fetchone()
    if user_credits:
        embed = discord.Embed(title="Deine Credits", color=discord.Color.gold())
        embed.add_field(name="Credits", value=user_credits[0], inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Du hast keine Credits.")

@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="Shop", color=discord.Color.blurple())

    for item_key, item in shop_items.items():
        embed.add_field(name=f"{item['name']} {item['emoji']}", value=f"Preis: {item['price']} Credits\nBeschreibung: {item['description']}", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, item_key: str):
    item = shop_items.get(item_key)

    if item:
        user = ctx.author
        user_credits = cursor.execute("SELECT credits FROM credits WHERE user_id=?", (user.id,)).fetchone()

        if user_credits and user_credits[0] >= item['price']:
            cursor.execute("UPDATE credits SET credits = credits - ? WHERE user_id = ?", (item['price'], user.id))
            conn.commit()

            
            channel_name = f"🛒︲{user.name}"
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites)
        
            embed = discord.Embed(title="Kauf abgeschlossen", color=discord.Color.green())
            embed.add_field(name="Benutzer", value=user.mention, inline=False)
            embed.add_field(name="Gekauftes Item", value=f"{item['name']} {item['emoji']}", inline=False)
            embed.add_field(name="Preis", value=item['price'], inline=False)
            

            await channel.send(embed=embed)
        else:
            await ctx.send("Du hast nicht genügend Credits, um diesen Artikel zu kaufen.")
    else:
        await ctx.send("Dieser Artikel existiert nicht im Shop.")


bot.run('your bot token')
