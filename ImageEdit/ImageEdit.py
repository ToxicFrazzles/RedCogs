from redbot.core import commands


class ImageEdit(commands.Cog):
	"""Image editing cog"""

	@commands.command()
	async def imageecho(self, ctx):
		"""Extract images from a message and send the URLs back"""
		await ctx.send("Test")
