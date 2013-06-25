import llvm
import numpy
import ctypes

import codes

#------------------------------------------------------------------------
# Exceptions
#------------------------------------------------------------------------

class NoLlvmMapping(Exception):
    pass
class NoCtypeMapping(Exception):
    pass
class NoDtypeMapping(Exception):
    pass

#------------------------------------------------------------------------
# Types
#------------------------------------------------------------------------

class Type(object):

    def to_llvm(self):
        raise NoLlvmMapping(self)

    def to_ctypes(self):
        raise NoCtypeMapping(self)

    def to_dtype(self):
        raise NoDtypeMapping(self)

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.name)

class Struct(Type):
    def __init__(self, name, *fields):
        self.name = name
        self.fields = fields

    def to_ctypes(self):
        class struct(ctypes.Structure):
            _fields_ = [
                (field.name, field.to_ctypes())
                for field in self.fields
            ]
        struct.__name__ = self.name
        return struct

class Field(Type):
    def __init__(self, name, endianness, format):
        self.name = name
        self.endianness = endianness
        self.format = format

    def to_dtype(self):
        return numpy.dtype(self.endianess + self.format)

    def to_ctypes(self):
        return codes.format_ctypes[self.format]

class Enum(Type):
    def __init__(self, name, **kw):
        self.name = name
        self.idx = Byte(name)

class Union(Type):

    def __init__(self, name, tag, options):
        self.name = name
        self.tag = tag
        self.options = options

class Vector(Type):

    def __init__(self, width, options):
        self.options = options

class Pointer(Type):

    def __init__(self, ty):
        self.ty = ty

    @property
    def name(self):
        return self.ty.name

    def to_ctypes(self):
        return ctypes.POINTER(self.ty.to_ctypes())

#------------------------------------------------------------------------
# Big Endian
#------------------------------------------------------------------------

def UBInt8(name):
    return Field(name, ">", "B")
def UBInt16(name):
    return Field(name, ">", "H")
def UBInt32(name):
    return Field(name, ">", "L")
def UBInt64(name):
    return Field(name, ">", "Q")

def SBInt8(name):
    return Field(name, ">", "b")
def SBInt16(name):
    return Field(name, ">", "h")
def SBInt32(name):
    return Field(name, ">", "l")
def SBInt64(name):
    return Field(name, ">", "q")

#------------------------------------------------------------------------
# Little Endian Integers
#------------------------------------------------------------------------

def ULInt8(name):
    return Field(name, "<", "B")
def ULInt16(name):
    return Field(name, "<", "H")
def ULInt32(name):
    return Field(name, "<", "L")
def ULInt64(name):
    return Field(name, "<", "Q")

def SLInt8(name):
    return Field(name, "<", "b")
def SLInt16(name):
    return Field(name, "<", "h")
def SLInt32(name):
    return Field(name, "<", "l")
def SLInt64(name):
    return Field(name, "<", "q")

#------------------------------------------------------------------------
# Native Endian Integers
#------------------------------------------------------------------------

def UNInt8(name):
    return Field(name, "=", "B")
def UNInt16(name):
    return Field(name, "=", "H")
def UNInt32(name):
    return Field(name, "=", "L")
def UNInt64(name):
    return Field(name, "=", "Q")

def SNInt8(name):
    return Field(name, "=", "b")
def SNInt16(name):
    return Field(name, "=", "h")
def SNInt32(name):
    return Field(name, "=", "l")
def SNInt64(name):
    return Field(name, "=", "q")

#------------------------------------------------------------------------
# IEEE Floating Point
#------------------------------------------------------------------------

def BFloat32(name):
    return Field(name, ">", "f")
def LFloat32(name):
    return Field(name, "<", "f")
def NFloat32(name):
    return Field(name, "=", "f")

def BFloat64(name):
    return Field(name, ">", "d")
def LFloat64(name):
    return Field(name, "<", "d")
def NFloat64(name):
    return Field(name, "=", "d")

#------------------------------------------------------------------------
# Boolean
#------------------------------------------------------------------------

def Bool(name):
    return Field(name, "=", "?")

Byte  = UBInt8
SChar = SLInt8
UChar = ULInt8
Char  = SChar

#------------------------------------------------------------------------
# Strings
#------------------------------------------------------------------------

class Sequence(Type):
    """ Fixed sequence of type ``ty`` with integral ``length``
    """

    def __init__(self, name, ty, length):
        self.name = name
        self.ty = ty
        self.length = length

    def to_ctypes(self):
        return self.ty.to_ctypes() * self.length

class VariableString(Type):

    def __init__(self, name, ptr, length):
        self.name = name
        self.ptr = ptr
        self.length = length

class TerminatedString(Type):

    def __init__(self, name, terminator):
        self.name = name
        self.terminator = terminator

def FixedString(length):
    return Sequence(Char, length)

def CString():
    return TerminatedString('0x00')

#------------------------------------------------------------------------
# LLArrays
#------------------------------------------------------------------------


def Array_C(name, ty, nd):
    return Struct('Array_C',
        Pointer(ty('data')),
        Sequence('shape', UNInt8(''), nd),
    )

def Array_F(name, ty, nd):
    return Struct('Array_F',
        Pointer(ty('data')),
        Sequence('shape', UNInt8(''), nd),
    )

def Array_S(name, ty, nd):
    return Struct('Array_S',
        Pointer(ty('data')),
        Sequence('shape', UNInt8(''), nd),
        Sequence('stride', UNInt8(''), nd),
    )

if __name__ == '__main__':
    c = Array_C('foo', SNInt8, 3)
    f = Array_F('foo', SNInt8, 3)
    s = Array_S('foo', SNInt8, 3)

    print c.to_ctypes()
    print f.to_ctypes()
    print s.to_ctypes()
