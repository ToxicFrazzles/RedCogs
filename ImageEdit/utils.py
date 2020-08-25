import aiohttp
import cv2
import numpy as np
from io import BytesIO


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


async def image_from_url(session: aiohttp.ClientSession, url: str):
	resp = await session.get(url)
	async with resp:
		status = resp.status
		reason = resp.reason
		content_type = resp.headers['content-type']
		content = await resp.read()
	np_arr = np.frombuffer(content, dtype=np.uint8)
	np_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
	return np_img


async def image_to_bytesio(np_img):
	return BytesIO(await encode_jpg(np_img))


async def flip_image(np_img, direction='v'):
	dir_param = 0 if direction == 'v' else (1 if direction == 'h' else -1)
	result = cv2.flip(np_img, dir_param)
	return result


async def jpegify_image(np_img):
	byte_buf = await encode_jpg(np_img, quality=5)
	return await decode_img(byte_buf)


async def encode_jpg(np_img, quality=95):
	params = [cv2.IMWRITE_JPEG_QUALITY, quality]
	return cv2.imencode(".jpg", np_img, params=params)[1].tobytes()


async def decode_img(byte_buf):
	np_arr = np.frombuffer(byte_buf, dtype=np.uint8)
	return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
