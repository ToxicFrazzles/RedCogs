from redbot.core import commands
import re
from .utils import *


class ImageEdit(commands.Cog):
	"""Image editing cog"""

	@commands.command()
	async def imageecho(self, ctx):
		"""Extract images from a message and send the URLs back"""
		message_urls = re.findall(r"https?://(?:[^/\s]{1,253})/(?:[\S]{1,1800})", ctx.message.content)
		attachment_urls = [attachment.url for attachment in ctx.message.attachments]
		image_urls = [url for url in message_urls if url_is_image(url)]
		image_urls += [url for url in attachment_urls if url_is_image(url)]
		await ctx.send(f"Found {len(image_urls)} images associated with your message:\n" + "\n".join(image_urls))
