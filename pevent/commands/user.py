import discord
from redbot.core import bank, commands
import asyncio

from ..abc import MixinMeta


class User(MixinMeta):
    @commands.command(name="mypevents", aliases=["mypevent", "myevents"])
    async def mypevents(self, ctx: commands.Context):
        """View your own player event statistics."""
        # Get user data from database
        guild_config = self.db.get_conf(ctx.guild)
        user_data = guild_config.get_user(ctx.author)

        # Check if user is banned from hosting
        if user_data.is_banned_from_host:
            await ctx.send("You are currently banned from hosting player events and may not use this command.")
            return

        # Create output message
        embed = discord.Embed(
            title=f"Player Event Statistics for {ctx.author.display_name}",
            description=f"```\n"
                        f"Setup:              {user_data.user_total_setup}\n"
                        f"Complete:           {user_data.user_total_complete}\n"
                        f"Success:            {user_data.user_total_success}\n"
                        f"----------------------\n"
                        f"Cancelled:          {user_data.user_total_cancelled}\n"
                        f"-with notice:       {user_data.user_total_cancelled_withnotice}\n"
                        f"-without notice:    {user_data.user_total_cancelled_withoutnotice}\n"
                        f"----------------------\n"
                        f"Has Deposit:       {'Yes' if user_data.has_active_deposit else 'No'}\n"
                        f"```",
            color=discord.Color.blue(),
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="pdeposit")
    async def make_event_deposit(self, ctx: commands.Context):
        """Command to make a deposit."""
        # Get user data from database
        guild_config = self.db.get_conf(ctx.guild)
        user_data = guild_config.get_user(ctx.author)

        # Check if user is banned from hosting
        if user_data.is_banned_from_host:
            await ctx.send("You are currently banned from hosting player events and may not use this command.")
            return

        # Check if user can make deposit
        if not user_data.can_make_deposit:
            await ctx.send("You are not permitted to make a deposit.")
            return
        
        # Check if user already has an active deposit
        if user_data.has_active_deposit:
            await ctx.send("You already have an active deposit. Please wait until it is completed before making another.")
            return

        # Get user's bank balance
        user_balance = await bank.get_balance(ctx.author)
        deposit_amount = self.db.deposit_value
        
        # Check if user has enough balance
        if user_balance < deposit_amount:
            await ctx.send(f"You do not have the required {deposit_amount} needed to make a deposit.")
            return
        
        # Ask for confirmation
        await ctx.send(f"Are you sure you want to make a deposit of {deposit_amount}?")
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            response_text = response.content.strip()
            
            if response_text.lower() in ["yes", "y"]:
                # Deduct the amount from user's bank
                await bank.withdraw_credits(ctx.author, deposit_amount)
                
                # Update user's deposit status
                user_data.has_active_deposit = True
                # Update user's Setup count
                user_data.user_total_setup += 1
                # Save the changes
                self.save()
                
                await ctx.send(f"Deposit of {deposit_amount} has been made successfully.")
            else:
                await ctx.send("Deposit cancelled.")
                
        except asyncio.TimeoutError:
            await ctx.send("Deposit cancelled due to timeout.")