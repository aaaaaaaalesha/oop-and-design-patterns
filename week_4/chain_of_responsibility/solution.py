from enum import Enum


class SomeObject:
    def __init__(self):
        self.integer_field = 0
        self.float_field = 0.0
        self.string_field = ""


class Kinds(Enum):
    INT = 0
    FLOAT = 1
    STR = 2


class EventGet:
    """Ex.: EventGet(float)"""

    def __init__(self, type_):
        if type_ is int:
            self.kind = Kinds.INT
        elif type_ is float:
            self.kind = Kinds.FLOAT
        elif type_ is str:
            self.kind = Kinds.STR

        self.value = None


class EventSet:
    """Ex.: EventSet('new text')"""

    def __init__(self, value):
        if isinstance(value, int):
            self.kind = Kinds.INT
        elif isinstance(value, float):
            self.kind = Kinds.FLOAT
        elif isinstance(value, str):
            self.kind = Kinds.STR

        self.value = value


class NullHandler:

    def __init__(self, successor=None):
        self.__successor = successor

    def handle(self, object_, event):
        if self.__successor is not None:
            return self.__successor.handle(object_, event)


class IntHandler(NullHandler):
    def handle(self, object_, event):
        if event.kind == Kinds.INT:
            if event.value is None:
                return object_.integer_field
            else:
                object_.integer_field = event.value
        else:
            return super().handle(object_, event)


class FloatHandler(NullHandler):
    def handle(self, object_, event):
        if event.kind == Kinds.FLOAT:
            if event.value is None:
                return object_.float_field
            else:
                object_.float_field = event.value
        else:
            return super().handle(object_, event)


class StrHandler(NullHandler):
    def handle(self, object_, event):
        if event.kind == Kinds.STR:
            if event.value is None:
                return object_.string_field
            else:
                object_.string_field = event.value
        else:
            return super().handle(object_, event)
          
          
if __name__ == '__main__':
    obj = SomeObject()
    obj.integer_field = 42
    obj.float_field = 3.14
    obj.string_field = "some text"
    chain = IntHandler(FloatHandler(StrHandler(NullHandler)))

    print(chain.handle(obj, EventGet(int)))

    print(chain.handle(obj, EventGet(str)))

    chain.handle(obj, EventSet(100))
    print(chain.handle(obj, EventGet(int)))

    chain.handle(obj, EventSet(0.5))
    print(chain.handle(obj, EventGet(float)))

    chain.handle(obj, EventSet('new text'))
    print(chain.handle(obj, EventGet(str)))
