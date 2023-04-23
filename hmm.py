class Base:
    def __init__(self):
        print("Base.__init__")
        self.x = "Base"
        super().__init__()
        self.y = "Base"

class Base2:
    def __init__(self):
        print("Base2.__init__")
        self.x = "Base2"
        super().__init__()
        self.y = "Base2"
    
class A1(Base):
    def __init__(self):
        print("A1.__init__")
        self.x = "A1"
        super().__init__()
        self.y = "A1"
class A2(Base2, A1):
    def __init__(self):
        print("A2.__init__")
        self.x = "A2"
        super().__init__()
        self.y = "A2"
class B1(Base):
    def __init__(self):
        print("B1.__init__")
        self.x = "B1"
        super().__init__()
        self.y = "B1"
class B2(Base2,B1):
    def __init__(self):
        print("B2.__init__")
        self.x = "B2"
        super().__init__()
        self.y = "B2"
class C(A2,B2):
    def __init__(self):
        print("C.__init__")
        self.x = "C"
        super().__init__()
        self.y = "C"



a = Base()
print(a.x)
print(a.y)
a = A2()
print(a.x)
print(a.y)
a = B2()
print(a.x)
print(a.y)
a = C()
print(a.x)
print(a.y)