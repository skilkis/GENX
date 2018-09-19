class Unassigned(object):

    __slots__ = ['__name__', 'value']

    def __init__(self, name):
        self.__name__ = name
        self.value = None

    def __get__(self, instance, owner):
        raise self.error_msg()

    def __repr__(self):
        raise self.error_msg()

    def __add__(self, other):
        raise self.error_msg()

    def __sub__(self, other):
        raise self.error_msg()

    def __div__(self, other):
        raise self.error_msg()

    def __mul__(self, other):
        raise self.error_msg()

    def __eq__(self, other):
        raise self.error_msg()

    def __pow__(self, other):
        return self.error_msg()

    def __float__(self):
        return self.error_msg()

    def __int__(self):
        return self.error_msg()

    def __abs__(self):
        return self.error_msg()

    def error_msg(self):
        msg = "A state variable '{}' required to compute the requested flow " \
              "parameters was not provided.".format(self.__name__)
        raise AttributeError(msg)