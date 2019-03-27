from display import OLED
from font import *
from utilities import Indexable
from context import Context


class Console(object):
	def __init__(self, display: OLED):
		self.__display = display
		self.width = display.width // HALF_WIDTH_MIN_WIDTH
		self.height = display.height // HALF_WIDTH_MIN_HEIGHT
		self.__buffer = [[' ' for _ in range(self.height)] for _ in range(self.width)]
		self.reverse = Context()
		# 没有在上下文中, 则自动更新
		pass

	def __getitem__(self, item):
		def getter(key):
			return self.__buffer[item][key]

		def setter(key, value):
			cur_page = item
			cur_column = key * 6
			self.__buffer[item][key] = value
			with self.__display.session:
				print(self.reverse.nest_count)
				for char in value:
					for column in HALF_WIDTH_MIN[char]:
						if self.reverse.nest_count > 0:
							column ^= 0xff
						self.__display.draw_column(cur_page, cur_column, column)
						cur_column += 1
						if cur_column > self.width * HALF_WIDTH_MIN_WIDTH:
							cur_column = 0
							cur_page += 1

		return Indexable(getter, setter)
