from redbot.core import commands
import re
from .utils import *
from .caption import caption_image
import aiohttp
import io
import discord
import asyncio
from PIL import Image
import requests
import os


class ImageEdit(commands.Cog):
	"""Image editing cog"""
	def __init__(self, bot, *args, **kwargs):
		self.cog_folder = os.path.dirname(os.path.realpath(__file__))
		self.bot = bot
		if not os.path.isdir(os.path.join(self.cog_folder, "Fonts")):
			os.makedirs(os.path.join(self.cog_folder, "Fonts"))
		font_files = {
			"NotoColorEmoji.ttf": "https://github.com/googlefonts/noto-emoji/raw/master/fonts/NotoColorEmoji.ttf",
			"NotoSans-Regular.ttf": "https://github.com/googlefonts/noto-fonts/raw/master/hinted/NotoSans/NotoSans-Regular.ttf"
		}
		for filename, url in font_files.items():
			with requests.get(url) as r, open(os.path.join(self.cog_folder, "Fonts", filename), "wb") as f:
				f.write(r.content)

		super().__init__(*args, **kwargs)

	aiohttp_session = aiohttp.ClientSession()

	async def extract_image_urls(self, message):
		message_urls = re.findall(r"https?://(?:[^/\s]{1,253})/(?:[\S]{1,1800})", message.content)
		attachment_urls = [attachment.url for attachment in message.attachments]
		image_urls = [url for url in message_urls if await url_is_image(self.aiohttp_session, url)]
		image_urls += [url for url in attachment_urls if await url_is_image(self.aiohttp_session, url)]
		return image_urls

	async def images_from_message(self, message):
		image_urls = await self.extract_image_urls(message)
		return [await image_from_url(self.aiohttp_session, url) for url in image_urls]

	async def upload_image(self, channel, byte_buffer: io.BytesIO, extension=".jpg"):
		await channel.send(file=discord.File(io.BytesIO(byte_buffer.getvalue()), "result"+extension))

	@commands.command()
	async def imageecho(self, ctx):
		"""Extract images from a message and send the URLs back"""
		image_urls = await self.extract_image_urls(ctx.message)
		await ctx.send(f"Found {len(image_urls)} images associated with your message:\n" + "\n".join(image_urls))

	@commands.command()
	async def imagevflip(self, ctx):
		"""Extract images from a message and send them back but flipped vertically"""
		images = await self.images_from_message(ctx.message)
		async with ctx.typing():
			for image in images:
				image = await flip_image(image, 'v')
				byte_buf = await encode_img(image)
				await self.upload_image(ctx.channel, byte_buf)

	@commands.command()
	async def imagehflip(self, ctx):
		"""Extract images from a message and send them back but flipped horizontally"""
		images = await self.images_from_message(ctx.message)
		async with ctx.typing():
			for image in images:
				image = await flip_image(image, 'h')
				byte_buf = await encode_img(image)
				await self.upload_image(ctx.channel, byte_buf)

	@commands.command()
	async def jpegify(self, ctx):
		"""Extract images from the message and \"deep fry\" them before sending them back"""
		images = await self.images_from_message(ctx.message)
		async with ctx.typing():
			for image in images:
				image = await jpegify_image(image)
				print(image.getbands(), image.size)
				byte_buf = await encode_img(image)
				print("Bytes 2 electric boogaloo:", len(byte_buf.getvalue()))
				await self.upload_image(ctx.channel, byte_buf, ".png" if len(image.getbands()) == 4 else ".jpg")

	@commands.command()
	async def topcaption(self, ctx, *, message_content: str):
		image_urls = await self.extract_image_urls(ctx.message)
		caption = message_content
		for url in image_urls:
			caption = caption.replace(url, "")
		caption = caption.strip()
		images = [await image_from_url(self.aiohttp_session, url) for url in image_urls]
		async with ctx.typing():
			for image in images:
				image = await caption_image(image, caption, caption_type="top")
				byte_buf = await encode_img(image)
				await self.upload_image(ctx.channel, byte_buf)

	@commands.command()
	async def botcaption(self, ctx, *, message_content: str):
		image_urls = await self.extract_image_urls(ctx.message)
		caption = message_content
		for url in image_urls:
			caption = caption.replace(url, "")
		caption = caption.strip()
		images = [await image_from_url(self.aiohttp_session, url) for url in image_urls]
		async with ctx.typing():
			for image in images:
				image = await caption_image(image, caption, caption_type="bottom")
				byte_buf = await encode_img(image)
				await self.upload_image(ctx.channel, byte_buf)

	def cog_unload(self):
		loop = asyncio.get_running_loop()
		loop.create_task(self.aiohttp_session.close())
