class Parent:
    def get_limit(self):
        print(self.__class__.__name__)
        if self.__class__ == ChildA:
            return 10  # ChildA 的限制
        elif self.__class__ == ChildB:
            return 20  # ChildB 的限制
        else:
            return 5   # 默认限制

class ChildA(Parent):
    pass

class ChildB(Parent):
    pass

a = ChildA()
b = ChildB()

print(a.get_limit())  # 输出 10
print(b.get_limit())  # 输出 20
