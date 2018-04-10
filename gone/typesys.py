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

# List of builtin types.  These will get added to the symbol table
builtin_types = [ 'int', 'float', 'string' ]

# Dict mapping all valid binary operations to a result type
_supported_binops = {
    ('int', '+', 'int') : 'int',
    ('int', '-', 'int') : 'int',
    # You define
    }

# Dict mapping all valid unary operations to result type
_supported_unaryops = {
    ('-', 'int') : 'int',
    # You define
    }
    
def check_binop(left_type, op, right_type):
    ''' 
    Check the validity of a binary operator. 
    '''
    return _supported_binops.get((left_type, op, right_type))

def check_unaryop(op, type):
    '''
    Check the validity of a unary operator. 
    '''
    return _supported_unaryops.get((op, type))




          




