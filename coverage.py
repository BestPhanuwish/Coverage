"""
Write your program here.
"""

import sys, os, ast, io, trace, inspect

# getting input from argument
python_program = sys.argv[1]
input_files = sys.argv[2]

"""
Coverage class had been inspired and modified from tutorial 6
edstem.org. (n.d.). Ed Discussion. [online] 
Available at: https://edstem.org/au/courses/15196/lessons/51460/slides/349548 
[Accessed 6 May 2024].
"""
class Coverage:
    """
    A simple coverage analysis tool that hooks into the Python trace framework
    to record which lines of code are executed during the runtime of a script.
    """
    def __init__(self) -> None:
        """
        Initialises the Coverage instance with an empty trace list.
        """
        self.trace = []

    def traceit(self, frame, event, arg):
        """
        Trace function called by sys.settrace for each event.
        """
        if self.orig_trace is not None:
            self.orig_trace(frame, event, arg)
        if event == "line":
            fi = inspect.getframeinfo(frame)
            name, num = fi.function, fi.lineno
            # when I inspect this property from frame execute from different file it return <string>
            # so, it will only append trace from other file that execute via exec()
            if inspect.getfile(frame) == "<string>":
                name = "<module>" # group all of that line in file in one name
                self.trace.append((name, num))
        return self.traceit

    def __enter__(self):
        """
        Sets the trace function to this instance's traceit method.
        """
        self.orig_trace = sys.gettrace()
        sys.settrace(self.traceit)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """
        Restores the original trace function upon exiting the context.
        """
        sys.settrace(self.orig_trace)

    def coverage(self):
        """
        Returns a set of tuples representing the covered lines.
        """
        return set(self.trace)

    def __repr__(self) -> str:
        """ Provides a visual representation of the covered lines in the source code. """
        txt = ""
        for f_name in set(f_name for (f_name, line_number) in self.coverage()):
            # Handle the <module> case by reading file
            if f_name == "<module>":
                try:
                    src = open(python_program).readlines() # src is all the code from other file instead
                    start_ln = 1
                    for lineno in range(start_ln, start_ln + len(src)):
                        ind = ""
                        if (f_name, lineno) in self.trace:
                            ind = "| "
                        else:
                            ind = "  "
                        fmt = "%s%2d %s" % (ind, lineno, src[lineno - start_ln].rstrip())
                        txt += fmt + "\n"
                except Exception as exc:
                    print(exc)
            else:
                try:
                    fun = eval(f_name)  # Convert to code object
                except Exception as exc:
                    continue
                src, start_ln = inspect.getsourcelines(fun)
                for lineno in range(start_ln, start_ln + len(src)):
                    ind = ""
                    if (f_name, lineno) in self.trace:
                        ind = "| "
                    else:
                        ind = "  "
                    fmt = "%s%2d %s" % (ind, lineno, src[lineno - start_ln].rstrip())
                    txt += fmt + "\n"

        return txt
    
    def count_statement_percent(self) -> str:
        total_statement = 0
        statement_cov = 0
        
        src = open(python_program).readlines() # src is all the code from other file instead
        start_ln = 1
        found_multi_comment = False
        for lineno in range(start_ln, start_ln + len(src)):
            
            # ignore multi comment
            code_str = src[lineno - start_ln].rstrip()
            if '"""' in code_str:
                found_multi_comment = not found_multi_comment
                continue
            if found_multi_comment:
                continue
            
            # if it got traced, that mean it's sure to be statement
            if ("<module>", lineno) in self.trace:
                statement_cov += 1
                total_statement += 1
                continue
            
            # otherwise evaluate the code string
            if is_statement(code_str):
                total_statement += 1
            
        percent = (statement_cov/total_statement) * 100
        return f"Statement Coverage: {percent:.2f}%"
    
    def count_statement(self) -> str:
        total_statement = 0
        statement_cov = 0
        
        src = open(python_program).readlines() # src is all the code from other file instead
        start_ln = 1
        found_multi_comment = False
        for lineno in range(start_ln, start_ln + len(src)):
            
            # ignore multi comment
            code_str = src[lineno - start_ln].rstrip()
            if '"""' in code_str:
                found_multi_comment = not found_multi_comment
                continue
            if found_multi_comment:
                continue
            
            # if it got traced, that mean it's sure to be statement
            if ("<module>", lineno) in self.trace:
                statement_cov += 1
                total_statement += 1
                continue
            
            # otherwise evaluate the code string
            if is_statement(code_str):
                total_statement += 1
            
        return f"Total Statement: {total_statement} Covered Statement: {statement_cov}"
    
def is_statement(code_str: str) -> bool:
    if code_str == "":
        return False
    if "else:" in code_str:
        return False
    if "#" in code_str:
        return False
    return True

