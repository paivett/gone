# gone/typesys.py
'''
Gone Type System
================
This file implements basic features of the Gone type system.  There is
a lot of flexibility possible here, but the best strategy might be to
not overthink the problem.  At least not at first.  Here are the
minimal basic requirements:

1. Types have names (e.g., 'int', 'float', 'string')
2. Types have to be comparable. (e.g., int != float).
3. Types support different operators (e.g., +, -, *, /, etc.)

To deal with all this initially, I'd recommend representing types
as simple strings.  Make tables that represent the capabilities
of different types. Make some utility functions that check operators.
KEEP IT SIMPLE. REPEAT. SIMPLE.

'''

class Type():
    """Base class for our type system"""

    @classmethod
    def binop_type(cls, op, right_type):
        """Returns the type of applying the binary operator with the current
        type and the type of the right operand, or returns None if the
        operation is not valid"""
        return None

    @classmethod
    def unaryop_type(cls, op):
        """Returns the type of applying the unary operator to the current type"""
        return None

    @classmethod
    def get_by_name(cls, type_name):
        for type_cls in cls.__subclasses__():
            if type_cls.name == type_name:
                return type_cls

        return None

class FloatType(Type):
    name = "float"
    binary_operators = ["+", "-", "*", "/"]
    unary_operators = ["+", "-"]

    @classmethod
    def binop_type(cls, op, right_type):
        if op in cls.binary_operators and issubclass(right_type, FloatType):
            return FloatType

        return None

    @classmethod
    def unaryop_supported(cls, op):
        if op in cls.unary_operators:
            return FloatType

        return None

class IntType(Type):
    name = "int"
    binary_operators = ["+", "-", "*", "/"]
    unary_operators = ["+", "-"]

    @classmethod
    def binop_type(cls, op, right_type):
        if op in cls.binary_operators and issubclass(right_type, IntType):
            return IntType

        return None

    @classmethod
    def unaryop_supported(cls, op):
        if op in cls.unary_operators:
            return IntType

        return None

class CharType(Type):
    name = "char"
