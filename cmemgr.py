import pyb
import syncpri
import _thread


def map_to_thread(callback, *args):
	def func(f):
		def wrapper():
			f(*args)
		return Mapper(callback, wrapper, nargs=1, forward_args=False)
	return func


class Mapper(object):
	__default_event = syncpri.Event(mutex=syncpri.SpinMutex(restrict_owner=False))
	__internal_thread_running = False
	__mappers = []

	@classmethod
	def __internal_thread(cls):
		while True:
			syncpri.Event.wait_any(map(lambda m: m.__event, cls.__mappers))
			for mapper in cls.__mappers:
				if mapper.__raised:
					mapper.__raised = False
					if mapper.__disposed:
						cls.__mappers.remove(mapper)
						continue

					if mapper.__forward_args:
						mapper.__func(*mapper.__args, **mapper.__kw)
					else:
						mapper.__func()
			pyb.delay(1)  # the magic code :)

	def __init__(self, caller, func, *, interrpt_func=None, nargs=None, event=None, forward_args=True):
		if event is None:
			event = type(self).__default_event
		self.__event = event
		self.__caller = caller
		self.__disposed = False
		self.__raised = False
		self.__func = func
		self.__forward_args = forward_args
		wrapper = None

		if nargs is None:
			def var_param_func(*args, **kw):
				if interrpt_func is not None:
					interrpt_func()
				self.__args = args
				self.__kw = kw
				self.__raise_event()
			wrapper = var_param_func
		elif nargs == 1:
			# when entering interrupt mode, you cannot create the mp object
			# required by *args, so we must provide special support for that
			self.__kw = {}
			self.__args = [None]

			def one_param_func(arg):
				if interrpt_func is not None:
					interrpt_func()
				if forward_args:
					self.__args[0] = arg
				self.__raise_event()
			wrapper = one_param_func

		caller(wrapper)
		type(self).__mappers.append(self)
		if not type(self).__internal_thread_running:
			type(self).__internal_thread_running = True
			_thread.start_new_thread(type(self).__internal_thread, [])

	def __raise_event(self):
		self.__raised = True
		self.__event.set()

	def dispose(self):
		self.__disposed = True
		self.__caller(None)
		self.__raise_event()  # wakeup the thread and commit suicide
