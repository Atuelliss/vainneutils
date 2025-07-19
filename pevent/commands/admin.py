import asyncio
import discord
from redbot.core import bank, commands

from ..abc import MixinMeta

class Admin(MixinMeta):
    # Add field mapping as class constant
    FIELD_MAPPING = {
        "setup": "user_total_setup",
        "complete": "user_total_complete", 
        "success": "user_total_success",
        "cancelled": "user_total_cancelled",
        "withnotice": "user_total_cancelled_withnotice",
        "nonotice": "user_total_cancelled_withoutnotice"
    }

    def reset_user_event_data(self, user_data):
        """Reset a user's event data to default values (0)."""
        user_data.user_total_setup = 0
        user_data.user_total_complete = 0
        user_data.user_total_success = 0
        user_data.user_total_cancelled = 0
        user_data.user_total_cancelled_withnotice = 0
        user_data.user_total_cancelled_withoutnotice = 0
        user_data.can_make_deposit = False
        user_data.has_active_deposit = False

    @commands.group(name="pevent")
    @commands.admin_or_permissions(manage_guild=True)  # Only Admins can use this command
    async def pevent(self, ctx: commands.Context):
        """-Player-Event management commands.-
        """
        pass

    @pevent.command(name="list")
    async def pevent_list(self, ctx: commands.Context, user: discord.Member = None):
        """-List player event statistics for a specific user.-"""
        if user is None:
            await ctx.send("Please specify a user. Usage: `[p]pevent list @user` or `[p]pevent list user_id`")
            return
        
        if user.bot:
            await ctx.send("You cannot use this command on a bot.")
            return
        
        # Get user data from database
        guild_config = self.db.get_conf(ctx.guild)
        user_data = guild_config.get_user(user)
        
        # Create output message
        embed = discord.Embed(
            title=f"Player Event Statistics for {user.display_name}",
            description=f"```\n"
                        f"Setup:               {user_data.user_total_setup}\n"
                        f"Complete:            {user_data.user_total_complete}\n"
                        f"Success:             {user_data.user_total_success}\n"
                        f"----------------------\n"
                        f"Cancelled:           {user_data.user_total_cancelled}\n"
                        f"-with notice:        {user_data.user_total_cancelled_withnotice}\n"
                        f"-without notice:     {user_data.user_total_cancelled_withoutnotice}\n"
                        f"----------------------\n"
                        f"Can Make Deposit:    {'Yes' if user_data.can_make_deposit else 'No'}\n"
                        f"Has Deposit:         {'Yes' if user_data.has_active_deposit else 'No'}\n"
                        f"Banned from Hosting: {'Yes' if user_data.is_banned_from_host else 'No'}\n"
                        f"```",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        await ctx.send(embed=embed)

    @pevent.command(name="add")
    async def pevent_add(self, ctx: commands.Context, user: discord.Member, field: str, quantity: int):
        """-Add to a player's event statistics.-
        Specify the field to update: *setup*, *complete*, *success*, *cancelled*, *withnotice*, or *nonotice*.
        """
        if user.bot:
            await ctx.send("You cannot use this command on a bot.")
            return
        
        # Validate quantity is positive
        if quantity <= 0:
            await ctx.send("Quantity must be a positive number.")
            return
            
        if field.lower() not in self.FIELD_MAPPING:
            valid_fields = ", ".join(self.FIELD_MAPPING.keys())
            await ctx.send(f"Invalid field. Valid fields are: {valid_fields}")
            return
        
        # Get user data from database
        guild_config = self.db.get_conf(ctx.guild)
        user_data = guild_config.get_user(user)
        
        # Update the specified field
        attr_name = self.FIELD_MAPPING[field.lower()]
        current_value = getattr(user_data, attr_name)
        new_value = current_value + quantity
        setattr(user_data, attr_name, new_value)
        
        # Save the changes
        self.save()
        
        await ctx.send(f"Added {quantity} to {user.display_name}'s {field} count. New total: {new_value}")

    @pevent.command(name="remove")
    async def pevent_remove(self, ctx: commands.Context, user: discord.Member, field: str, quantity: int):
        """-Remove from a player's event statistics.-
        Specify the field to update: *setup*, *complete*, *success*, *cancelled*, *withnotice*, or *nonotice*.
        """
        if user.bot:
            await ctx.send("You cannot use this command on a bot.")
            return
        
        if field.lower() not in self.FIELD_MAPPING:
            valid_fields = ", ".join(self.FIELD_MAPPING.keys())
            await ctx.send(f"Invalid field. Valid fields are: {valid_fields}")
            return
        
        # Get user data from database
        guild_config = self.db.get_conf(ctx.guild)
        user_data = guild_config.get_user(user)
        
        # Update the specified field
        attr_name = self.FIELD_MAPPING[field.lower()]
        current_value = getattr(user_data, attr_name)
        new_value = max(0, current_value - quantity)  # Prevent negative values
        setattr(user_data, attr_name, new_value)
        
        # Save the changes
        self.save()
        
        await ctx.send(f"Removed {quantity} from {user.display_name}'s {field} count. New total: {new_value}")

    @pevent.command(name="wipe")
    async def pevent_wipe(self, ctx: commands.Context, user: discord.Member):
        """-Wipe a specific user's player event data.-"""
        if user.bot:
            await ctx.send("You cannot use this command on a bot.")
            return
        
        # Get user data from database
        guild_config = self.db.get_conf(ctx.guild)
        user_data = guild_config.get_user(user)
        
        # Create output message showing current stats before wiping
        embed = discord.Embed(
            title=f"Player Event Statistics for {user.display_name}",
            description=f"```\n"
                        f"Setup:              {user_data.user_total_setup}\n"
                        f"Complete:           {user_data.user_total_complete}\n"
                        f"Success:            {user_data.user_total_success}\n"
                        f"----------------------\n"
                        f"Cancelled:          {user_data.user_total_cancelled}\n"
                        f"-with notice:       {user_data.user_total_cancelled_withnotice}\n"
                        f"-without notice:    {user_data.user_total_cancelled_withoutnotice}\n"
                        f"```",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        await ctx.send(embed=embed)
        
        # Ask for confirmation
        await ctx.send("Are you sure you want to wipe this User's data?")
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            response_text = response.content.strip()
            
            if response_text in ["Yes", "yes"]:
                # Reset the user's data using helper function
                self.reset_user_event_data(user_data)
                
                # Save the changes
                self.save()
                
                await ctx.send("This User's information has been removed from the database.")
            else:
                await ctx.send("Cancelling wipe action.")
                
        except asyncio.TimeoutError:
            await ctx.send("Cancelling wipe action.")

    @pevent.command(name="allow")
    async def pevent_allow(self, ctx: commands.Context, user: discord.Member = None):
        """-Permits a Player to make a deposit for an event.-"""
        if user.bot:
            await ctx.send("You cannot use this command on a bot.")
            return
        
        if user is None:
            await ctx.send("Please specify a user. Usage: `[p]pevent allow @user` or `[p]pevent allow user_id`")
            return
        
        # Get user data from database
        guild_config = self.db.get_conf(ctx.guild)
        user_data = guild_config.get_user(user)

        # Update the user's permission
        user_data.can_make_deposit = True

        # Save the changes
        self.save()

        await ctx.send(f"Permitted {user.display_name} to make a deposit for an event.")

    @pevent.command(name="setdeposit")
    async def pevent_setdeposit(self, ctx: commands.Context, amount: int = None):
        """-Set the deposit value for events.-"""
        # If no amount provided, show current value
        if amount is None:
            await ctx.send(f"Current deposit value: {self.db.deposit_value}\n*Please provide a number to change the deposit value.*")
            return
        
        # Validate amount is positive
        if amount <= 0:
            await ctx.send("Deposit amount must be a positive number.")
            return
        
        # Update the deposit value
        self.db.deposit_value = amount
        
        # Save the changes
        self.save()
        
        await ctx.send(f"Deposit value has been set to {amount}.")

    @pevent.command(name="complete")
    async def pevent_complete(self, ctx: commands.Context, user: discord.Member = None):
        """-Marks a Player's event as complete.-"""
        if user is None:
            await ctx.send("Please specify a user. Usage: `[p]pevent complete @user` or `[p]pevent complete user_id`")
            return
        
        if user.bot:
            await ctx.send("You cannot use this command on a bot.")
            return
        
        # Get user data from database
        guild_config = self.db.get_conf(ctx.guild)
        user_data = guild_config.get_user(user)

        # Update the user's complete count
        user_data.user_total_complete += 1
        # Clear User's deposit.
        user_data.has_active_deposit = False
        # Set User's can_make_deposit to False
        user_data.can_make_deposit = False
        # Ask author if Success and update accordingly
        await ctx.send(f"Event for {user.display_name} marked as complete and deposit has been refunded. Do you want to mark it as successful? (yes/no)")
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            response_text = response.content.strip()

            if response_text.lower() in ["yes", "y"]:
                user_data.user_total_success += 1
                await ctx.send(f"Event for {user.display_name} marked as successful.")
                # Refund the deposit
                try:
                    await bank.deposit_credits(user, self.db.deposit_value)
                    await ctx.send(f"Refunded {self.db.deposit_value} to {user.display_name}.")
                except Exception as e:
                    await ctx.send(f"Failed to refund deposit: {e}")
            else:
                await ctx.send(f"Event for {user.display_name} not marked as successful.")

        except asyncio.TimeoutError:
            await ctx.send("No response received. Event not marked as successful.")
        # Save the changes
        self.save()

    @pevent.command(name="cancel")
    async def pevent_cancel(self, ctx: commands.Context, user: discord.Member = None):
        """-Marks a Player's event as cancelled.-"""
        if user is None:
            await ctx.send("Please specify a user. Usage: `[p]pevent cancel @user` or `[p]pevent cancel user_id`")
            return

        if user.bot:
            await ctx.send("You cannot use this command on a bot.")
            return

        # Get user data from database
        guild_config = self.db.get_conf(ctx.guild)
        user_data = guild_config.get_user(user)
        # Update the user's cancelled count
        user_data.user_total_cancelled += 1
        # Ask if user wants to mark as cancelled with or without notice
        await ctx.send(f"Event for {user.display_name} marked as cancelled. Did they give notice? (yes/no)")
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            response_text = response.content.strip()

            if response_text.lower() in ["yes", "y"]:
                user_data.user_total_cancelled_withnotice += 1
                await ctx.send(f"Event for {user.display_name} marked as cancelled with notice.")
                # Set User's can_make_deposit to False
                user_data.can_make_deposit = False
                # Ask if you want to refund the deposit
                await ctx.send(f"Do you want to refund the deposit for {user.display_name}? (yes/no)")
                
                try:
                    response = await self.bot.wait_for('message', check=check, timeout=30.0)
                    response_text = response.content.strip()

                    if response_text.lower() in ["yes", "y"]:
                        # Refund the deposit
                        await bank.deposit_credits(user, self.db.deposit_value)
                        await ctx.send(f"Refunded {self.db.deposit_value} to {user.display_name}.")
                        # Set user's has_active_deposit to False
                        user_data.has_active_deposit = False
                        # Set user can_make_deposit to False
                        user_data.can_make_deposit = False
                    else:
                        await ctx.send(f"No refund made for {user.display_name}.")
                        # Set user's has_active_deposit to False
                        user_data.has_active_deposit = False
                        # Set user can_make_deposit to False
                        user_data.can_make_deposit = False
                except Exception as e:
                    await ctx.send(f"Failed to refund deposit: {e}")
            else:
                user_data.user_total_cancelled_withoutnotice += 1
                user_data.has_active_deposit = False
                await ctx.send(f"Event for {user.display_name} marked as cancelled without notice.")

        except asyncio.TimeoutError:
            await ctx.send("No response received. Event not marked as cancelled.")

        # Save the changes
        self.save()
        await ctx.send(f"Event for {user.display_name} marked as cancelled.")

    @pevent.command(name="ban")
    async def pevent_ban(self, ctx: commands.Context, user: discord.Member = None):
        """-Marks a Player as not allowed to Host events.-"""
        if user is None:
            await ctx.send("Please specify a user. Usage: `[p]pevent ban @user` or `[p]pevent ban user_id`")
            return

        if user.bot:
            await ctx.send("You cannot use this command on a bot.")
            return

        # Get user data from database
        guild_config = self.db.get_conf(ctx.guild)
        user_data = guild_config.get_user(user)
        # Update the user's ban status
        user_data.is_banned_from_host = True
        # Return to author that user is banned
        await ctx.send(f"{user.display_name} has been banned from hosting events.")
        # Save the changes
        self.save()
    
    @pevent.command(name="unban")
    async def pevent_unban(self, ctx: commands.Context, user: discord.Member = None):
        """-Marks a Player as allowed to Host events again.-"""
        if user is None:
            await ctx.send("Please specify a user. Usage: `[p]pevent unban @user` or `[p]pevent unban user_id`")
            return

        if user.bot:
            await ctx.send("You cannot use this command on a bot.")
            return  
                
        # Get user data from database
        guild_config = self.db.get_conf(ctx.guild)
        user_data = guild_config.get_user(user)
        # Update the user's ban status
        user_data.is_banned_from_host = False
        # Return to author that user is unbanned
        await ctx.send(f"{user.display_name} has been unbanned from hosting events.")
        # Save the changes
        self.save()

    @pevent.command(name="help")
    async def explain_pevent_process(self, ctx: commands.Context):
        """Command to explain the event process."""
        embed = discord.Embed(
            title="Event How-To:",
            description=("```\n"
                        "1 - Player and Staff member begin discussion about Event.\n"
                        "\n"
                        "2 - Player explains their event, has all prerequisite information, "
                        "and alotted discord-bank currency as deposit.\n"
                        "\n"
                        "3 - Admin uses `pevent allow (user)`. This allows the Player to make "
                        "a deposit, and adds a +1 to their setup tally.\n"
                        "\n"
                        "4 - Player uses `pdeposit` by itself, it will then deduct the deposit.\n"
                        "\n"
                        "5 - Staff Member makes the Announcement or Calendar post, gets any "
                        "needed in-game admin commands ready.\n"
                        "\n"
                        "6 - If Player-Host cancels then Staff uses `pevent cancel (user)` and "
                        "follows the prompts. If user gave ample notice(24hours+) then make "
                        "appropriate selection as well as refund. If not, say no and no refund.\n"
                        "\n"
                        "7 - Event date and time arrive, Player hosts their event. Once completed "
                        "Staff monitors chat and verifies at least 2 participants were involved.\n"
                        "\n"
                        "8 - Staff member then uses `pevent complete (user)` and then makes a selection of successful or not. "
                        "Player is refunded their deposit and tallies are made to the appropriate fields.\n"
                        "```"),
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
