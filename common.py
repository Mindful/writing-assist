from abc import ABC
English = 'English'
Japanese = 'Japanese'


class SlotPrinter:

    def __str__(self):
        return ''.join(['<', ', '.join(['{}={}'.format(attr_name, getattr(self, attr_name))
                                        for attr_name in self.__slots__]), '>'])

    def __repr__(self):
        return self.__str__()