import aiohttp
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
