# require是函数元组, micropy不支持functools, 故可自定义私有字段名
def aip(*, default=None, name=None, require=None, state_assume=None):
	def decorator(func):
		private_name = '__' + func.__name__ if name is None else name

		def getter(self):
			# 判断是否可在当前状态下访问该属性, 下同
			assert state_assume is None or state_assume(self), 'unexpected AIP access state'
			return getattr(self, private_name) if hasattr(self, private_name) else default

		def setter(self, value):
			assert state_assume is None or state_assume(self), 'unexpected AIP access state'

			if require is not None:
				require_post = [require] if type(require) not in (tuple, list) else require
				assert all([predict(value) for predict in require_post]), 'illegal AIP assignment'

			func(self, value)
			setattr(self, private_name, value)

		return property(getter, setter)

	return decorator
