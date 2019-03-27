from display import OLED
from font import *
from utilities import Indexable


class Console(object):
	def __init__(self, display: OLED):
		self.__display = display
		self.width = display.width // HALF_WIDTH_MIN_WIDTH
		self.height = display.height // HALF_WIDTH_MIN_HEIGHT
		self.__buffer = [[' ' for _ in range(self.height)] for _ in range(self.width)]
		# 没有在上下文中, 则自动更新
		pass

	def __getitem__(self, item):
		def getter(key):
			return self.__buffer[item][key]

		def setter(key, value):
			cur_page = item
			cur_column = value * 6
			self.__buffer[item][key] = value
			with self.__display.session:
				for char in value:
					for column in HALF_WIDTH_MIN[char]:
						print(cur_page, cur_column)
						self.__display.draw_column(cur_page, cur_column, column)
						cur_column += 1
						if cur_column > self.width:
							cur_column = 0
							cur_page += 1

		return Indexable(getter, setter)
