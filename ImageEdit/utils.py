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
	return BytesIO(cv2.imencode(".jpg", np_img)[1].tobytes())


async def flip_image(np_img, direction='v'):
	dir_param = 0 if direction == 'v' else (1 if direction == 'h' else -1)
	result = cv2.flip(np_img, dir_param)
	return result
