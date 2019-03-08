import pyb
import _thread


class Event(object):
	def __init__(self, initval=False, *, auto_reset=True, mutex=None):
		self.__val = initval
		self.__auto_reset = auto_reset
		if mutex is None:
			mutex = _thread.allocate_lock()
		self.__mutex = mutex

	@staticmethod
	def wait_any(events):
		# to avoid iterator
		events = list(events)
		loop_cond = True
		while loop_cond:
			for event in events:
				if event.__val:
					event.wait()
					loop_cond = False
					break

	def wait(self):
		# sync current state with __val
		# assume that the reason is not effect
		if not self.__val:
			self.reset()
			# to make sure this thread will be blocked, not the other
			while not self.__mutex.locked():
				pass
			self.__mutex.acquire()
			self.__mutex.release() # FIXED
		if self.__auto_reset:
			self.reset()

	def __enter__(self):
		self.wait()

	def __exit__(self, *args):
		pass

	def set(self):
		self.__val = True
		if self.__mutex.locked():
			self.__mutex.release()

	def reset(self):
		self.__val = False
		if not self.__mutex.locked():
			# avoid the situation that the same thread acquire __lock twice
			_thread.start_new_thread(self.__mutex.acquire, [])

	@property
	def value(self):
		return self.__val

class SpinMutex(object):
	def __init__(self, *, restrict_owner=True, using_critical_section=False):
		self.__val = False
		self.__restrict_owner = restrict_owner
		self.__owner = -1
		self.__using_critical_section = using_critical_section

	def acquire(self):
		thread_id = _thread.get_ident()
		if self.__val:
			if self.__owner == thread_id:
				raise RuntimeError('dead lock')
			while self.__val:
				pass
		irq_state = None
		if self.__using_critical_section:
			irq_state = pyb.disable_irq()
		self.__val = True
		self.__owner = thread_id
		if self.__using_critical_section:
			pyb.enable_irq(irq_state)

	def release(self):
		if not self.__val:
			raise RuntimeError('mutex didnt aquired yet')
		thread_id = _thread.get_ident()
		if self.__restrict_owner and self.__owner != thread_id:
			raise RuntimeError('mutex been released by other thread')
		irq_state = None
		if self.__using_critical_section:
			irq_state = pyb.disable_irq()
		self.__owner = -1
		self.__val = False
		if self.__using_critical_section:
			pyb.enable_irq(irq_state)

	def locked(self):
		return self.__val

	def __enter__(self):
		self.acquire()

	def __exit__(self, *args):
		self.release()
