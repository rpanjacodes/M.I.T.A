import discord
from discord.ext import commands
from discord import app_commands

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ====== HELPER FUNCTIONS ======
    async def create_rule(self, guild_id: int, name: str, trigger_type: int, metadata: dict = {}, actions: list = None):
        route = discord.http.Route("POST", f"/guilds/{guild_id}/auto-moderation/rules")
        payload = {
            "name": name,
            "event_type": 1,  # MESSAGE_SEND
            "trigger_type": trigger_type,
            "trigger_metadata": metadata,
            "actions": actions or [{"type": 1}],  # Type 1: block message
        }
        await self.bot.http.request(route, json=payload)

    async def delete_all_rules(self, guild_id: int):
        route = discord.http.Route("GET", f"/guilds/{guild_id}/auto-moderation/rules")
        rules = await self.bot.http.request(route)
        for rule in rules:
            delete_route = discord.http.Route("DELETE", f"/guilds/{guild_id}/auto-moderation/rules/{rule['id']}")
            await self.bot.http.request(delete_route)

    # ====== COMMANDS ======

    @app_commands.command(name="automod_invites", description="Enable automod to block Discord invite links")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_invites(self, interaction: discord.Interaction):
        await self.create_rule(
            interaction.guild_id,
            name="Block Invites",
            trigger_type=4,
            metadata={"keyword_filter": ["discord.gg", "discord.com/invite"]},
        )
        await interaction.response.send_message("✅ Invite link filter enabled.", ephemeral=True)

    @app_commands.command(name="automod_links", description="Enable automod to block all links")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_links(self, interaction: discord.Interaction):
        await self.create_rule(
            interaction.guild_id,
            name="Block Links",
            trigger_type=4,
            metadata={"regex_patterns": [r"https?://"]},
        )
        await interaction.response.send_message("✅ Link filter enabled.", ephemeral=True)

    @app_commands.command(name="automod_spam", description="Enable automod anti-spam")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_spam(self, interaction: discord.Interaction):
        await self.create_rule(
            interaction.guild_id,
            name="Anti-Spam",
            trigger_type=3,  # Spam
        )
        await interaction.response.send_message("✅ Spam filter enabled.", ephemeral=True)

    @app_commands.command(name="automod_clear", description="Remove all automod rules created by the bot")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_clear(self, interaction: discord.Interaction):
        await self.delete_all_rules(interaction.guild_id)
        await interaction.response.send_message("♻️ All automod rules cleared.", ephemeral=True)

    @app_commands.command(name="automod_custom", description="Create a custom Automod rule")
    @app_commands.describe(
        name="Name of the rule",
        trigger="Type of trigger: 'keyword', 'regex', 'spam'",
        keyword_or_pattern="Blocked words or regex pattern",
        timeout_seconds="Time (in seconds) to timeout offenders (optional)",
        send_alerts="Send alert to mods/logs channel"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_custom(
        self,
        interaction: discord.Interaction,
        name: str,
        trigger: str,
        keyword_or_pattern: str,
        timeout_seconds: int = 0,
        send_alerts: bool = False
    ):
        trigger_map = {"keyword": 4, "regex": 4, "spam": 3}
        trigger_type = trigger_map.get(trigger.lower())
        if not trigger_type:
            return await interaction.response.send_message("❌ Invalid trigger type. Use `keyword`, `regex`, or `spam`.", ephemeral=True)

        metadata = {}
        if trigger == "keyword":
            metadata["keyword_filter"] = [keyword_or_pattern]
        elif trigger == "regex":
            metadata["regex_patterns"] = [keyword_or_pattern]

        actions = [{"type": 1}]  # Block message
        if timeout_seconds > 0:
            actions.append({
                "type": 2,  # Timeout
                "metadata": {"duration_seconds": timeout_seconds}
            })
        if send_alerts:
            actions.append({
                "type": 3,  # Send alert
                "metadata": {}  # You can add custom channel_id if needed
            })

        await self.create_rule(interaction.guild_id, name, trigger_type, metadata, actions)
        await interaction.response.send_message(f"✅ Custom Automod rule `{name}` created.", ephemeral=True)

    # ====== PERMISSION ERROR HANDLER ======
    @automod_invites.error
    @automod_links.error
    @automod_spam.error
    @automod_clear.error
    @automod_custom.error
    async def on_perm_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ You need `Manage Server` permission to use this command.", ephemeral=True)
        else:
            raise error  # For other errors

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
