from driver import SSD1306


class OLED(object):

	def __init__(self, prot):
		self.driver = SSD1306(prot)
		
		# buffer[页][列]
		self.__buffer = [[0 for _ in range(SSD1306.COLUMN_NUM)] for _ in range(SSD1306.PAGE_NUM)]
		self.__flag = [[True for _ in range(SSD1306.COLUMN_NUM)] for _ in range(SSD1306.PAGE_NUM)]
	
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
		self.submit()
	
	def clear(self):
		for y in range(64):
			for x in range(128):
				self.draw_point(x, y, False)
	
	# color: True for white, False for black
	def draw_point(self, x, y, color=True, *,auto_submit=True):
		page = y // 8
		column = x
		bit_pos = y % 8
		
		if color:
			if self.__buffer[page][column] & (1 << bit_pos) == 0:
				self.__buffer[page][column] |= 1 << bit_pos
				self.__flag[page][column] = True
		else:
			if self.__buffer[page][column] & (1 << bit_pos) != 0:
				self.__buffer[page][column] &= ~(1 << bit_pos)
				self.__flag[page][column] = True

		if auto_submit:
			self.submit()
	
	def submit(self):
		for page in range(SSD1306.PAGE_NUM):
			for column in range(SSD1306.COLUMN_NUM):
				if self.__flag[page][column]:
					self.__flag[page][column] = False
					self.driver.address_page = page
					self.driver.address_column = column
					self.driver.ram = self.__buffer[page][column]

