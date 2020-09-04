import aiohttp
import cv2
import numpy as np
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
import os


async def url_is_image(session: aiohttp.ClientSession, url: str) -> bool:
	resp = await session.head(url)
	async with resp:
		status = resp.status
		reason = resp.reason
		content_type = resp.headers['content-type']
	if status == 405:
		# HEAD request not allowed
		return False
	return content_type.startswith("image/")


async def image_from_url(session: aiohttp.ClientSession, url: str) -> Image.Image:
	resp = await session.get(url)
	async with resp:
		status = resp.status
		reason = resp.reason
		content_type = resp.headers['content-type']
		content = await resp.read()
	byte_buf = BytesIO(content)
	return await decode_img(byte_buf)


async def flip_image(pil_img: Image.Image, direction='v') -> Image.Image:
	dir_param = Image.FLIP_TOP_BOTTOM if direction == 'v' else (Image.FLIP_LEFT_RIGHT if direction == 'h' else Image.ROTATE_180)
	return pil_img.transpose(dir_param)


async def jpegify_image(pil_img: Image.Image) -> Image.Image:
	bands = pil_img.getbands()
	if len(bands) == 4:
		alpha = pil_img.getchannel("A")
		triband = pil_img.convert(mode="RGB")
		byte_buf = await encode_jpg(triband, quality=5)
		triband = await decode_img(byte_buf)
		triband.putalpha(alpha)
		return triband
	byte_buf = await encode_jpg(pil_img, quality=5)
	return await decode_img(byte_buf)


async def encode_img(pil_img: Image.Image) -> BytesIO:
	byte_buf = BytesIO()
	bands = pil_img.getbands()
	if len(bands) == 4:
		im_format = "PNG"
	else:
		im_format = "JPEG"
	pil_img.save(byte_buf, format=im_format)
	return byte_buf


async def encode_jpg(pil_img: Image.Image, quality=95) -> BytesIO:
	byte_buf = BytesIO()
	pil_img.save(byte_buf, format="jpeg", quality=quality, optimize=True, progressive=True)
	return byte_buf


async def decode_img(byte_buf: BytesIO) -> Image.Image:
	pil_img = Image.open(byte_buf)
	return pil_img


async def caption_image(pil_img: Image.Image, caption: str, caption_type="top") -> Image.Image:
	# Set up some values for easy usage
	main_font_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Fonts", "NotoSans-Regular.ttf")
	emoji_font_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Fonts", "NotoColorEmoji.ttf")
	image_width, image_height = pil_img.size

	# "Calculate" the ideal text size to fit the width of the image
	main_font = ImageFont.truetype(main_font_file, size=109)
	emoji_font = ImageFont.truetype(emoji_font_file, size=109)		# NotoEmojiColor only supports point size 109

	caption_lines = [line.strip() for line in caption.split("\n")]
	caption_width = 0
	caption_height = 0
	for caption_line in caption_lines:
		width, height = main_font.getsize(caption_line)
		caption_width = max(caption_width, width)
		caption_height += height
	caption_image = Image.new(pil_img.mode, (caption_width, caption_height))
	draw = ImageDraw.Draw(caption_image)
	line_height = 0
	for caption_line in caption_lines:
		width, height = main_font.getsize(caption_line)
		draw.text(((caption_width-width)/2, line_height), caption_line, font=main_font)
		line_height += height
	caption_height = int((caption_height/caption_width)*image_width)
	caption_image = caption_image.resize((image_width, caption_height))

	out_img = Image.new(pil_img.mode, (image_width, image_height+caption_height))
	if caption_type == "top":
		out_img.paste(caption_image, (0, 0))
		out_img.paste(pil_img, (0, out_img.size[1]-image_height))
	else:
		out_img.paste(pil_img)
		out_img.paste(caption_image, (0, image_height))
	return out_img
