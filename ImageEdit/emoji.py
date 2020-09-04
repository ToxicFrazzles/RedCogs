class EmojiRange:
	def __init__(self, start, end):
		self.start = ord(start)
		self.end = ord(end)

	def char_in_range(self, character):
		return self.start <= ord(character) <= self.end


lone_emojis = []

emoji_ranges = []


if __name__ == "__main__":
	emoji_data = {
		"ranges": [],
		"lone_points": []
	}
	import requests
	url = 'https://unicode.org/Public/emoji/13.0/emoji-sequences.txt'
	with requests.get(url, stream=True) as r:
		r.raise_for_status()
		for line in r.text.split("\n"):
			if line.startswith("#"):
				continue
			if line.strip() == "":
				continue
			code_points = line.split(";", 1)[0].strip().split("..")
			if len(code_points) > 1:
				emoji_data['ranges'].append({"start": int(code_points[0], 16), "end": int(code_points[1], 16)})
			else:
				emoji_data['lone_points'].append(code_points[0])
	print(emoji_data)

