import discord
from discord.ext import commands
from discord import app_commands

class VCMove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="move_user", description="Move a user to another voice channel.")
    @app_commands.checks.has_permissions(move_members=True)
    async def move_user(self, interaction: discord.Interaction,
                        member: discord.Member,
                        target_channel: discord.VoiceChannel):
        if not member.voice:
            await interaction.response.send_message(f"{member.display_name} is not in a voice channel.", ephemeral=True)
            return

        try:
            await member.move_to(target_channel)
            await interaction.response.send_message(f"Moved {member.display_name} to {target_channel.name}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to move that member.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ An unexpected error occurred: {e}", ephemeral=True)

    @app_commands.command(name="move_all", description="Move all members from one VC to another.")
    @app_commands.checks.has_permissions(move_members=True)
    async def move_all(self, interaction: discord.Interaction,
                       from_channel: discord.VoiceChannel,
                       to_channel: discord.VoiceChannel):
        if from_channel.id == to_channel.id:
            await interaction.response.send_message("❌ Source and target channels are the same.", ephemeral=True)
            return

        if not from_channel.members:
            await interaction.response.send_message("❌ There are no members in the source VC.", ephemeral=True)
            return

        failed = []
        for member in from_channel.members:
            try:
                await member.move_to(to_channel)
            except:
                failed.append(member.display_name)

        if failed:
            await interaction.response.send_message(
                f"⚠️ Moved others, but failed to move: {', '.join(failed)}", ephemeral=True)
        else:
            await interaction.response.send_message(
                f"✅ Moved all members from {from_channel.name} to {to_channel.name}.", ephemeral=True)

    @app_commands.command(name="vc_kick", description="Disconnect a user from their current voice channel.")
    @app_commands.checks.has_permissions(move_members=True)
    async def vc_kick(self, interaction: discord.Interaction, member: discord.Member):
        if not member.voice:
            await interaction.response.send_message(f"{member.display_name} is not connected to any voice channel.", ephemeral=True)
            return

        try:
            await member.move_to(None)
            await interaction.response.send_message(f"✅ {member.display_name} has been disconnected.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to disconnect that member.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ An unexpected error occurred: {e}", ephemeral=True)

    @app_commands.command(name="vc_ban", description="Prevent a member from joining any voice channels.")
    @app_commands.checks.has_permissions(mute_members=True)
    async def vc_ban(self, interaction: discord.Interaction, member: discord.Member):
        overwrites = {channel: channel.overwrites_for(member) for channel in interaction.guild.voice_channels}
        for channel, overwrite in overwrites.items():
            overwrite.connect = False
            try:
                await channel.set_permissions(member, overwrite=overwrite)
            except discord.Forbidden:
                continue  # Skip channels the bot can't edit

        await interaction.response.send_message(f"❌ {member.mention} has been voice-banned from all voice channels.", ephemeral=True)

    @app_commands.command(name="vc_unban", description="Allow a previously voice-banned member to join voice channels.")
    @app_commands.checks.has_permissions(mute_members=True)
    async def vc_unban(self, interaction: discord.Interaction, member: discord.Member):
        for channel in interaction.guild.voice_channels:
            try:
                await channel.set_permissions(member, overwrite=None)
            except discord.Forbidden:
                continue

        await interaction.response.send_message(f"✅ {member.mention} can now join voice channels again.", ephemeral=True)

    @move_user.error
    @move_all.error
    @vc_kick.error
    @vc_ban.error
    @vc_unban.error
    async def on_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have the required permissions to use this command.", ephemeral=True)
        elif isinstance(error, discord.Forbidden):
            await interaction.response.send_message("❌ I lack the required permissions to complete this action.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ An unexpected error occurred: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VCMove(bot))
