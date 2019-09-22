def is_type(x):
	def func(t):
		return type(t) == x
	return func


def is_between(a, b):
	def func(t):
		return a <= t <= b
	return func


def is_pair_between(a, b):
	def func(t):
		if type(t) != tuple or len(t) != 2:
			return False
		return a <= t[0] <= t[1] <= b
	return func


def if_pair(a, b):
	def func(t):
		if type(t) != tuple or len(t) != 2:
			return False
		return a(t[0]) and b(t[1])
	return func


def is_in(*params):
	def func(t):
		return t in params
	return func


def toggle(func):
	def wrapper(*params, **kw):
		return not func(*params, **kw)
	return wrapper
