# gone/llvmgen.py
'''
Project 5 : Generate LLVM
=========================
In this project, you're going to translate the intermediate code
into LLVM IR.    Once you're done, your code will be runnable.  It
is strongly advised that you do *all* of the steps of Exercise 5
prior to starting this project.   Don't rush into it.

For Project 5, you are going to emit all of the LLVM instructions into
a single function main().  This is a temporary shim to get things to
work before we implement further support for user-defined functions later.

Further instructions are contained in the comments below.
'''
from functools import partialmethod

# LLVM imports. Don't change this.

from llvmlite.ir import (
    Module, IRBuilder, Function, IntType, DoubleType, VoidType, Constant, GlobalVariable,
    FunctionType
    )

# Declare the LLVM type objects that you want to use for the low-level
# in our intermediate code.  Basically, you're going to need to
# declare the integer, float, and char types here.  These correspond
# to the types being used the intermediate code being created by
# the ircode.py file.

int_type    = IntType(32)         # 32-bit integer
float_type  = DoubleType()        # 64-bit float
byte_type   = IntType(8)          # 8-bit integer

void_type   = VoidType()          # Void type.  This is a special type
                                  # used for internal functions returning
                                  # no value

# The following class is going to generate the LLVM instruction stream.
# The basic features of this class are going to mirror the experiments
# you tried in Exercise 5.  The execution model is somewhat similar
# to the visitor class.
#
# Given a sequence of instruction tuples such as this:
#
#         code = [
#              ('MOVI', 1, 'R1'),
#              ('MOVI', 2, 'R2')
#              ('ADDI', 'R1', 'R2', 'R3')
#              ('PRINTI', 'R3')
#              ...
#         ]
#
#    The class executes methods self.emit_opcode(args).  For example:
#
#             self.emit_MOVI(1, 'R1')
#             self.emit_MOVI(2, 'R2')
#             self.emit_ADDI('R1', 'R2', 'R3')
#             self.emit_PRINTI('R3')
#
#    Internally, you'll need to track variables, constants and other
#    objects being created.  Use a Python dictionary to emulate
#    storage.

