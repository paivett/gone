# gone/parser.py
'''
Project 2:  Write a parser
==========================
In this project, you write the basic shell of a parser for Gone.  A
formal BNF of the language follows.  Your task is to write parsing
rules and build the AST for this grammar using SLY.  The following
grammar is partial.  More features get added in later projects.

program : statements
        | empty

statements :  statements statement
           |  statement

statement :  const_declaration
          |  var_declaration
          |  assign_statement
          |  print_statement
    
const_declaration : CONST ID = expression ;

var_declaration : VAR ID datatype ;
                | VAR ID datatype = expression ;

assign_statement : location = expression ;

print_statement : PRINT expression ;

expression :  + expression
           |  - expression
           | expression + expression
           | expression - expression
           | expression * expression
           | expression / expression
           | ( expression )
           | location
           | literal

literal : INTEGER     
        | FLOAT       
        | CHAR      

location : ID
         ;

datatype : ID
         ;

empty    :

To do the project, follow the instructions contained below.
'''

# ----------------------------------------------------------------------
# parsers are defined using SLY.  You inherit from the Parser class
#
# See http://sly.readthedocs.io/en/latest/
# ----------------------------------------------------------------------
from sly import Parser

# ----------------------------------------------------------------------
# The following import loads a function error(lineno,msg) that should be
# used to report all error messages issued by your parser.  Unit tests and
# other features of the compiler will rely on this function.  See the
# file errors.py for more documentation about the error handling mechanism.
from .errors import error

# ----------------------------------------------------------------------
# Import the lexer class.  It's token list is needed to validate and
# build the parser object.
from .tokenizer import GoneLexer

# ----------------------------------------------------------------------
# Get the AST nodes.  
# Read instructions in ast.py
from .ast import *

class GoneParser(Parser):
    # Same token set as defined in the lexer
    tokens = GoneLexer.tokens

    # ----------------------------------------------------------------------
    # Operator precedence table.   Operators must follow the same 
    # precedence rules as in Python.  Instructions to be given in the project.

    precedence = (
    )

    # ----------------------------------------------------------------------
    # YOUR TASK.   Translate the BNF in the string below into a collection
    # of parser functions.  For example, a rule such as :
    #
    #   program : statements
    #
    # Gets turned into a Python method like this:
    #
    # @_('statements')
    # def program(self, p):
    #      return Program(p.statements)
    #
    # For symbols such as '(' or '+', you'll need to replace with the name
    # of the corresponding token such as LPAREN or PLUS.
    #
    # In the body of each rule, create an appropriate AST node and return it
    # as shown above.
    #
    # For the purposes of lineno number tracking, you should assign a line number
    # to each AST node as appropriate.  To do this, I suggest pulling the 
    # line number off of any nearby terminal symbol.  For example:
    #
    # @_('PRINT expr SEMI')
    # def print_statement(self, p):
    #     return PrintStatement(p.expr, lineno=p.lineno)
    #
    # STARTING OUT
    # ============
    # The following grammar rules should give you an idea of how to start.
    # Try running this file on the input Tests/parsetest0.g
    #
    # Afterwards, add features by looking at the code in Tests/parsetest1-6.g


    @_('PRINT expression SEMI')
    def print_statement(self, p):
        return PrintStatement(p.expression)

    @_('literal')
    def expression(self, p):
        return p.literal

    @_('INTEGER')
    def literal(self, p):
        return IntegerLiteral(int(p.INTEGER))

    @_('FLOAT')
    def literal(self, p):
        return FloatLiteral(float(p.FLOAT))

    @_('CHAR')
    def literal(self, p):
        return CharLiteral(eval(p.CHAR))

    # ----------------------------------------------------------------------
    # DO NOT MODIFY
    #
    # catch-all error handling.   The following function gets called on any
    # bad input.  p is the offending token or None if end-of-file (EOF).
    def error(self, p):
        if p:
            error(p.lineno, "Syntax error in input at token '%s'" % p.value)
        else:
            error('EOF','Syntax error. No more input.')

# ----------------------------------------------------------------------
#                     DO NOT MODIFY ANYTHING BELOW HERE
# ----------------------------------------------------------------------

def parse(source):
    '''
    Parse source code into an AST. Return the top of the AST tree.
    '''
    lexer = GoneLexer()
    parser = GoneParser()
    ast = parser.parse(lexer.tokenize(source))
    return ast

def main():
    '''
    Main program. Used for testing.
    '''
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m gone.parser filename\n')
        raise SystemExit(1)

    # Parse and create the AST
    ast = parse(open(sys.argv[1]).read())

    # Output the resulting parse tree structure
    for depth, node in flatten(ast):
        print('%s%s' % (' '*(4*depth), node))

if __name__ == '__main__':
    main()
