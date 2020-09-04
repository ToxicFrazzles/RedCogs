from PIL import Image, ImageFont, ImageDraw
import os

main_font_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Fonts", "NotoSans-Regular.ttf")
emoji_font_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Fonts", "NotoColorEmoji.ttf")

main_font = ImageFont.truetype(main_font_file, size=109)
emoji_font = ImageFont.truetype(emoji_font_file, size=109)


async def text_image(text: str, mode):
	caption_lines = [line.strip() for line in text.split("\n")]
	caption_width = 0
	caption_height = 0
	for caption_line in caption_lines:
		width, height = main_font.getsize(caption_line)
		caption_width = max(caption_width, width)
		caption_height += height
	caption_width = int(1.2*caption_width)
	caption_img = Image.new(mode, (caption_width, caption_height))
	draw = ImageDraw.Draw(caption_img)
	line_height = 0
	for caption_line in caption_lines:
		width, height = main_font.getsize(caption_line)
		draw.text(((caption_width-width)/2, line_height), caption_line, font=main_font, fill="#FFFFFF", stroke_fill="#000000", stroke_width=5)
		line_height += height
	return caption_img


async def caption_image(pil_img: Image.Image, caption: str, caption_type="top") -> Image.Image:
	# Set up some values for easy usage
	image_width, image_height = pil_img.size

	caption_img = await text_image(caption, pil_img.mode)
	caption_height = int((caption_img.size[1]/caption_img.size[0])*image_width)
	caption_img = caption_img.resize((image_width, caption_height))

	out_img = Image.new(pil_img.mode, (image_width, image_height+caption_height))
	if caption_type == "top":
		out_img.paste(caption_img, (0, 0))
		out_img.paste(pil_img, (0, out_img.size[1]-image_height))
	else:
		out_img.paste(pil_img)
		out_img.paste(caption_img, (0, image_height))
	return out_img