class GenerateLLVM(object):
    def __init__(self):
        # Perform the basic LLVM initialization.  You need the following parts:
        #
        #    1.  A top-level Module object
        #    2.  A Function instance in which to insert code
        #    3.  A Builder instance to generate instructions
        #
        # Note: For project 5, we don't have any user-defined
        # functions so we're just going to emit all LLVM code into a top
        # level function void main() { ... }.   This will get changed later.

        self.module = Module('module')
        self.function = Function(self.module,
                                 FunctionType(void_type, []),
                                 name='main')

        self.block = self.function.append_basic_block('entry')
        self.builder = IRBuilder(self.block)

        # Dictionary that holds all of the global variable/function declarations.
        # Any declaration in the Gone source code is going to get an entry here
        self.vars = {}

        # Dictionary that holds all of the temporary registers created in
        # the intermediate code.
        self.temps = {}

        # Initialize the runtime library functions (see below)
        self.declare_runtime_library()


    def declare_runtime_library(self):
        # Certain functions such as I/O and string handling are often easier
        # to implement in an external C library.  This method should make
        # the LLVM declarations for any runtime functions to be used
        # during code generation.    Please note that runtime function
        # functions are implemented in C in a separate file gonert.c

        self.runtime = {}

        # Declare printing functions
        self.runtime['_print_int'] = Function(self.module,
                                              FunctionType(void_type, [int_type]),
                                              name="_print_int")

        self.runtime['_print_float'] = Function(self.module,
                                                FunctionType(void_type, [float_type]),
                                                name="_print_float")

        self.runtime['_print_byte'] = Function(self.module,
                                                FunctionType(void_type, [byte_type]),
                                                name="_print_byte")

    def generate_code(self, ircode):
        # Given a sequence of SSA intermediate code tuples, generate LLVM
        # instructions using the current builder (self.builder).  Each
        # opcode tuple (opcode, args) is dispatched to a method of the
        # form self.emit_opcode(args)

        for opcode, *args in ircode:
            if hasattr(self, 'emit_'+opcode):
                getattr(self, 'emit_'+opcode)(*args)
            else:
                print('Warning: No emit_'+opcode+'() method')

        # Add a return statement.  Note, at this point, we don't really have
        # user-defined functions so this is a bit of hack--it may be removed later.
        self.builder.ret_void()

    # ----------------------------------------------------------------------
    # Opcode implementation.   You must implement the opcodes.  A few
    # sample opcodes have been given to get you started.
    # ----------------------------------------------------------------------

    # Creation of literal values.  Simply define as LLVM constants.
    def emit_MOV(self, value, target, val_type):
        self.temps[target] = Constant(val_type, value)

    emit_MOVI = partialmethod(emit_MOV, val_type=int_type)
    emit_MOVF = partialmethod(emit_MOV, val_type=float_type)
    emit_MOVB = partialmethod(emit_MOV, val_type=byte_type)

    # Allocation of variables.  Declare as global variables and set to
    # a sensible initial value.
    def emit_VAR(self, name, var_type):
        var = GlobalVariable(self.module, var_type, name=name)
        var.initializer = Constant(var_type, 0)
        self.vars[name] = var

    emit_VARI = partialmethod(emit_VAR, var_type=int_type)
    emit_VARF = partialmethod(emit_VAR, var_type=float_type)
    emit_VARB = partialmethod(emit_VAR, var_type=byte_type)

    # Load/store instructions for variables.  Load needs to pull a
    # value from a global variable and store in a temporary. Store
    # goes in the opposite direction.
    def emit_LOADI(self, name, target):
        self.temps[target] = self.builder.load(self.vars[name], name=target)

    emit_LOADF = emit_LOADI
    emit_LOADB = emit_LOADI

    def emit_STOREI(self, source, target):
        self.builder.store(self.temps[source], self.vars[target])

    emit_STOREF = emit_STOREI
    emit_STOREB = emit_STOREI

    # Binary + operator
    def emit_ADDI(self, left, right, target):
        self.temps[target] = self.builder.add(self.temps[left], self.temps[right], name=target)

    def emit_ADDF(self, left, right, target):
        self.temps[target] = self.builder.fadd(self.temps[left], self.temps[right], name=target)

    # Binary - operator
    def emit_SUBI(self, left, right, target):
        self.temps[target] = self.builder.sub(self.temps[left], self.temps[right], name=target)

    def emit_SUBF(self, left, right, target):
        self.temps[target] = self.builder.fsub(self.temps[left], self.temps[right], name=target)

    # Binary * operator
    def emit_MULI(self, left, right, target):
        self.temps[target] = self.builder.mul(self.temps[left], self.temps[right], name=target)

    def emit_MULF(self, left, right, target):
        self.temps[target] = self.builder.fmul(self.temps[left], self.temps[right], name=target)

    # Binary / operator
    def emit_DIVI(self, left, right, target):
        self.temps[target] = self.builder.sdiv(self.temps[left], self.temps[right], name=target)

    def emit_DIVF(self, left, right, target):
        self.temps[target] = self.builder.fdiv(self.temps[left], self.temps[right], name=target)

    # Print statements
    def emit_PRINT(self, source, runtime_name):
        self.builder.call(self.runtime[runtime_name], [self.temps[source]])

    emit_PRINTI = partialmethod(emit_PRINT, runtime_name="_print_int")
    emit_PRINTF = partialmethod(emit_PRINT, runtime_name="_print_float")
    emit_PRINTB = partialmethod(emit_PRINT, runtime_name="_print_byte")

#######################################################################
#                      TESTING/MAIN PROGRAM
#######################################################################

def compile_llvm(source):
    from .ircode import compile_ircode

    # Compile intermediate code
    # !!! This needs to be changed in Project 7/8
    code = compile_ircode(source)

    # Make the low-level code generator
    generator = GenerateLLVM()

    # Generate low-level code
    generator.generate_code(code)
    return str(generator.module)

def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.llvmgen filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    llvm_code = compile_llvm(source)
    print(llvm_code)

if __name__ == '__main__':
    main()






