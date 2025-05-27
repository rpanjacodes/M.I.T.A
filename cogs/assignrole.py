import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random

class AssignRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="assignrole_everyone", description="Assign a role to every human (non-bot) member.")
    @app_commands.describe(role="The role to assign to everyone.")
    async def assignrole_everyone(self, interaction: discord.Interaction, role: discord.Role):
        # Permission Check
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need the **Manage Server** permission to use this command.",
                ephemeral=True
            )
            return

        # Filter human members who don't already have the role
        members = [m for m in interaction.guild.members if not m.bot and role not in m.roles]
        total = len(members)

        if total == 0:
            await interaction.response.send_message("✅ All human members already have that role.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"⏳ Starting to assign **{role.name}** to **{total}** human members...", ephemeral=True
        )

        success = 0
        for i, member in enumerate(members, 1):
            try:
                await member.add_roles(role, reason="Mass human role assignment")
                success += 1
                await asyncio.sleep(1)  # Delay to prevent instant rate limit
            except discord.HTTPException as e:
                if e.status == 429:  # Handle rate limiting
                    retry_after = getattr(e, "retry_after", 5)
                    await asyncio.sleep(retry_after + random.uniform(1, 3))
                else:
                    print(f"HTTP error on {member}: {e}")
            except Exception as e:
                print(f"Unexpected error on {member}: {e}")

        await interaction.followup.send(
            f"✅ Finished assigning role **{role.name}** to **{success}** human members."
        )

async def setup(bot):
    await bot.add_cog(AssignRole(bot))
