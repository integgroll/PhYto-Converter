import ast

BASE_FILE = ast.Module(body=[])

MODULE_DEFINITION = ast.ClassDef(name='PhYtoModule', bases=[
    ast.Name(id='Exploit', ctx=ast.Load(), lineno=7, col_offset=17),
], keywords=[], body=[
    ast.FunctionDef(name='__init__', args=ast.arguments(args=[
        ast.arg(arg='self', annotation=None, lineno=8, col_offset=17),
        ast.arg(arg='provided_argument_string', annotation=None, lineno=8, col_offset=23),
    ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[
        ast.Str(s='', lineno=8, col_offset=48),
    ]), body=[
        ast.Expr(value=ast.Call(func=ast.Attribute(
            value=ast.Call(func=ast.Name(id='super', ctx=ast.Load(), lineno=9, col_offset=8), args=[], keywords=[],
                           lineno=9, col_offset=8), attr='__init__', ctx=ast.Load(), lineno=9, col_offset=8), args=
        [
            ast.Name(id='provided_argument_string', ctx=ast.Load(), lineno=9, col_offset=25),
        ], keywords=[], lineno=9, col_offset=8), lineno=9, col_offset=8),
    ], decorator_list=[], returns=None, lineno=8, col_offset=4)],  ## More klass functions can go here
                                 decorator_list=[], lineno=7, col_offset=0)

ARGUMENTS_ARRAY = ast.FunctionDef(name='local_arguments', args=ast.arguments(args=[
    ast.arg(arg='self', annotation=None, lineno=14, col_offset=24),
], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
    ast.Return(value=ast.List(elts=[], ctx=ast.Load(), lineno=15, col_offset=15), lineno=15, col_offset=8),
], decorator_list=[], returns=None, lineno=14, col_offset=4)

ARGUMENTS_ARRAY_STRING_ARGUMENT = ast.Dict(keys=[
    ast.Str(s='name', lineno=16, col_offset=13),
    ast.Str(s='type', lineno=16, col_offset=31),
    ast.Str(s='nargs', lineno=16, col_offset=44),
    ast.Str(s='help', lineno=16, col_offset=58),
    ast.Str(s='default', lineno=17, col_offset=13),
], values=[
    ast.Str(s='target', lineno=16, col_offset=21),
    ast.Name(id='str', ctx=ast.Load(), lineno=16, col_offset=39),
    ast.Str(s='+', lineno=16, col_offset=53),
    ast.Str(s='HelpText', lineno=16, col_offset=66),
    ast.Str(s='DefaultValueHere', lineno=17, col_offset=24),
], lineno=16, col_offset=12)

ARGUMENTS_ARRAY_INT_ARGUMENT = ast.Dict(keys=[
    ast.Str(s='name', lineno=16, col_offset=13),
    ast.Str(s='type', lineno=16, col_offset=31),
    ast.Str(s='nargs', lineno=16, col_offset=44),
    ast.Str(s='help', lineno=16, col_offset=58),
    ast.Str(s='default', lineno=17, col_offset=13),
], values=[
    ast.Str(s='target', lineno=16, col_offset=21),
    ast.Name(id='int', ctx=ast.Load(), lineno=16, col_offset=39),
    ast.Str(s='+', lineno=16, col_offset=53),
    ast.Str(s='HelpText', lineno=16, col_offset=66),
    ast.Num(n=0, lineno=17, col_offset=24),
    # This 0 is a default value, it will get updated most likely by the code
], lineno=16, col_offset=12)

ARGUMENTS_ARRAY_BOOL_ARGUMENT = ast.Dict(keys=[
    ast.Str(s='name', lineno=16, col_offset=13),
    ast.Str(s='type', lineno=16, col_offset=31),
    ast.Str(s='nargs', lineno=16, col_offset=44),
    ast.Str(s='help', lineno=16, col_offset=58),
    ast.Str(s='default', lineno=17, col_offset=13),
], values=[
    ast.Str(s='target', lineno=16, col_offset=21),
    ast.Name(id='bool', ctx=ast.Load(), lineno=16, col_offset=39),
    ast.Str(s='+', lineno=16, col_offset=53),
    ast.Str(s='HelpText', lineno=16, col_offset=66),
    ast.NameConstant(value=False, lineno=17, col_offset=24),
    # This 0 is a default value, it will get updated most likely by the code
], lineno=16, col_offset=12)



EXPLOIT_FUNCTION_DEFINITION = ast.FunctionDef(name='exploit', args=ast.arguments(args=[
            ast.arg(arg='self', annotation=None, lineno=27, col_offset=16),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            ast.Pass(lineno=28, col_offset=8),
          ], decorator_list=[], returns=None, lineno=27, col_offset=4)


HELP_FUNCTION_DEFINITON = ast.FunctionDef(name='help', args=ast.arguments(args=[
            ast.arg(arg='self', annotation=None, lineno=31, col_offset=13),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            ast.Expr(value=ast.Call(func=ast.Name(id='print', ctx=ast.Load(), lineno=32, col_offset=8), args=[
                ast.Str(s='\n        Some Help Information\n        ', lineno=34, col_offset=-1),
              ], keywords=[], lineno=32, col_offset=8), lineno=32, col_offset=8),
          ], decorator_list=[], returns=None, lineno=31, col_offset=4)

THANKS_FUNCTION_DEFINITON = ast.FunctionDef(name='thanks', args=ast.arguments(args=[
            ast.arg(arg='self', annotation=None, lineno=37, col_offset=15),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            ast.Return(value=ast.Str(s="\n        All of the thanks that appear in the respective module, I especially don't want to lose the badass ASCII ART\n        ", lineno=40, col_offset=-1), lineno=38, col_offset=8),
          ], decorator_list=[], returns=None, lineno=37, col_offset=4)

IMPORT_FROM_SETUP = ast.ImportFrom(module='PLACEHOLDER', names=[], level=0, lineno=2, col_offset=0)

IMPORT_SETUP = ast.Import(names=[], lineno=3, col_offset=0)

IMPORT_ITEM = ast.alias(name='oops', asname=None)

BLANK_MODULE_SKELETON = ast.Module(body=[])

VARIABLE_SELF_REPLACEMENT = ast.Attribute(value=ast.Name(id='self', ctx=ast.Load(), lineno=33, col_offset=15), attr='apples', ctx=ast.Load(), lineno=33, col_offset=15)
