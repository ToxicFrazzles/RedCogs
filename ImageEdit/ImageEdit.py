from redbot.core import commands
import re
from .utils import *
import aiohttp
import io
import discord


class ImageEdit(commands.Cog):
	"""Image editing cog"""
	aiohttp_session = aiohttp.ClientSession()

	async def extract_image_urls(self, message):
		message_urls = re.findall(r"https?://(?:[^/\s]{1,253})/(?:[\S]{1,1800})", message.content)
		attachment_urls = [attachment.url for attachment in message.attachments]
		image_urls = [url for url in message_urls if await url_is_image(self.aiohttp_session, url)]
		image_urls += [url for url in attachment_urls if await url_is_image(self.aiohttp_session, url)]
		return image_urls

	async def upload_image(self, channel, byte_buffer: io.BytesIO):
		await channel.send(file=discord.File(byte_buffer, 'result.jpg'))

	@commands.command()
	async def imageecho(self, ctx):
		"""Extract images from a message and send the URLs back"""
		image_urls = await self.extract_image_urls(ctx.message)
		await ctx.send(f"Found {len(image_urls)} images associated with your message:\n" + "\n".join(image_urls))

	@commands.command()
	async def imagevflip(self, ctx):
		"""Extract images from a message and send them back but flipped vertically"""
		image_urls = await self.extract_image_urls(ctx.message)
		images = []
		for url in image_urls:
			images.append(await image_from_url(self.aiohttp_session, url))
		async with ctx.typing():
			for image in images:
				image = await flip_image(image, 'v')
				byte_buf = await image_to_bytesio(image)
				await self.upload_image(ctx.channel, byte_buf)

	@commands.command()
	async def imagehflip(self, ctx):
		"""Extract images from a message and send them back but flipped horizontally"""
		image_urls = await self.extract_image_urls(ctx.message)
		images = []
		for url in image_urls:
			images.append(await image_from_url(self.aiohttp_session, url))
		async with ctx.typing():
			for image in images:
				image = await flip_image(image, 'h')
				byte_buf = await image_to_bytesio(image)
				await self.upload_image(ctx.channel, byte_buf)

	@commands.command()
	async def jpegify(self, ctx):
		"""Extract images from the message and \"deep fry\" them before sending them back"""
		image_urls = await self.extract_image_urls(ctx.message)
		images = []
		for url in image_urls:
			images.append(await image_from_url(self.aiohttp_session, url))
		async with ctx.typing():
			for image in images:
				image = await jpegify_image(image)
				byte_buf = await image_to_bytesio(image)
				await self.upload_image(ctx.channel, byte_buf)

	def cog_unload(self):
		self.aiohttp_session.close()
