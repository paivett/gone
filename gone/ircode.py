# gone/ircode.py
'''
Project 4
=========
In this project, you are going to turn the AST into an intermediate
machine code based on 3-address code. There are a few important parts
you'll need to make this work.  Please read carefully before
beginning:

A "Virtual" Machine
===================
A CPU typically consists of registers and a small set of basic opcodes
for performing mathematical calculations, loading/storing values from
memory, and basic control flow (branches, jumps, etc.).  For example,
suppose you want to evaluate an operation like this:

    a = 2 + 3 * 4 - 5

On a CPU, it might be decomposed into low-level instructions like this:

    MOVI   #2, R1
    MOVI   #3, R2
    MOVI   #4, R3
    MULI   R2, R3, R4
    ADDI   R4, R1, R5
    MOVI   #5, R6
    SUBI   R5, R6, R7
    STOREI R7, "a"

Each instruction represents a single operation such as add, multiply, etc.
There are always two input operands and a destination.

CPUs also feature a small set of core datatypes such as integers,
bytes, and floats. There are dedicated instructions for each type.
For example:

    ADDI   R1, R2, R3        ; Integer add
    ADDF   R4, R5, R6        ; Float add

There is often a disconnect between the types used in the source
programming language and the generated IRCode.  For example, a target
machine might only have integers and floats.  To represent a value
such as a boolean, you have to represent it as one of the native types
such as an integer.   This is an implementation detail that users
won't worry about (they'll never see it, but you'll have to worry
about it in the compiler).

Here is an instruction set specification for our IRCode:

    MOVI   value, target       ;  Load a literal integer
    VARI   name                ;  Declare an integer variable
    ALLOCI name                ;  Allocate an integer variabe on the stack
    LOADI  name, target        ;  Load an integer from a variable
    STOREI target, name        ;  Store an integer into a variable
    ADDI   r1, r2, target      ;  target = r1 + r2
    SUBI   r1, r2, target      ;  target = r1 - r2
    MULI   r1, r2, target      ;  target = r1 * r2
    DIVI   r1, r2, target      ;  target = r1 / r2
    PRINTI source              ;  print source  (debugging)
    CMPI   op, r1, r2, target  ;  Compare r1 op r2 -> target
    AND    r1, r2, target      :  target = r1 & r2
    OR     r1, r2, target      :  target = r1 | r2
    XOR    r1, r2, target      :  target = r1 ^ r2
    ITOF   r1, target          ;  target = float(r1)

    MOVF   value, target       ;  Load a literal float
    VARF   name                ;  Declare a float variable
    ALLOCF name                ;  Allocate a float variable on the stack
    LOADF  name, target        ;  Load a float from a variable
    STOREF target, name        ;  Store a float into a variable
    ADDF   r1, r2, target      ;  target = r1 + r2
    SUBF   r1, r2, target      ;  target = r1 - r2
    MULF   r1, r2, target      ;  target = r1 * r2
    DIVF   r1, r2, target      ;  target = r1 / r2
    PRINTF source              ;  print source (debugging)
    CMPF   op, r1, r2, target  ;  r1 op r2 -> target
    FTOI   r1, target          ;  target = int(r1)

    MOVB   value, target       ; Load a literal byte
    VARB   name                ; Declare a byte variable
    ALLOCB name                ; Allocate a byte variable
    LOADB  name, target        ; Load a byte from a variable
    STOREB target, name        ; Store a byte into a variable
    PRINTB source              ; print source (debugging)
    BTOI   r1, target          ; Convert a byte to an integer
    ITOB   r2, target          ; Truncate an integer to a byte
    CMPB   op, r1, r2, target  ; r1 op r2 -> target

There are also some control flow instructions

    LABEL  name                  ; Declare a label
    BRANCH label                 ; Unconditionally branch to label
    CBRANCH test, label1, label2 ; Conditional branch to label1 or label2 depending on test being 0 or not
    CALL   name, arg0, arg1, ... argN, target    ; Call a function name(arg0, ... argn) -> target
    RET    r1                    ; Return a result from a function

Single Static Assignment
========================
On a real CPU, there are a limited number of CPU registers.
In our virtual memory, we're going to assume that the CPU
has an infinite number of registers available.  Moreover,
we'll assume that each register can only be assigned once.
This particular style is known as Static Single Assignment (SSA).
As you generate instructions, you'll keep a running counter
that increments each time you need a temporary variable.
The example in the previous section illustrates this.

Your Task
=========
Your task is as follows: Write a AST Visitor() class that takes a
program and flattens it to a single sequence of SSA code instructions
represented as tuples of the form

       (operation, operands, ..., destination)

Testing
=======
The files Tests/irtest0-5.g contain some input text along with
sample output. Work through each file to complete the project.
'''

from . import ast


