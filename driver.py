from pyb import I2C
from deco import aip
from func import *

class SSD1306(object):
	PAGE_NUM = 8
	COLUMN_NUM = 128
	__DEVICE_ADDR = 60
	
	def __init__(self, prot):
		if type(prot) not in (I2C,):
			raise TypeError
		self.__prot = prot
	
	def __write(self, **info):
		assert len(info) == 1
		
		transmit_type, data = info.popitem()
		assert type(data) in (list, int, tuple)
		assert transmit_type in ('cmd', 'data')
		
		if type(data) == int:
			data = [data]
		
		data_cmd_selector = 0x00 if transmit_type == 'cmd' else 0x40
		
		for item in data:
			assert 0 <= item <= 255
			self.__prot.send(b'%c%c' % (data_cmd_selector, item), addr=SSD1306.__DEVICE_ADDR)
			
	def write(self, *data_arg):
		self.__write(data=data_arg)
		if self.address_mode == SSD1306.ADDRESS_MODE_PAGE:
			self.__address_column += 1
			self.__address_column %= 128
		elif self.address_mode == SSD1306.ADDRESS_MODE_HORIZONTAL:
			pass  # TODO
		elif self.address_mode == SSD1306.ADDRESS_MODE_VERTICAL:
			pass  # TODO
			
	@property
	def ram(self):
		pass  # TODO
		
	@ram.setter
	def ram(self, value):
		self.write(value)
	
	def oled_attr(**kw):
		def decorator(func):
			private_name = '__' + func.__name__

			def wrapper(self, value):
				# 如果值相同, 就不调用
				if not hasattr(self, private_name) or getattr(self, private_name) != value:
					self.__write(cmd=func(self, value))
				
			return aip(**kw, name=private_name)(wrapper)
		return decorator
	
	@oled_attr(default=0x7F, require=is_between(0, 255))
	def contrast(self, value): return 0x81, value
	
	@oled_attr(default=False, require=is_type(bool))
	def entire_display_on(self, value): return 0xa4 | value
		
	@oled_attr(default=False, require=is_type(bool))
	def display_inverse(self, value): return 0xa6 | value
		
	@oled_attr(default=False, require=is_type(bool))
	def display_on(self, value): return 0xae | value
		
	SCROLL_HORIZONTAL_DIR_RIGHT = 0
	SCROLL_HORIZONTAL_DIR_LEFT = 1
	SCROLL_INTERVAL_5_FRAMES = 0
	SCROLL_INTERVAL_64_FRAMES = 1
	SCROLL_INTERVAL_128_FRAMES = 2
	SCROLL_INTERVAL_256_FRAMES = 3
	SCROLL_INTERVAL_3_FRAMES = 4
	SCROLL_INTERVAL_4_FRAMES = 5
	SCROLL_INTERVAL_25_FRAMES = 6
	SCROLL_INTERVAL_2_FRAMES = 7

	def scroll_horizontal_setup(self, dir, start_page, interval, end_page):
		assert dir in (SSD1306.SCROLL_HORIZONTAL_DIR_RIGHT, SSD1306.SCROLL_HORIZONTAL_DIR_LEFT)
		assert 0 <= start_page <= 7
		assert start_page <= end_page <= 7
		assert interval in (
			SSD1306.SCROLL_INTERVAL_5_FRAMES, 
			SSD1306.SCROLL_INTERVAL_64_FRAMES,
			SSD1306.SCROLL_INTERVAL_128_FRAMES,
			SSD1306.SCROLL_INTERVAL_256_FRAMES,
			SSD1306.SCROLL_INTERVAL_3_FRAMES,
			SSD1306.SCROLL_INTERVAL_4_FRAMES,
			SSD1306.SCROLL_INTERVAL_25_FRAMES,
			SSD1306.SCROLL_INTERVAL_2_FRAMES,
		)
		self.__write(cmd=[0x26 | dir, 0, start_page, interval, end_page, 0, 0xff])
	
	# 水平滚动每次一列
	def scroll_vertical_horizontal_setup(self, horizontal_dir, start_page, interval, end_page, vertical_offset):
		assert horizontal_dir in (SSD1306.SCROLL_HORIZONTAL_DIR_RIGHT, SSD1306.SCROLL_HORIZONTAL_DIR_LEFT)
		assert 0 <= start_page <= end_page <= 7
		assert interval in (
			SSD1306.SCROLL_INTERVAL_5_FRAMES, 
			SSD1306.SCROLL_INTERVAL_64_FRAMES,
			SSD1306.SCROLL_INTERVAL_128_FRAMES,
			SSD1306.SCROLL_INTERVAL_256_FRAMES,
			SSD1306.SCROLL_INTERVAL_3_FRAMES,
			SSD1306.SCROLL_INTERVAL_4_FRAMES,
			SSD1306.SCROLL_INTERVAL_25_FRAMES,
			SSD1306.SCROLL_INTERVAL_2_FRAMES,
		)
		assert 1 <= vertical_offset <= 63
		self.__write(cmd=[0x28 | (dir << 1) | (~dir & 1), 0, start_page, interval, end_page, vertical_offset])
		
	def scroll_deactivate(self):
		self.__write(cmd=[0x2e])
		
	# 需先调用scroll_**_setup, 多次调用scroll_**_setup将保留最后的配置
	def scroll_activate(self):
		self.__write(cmd=[0x2f])
		
	def scroll_set_vertical_area(self, start_page, end_page):
		assert 0 <= start_page <= end_page <= 7
		self.__write(cmd=[0xa3, start_page, end_page - start_page + 1])
		
	ADDRESS_MODE_HORIZONTAL = 0
	ADDRESS_MODE_VERTICAL = 1
	ADDRESS_MODE_PAGE = 2

	@oled_attr(default=2, require=is_in(0, 1, 2))
	def address_mode(self, value): return 0x20, value

	def __is_paged_state(self): return self.address_mode == SSD1306.ADDRESS_MODE_PAGE
	
	@oled_attr(default=0, require=is_between(0, 255), state_assume=__is_paged_state)
	def address_column(self, value): return value & 0x0f, 0x10 | (value >> 4)
	
	@oled_attr(default=0, require=is_between(0, 7), state_assume=__is_paged_state)
	def address_page(self, value): return 0xb0 | value
	
	@oled_attr(default=(0,127), require=is_pair_between(0, 127), state_assume=toggle(__is_paged_state))
	def address_column_range(self, value): return 0x21, value[0], value[1]
		
	@oled_attr(default=(0,7), require=is_pair_between(0, 7), state_assume=toggle(__is_paged_state))
	def address_page_range(self, value): return 0x22, value[0], value[1]
		
	@oled_attr(default=0, require=is_between(0, 63))
	def hardware_start_line(self, value): return 0x40 | value
		
	# 大概是水平镜像的意思
	@oled_attr(default=False, require=is_type(bool))
	def hardware_segment_remap(self, value): return 0xa0 | value
		
	@oled_attr(default=64, require=is_between(15, 64))
	def hardware_multiplex_ratio(self, value): return 0xa8, value - 1
		
	COM_SCAN_DIR_NORMAL = 0
	COM_SCAN_DIR_REMAPPED = 1

	# 大概是垂直镜像的意思
	@oled_attr(default=0, require=is_in(0, 1))
	def hardware_com_scan_dir(self, value): return 0xc0 | (value << 3)

	@oled_attr(default=0, require=is_between(0, 63))
	def hardware_vertical_offset(self, value): return 0xd3, value
		
	HARDWARE_COM_PIN_MODE_SEQUENTIAL = 0
	HARDWARE_COM_PIN_MODE_ALTERNATIVE = 1

	@oled_attr(default=(1, False), require=if_pair(is_in(0, 1), is_type(bool)))
	def hardware_com_pin_config(self, value): return 0xda, 0x02 | (value[1] << 5) | value[0] << 4
	
	# ### TODO
	CLOCKDIV_AND_OSCFREQ_MAX_FPS = (1, 15)
	CLOCKDIV_AND_OSCFREQ_MIN_FPS = (16, 0)

	@oled_attr(default=(1, 8), require=if_pair(is_between(1, 16),is_between(0, 15)))
	def timing_clockdiv_and_oscfreq(self, value): return 0xd5, ((value[0] - 1) | value[1] << 4)
	
	# (phase1_period, phase2_period)
	@oled_attr(default=(2, 2), require=if_pair(is_between(1, 15),is_between(2, 15)))
	def timing_precharge_period(self, value): return 0xd9, value[0] | (value[1] << 4)
	
	# ###TODO
	TIMING_VCOMH_DESELECT_LEVEL_65_PERCENT_VCC = 0
	TIMING_VCOMH_DESELECT_LEVEL_77_PERCENT_VCC = 2
	TIMING_VCOMH_DESELECT_LEVEL_83_PERCENT_VCC = 3

	@oled_attr(default=2, require=is_in(0, 2, 3))
	def timing_vcomh_deselect_level(self, value): return 0xdb, value << 4
		
	def timing_nop(self):
		self.__write(cmd=[0xe3])
		
	@oled_attr(default=False, require=is_type(bool))
	def charge_pump_enable(self, value): return 0x8d, 0x10 | value << 2
