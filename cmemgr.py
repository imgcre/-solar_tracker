import pyb
import syncpri
import _thread

# TODO: a mapper use only one thread and one event but provide multi mapping service
# alloc user to use the same event object
class Mapper(object):
	default_event = syncpri.Event(mutex=syncpri.SpinMutex(restrict_owner=False))

	def __init__(self, caller, func, *, interrpt_func=None, nargs=None, event=None, forward_args=True):
		if event is None:
			event = default_event
		self.__event = event
		self.__caller = caller
		self.__disposed = False
		wrapper = None
		if nargs is None:
			def var_param_func(*args, **kw):
				if interrpt_func is not None:
					interrpt_func()
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
				if interrpt_func is not None:
					interrpt_func()
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
				pyb.delay(1)  # the magic code :)
		caller(wrapper)
		_thread.start_new_thread(internal_thread, [])

	def dispose(self):
		self.__disposed = True
		self.__caller(None)
		self.__event.set()  # wakeup the thread and commit suicide
