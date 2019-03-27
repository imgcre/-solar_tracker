from driver import SSD1306
from utilities import Indexable
from pyb import delay

class OLED(object):

	def __init__(self, prot):
		self.driver = SSD1306(prot)
		self.width = SSD1306.COLUMN_NUM
		self.height = SSD1306.PAGE_NUM * 8

		# buffer[页][列]
		self.__buffer = [[0 for _ in range(SSD1306.COLUMN_NUM)] for _ in range(SSD1306.PAGE_NUM)]

		self.__flag_modified = [[False for _ in range(SSD1306.COLUMN_NUM)] for _ in range(SSD1306.PAGE_NUM)]
		self.__flag_page = [-1 for _ in range(SSD1306.COLUMN_NUM * SSD1306.PAGE_NUM)]
		self.__flag_column = [-1 for _ in range(SSD1306.COLUMN_NUM * SSD1306.PAGE_NUM)]
		self.__fpos = 0
	
	def init(self):
		self.driver.display_on = False  # 默认
		self.driver.address_column = 0  # 默认
		self.driver.hardware_start_line = 0  # 默认
		self.driver.address_page = 0  # 默认
		self.driver.contrast = 0xff  # 可默认
		self.driver.hardware_segment_remap = True
		self.driver.display_inverse = False  # 默认
		self.driver.hardware_multiplex_ratio = 64  # 默认
		self.driver.hardware_com_scan_dir = SSD1306.COM_SCAN_DIR_REMAPPED
		self.driver.hardware_vertical_offset = 0  # 默认
		self.driver.timing_clockdiv_and_oscfreq = SSD1306.CLOCKDIV_AND_OSCFREQ_MAX_FPS
		self.driver.timing_precharge_period = (1, 15)
		self.driver.hardware_com_pin_config = (SSD1306.HARDWARE_COM_PIN_MODE_ALTERNATIVE, False)  # 默认
		self.driver.timing_vcomh_deselect_level = SSD1306.TIMING_VCOMH_DESELECT_LEVEL_83_PERCENT_VCC
		self.driver.charge_pump_enable = True
		self.driver.display_on = True
	
	def clear(self, color=False):
		for y in range(64):
			for x in range(128):
				self.draw_point(x, y, color, auto_submit=False, force_refresh=True)
		self.submit()
	
	# color: True for white, False for black
	def draw_point(self, x, y, color=True, *, auto_submit=True, force_refresh=False):
		page = y // 8
		column = x
		bit_pos = y % 8
		changed = False
		if color:
			if self.__buffer[page][column] & (1 << bit_pos) == 0:
				self.__buffer[page][column] |= 1 << bit_pos
				changed = True
		else:
			if self.__buffer[page][column] & (1 << bit_pos) != 0:
				self.__buffer[page][column] &= ~(1 << bit_pos)
				changed = True
		if (force_refresh or changed) and not self.__flag_modified[page][column]:
			self.__flag_modified[page][column] = True
			self.__flag_page[self.__fpos] = page
			self.__flag_column[self.__fpos] = column
			self.__fpos += 1

		if auto_submit:
			self.submit()

	def __getitem__(self, item):
		def getter(key):
			page = key // 8
			column = item
			bit_pos = key % 8
			return bool(self.__buffer[page][column] & (1 << bit_pos))

		def setter(key, value):
			self.draw_point(item, key, value)

		return Indexable(getter, setter)

	def submit(self):
		prev_page = None
		prev_column = None
		for i in range(self.__fpos):
			page = self.__flag_page[i]
			column = self.__flag_column[i]
			self.__flag_modified[page][column] = False
			assign_addr = True
			if prev_page is not None and prev_column is not None:
				if prev_page == page and prev_column + 1 == column:
					assign_addr = False
			if assign_addr:
				self.driver.address_page = page
				self.driver.address_column = column
			prev_page, prev_column = page, column
			self.driver.ram = self.__buffer[page][column]
		self.__fpos = 0
		pass
