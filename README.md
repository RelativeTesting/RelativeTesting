# RelativeTesting

## Automated Test Case Generation with Symbolic Execution and LLM-Powered Constraint Solving

**RelativeTesting** is a dynamic symbolic execution engine for Python that automatically generates test cases achieving condition coverage. It extends [PyExZ3](http://research.microsoft.com/apps/pubs/?id=233035) (by Thomas Ball, Microsoft Research) with GPT-4 fallback constraint solving, AST-based loop unfolding, string type support, and a pre-constraint mechanism for defining input constraints via AST annotations.

This project was developed as a Sabanci University graduation project (ENS 492).

---

## Key Features

RelativeTesting builds on the PyExZ3 foundation with the following additions:

- **GPT-4 Fallback Constraint Solving** -- When Z3 cannot solve a constraint (e.g., semantic or non-linear constraints), the system falls back to OpenAI GPT-4 to generate satisfying inputs.
- **AST-Based Loop Unfolding** -- Loops are transformed into sequential code via AST rewriting, enabling symbolic analysis of iterative constructs that would otherwise be difficult to explore.
- **String Symbolic Execution** -- Support for symbolic string parameters (`SymbolicStr`), extending beyond the original integer-only symbolic types.
- **Pre-Constraint Mechanism** -- Users can define constraints on test inputs via AST annotations, allowing more targeted test generation.
- **Input-to-Function Parameter Conversion** -- Automated conversion of generated inputs into function parameters for direct execution.

---

## How It Works

Dynamic symbolic execution in RelativeTesting follows these steps:

1. **Concrete execution on symbolic arguments.** The target function is executed with symbolic arguments (`SymbolicInteger` and `SymbolicStr` inherit from both `SymbolicObject` and the native `int`/`str` types). This dual inheritance allows the function to run concretely while collecting symbolic information.
2. **Branch condition interception.** Python's `__bool__` method is overridden to intercept all branch conditions during execution, building a constraint tree that captures the path taken through the program.
3. **Constraint solving with Z3.** The Z3 theorem prover is used as the primary solver to negate path constraints and generate new inputs that will drive execution down previously uncovered paths.
4. **GPT-4 fallback.** When Z3 cannot solve a constraint (e.g., due to semantic or non-linear relationships), the constraint is passed to GPT-4, which attempts to produce a satisfying assignment.
5. **Loop unfolding via AST rewriting.** Before symbolic execution, loops in the target code are unfolded into sequential if-statements using AST transformations, enabling the symbolic engine to reason about iterative behavior.

---

## Architecture

```
User Code --> Loader --> ExplorationEngine
                             |-- PathToConstraint (branch interception via __bool__)
                             |-- Z3Wrapper (primary solver)
                             |-- Openai_wrap (GPT-4 fallback)
                             +-- LoopUnfolding (AST preprocessing)
```

---

## Project Structure

```
pyexz3.py                  -- CLI entry point
symbolic/                   -- Core symbolic execution engine
    explore.py              -- ExplorationEngine
    path_to_constraint.py   -- Constraint tree builder
    openai_wrap.py          -- GPT-4 fallback solver
    symbolic_types/         -- SymbolicInteger, SymbolicStr, SymbolicDict
    z3_expr/                -- Z3 expression builders
AST/                        -- Loop unfolding and input detection
    AST_loop_unfolding/
        loop_unfolding.py   -- AST-based loop transformation
generator/                  -- Input-to-function conversion
    func_generator.py       -- Parameter conversion utilities
test/                       -- Test cases for symbolic execution
reports/                    -- Project report
run_tests.py                -- Test runner
```

---

## Installation

### Setup Instructions

- Make sure that you use Python 32-bit (64-bit) if-and-only-if you use the Z3 32-bit (64-bit) binaries.
Testing so far has been on Python 3.2.3 and 32-bit.
- Install Python 3.2.3 (https://www.python.org/download/releases/3.2.3/)
- Install the latest "unstable" release of Z3 to directory Z3HOME from http://z3.codeplex.com/releases
(click on the "Planned" link on the right to get the latest binaries for all platforms)
- Add Z3HOME\bin to PATH and PYTHONPATH
- MacOS: setup.sh for Homebrew default locations for Python and Z3; see end for MacOS specific instructions
- Optional:
  - Install GraphViz utilities (http://graphviz.org/)

### MacOS Specific

1. Grab yourself a Brew at http://brew.sh/
2. Get the newest python or python3 version: `brew install python`
3. Have the system prefer brew python over system python: `echo export PATH='/usr/local/bin:$PATH' >> ~/.bash_profile`
4. Get z3: `brew install homebrew/science/z3`
5. Clone this repository: `git clone https://github.com/thomasjball/PyExZ3.git`
6. Set the PATH: `. PyExZ3/setup.sh`  (do not run the setup script in a subshell `./ PyExZ3/`)

### Vagrant Specific

[Vagrant](http://www.vagrantup.com/) is a cross-platform tool to manage
virtualized development environments. Vagrant runs on Windows, OS X, and
Linux and can manage virtual machines running on VirtualBox, VMware,
Docker, and Hyper-V.

1. [Download Vagrant](http://www.vagrantup.com/downloads.html).
2. Install [VirtualBox](https://www.virtualbox.org/) or configure an
[alternative
provider](http://docs.vagrantup.com/v2/providers/index.html).
3. Run `vagrant up` from the PyExZ3 directory. The Vagrantfile in the
repository tells Vagrant to download a Debian base image, launch it with
the default provider (VirtualBox), and run the script `vagrant.sh` to
provision the machine.
4. Once the provisioning is done you can SSH into the machine using
`vagrant ssh` and PyExZ3 is ready to run. Please note that the
provisioning takes a while as Git is compiled from source as Debian's
Git is incompatible with [CodePlex](http://www.codeplex.com/) where Z3
is hosted.

### CVC SMT Solver

By default PyExZ3 uses the Z3 to solve path predicates. Optionally, the
[CVC SMT](http://cvc4.cs.nyu.edu/web/) solver can be enabled with the
`--cvc` argument. While the two solvers offer a similar feature set, the
integration of CVC differs from Z3 in a number of ways. Most
predominately, the CVC integration uses an unbounded rational number
representation for Python numbers, converting to bit vectors only for
bitwise operations. The Z3 integration uses bounded bit vectors for all
numbers. For programs that use any significant number of bitwise
operations, the default Z3-based configuration is strongly recommended.
Additionally, CVC does not support generating models for non-linear
relationships causing a few of the included PyExZ3 test cases to fail
with a `LogicException`.

### Check That Everything Works

- `python run_tests.py test` should pass all tests
- `python pyexz3.py test/FILE.py` to run a single test from the test directory

---

## Usage

### Basic Usage

Give a Python file `FILE.py` as input. By default, `pyexz3` expects `FILE.py`
to contain a function named `FILE` where symbolic execution will start:

```bash
python pyexz3.py test/simple.py
```

### Starting Function

You can override the default starting function with `--start MAIN`,
where `MAIN` is the name of a function in `FILE`:

```bash
python pyexz3.py --start=MAIN test/FILE.py
```

### Bounding Iterations

Bounding the number of iterations of the path exploration is essential when
analyzing functions with loops and/or recursion. Specify a bound using the `--max-iters` flag:

```bash
python pyexz3.py --max-iters=42 test/binary_search.py
```

### Arguments to Starting Function

By default, pyexz3 associates a symbolic integer (with initial value 0) for each
parameter of the starting function. Import from `symbolic.args` to get the
`@concrete` and `@symbolic` decorators that let you override the defaults on the
starting function:

```python
from symbolic.args import *

@concrete(a=1, b=2)
@symbolic(c=3)
def startingfun(a, b, c, d):
    ...
```

The `@concrete` decorator declares that a parameter will not be treated symbolically
and provides an initial value for the parameter. The `@symbolic` decorator declares
that a parameter will be treated symbolically -- the type of the associated initial
value for the argument will be used to determine the proper symbolic type (if one
exists). In the above example, parameters `a` and `b` are treated concretely and
will have initial values `1` and `2` (for all paths explored), and parameter `c`
will be treated as a symbolic integer input with the initial value `3` (its value
can change after the first path has been explored). Since parameter `d` is not
specified, it will be treated as a symbolic integer input with the initial value 0.

### Running the Test Suite

```bash
python run_tests.py test
```

### Other Options

- `--graph=DOTFILE` -- Generate a graph of the explored paths in DOT format.
- `--log=LOGFILE` -- Write a log of the exploration to a file.
- `--cvc` -- Use the CVC SMT solver instead of Z3.

### Output

`pyexz3` prints the list of generated inputs and corresponding observed
return values to standard out. The lists of generated inputs and the corresponding
return values are returned by the exploration engine to `pyexz3` where they can be
used for other purposes.

### Expected Result Functions

If `FILE.py` contains a function named `expected_result`, then after path
exploration is complete, the list of return values will be compared against the
list returned by `expected_result`. More precisely, the two lists are converted
into bags and the bags compared for equality. If a function named
`expected_result_set` is present instead, the lists are converted into sets and
the sets are compared for equality. List equality is too strong a criteria for
testing, since small changes to programs can lead to paths being explored in
different orders.

### Import Behavior

The location of `FILE.py` is added to the import path so that all imports in
`FILE.py` relative to that file will work.

---

## Tech Stack

- **Python 3** -- Core language
- **Z3 Theorem Prover** -- Primary constraint solver
- **OpenAI GPT-4 API** -- Fallback constraint solver
- **Python AST module** -- Loop unfolding and code transformation
- **astor** -- AST-to-source conversion

---

## Report

The project report is available at:

`reports/ENS 492_Progress Report-II .docx.pdf`

---

## Authors

**Students:**
- Gorkem Yar
- Enis Mert Kuzu
- Huseyin Alper Karadeniz
- Rebah Ozkoc

**Supervisors:**
- Cemal Yilmaz
- Husnu Yenigun

---

## Acknowledgments

This project is based on **PyExZ3** by Thomas Ball (Microsoft Research). The original tool and its design are described in the paper [Deconstructing Dynamic Symbolic Execution](http://research.microsoft.com/apps/pubs/?id=233035).

The NICE project (http://code.google.com/p/nice-of/) provided the original symbolic execution engine for Python. Bruni, Disney, and Flanagan described encoding symbolic execution for Python in Python in their 2008 paper [A Peer Architecture for Lightweight Symbolic Execution](http://hoheinzollern.files.wordpress.com/2008/04/seer1.pdf).

---

## License

See `copyright.txt` for license information.