class CoverageTransformer(ast.NodeTransformer):
    """
    A custom AST transformer that instruments the code for branch coverage analysis.
    """
    def __init__(self):
        super().__init__()
        self.Counter = 0
    
    def visit_If(self, node):
        """
        Visits each 'if' node in the AST and instruments it for branch coverage.
        """
        self.generic_visit(node)  # Visit all other node types
        node.test = self.make_test(node.test, self.Counter)
        node.body = self.make_body(node.body, node, self.Counter, 1)
        node.orelse = self.make_body(node.orelse, node, self.Counter, 0)
        self.Counter += 1
        return node
    
    def visit_While(self, node):
        """
        Visits each 'while' node in the AST and instruments it for branch coverage.
        """
        self.generic_visit(node)
        node.test = self.make_test(node.test, self.Counter)
        node.body = self.make_body(node.body, node, self.Counter, 1)
        node.orelse = self.make_body([], node, self.Counter, 0)
        self.Counter += 1
        return node

    def visit_For(self, node):
        """
        Visits each 'for' node in the AST and instruments it for branch coverage.
        """
        self.generic_visit(node)
        node.iter = self.make_test(node.iter, self.Counter)
        node.body = self.make_body(node.body, node, self.Counter, 1)
        node.orelse = self.make_body([], node, self.Counter, 0) 
        self.Counter += 1
        return node

    def make_body(self, block, node, Counter, kind):
        """
        Instruments the body of an 'if' or 'else' block.
        """
        new_node = ast.Expr(ast.Call(func=ast.Name(id='_branch', ctx=ast.Load()),
                            args=[ast.Constant(Counter), ast.Constant(kind)],
                            keywords=[]))
        ast.copy_location(new_node, node)
        return [new_node] + block

    def make_test(self, test, Counter):
        """
        Instruments the test condition of an 'if' statement.
        """
        new_test = ast.Call(func=ast.Name(id="_cond", ctx=ast.Load()),
                         args=[ast.Constant(Counter), test],
                         keywords=[])
        ast.copy_location(new_test, test)
        return new_test
    
branch_coverage = {}

def _cond(cond_id, condition):
    """
    Records the evaluation of a condition.
    """
    global branch_coverage
    branch_coverage.setdefault(cond_id, [0, {}])[0] += 1
    return condition

def _branch(cond_id, branch_id):
    """
    Records the branch taken for a given condition.
    """
    global branch_coverage
    branch_coverage.setdefault(cond_id, [0, {}])[1].setdefault(branch_id, 0)
    branch_coverage[cond_id][1][branch_id] += 1

def count_branch(br_cov):
    total = 0
    for cond_id, (conditions_evaluated, branches) in br_cov.items():
        for branch_num, branches_taken in branches.items():
            total += 1
    return total

class BranchCoverage:
    """
    A class to analyze and report branch coverage based on the recorded execution paths.
    """
    def __init__(self) -> None:
        self.full_branch_coverage = None
        
    def set_full_branch(self, v):
        global branch_coverage
        sys.stdout = open(os.devnull, 'w')
        for line in ast.unparse(v).split("\n"):
            try:
                eval(line)
            except Exception:
                continue
        sys.stdout = sys.__stdout__
        self.full_branch_coverage = branch_coverage.copy()
        branch_coverage = {}
    
    def report(self):
        """
        Generates a report of the branch coverage analysis.
        """
        for cond_id, (conditions_evaluated, branches) in branch_coverage.items():
            print(f"Condition {cond_id}: Evaluated {conditions_evaluated} times")
            for branch_num, branches_taken in branches.items():
                print(f"Branch {branch_num}: taken {branches_taken} times")
    
    def count_branch_percent(self):
        global branch_coverage
        try:
            percent = (count_branch(branch_coverage)/count_branch(self.full_branch_coverage)) * 100
            return f"Branch Coverage: {percent:.2f}%"
        except Exception: # omly happened when there's no branch in code
            return f"Branch Coverage: 100.00%"
        
    def count_branch(self):
        global branch_coverage
        return f"Total Branch: {count_branch(self.full_branch_coverage)} Branch Covered: {count_branch(branch_coverage)}"
    
# Setup for branch coverage #

bc = BranchCoverage()
v = ast.parse(open(python_program, 'r').read())
CoverageTransformer().visit(v)
bc.set_full_branch(v)

# run the test #

sys.stdout = open(os.devnull, 'w')
with Coverage() as cov:
    # Iterate over input files in directory
    for name in os.listdir(input_files):
        try:
            sys.stdin = io.StringIO(open(f"{input_files}/{name}").read())
            exec(open(python_program).read())
        except Exception:
            continue
for name in os.listdir(input_files):
    try:
        sys.stdin = io.StringIO(open(f"{input_files}/{name}").read())
        exec(ast.unparse(v))
    except Exception as e:
        continue
sys.stdout = sys.__stdout__

print(cov.count_statement_percent())
print(bc.count_branch_percent())