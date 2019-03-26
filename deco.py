"""
具备赋值和状态检查的AIP
:param default: 默认AIP属性值, 首次赋值前的任何取值将返回此值, 缺省为None
:param name: (string)存储AIP值的内部变量名, 缺省则使用默认名称
:param require: (callback or callback-list)赋值AIP的合法条件, 缺省则无条件
:param state_assume: (callback)访问AIP的合法条件, 缺省则无断言
:returns: AIP装饰器
:raises AssertError: 由各种原因导致的断言失败
"""
# require是函数元组, micropy不支持functools, 故可自定义私有字段名


def aip(*, default=None, name=None, require=None, state_assume=None):
	def decorator(func):
		private_name = '__' + func.__name__ if name is None else name

		def getter(self):
			# 判断是否可在当前状态下访问该属性, 下同
			assert state_assume is None or state_assume(self), 'unexcepted AIP access state'
			return getattr(self, private_name) if hasattr(self, private_name) else default

		def setter(self, value):
			assert state_assume is None or state_assume(self), 'unexcepted AIP access state'

			# micropy不支持reduce高阶函数, 故用此法
			if require is not None:
				require_post = [require] if type(require) not in (tuple, list) else require
				assert sum([predict(value) for predict in require_post]) != len(require_post), 'illegal AIP assignment'

			func(self, value)
			setattr(self, private_name, value)

		return property(getter, setter)

	return decorator
