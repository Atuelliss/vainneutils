from .choosereact import ChooseReact

async def setup(bot):
    await bot.add_cog(ChooseReact(bot))