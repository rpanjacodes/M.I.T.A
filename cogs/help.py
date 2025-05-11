import discord
from discord.ext import commands
from discord import app_commands

class HelpDropdown(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpSelect())

class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moderation", description="Here's Your All Mod Cmds.", emoji=discord.PartialEmoji(name="mod_hammer", id=1370395205697671218)),
            discord.SelectOption(label="AI", description="Here's Your all AI Related Cmds.", emoji=discord.PartialEmoji(name="ai", id=1370395105676234883)),
            discord.SelectOption(label="Automations", description="Here's Your all Automation Related Commamds.", emoji=discord.PartialEmoji(name="automation", id=1370395539727978547)),
            discord.SelectOption(label="Information", description="Here's Your All Information Related Cmds.", emoji=discord.PartialEmoji(name="lu", id=1371214359107473469)),
            discord.SelectOption(label="VC Commands", description="Here's Your all Vc Management Related Cmds.", emoji=discord.PartialEmoji(name="vc", id=1371211561053585448)),
            discord.SelectOption(label="Decoration", description="Here's Your All Server Decoration Related Cmds.", emoji=discord.PartialEmoji(name="deco", id=1371211930399801454)),
            discord.SelectOption(label="Automod", description="Here's Your All Automod Related Cmds.", emoji=discord.PartialEmoji(name="atmd", id=1371216174075088997)),
        ]
        super().__init__(placeholder="Choose a command category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.blurple())

        if self.values[0] == "Moderation":
            embed.title = "Moderation Commands"
            embed.description = (
                "<:ff:1371144418387693731> `/ban` - Ban a user\n"
                "<:ff:1371144418387693731> `/kick` - Kick a user\n"
                "<:ff:1371144418387693731> `/timeout` - Timeout a user\n"
                "<:ff:1371144418387693731> `/unban` - Unban the user\n"
                "<:ff:1371144418387693731> `/untimeout` - Untimeout the user\n"
            )

        elif self.values[0] == "AI":
            embed.title = "AI Commands"
            embed.description = (
                "<:ff:1371144418387693731> `/set_chatbot #channel` - To set the chatbot on a channel.\n"
                "<:ff:1371144418387693731> `/disable_chatbot` - Disable the chatbot.\n"
            )

        elif self.values[0] == "Automations":
            embed.title = "Automations"
            embed.description = (
                "<:ff:1371144418387693731> `/set_nickformat` - Changes nick when a new member joins.\n"
                "<:ff:1371144418387693731> `/regular_role` - Assigns a role to new members.\n"
                "<:ff:1371144418387693731> `/toogle_nickname` - Toggle nickname feature.\n"
                "<:ff:1371144418387693731> `/toogle_regular-role` - Toggle regular role feature.\n"
                "<:ff:1371144418387693731> `/set_log` - Set log channel.\n"
                "<:ff:1371144418387693731> `/toogle_logs` - Toggle log feature."
            )

        elif self.values[0] == "Information":
            embed.title = "Information"
            embed.description = (
                "<:ff:1371144418387693731> `/user_info` - Shows user info.\n"
                "<:ff:1371144418387693731> `/serverinfo` - Shows server info.\n"
            )

        elif self.values[0] == "VC Commands":
            embed.title = "VC Commands"
            embed.description = (
                "<:ff:1371144418387693731> `/vc_unban` - Unban a member from VC.\n"
                "<:ff:1371144418387693731> `/vc_ban` - Ban a member from VC.\n"
                "<:ff:1371144418387693731> `/vc_kick` - Kick a member from VC.\n"
                "<:ff:1371144418387693731> `/move_user` - Move a user between VCs.\n"
                "<:ff:1371144418387693731> `/move_all` - Move all VC members to another VC.\n"
            )

        elif self.values[0] == "Decoration":
            embed.title = "Decoration"
            embed.description = (
                "<:ff:1371144418387693731> `/bottom_pin` - A Message Can Set On channel and won't Disappear.\n"
                "<:ff:1371144418387693731> `/toogle_bottom-pin` - Enables Or Disables The Sticky Text Feature.\n"
                "<:ff:1371144418387693731> `/embed` - sends a customised embed message to a choosed channel.\n"
            )

        elif self.values[0] == "Automod":
            embed.title = "Automod"
            embed.description = (
                "<:ff:1371144418387693731> `/toogle_anti-spam` - Toggle caps spam protection.\n"
                "<:ff:1371144418387693731> `/toogle_anti-link` - Toggle link blocker.\n"
                "<:ff:1371144418387693731> `/toogle_anti-invite` - Toggle invite blocker.\n"
            )

        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all bot commands.")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="<:ff:1371144418387693731> Bot Help Menu",
            description="Please tap the dropdown menu to view each command category.",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=HelpDropdown(), ephemeral=False)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
