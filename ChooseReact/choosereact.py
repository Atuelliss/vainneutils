import discord
from redbot.core import commands
from random import sample

class ChooseReact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def choosereact(self, ctx, message_id: int, emoji: str, count: int):
        """
        Randomly select X users who reacted to (emoji) on (message ID)
        Usage: .choosereact <message_id> <emoji> <count>
        Example: .choosereact 1316865261508493425 :white_check_mark: 3
        """
        try:
            # find the message using the message ID
            message = await ctx.channel.fetch_message(message_id)
        except discord.NotFound:
            return await ctx.send("Message not found. Please provide a valid message ID.")
        except discord.Forbidden:
            return await ctx.send("I don't have permission to view that message.")
        except discord.HTTPException:
            return await ctx.send("An error occurred while fetching the message.")

        # Extract users who reacted with the given emoji
        selected_users = []
        for reaction in message.reactions:
            if str(reaction.emoji) == emoji or reaction.emoji == emoji:
                try:
                    users = [user async for user in reaction.users() if not user.bot]
                    if len(users) < count:
                        return await ctx.send(f"Not enough users reacted with {emoji}.")
                    selected_users = sample(users, count)
                except discord.HTTPException:
                    return await ctx.send("An error occurred while fetching the reactions.")
                break
        else:
            return await ctx.send(f"No reactions with {emoji} were found on the specified message.")

        # Send the list of selected users
        user_mentions = ", ".join(user.mention for user in selected_users)
        await ctx.send(f"Randomly selected {count} user(s) who reacted with {emoji}: {user_mentions}")

# Red Bot Setup
async def setup(bot):
    cog = ChooseReact(bot)
    await bot.add_cog(cog)