OP_CODES = {
    'int': {
        'mov': 'MOVI',
        '+': 'ADDI',
        '-': 'SUBI',
        '*': 'MULI',
        '/': 'DIVI',
        'print': 'PRINTI',
        'store': 'STOREI',
        'var': 'VARI',
        'load': 'LOADI'
    },
    'float': {
        'mov': 'MOVF',
        '+': 'ADDF',
        '-': 'SUBF',
        '*': 'MULF',
        '/': 'DIVF',
        'print': 'PRINTF',
        'store': 'STOREF',
        'var': 'VARF',
        'load': 'LOADF'
    },
    'char': {
        'mov': 'MOVB',
        'print': 'PRINTB',
        'store': 'STOREB',
        'var': 'VARB',
        'load': 'LOADB'
    }
}


class GenerateCode(ast.NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''
    def __init__(self):
        # counter for registers
        self.register_count = 0

        # The generated code (list of tuples)
        self.code = []

    def new_register(self):
         '''
         Creates a new temporary register
         '''
         self.register_count += 1
         return f'R{self.register_count}'

    # You must implement visit_Nodename methods for all of the other
    # AST nodes.  In your code, you will need to make instructions
    # and append them to the self.code list.
    #
    # A few sample methods follow.  You may have to adjust depending
    # on the names and structure of your AST nodes.

    def visit_IntegerLiteral(self, node):
        target = self.new_register()
        op_code = OP_CODES['int']['mov']
        self.code.append((op_code, node.value, target))
        # Save the name of the register where the value was placed
        node.register = target

    def visit_FloatLiteral(self, node):
        target = self.new_register()
        op_code = OP_CODES['float']['mov']
        self.code.append((op_code, node.value, target))
        node.register = target

    def visit_CharLiteral(self, node):
        target = self.new_register()
        op_code = OP_CODES['char']['mov']
        # We treat chars as their ascii value
        self.code.append((op_code, ord(node.value), target))
        # This is just to remember where the literal was put in
        node.register = target

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        operator = node.op

        op_code = OP_CODES[node.type.name][operator]

        target = self.new_register()
        inst = (op_code, node.left.register, node.right.register, target)
        self.code.append(inst)
        node.register = target

    def visit_UnaryOp(self, node):
        self.visit(node.right)
        operator = node.op

        if operator == "-":
            sub_op_code = OP_CODES[node.type.name][operator]
            mov_op_code = OP_CODES[node.type.name]['mov']

            # To account for the fact that the machine code does not support
            # unary operations, we must load a 0 into a new register first
            zero_target = self.new_register()
            zero_inst = (mov_op_code, 0, zero_target)
            self.code.append(zero_inst)

            target = self.new_register()
            inst = (sub_op_code, zero_target, node.right.register, target)
            self.code.append(inst)
            node.register = target
        else:
            # The plus unary operator produces no extra code
            node.register = node.right.register

    # CHALLENGE:  Figure out some more sane way to refactor the above code

    def visit_PrintStatement(self, node):
        self.visit(node.value)
        op_code = OP_CODES[node.value.type.name]['print']
        inst = (op_code, node.value.register)
        self.code.append(inst)

    def visit_ReadLocation(self, node):
        op_code = OP_CODES[node.location.type.name]['load']
        register = self.new_register()
        inst = (op_code, node.location.name, register)
        self.code.append(inst)
        node.register = register

    def visit_WriteLocation(self, node):
        self.visit(node.value)
        op_code = OP_CODES[node.location.type.name]['store']
        inst = (op_code, node.value.register, node.location.name)
        self.code.append(inst)
        # node.register = register

    def visit_ConstDeclaration(self, node):
        self.visit(node.value)

        # First we must declare the variable
        op_code = OP_CODES[node.type.name]['var']
        inst = (op_code, node.name)
        self.code.append(inst)

        op_code = OP_CODES[node.type.name]['store']
        inst = (op_code, node.value.register, node.name)
        self.code.append(inst)

    def visit_VarDeclaration(self, node):
        self.visit(node.datatype)

        op_code = OP_CODES[node.type.name]['var']
        def_inst = (op_code, node.name)

        if node.value:
            self.visit(node.value)
            self.code.append(def_inst)
            op_code = OP_CODES[node.type.name]['store']
            inst = (op_code, node.value.register, node.name)
            self.code.append(inst)
        else:
            self.code.append(def_inst)

# ----------------------------------------------------------------------
#                          TESTING/MAIN PROGRAM
#
# Note: Some changes will be required in later projects.
# ----------------------------------------------------------------------

def compile_ircode(source):
    '''
    Generate intermediate code from source.
    '''
    from .parser import parse
    from .checker import check_program
    from .errors import errors_reported

    ast = parse(source)
    check_program(ast)

    # If no errors occurred, generate code
    if not errors_reported():
        gen = GenerateCode()
        gen.visit(ast)
        return gen.code
    else:
        return []

def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.ircode filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    code = compile_ircode(source)

    for instr in code:
        print(instr)

if __name__ == '__main__':
    main()
