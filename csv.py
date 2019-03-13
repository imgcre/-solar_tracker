

# TODO: 从Wrapper继承
class CSV:
    def __init__(self, file_name):
        self.__file = open(file_name, 'rt')

    # 获取当前记录, 指针移到下一条记录
    def cur_record(self, *, move_to_next=True):
        id = self.__seek_to_start_of_record()
        content = self.__file.readline()
        if not move_to_next:
            self.__file.seek(id)
        return content[:-1].split(',') if content else content

    # 指针指向之前的记录
    def prev_record(self):
        if self.__seek_to_start_of_record() == 0:
            return ''
        self.__file.seek(-1, 1)
        return self.cur_record(move_to_next=False)

    def get_cur_record_id(self):
        return self.__seek_to_start_of_record()

    def set_cur_record(self, record_id):
        self.__file.seek(record_id)
        return self.__seek_to_start_of_record()

    # 请保证CSV记录满足某种有序性
    # gt: 大于目标, 则返回True
    def binary_search(self, gt):
        # 检查是否落在同一条记录
        left = 0
        right = self.__file.seek(0, 2)

        while True:
            backup = self.get_cur_record_id()
            left = self.set_cur_record(left)
            right = self.set_cur_record(right)
            self.set_cur_record(backup)
            middle = self.set_cur_record(left + (right - left) // 2)
            if left >= right or middle == left or middle == right:
                break

            if gt(self.cur_record(move_to_next=False)):
                right = middle
            else:
                left = middle
        # 这边都是返回值等于或小于目标值的情况
        return self.cur_record(move_to_next=False)

    # record
    def __seek_to_start_of_record(self):
        while True:
            if self.__file.tell() == 0:  # 到达文件开头, 行首已定位
                break
            self.__file.seek(-1, 1)
            c = self.__file.read(1)
            if c == '\n':
                break
            # 没有找到, 继续向前查找
            self.__file.seek(-1, 1)
        return self.__file.tell()


