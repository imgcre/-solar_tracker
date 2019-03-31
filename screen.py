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
		self.padding = Context()  # padding(size, *, char=' ')

	def __getitem__(self, item):
		def getter(key):
			return self.__buffer[item][key]

		def setter(key, value, flag=False):
			if not flag:
				# 对context进行处理
				if self.padding.nest_count > 0:
					padding_char = ' '
					try:
						padding_char = self.padding.cur_args[1]['char']
					except Exception:
						pass
					value = padding_char * self.padding.cur_args[0][0] + str(value)
				setter(key, value, flag=True)
			else:
				cur_page = item
				cur_column = key * 6
				self.__buffer[item][key] = value
				with self.__display.session:
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

	@property
	def session(self):
		return self.__display.session
