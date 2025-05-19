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
            discord.SelectOption(label="Moderation", description="Here's Your All Mod Cmds.", emoji=discord.PartialEmoji(name="kirtikaze_with_tool", id=1371362714475167856)),
            discord.SelectOption(label="AI", description="Here's Your all AI Related Cmds.", emoji=discord.PartialEmoji(name="kirtikaze_salute", id=1360664658712854820)),
            discord.SelectOption(label="Automations", description="Here's Your all Automation Related Commamds.", emoji=discord.PartialEmoji(name="kirtikaze_work", id=1371362447033761862)),
            discord.SelectOption(label="Information", description="Here's Your All Information Related Cmds.", emoji=discord.PartialEmoji(name="kirtikaze_work2", id=1371362515946176533)),
            discord.SelectOption(label="VC Commands", description="Here's Your all Vc Management Related Cmds.", emoji=discord.PartialEmoji(name="kirtikaze_happy", id=1360663196838395986)),
            discord.SelectOption(label="Decoration", description="Here's Your All Server Decoration Related Cmds.", emoji=discord.PartialEmoji(name="kirtikaze_blushed", id=1360664907426562239)),
            discord.SelectOption(label="Automod", description="Here's Your All Automod Related Cmds.", emoji=discord.PartialEmoji(name="kirtikaze_teacher", id=1371362631306182676)),
            discord.SelectOption(label="Fun and Enjoy", description="Here's Your All Fun And Enjoyable Cmds.", emoji=discord.PartialEmoji(name="kirtikaze_congratulate",id=1360663897211797666)),
        ]
        super().__init__(placeholder="Choose a command category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.blurple())

        if self.values[0] == "Moderation":
            embed.title = "Moderation Commands"
            embed.description = (
                "<a:arr:1371326929042407435> `/ban` - Ban a user\n"
                "<a:arr:1371326929042407435> `/kick` - Kick a user\n"
                "<a:arr:1371326929042407435> `/timeout` - Timeout a user\n"
                "<a:arr:1371326929042407435> `/unban` - Unban the user\n"
                "<a:arr:1371326929042407435> `/untimeout` - Untimeout the user\n"
            )

        elif self.values[0] == "AI":
            embed.title = "AI Commands"
            embed.description = (
                "<a:arr:1371326929042407435> `/set_chatbot #channel` - To set the chatbot on a channel.\n"
                "<a:arr:1371326929042407435> `/disable_chatbot` - Disable the chatbot.\n"
            )

        elif self.values[0] == "Automations":
            embed.title = "Automations"
            embed.description = (
                "<a:arr:1371326929042407435> `/set_nickformat` - Changes nick when a new member joins.\n"
                "<a:arr:1371326929042407435> `/regular_role` - Assigns a role to new members.\n"
                "<a:arr:1371326929042407435> `/toogle_nickname` - Toggle nickname feature.\n"
                "<a:arr:1371326929042407435> `/toogle_regular-role` - Toggle regular role feature.\n"
                "<a:arr:1371326929042407435> `/set_log` - Set log channel.\n"
                "<a:arr:1371326929042407435> `/toogle_logs` - Toggle log feature."
            )

        elif self.values[0] == "Information":
            embed.title = "Information"
            embed.description = (
                "<a:arr:1371326929042407435> `/user_info` - Shows user info.\n"
                "<a:arr:1371326929042407435> `/serverinfo` - Shows server info.\n"
                "<a:arr:1371326929042407435> `/avatar` - Shows user's Avatar.\n"
            )

        elif self.values[0] == "VC Commands":
            embed.title = "VC Commands"
            embed.description = (
                "<a:arr:1371326929042407435> `/vc_unban` - Unban a member from VC.\n"
                "<a:arr:1371326929042407435> `/vc_ban` - Ban a member from VC.\n"
                "<a:arr:1371326929042407435> `/vc_kick` - Kick a member from VC.\n"
                "<a:arr:1371326929042407435> `/move_user` - Move a user between VCs.\n"
                "<a:arr:1371326929042407435> `/move_all` - Move all VC members to another VC.\n"
            )

        elif self.values[0] == "Decoration":
            embed.title = "Decoration"
            embed.description = (
                "<a:arr:1371326929042407435> `/bottom_pin` - A Message Can Set On channel and won't Disappear.\n"
                "<a:arr:1371326929042407435> `/toogle_bottom-pin` - Enables Or Disables The Sticky Text Feature.\n"
                "<a:arr:1371326929042407435> `/embed` - sends a customised embed message to a choosed channel.\n"
                "<a:arr:1371326929042407435> `/clear_chat` - Clears Chat/embed messages/bot messages in one go.\n"
                "<a:arr:1371326929042407435> `/giveaway` - Set Giveaway On Your Server.\n"
                "<a:arr:1371326929042407435> `/reroll` - You Can Reroll The Winner If He/She Invalid For You !\n"
            )

        elif self.values[0] == "Automod":
            embed.title = "Automod"
            embed.description = (
                "<a:arr:1371326929042407435> `/automod_block_mentions` - Block Mentions With Automod.\n"
                "<a:arr:1371326929042407435> `/automod_block_link` - Block Links with Automod.\n"
                "<a:arr:1371326929042407435> `/automod_rule` - You Can Customise Automod.\n"
                "<a:arr:1371326929042407435> `/automod_block_invite` - You Can Block Discord Invites with automod.\n"
                "<a:arr:1371326929042407435> `/automod_block_word` - You can use to block default words that prohibited.\n"
            )
            
        elif self.values[0] == "Fun And Enjoy":
            embed.title = "Fun And Enjoy"
            embed.description = (
                "<a:arr:1371326929042407435> `/react` - Use for React With anime pics.\n"
                "<a:arr:1371326929042407435> `/count_channel` - You Can set count channel.\n"
                "<a:arr:1371326929042407435> `/reset_count` - Reset Progress of Count.\n"
            )

        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all bot commands.")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="<:kirtikaze_work2:1371362515946176533> Bot Help Menu",
            description="<a:arr:1371326929042407435> Please tap the dropdown menu to view each command category.",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=HelpDropdown(), ephemeral=False)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
