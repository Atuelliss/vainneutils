from discord.ext import commands
from ..abc import CompositeMetaClass
from .admin import Admin
from .user import User


class Commands(Admin, User, metaclass=CompositeMetaClass):
    """Subclass all command classes"""
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("That user is no longer in this Server.")
            return
        if isinstance(error, commands.CommandNotFound):
            return
        # Let other errors propagate normally
        raise error
