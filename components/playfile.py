class Test(object):

    def __init__(self, test=20):
        self.test = test

    @property
    def dependent(self):
        return self.test * 2.0


if __name__ == '__main__':
    obj = Test(10)
    print(obj.dependent)
    obj.test = 20
    print(obj.dependent)
