from display import OLED
from font import *
from utilities import Indexable


class Console(object):
	def __init__(self, display):
		# 用字库把屏幕抽象成字符点阵
		# 整除, 右边的部分就不要了XD
		# 使用数组语法来访问字符
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
			self.__buffer[item][key] = value

		return Indexable(getter, setter)
