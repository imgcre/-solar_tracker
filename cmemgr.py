import syncpri
import _thread

class Mapper(object):
	def __init__(self, caller, func, *, nargs=None, event=None, forward_args=True):
		if event is None:
			event = syncpri.Event()
		self.__event = event
		self.__caller = caller
		self.__disposed = False
		wrapper = None
		if nargs is None:
			def var_param_func(*args, **kw):
				self.__args = args
				self.__kw = kw
				event.set()
			wrapper = var_param_func
		elif nargs == 1:
			# you can't create mp object when entered interrupt mode
			# including list object, so we need a special support for it
			self.__kw = {}
			self.__args = [None]
			def one_param_func(arg):
				if forward_args:
					self.__args[0] = arg
				event.set()
			wrapper = one_param_func
		def internal_thread():
			while True:
				event.wait()
				if self.__disposed:
					_thread.exit()
					return
				if forward_args:
					func(*self.__args, **self.__kw)
				else:
					func()
		caller(wrapper)
		_thread.start_new_thread(internal_thread, [])
	def dispose(self):
		self.__disposed = True
		self.__caller(None)
		self.__event.set()  # wakeup the thread and commit suicide
