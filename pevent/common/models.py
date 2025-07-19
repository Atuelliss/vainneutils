import discord

from . import Base


class User(Base):
    # Player-Event Data
    user_total_setup: int = 0
    user_total_complete: int = 0
    user_total_success: int = 0
    user_total_cancelled: int = 0
    user_total_cancelled_withnotice: int = 0
    user_total_cancelled_withoutnotice: int = 0
    can_make_deposit: bool = False
    has_active_deposit: bool = False
    is_banned_from_host: bool = False
    
class GuildSettings(Base):
    users: dict[int, User] = {}

    def get_user(self, user: discord.User | int) -> User:
        uid = user if isinstance(user, int) else user.id
        return self.users.setdefault(uid, User())


class DB(Base):
    configs: dict[int, GuildSettings] = {}
    deposit_value: int = 2500

    def get_conf(self, guild: discord.Guild | int) -> GuildSettings:
        gid = guild if isinstance(guild, int) else guild.id
        return self.configs.setdefault(gid, GuildSettings())
