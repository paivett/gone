# Gone compiler

This is a compiler for a tiny programming language called *Gone*, implemented using Python 3.6, [SLY](https://github.com/dabeaz/sly) and [llvmlite](https://llvmlite.readthedocs.io/en/latest/). Gone is a very small language based on Go.

This compiler was developed as part of the January 2018 [Write a compiler](http://www.dabeaz.com/compiler.html) course, under the supervision of David Beazly.

## Requisites
The gone project requires the following dependencies
 * SLY
 * llvmlite
 * clang compiler

In order to install Python requirements, just run

    pip install -r requirements.txt

clang installation depends on your OS

## Compilation
To compile a *gone* program, run

    python -m gone.compile examples/mandel.g

The examples directory has some example programs in *gone*

After compilation, an executable ```a.out``` will be generated.
