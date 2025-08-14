import discord
from discord.ext import commands, tasks
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import json
import os
from datetime import datetime, timedelta
import aiohttp
import io

DATA_FILE = os.path.join("data", "duos.json")
TEMPLATE_PATH = os.path.join("assets", "duo_template.png")

# Manual positioning for avatars & names
AVATAR1_POS = (100, 200)
AVATAR2_POS = (500, 200)
NAME1_POS = (200, 400)
NAME2_POS = (600, 400)
AVATAR_SIZE = (150, 150)

BREAKUP_TIMEOUT = timedelta(hours=10)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def fetch_avatar_bytes(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.read()

async def generate_duo_image(user1: discord.User, user2: discord.User):
    template = Image.open(TEMPLATE_PATH).convert("RGBA")

    avatar1_bytes = await fetch_avatar_bytes(user1.display_avatar.url)
    avatar2_bytes = await fetch_avatar_bytes(user2.display_avatar.url)

    avatar1 = Image.open(io.BytesIO(avatar1_bytes)).convert("RGBA").resize(AVATAR_SIZE)
    avatar2 = Image.open(io.BytesIO(avatar2_bytes)).convert("RGBA").resize(AVATAR_SIZE)

    template.paste(avatar1, AVATAR1_POS, avatar1)
    template.paste(avatar2, AVATAR2_POS, avatar2)

    draw = ImageDraw.Draw(template)
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()

    draw.text(NAME1_POS, user1.name, font=font, fill=(255, 255, 255))
    draw.text(NAME2_POS, user2.name, font=font, fill=(255, 255, 255))

    buffer = io.BytesIO()
    template.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

class Duo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.breakup_checker.start()

    def cog_unload(self):
        self.breakup_checker.cancel()

    @tasks.loop(minutes=5)
    async def breakup_checker(self):
        data = load_data()
        now = datetime.utcnow()
        changed = False

        to_remove = []
        for uid, info in list(data.items()):
            if info.get("breakup_pending", False):
                requested_at = datetime.fromisoformat(info["breakup_requested_at"])
                if now - requested_at >= BREAKUP_TIMEOUT:
                    partner_id = str(info["partner_id"])
                    to_remove.append(uid)
                    to_remove.append(partner_id)

        for uid in set(to_remove):
            data.pop(uid, None)
            changed = True

        if changed:
            save_data(data)

    @app_commands.command(name="duo_start", description="Start a dynamic duo with someone")
    async def duo_start(self, interaction: discord.Interaction, partner: discord.Member):
        data = load_data()
        uid = str(interaction.user.id)
        pid = str(partner.id)

        if uid in data or pid in data:
            return await interaction.response.send_message("❌ One of you is already in a duo!", ephemeral=True)

        embed = discord.Embed(
            title="💞 Dynamic Duo Request",
            description=f"{interaction.user.mention} wants to start a dynamic duo with {partner.mention}!\nDo you accept?",
            color=discord.Color.pink()
        )

        view = DuoConfirmView(interaction.user, partner)
        await interaction.response.send_message(content=partner.mention, embed=embed, view=view)

    @app_commands.command(name="dduo", description="Check someone's duo partner")
    async def dduo(self, interaction: discord.Interaction, member: discord.Member):
        data = load_data()
        uid = str(member.id)

        if uid not in data:
            return await interaction.response.send_message("❌ This user has no dynamic duo.", ephemeral=True)

        partner_id = data[uid]["partner_id"]
        partner = interaction.guild.get_member(partner_id) or await self.bot.fetch_user(partner_id)

        img = await generate_duo_image(member, partner)
        file = discord.File(img, filename="duo.png")
        await interaction.response.send_message(file=file)

    @app_commands.command(name="duo_breakup", description="Break up your dynamic duo")
    async def duo_breakup(self, interaction: discord.Interaction):
        data = load_data()
        uid = str(interaction.user.id)

        if uid not in data:
            return await interaction.response.send_message("❌ You have no duo to break up with.", ephemeral=True)

        partner_id = str(data[uid]["partner_id"])

        for u in [uid, partner_id]:
            data[u]["breakup_pending"] = True
            data[u]["breakup_requested_by"] = uid
            data[u]["breakup_requested_at"] = datetime.utcnow().isoformat()

        save_data(data)

        partner = interaction.guild.get_member(int(partner_id)) or await self.bot.fetch_user(int(partner_id))

        embed = discord.Embed(
            title="💔 Breakup Requested",
            description=f"{interaction.user.mention} wants to break up with {partner.mention}.\n"
                        f"Partner can confirm instantly or it will auto-break in **10 hours**.\n"
                        f"{interaction.user.mention} can cancel anytime with `/duo_breakup_cancel`.",
            color=discord.Color.red()
        )

        view = BreakupConfirmView(interaction.user, partner)
        await interaction.response.send_message(content=partner.mention, embed=embed, view=view)

    @app_commands.command(name="duo_breakup_cancel", description="Cancel a pending breakup within 10 hours")
    async def duo_breakup_cancel(self, interaction: discord.Interaction):
        data = load_data()
        uid = str(interaction.user.id)

        if uid not in data:
            return await interaction.response.send_message("❌ You have no duo to cancel breakup from.", ephemeral=True)

        if not data[uid].get("breakup_pending", False):
            return await interaction.response.send_message("❌ There is no breakup pending.", ephemeral=True)

        if data[uid].get("breakup_requested_by") != uid:
            return await interaction.response.send_message("❌ Only the initiator can cancel the breakup.", ephemeral=True)

        requested_at = datetime.fromisoformat(data[uid]["breakup_requested_at"])
        if datetime.utcnow() - requested_at > BREAKUP_TIMEOUT:
            return await interaction.response.send_message("⏳ Breakup time has already expired.", ephemeral=True)

        partner_id = str(data[uid]["partner_id"])
        for u in [uid, partner_id]:
            if u in data:
                data[u]["breakup_pending"] = False
                data[u].pop("breakup_requested_by", None)
                data[u].pop("breakup_requested_at", None)

        save_data(data)
        await interaction.response.send_message("✅ Breakup cancelled successfully.", ephemeral=True)

class DuoConfirmView(discord.ui.View):
    def __init__(self, user1, user2):
        super().__init__(timeout=60)
        self.user1 = user1
        self.user2 = user2
        self.accepted = set()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [self.user1.id, self.user2.id]:
            return await interaction.response.send_message("❌ This isn't your duo request!", ephemeral=True)

        self.accepted.add(interaction.user.id)
        if len(self.accepted) == 2:
            data = load_data()
            data[str(self.user1.id)] = {"partner_id": self.user2.id, "created_at": datetime.utcnow().isoformat(), "breakup_pending": False}
            data[str(self.user2.id)] = {"partner_id": self.user1.id, "created_at": datetime.utcnow().isoformat(), "breakup_pending": False}
            save_data(data)

            img = await generate_duo_image(self.user1, self.user2)
            file = discord.File(img, filename="duo.png")
            await interaction.response.edit_message(content="✅ Duo created!", embed=None, view=None, attachments=[file])

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Duo request declined.", embed=None, view=None)

class BreakupConfirmView(discord.ui.View):
    def __init__(self, user1, user2):
        super().__init__(timeout=None)
        self.user1 = user1
        self.user2 = user2

    @discord.ui.button(label="Confirm Breakup", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user2.id:
            return await interaction.response.send_message("❌ Only your partner can confirm breakup.", ephemeral=True)

        data = load_data()
        data.pop(str(self.user1.id), None)
        data.pop(str(self.user2.id), None)
        save_data(data)

        await interaction.response.edit_message(content="💔 Duo broken up.", embed=None, view=None)

async def setup(bot):
    await bot.add_cog(Duo(bot))
