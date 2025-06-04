import discord
from discord.ext import commands
from discord import app_commands
from db import set_log_settings, get_log_channel_id, is_log_enabled

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_log_channel(self, guild):
        if not is_log_enabled(guild.id):
            return None
        channel_id = get_log_channel_id(guild.id)
        return guild.get_channel(channel_id)

    async def send_log(self, guild, embed: discord.Embed):
        channel = self.get_log_channel(guild)
        if channel:
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                print(f"[Log Error] Missing permissions to send messages in {channel.name}")
            except Exception as e:
                print(f"[Log Error] Unexpected error in send_log: {e}")

    # ---------------- Member Events ----------------
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(title="🚫 Member Banned", description=f"**{user}**", color=discord.Color.red())
        embed.set_footer(text=f"User ID: {user.id}")
        await self.send_log(guild, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(title="♻️ Member Unbanned", description=f"**{user}**", color=discord.Color.green())
        embed.set_footer(text=f"User ID: {user.id}")
        await self.send_log(guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(title="👋 Member Left or Kicked", description=f"**{member}**", color=discord.Color.orange())
        embed.set_footer(text=f"User ID: {member.id}")
        await self.send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        embed = discord.Embed(title="📝 Member Updated", color=discord.Color.blurple())
        changes = []
        if before.nick != after.nick:
            changes.append(f"Nickname: `{before.nick}` → `{after.nick}`")
        if before.roles != after.roles:
            before_roles = ", ".join([r.name for r in before.roles[1:]])
            after_roles = ", ".join([r.name for r in after.roles[1:]])
            changes.append(f"Roles changed:\n➖ {before_roles}\n➕ {after_roles}")
        if changes:
            embed.description = "\n".join(changes)
            embed.set_author(name=str(after), icon_url=after.display_avatar.url)
            await self.send_log(after.guild, embed)

    # ---------------- Voice Events ----------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if not before.channel and after.channel:
                title = "🔊 Voice Channel Join"
                desc = f"{member.mention} joined {after.channel.mention}"
            elif before.channel and not after.channel:
                title = "📤 Voice Channel Leave"
                desc = f"{member.mention} left {before.channel.mention}"
            else:
                title = "🔄 Voice Channel Switch"
                desc = f"{member.mention} switched from {before.channel.mention} to {after.channel.mention}"
            embed = discord.Embed(title=title, description=desc, color=discord.Color.teal())
            await self.send_log(member.guild, embed)

    # ---------------- Channel Events ----------------
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        embed = discord.Embed(title="📁 Channel Created", description=f"{channel.mention} ({channel.name})", color=discord.Color.green())
        await self.send_log(channel.guild, embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        embed = discord.Embed(title="🗑️ Channel Deleted", description=f"{channel.name}", color=discord.Color.red())
        await self.send_log(channel.guild, embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if before.name != after.name:
            embed = discord.Embed(title="✏️ Channel Renamed", description=f"`{before.name}` → `{after.name}`", color=discord.Color.blurple())
            await self.send_log(before.guild, embed)

    # ---------------- Role Events ----------------
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        embed = discord.Embed(title="➕ Role Created", description=f"{role.mention} (`{role.name}`)", color=discord.Color.green())
        await self.send_log(role.guild, embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        embed = discord.Embed(title="➖ Role Deleted", description=f"`{role.name}`", color=discord.Color.red())
        await self.send_log(role.guild, embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        changes = []
        if before.name != after.name:
            changes.append(f"Name: `{before.name}` → `{after.name}`")
        if before.permissions != after.permissions:
            changes.append(f"Permissions updated.")
        if changes:
            embed = discord.Embed(title="⚙️ Role Updated", description="\n".join(changes), color=discord.Color.blurple())
            await self.send_log(before.guild, embed)

    # ---------------- Message Events ----------------
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        embed = discord.Embed(title="🗑️ Message Deleted", description=message.content or "*No content*", color=discord.Color.red())
        embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
        embed.set_footer(text=f"In #{message.channel.name}")
        await self.send_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        embed = discord.Embed(title="✏️ Message Edited", color=discord.Color.orange())
        embed.add_field(name="Before", value=before.content or "*Empty*", inline=False)
        embed.add_field(name="After", value=after.content or "*Empty*", inline=False)
        embed.set_author(name=str(before.author), icon_url=before.author.display_avatar.url)
        embed.set_footer(text=f"In #{before.channel.name}")
        await self.send_log(before.guild, embed)

    # ---------------- Slash Commands ----------------
    @app_commands.command(name="set_log_channel", description="Set the channel where logs will be posted.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        try:
            set_log_settings(interaction.guild.id, channel_id=channel.id)
            await interaction.response.send_message(f"✅ Logs will now be posted in {channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Failed to set log channel: `{e}`", ephemeral=True)

    @set_log_channel.error
    async def set_log_channel_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ You need `Manage Server` permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ Error: `{error}`", ephemeral=True)

    @app_commands.command(name="toggle_logs", description="Enable or disable log messages.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_logs(self, interaction: discord.Interaction, enabled: bool):
        try:
            set_log_settings(interaction.guild.id, enabled=enabled)
            status = "enabled" if enabled else "disabled"
            await interaction.response.send_message(f"✅ Logging has been **{status}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Failed to toggle logs: `{e}`", ephemeral=True)

    @toggle_logs.error
    async def toggle_logs_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ You need `Manage Server` permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ Error: `{error}`", ephemeral=True)

# ---------------- Cog Setup ----------------
async def setup(bot):
    await bot.add_cog(Logs(bot))
