from discord import app_commands, Interaction, Embed
from discord.ext import commands
from mcstatus import JavaServer, BedrockServer

class MinecraftStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mc_search", description="Check if a Minecraft Java or Bedrock server is online")
    @app_commands.describe(serverlink="IP/domain of the Minecraft server (e.g. play.hypixel.net or bedrock.example.com)")
    async def mc_search(self, interaction: Interaction, serverlink: str):
        await interaction.response.defer()

        java_success = False
        try:
            # Try Java server first
            server = JavaServer.lookup(serverlink)
            status = server.status()

            embed = Embed(title=f"🌍 Java: {serverlink}", color=0x00ff00)
            embed.add_field(name="Status", value="🟢 Online", inline=True)
            embed.add_field(name="Players", value=f"👥 {status.players.online} / {status.players.max}", inline=True)
            embed.add_field(name="Ping", value=f"📶 {round(status.latency)} ms", inline=True)
            desc = status.description.get("text") if isinstance(status.description, dict) else str(status.description)
            embed.add_field(name="MOTD", value=desc or "No MOTD", inline=False)
            await interaction.followup.send(embed=embed)
            java_success = True
        except:
            pass

        if not java_success:
            try:
                # Try Bedrock server
                server = BedrockServer.lookup(serverlink)
                status = server.status()

                embed = Embed(title=f"📱 Bedrock: {serverlink}", color=0x00aaff)
                embed.add_field(name="Status", value="🟢 Online", inline=True)
                embed.add_field(name="Players", value=f"👥 {status.players_online} / {status.players_max}", inline=True)
                embed.add_field(name="Ping", value=f"📶 {round(status.latency)} ms", inline=True)
                embed.add_field(name="MOTD", value=status.motd or "No MOTD", inline=False)
                await interaction.followup.send(embed=embed)
            except:
                # If both fail
                embed = Embed(title=f"❌ {serverlink}", description="Server is offline or unreachable.", color=0xff0000)
                await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MinecraftStatus(bot))
