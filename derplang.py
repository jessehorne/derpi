"""
Derplang, another Turing-complete esoteric programming language
This is a Python interpreter, written by Fox Wilson.
"""
import logging
import re


class NonexistentLabelException(Exception):
    pass


class IncompatibleDataTypeException(Exception):
    pass


class DeveloperDidNotReadTheDocumentationException(Exception):
    pass


class DerplangProgram:
    """
    This class runs a Derplang program. Incidentally, it's a pseudo-stack
    datastructure.
    """
    def __init__(self, l):
        self.program = l
        self.loc = 0
        self.labels = {}
        self.variables = {}
        self.defined_commands = {
            "var": variable,
            "out": output,
            "con": concatenate,
            "add": add,
            "sub": sub,
            "mul": mult,
            "div": div,
            "inp": getinput,
            "jmp": goto,
            "jlt": lessthan,
            "jeq": equals,
            "jgt": greaterthan
        }

    def scan_for_labels(self):
        """
        Scan for labels (la: statements) in the program.
        """
        pointer = 0
        while pointer < len(self.program):
            if self.program[pointer] != "la":
                pointer += 1
                continue
            label_name = self.program[pointer + 1]
            self.labels[label_name] = pointer
            pointer += 1

    def jump_to_label(self, label):
        """
        Jump to a given label. If the label does not exist, raise a
        NonexistentLabelException.
        """
        if label not in self.labels:
            raise NonexistentLabelException("Label %s not found" % label)
        self.loc = self.labels[label]

    def run_this(self):
        while self.loc < len(self.program):
            self.step()

    def step(self):
        current_statement = self.program[self.loc]
        if current_statement not in self.defined_commands:
            self.loc += 1
            return
        self.defined_commands[current_statement](self)


def can_be_float(n):
    try:
        float(n)
        return True
    except:
        return False


def variable(p):  # va:x:y
    key = p.program[p.loc + 1]
    value = p.program[p.loc + 2]
    p.variables[key] = value
    p.loc += 3


def output(p):  # ou:x
    key = p.program[p.loc + 1]
    if key not in p.variables:
        print key
    else:
        print p.variables[key]
    p.loc += 2


def concatenate(p):  # ca:z:x:y
    new_key = p.program[p.loc + 1]
    var1 = p.program[p.loc + 2]
    var2 = p.program[p.loc + 3]
    new_value = p.variables[var1] + p.variables[var2]
    p.variables[new_key] = new_value
    p.loc += 4


def do_math(p, math_to_do):  # generic math doing function
    new_key = p.program[p.loc + 1]
    var1 = p.program[p.loc + 2]
    var2 = p.program[p.loc + 3]
    value1 = value2 = None
    try:
        if var1 not in p.variables and can_be_float(var1):
            value1 = float(var1)
        else:
            value1 = float(p.variables[var1])
        if var2 not in p.variables and can_be_float(var2):
            value2 = float(var2)
        else:
            value2 = float(p.variables[var2])
    except:
        raise IncompatibleDataTypeException()
    if value1 is None or value2 is None:
        raise IncompatibleDataTypeException()
    new_value = str(math_to_do(value1, value2))
    p.variables[new_key] = new_value
    p.loc += 4


def add(p):  # ad:z:x:y
    do_math(p, lambda x, y: x + y)


def sub(p):  # su:z:x:y
    do_math(p, lambda x, y: x - y)


def mult(p):  # mu:z:x:y
    do_math(p, lambda x, y: x * y)


def div(p):  # di:z:x:y
    do_math(p, lambda x, y: x / y)


def forloop(p):  # fo:i:cmd:var1:var2:var3
    original_location = p.loc
    cmd_location = p.loc + 2
    i = int(p.program[p.loc + 1])
    cmd = p.program[p.loc + 2]

    if cmd not in p.defined_commands:
        raise DeveloperDidNotReadTheDocumentationException()

    for n in range(i):
        p.loc = cmd_location
        p.defined_commands[cmd](p)

    p.loc = original_location + 6


def getinput(p):  # ip:x
    key = p.program[p.loc + 1]
    p.variables[key] = raw_input()
    p.loc += 2


def goto(p):  # go:x
    label = p.program[p.loc + 1]
    p.jump_to_label(label)


def comparison(p, comp_func):  # Generic comparison thing
    var1 = p.program[p.loc + 1]
    var2 = p.program[p.loc + 2]
    if var1 not in p.variables:
        value1 = var1
    else:
        value1 = p.variables[var1]
    if var2 not in p.variables:
        value2 = var2
    else:
        value2 = p.variables[var2]
    if comp_func(value1, value2):
        p.jump_to_label(p.program[p.loc + 3])
    else:
        p.jump_to_label(p.program[p.loc + 4])


def lessthan(p):  # lt:x:y:j:k
    comparison(p, lambda x, y: x < y)


def equals(p):  # eq:x:y:j:k
    comparison(p, lambda x, y: x == y)


def greaterthan(p):  # gt:x:y:j:k
    comparison(p, lambda x, y: x > y)


if __name__ == '__main__':
    import shlex
    import sys
    logging.basicConfig(level=logging.DEBUG)
    program = sys.stdin.read(32768)
    program = [i.strip() for i in shlex.split(program)]
    print program
    p = DerplangProgram(program)
    p.scan_for_labels()
    p.run_this()
