import os
import re
import ast
import astor
import copy
import autopep8
from pprint import pprint
import phyto.module_skeleton as skeleton
from time import *
from base64 import b64encode as doggy
import _ast


class PhYtoMaker:
    def __init__(self, directory="."):
        self.directory = directory

        self.python_files = []
        self.not_python_files = []

    def find_python_files(self):
        found_files = []
        for (dirpath, dirnames, filenames) in os.walk(self.directory):
            found_files += ["{dirpath}{filename}".format(filename=filename, dirpath=dirpath) for filename in filenames
                            if filename[-3:] == ".py"]
        self.python_files = found_files
        return found_files

    def find_not_python_files(self):
        found_files = []
        for (dirpath, dirnames, filenames) in os.walk(self.directory):
            found_files += ["{dirpath}{filename}".format(filename=filename, dirpath=dirpath) for filename in filenames
                            if filename[-3:] != ".py"]
        self.not_python_files = found_files
        return found_files

    @staticmethod
    def get_ast_objects(ast_handle):
        if ast_handle.__module__ == "_ast":
            pass
        elif ast_handle.__module__ == "":
            pass
        else:
            return ast_handle

        pass

    @staticmethod
    def get_file_data(file_name):
        file_handle = open(file_name, "r", encoding="ISO-8859-1")
        file_data = file_handle.read()
        file_handle.close()
        return file_data

    @staticmethod
    def is_file_python_two(file_name):
        is_python_two = False
        file_data = PhYtoMaker.get_file_data(file_name)
        matches = re.search('print[^(A-Za-z0-9-_]]', file_data, flags=re.M | re.S)
        if matches != None:
            is_python_two = True
        return is_python_two

    @staticmethod
    def remove_files(file_array=[]):
        for file in file_array:
            try:
                os.remove(file)
            except Exception as e:
                print(e)


class PhYtoModule:
    def __init__(self, file_name=""):
        if file_name:
            self.file_name = file_name
            self.file_data = self.get_file_data()

            self.parsed_ast_handle = ast.parse(self.file_data)

            self.raw_imports = []
            self.imported_modules = []

        else:
            return False

    def get_file_data(self):
        file_handle = open(self.file_name, "r", encoding="ISO-8859-1")
        file_data = file_handle.read()
        file_handle.close()
        return file_data


class PhYtography_classifyer(ast.NodeTransformer):
    def __init__(self, variables_to_classify=[]):
        self.variables_to_classify = variables_to_classify

        # ast.Attribute(value=ast.Name(id='self', ctx=ast.Load(), lineno=33, col_offset=15), attr='apples', ctx=ast.Load(), lineno=33, col_offset=15)
        # Name(id='tuesday', ctx=Load(), lineno=36, col_offset=0)
        # Name(id='tuesday', ctx=Store(), lineno=36, col_offset=0)

    def visit_Name(self, node):
        if node.id in self.variables_to_classify:
            new_node = copy.deepcopy(skeleton.VARIABLE_SELF_REPLACEMENT)
            new_node.value.id = "self"
            new_node.attr = node.id
            return new_node
        return node


class PhYtographer_blix(ast.NodeTransformer):
    def __init__(self, variables_to_remove=[]):
        self.variables_to_remove = variables_to_remove

    def visit_ClassDef(self, node):
        return None

    def visit_FunctionDef(self, node):
        return None

    def visit_Import(self, node):
        return None

    def visit_ImportFrom(self, node):
        return None

    def visit_Assign(self, node):
        # This only works on simple variables, basically the ones that we want to find anyways
        # It will assign them to a local class dictionary that will track what values they have had over time (assuming basic end values)
        targets_to_assign = []
        ## Finds the variable names and plugs them into a list
        if hasattr(node.targets, '__iter__'):
            for target in node.targets:
                if isinstance(target, ast.Tuple):
                    for target_name in target.elts:
                        targets_to_assign.append(target_name.id)
                        if target_name.id in self.variables_to_remove:
                            return None
                elif isinstance(target, ast.List):
                    for target_name in target:
                        targets_to_assign.append(target_name.id)
                        if target_name.id in self.variables_to_remove:
                            return None
                elif isinstance(target, ast.Name):
                    targets_to_assign.append(target.id)
                    if target.id in self.variables_to_remove:
                        return None
                elif isinstance(target, ast.Attribute):
                    attr_name = "{klass}.{name}".format(klass=target.value.id, name=target.attr)
                    targets_to_assign.append(attr_name)
                    if attr_name in self.variables_to_remove:
                        return None
        return node


class PhYtographer_demainer(ast.NodeTransformer):
    def __init__(self):
        self.if_main_body = []

    def visit_If(self, node):
        is_it_main = False
        if isinstance(node.test, ast.Compare):
            if node.test.left.id == '__name__':
                if True in [True for op in node.test.ops if isinstance(op, ast.Eq)]:
                    for comparator in node.test.comparators:
                        if isinstance(comparator, ast.Str):
                            if comparator.s == "__main__":
                                is_it_main = True
        if is_it_main:
            # This is the new things that go on with this
            self.if_main_body = node.body
            return None
        return node


class PhYtographer_remainer(ast.NodeTransformer):
    def __init__(self, new_main=[], functions_by_name={}):
        self.new_main = new_main
        self.functions_by_name = functions_by_name
        self.function_names_to_delete = []

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                if node.value.func.id in self.functions_by_name:
                    self.function_names_to_delete.append(node.value.func.id)
                    return self.functions_by_name.get(node.value.func.id, []).body
        return node


class PhYtographer_assistant(ast.NodeVisitor):
    def __init__(self):
        self.stats = {"imports": [], "import_info": {"general": [], "import_from": {}}}
        self.variable_data = {}
        self.variable_state = {}
        self.variable_name = None
        self.nested_variable = []
        self.found_classes = []
        self.found_functions = []
        self.found_functions_by_name = {}

    def visit_ClassDef(self, node):
        self.found_classes.append(node)

    def visit_FunctionDef(self, node):
        found_self = False
        for argument in node.args.args:
            if argument.arg == "self":
                found_self = True
        if not found_self:
            self.found_functions.append(node)
            self.found_functions_by_name[node.name] = node

    def visit_Import(self, node):
        for alias in node.names:
            self.stats["imports"].append({"kind": "import", "name": alias.name, "pp": alias.name})
            self.stats["import_info"]["general"].append({"name": alias.name, "pp": alias.name})
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.stats["imports"].append({"kind": "import_from", "name": alias.name, "module": node.module,
                                          "pp": "{module}.{alias}".format(module=node.module, alias=alias.name)})
            self.stats["import_info"]["import_from"][node.module] = [
                *self.stats["import_info"]["import_from"].get(node.module, []),
                {"name": alias.name, "module": node.module}]
        self.generic_visit(node)

    def visit_Assign(self, node):
        # This only works on simple variables, basically the ones that we want to find anyways
        # It will assign them to a local class dictionary that will track what values they have had over time (assuming basic end values)

        values_to_assign = []
        targets_to_assign = []

        ## Finds the variable names and plugs them into a list
        if hasattr(node.targets, '__iter__'):
            for target in node.targets:
                if isinstance(target, ast.Tuple):
                    for target_name in target.elts:
                        targets_to_assign.append(target_name.id)
                        if target_name.id not in self.variable_data:
                            self.variable_data[target_name.id] = {"current_value": None, "previous_values": []}
                elif isinstance(target, ast.List):
                    for target_name in target:
                        targets_to_assign.append(target_name.id)
                        if target_name.id not in self.variable_data:
                            self.variable_data[target_name.id] = {"current_value": None, "previous_values": []}
                elif isinstance(target, ast.Name):
                    targets_to_assign.append(target.id)
                    if target.id not in self.variable_data:
                        self.variable_data[target.id] = {"current_value": None, "previous_values": []}
                elif isinstance(target, ast.Attribute):
                    attr_name = "{klass}.{name}".format(klass=target.value.id, name=target.attr)
                    targets_to_assign.append(attr_name)
                    if attr_name not in self.variable_data:
                        self.variable_data[attr_name] = {"current_value": None, "previous_values": []}

        # Finds the variable values and puts them into a list
        if isinstance(node.value, ast.Tuple):
            for value in node.value.elts:
                if isinstance(value, ast.Num):
                    values_to_assign.append(value.n)
                if isinstance(value, ast.Str):
                    values_to_assign.append(value.s)
        elif isinstance(node.value, ast.List):
            pass
        elif isinstance(node.value, ast.Dict):
            for key in node.value.keys:
                print(key.s, " : ", node.value.__dict__.get(key))
        elif isinstance(node.value, ast.Num):
            values_to_assign.append(node.value.n)
        elif isinstance(node.value, ast.Str):
            values_to_assign.append(node.value.s)
        else:
            pass

        # Conglomerates the values and the names of variables
        if len(values_to_assign) == 1 and len(values_to_assign) < len(targets_to_assign):
            for target in targets_to_assign:
                self.variable_data[target] = {"current_value": values_to_assign[0],
                                              "previous_values": [*self.variable_data.get(target, {}).get(
                                                  "previous_values", []), values_to_assign[0]]}
        elif len(values_to_assign) == len(targets_to_assign):
            for iterator in range(0, len(values_to_assign)):
                self.variable_data[targets_to_assign[iterator]] = {"current_value": values_to_assign[iterator],
                                                                   "previous_values": [*self.variable_data.get(
                                                                       targets_to_assign[iterator], {}).get(
                                                                       "previous_values", []),
                                                                                       values_to_assign[iterator]]}

        # We may need to reduce the number of visits called here because I don't think they will be as useful as we may like otherwise
        # check to see if one or more values is being grabbed

        # check to see if assignment is happening to one or many targets

        # Assign values to targets as possible

    def report(self):
        pprint(self.stats)
        pprint(self.variable_data)

    def possible_variables(self):
        return dict([(variable_name, variable_value) for variable_name, variable_value in self.variable_data.items() if
                     variable_value.get("current_value", False) and len(
                         variable_value.get("previous_values", [])) == 1])


class PhYtographer_argparse(ast.NodeTransformer):
    def __init__(self):
        # Maybe allow for people to include argparse as ssomething else
        # But totally screw the from argparse import * nonsense
        self.argparse_variable_names = ["argparse"]
        self.found_arguments = []
        self.found_parsed_argument_handles = []

    def visit_Assign(self, node):
        # Find the instances of argparse that are an ArgumentParser and add them to the argparse_variable_names section
        if not hasattr(node.value, '__iter__'):
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Attribute):
                    if isinstance(node.value.func.value, ast.Name):
                        # Finds the Argparse instances of Argument Parser or similar
                        if node.value.func.value.id in self.argparse_variable_names and node.value.func.attr in [
                            "ArgumentParser", "add_argument_group", "add_mutually_exclusive_group"]:
                            self.argparse_variable_names.append(node.targets[0].id)
                            return None
                        # Finds parsed args variable names to replace with self later
                        if len(node.targets) == 1:
                            if hasattr(node.value, "func"):
                                if node.value.func.attr == "parse_args":
                                    if node.value.func.value.id in self.argparse_variable_names:
                                        self.found_parsed_argument_handles.append(node.targets[0].id)
                                        return None
        return node

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            if node.value.id in self.found_parsed_argument_handles:
                print("Found and replaced ", node.value.id, ".", node.attr)
                print(self.found_parsed_argument_handles)
                node.value.id = 'self'
                return node
        return node

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute):
                if node.value.func.attr in ["add_argument"]:
                    if isinstance(node.value.func.value, ast.Name):
                        if node.value.func.value.id in self.argparse_variable_names:
                            temp_found_argument = {"static": [], "keyword": {}}
                            for static_argument in node.value.args:
                                if isinstance(static_argument, ast.Str):
                                    temp_found_argument["static"].append(static_argument.s)
                            for keyword_argument in node.value.keywords:
                                if isinstance(keyword_argument, ast.keyword):
                                    if isinstance(keyword_argument.value, ast.Str):
                                        temp_found_argument["keyword"][keyword_argument.arg] = keyword_argument.value.s
                                    if isinstance(keyword_argument.value, ast.NameConstant):
                                        temp_found_argument["keyword"][
                                            keyword_argument.arg] = keyword_argument.value.value
                                    if isinstance(keyword_argument.value, ast.Num):
                                        temp_found_argument["keyword"][keyword_argument.arg] = keyword_argument.value.n
                            self.found_arguments.append(temp_found_argument)
                            return None
        return node


class Dektol:
    def __init__(self, file_name=""):
        self.module_handle = PhYtoModule(file_name)

        phytographer = PhYtographer_assistant()
        phytographer.visit(self.module_handle.parsed_ast_handle)

        arg_parse_theif = PhYtographer_argparse()
        arg_parse_theif.visit(self.module_handle.parsed_ast_handle)
        print(arg_parse_theif.found_arguments)
        print(arg_parse_theif.found_parsed_argument_handles)

        self.module_arguments = {"argparse": arg_parse_theif.found_arguments,
                                 "found": phytographer.possible_variables()}
        self.module_argument_names = [
            *[argument.get("static", [])[-1].lstrip('-').replace('-', '_') for argument in
              self.module_arguments.get("argparse", [])],
            *list(self.module_arguments.get("found", {}).keys())]

        self.module_imports = phytographer.stats.get("import_info", {})
        self.import_array = []  # This is an output section
        self.found_classes = phytographer.found_classes
        self.found_functions = phytographer.found_functions
        self.module_functions_by_name = phytographer.found_functions_by_name

    def get_ugly_source(self):
        return astor.to_source(self.create_whole_file_ast())

    def get_pretty_source(self):
        return autopep8.fix_code(self.get_ugly_source(), options={"experimental": True, "aggressive": 2})

    def create_whole_file_ast(self):
        whole_file = copy.deepcopy(skeleton.BASE_FILE)
        file_parts = [self.create_import_ast, self.create_module_definition_ast, self.create_bonus_class_ast_list,
                      self.create_bonus_function_ast_list]
        for file_part in file_parts:
            processed_file_part = file_part()
            if processed_file_part:
                if isinstance(processed_file_part, list):
                    whole_file.body += processed_file_part
                else:
                    whole_file.body += [processed_file_part]
        return whole_file

    def create_module_definition_ast(self):
        module_copy = copy.deepcopy(skeleton.MODULE_DEFINITION)
        module_copy.body.append(self.create_variable_block_ast())
        module_copy.body.append(self.create_execute_ast())
        module_copy.body.append(self.create_help_block_ast())
        return module_copy

    def create_help_block_ast(self):
        help_copy = copy.deepcopy(skeleton.HELP_FUNCTION_DEFINITON)
        help_copy.body[0].value.args[
            0].s = "This is the new help string, it will eventually be ALL OF THE COMMENTS SHOVED IN HERE"
        return help_copy

    def create_variable_block_ast(self):
        # deepcopy the variable definition block.
        arguments_array_object = copy.deepcopy(skeleton.ARGUMENTS_ARRAY)

        for argument_name, argument_values in self.module_arguments.get("found", {}).items():
            if isinstance(argument_values.get("current_value"), (int, float)):
                argument_item_object = copy.deepcopy(skeleton.ARGUMENTS_ARRAY_INT_ARGUMENT)
                argument_item_object.values[4].n = argument_values.get("current_value")
            else:
                argument_item_object = copy.deepcopy(skeleton.ARGUMENTS_ARRAY_STRING_ARGUMENT)
                argument_item_object.values[4].s = argument_values.get("current_value")
            argument_item_object.values[0].s = argument_name
            arguments_array_object.body[0].value.elts.append(argument_item_object)

        for argument in self.module_arguments.get("argparse", []):
            argument_replacements = {"type": {"location": 1, "call": "s"}, "nargs": {"location": 2, "call": "s"},
                                     "help": {"location": 3, "call": "s"}}
            if isinstance(argument.get("keyword", {}).get("default", ""), (int, float)):
                argument_item_object = copy.deepcopy(skeleton.ARGUMENTS_ARRAY_INT_ARGUMENT)
                argument_replacements["default"] = {"location": 4, "call": "n"}
            elif isinstance(argument.get("keyword", {}).get("default", ""), bool):
                argument_item_object = copy.deepcopy(skeleton.ARGUMENTS_ARRAY_BOOL_ARGUMENT)
                argument_replacements["default"] = {"location": 4, "call": "value"}
            else:
                argument_item_object = copy.deepcopy(skeleton.ARGUMENTS_ARRAY_STRING_ARGUMENT)
                argument_replacements["default"] = {"location": 4, "call": "s"}
            for name, replacement in argument_replacements.items():
                if name in argument.get("keyword", {}):
                    setattr(argument_item_object.values[replacement.get("location", 0)],
                            replacement.get("call", "s"),
                            argument["keyword"].get(name))
            argument_item_object.values[0].s = argument["static"][-1].lstrip('-').replace('-', '_')
            arguments_array_object.body[0].value.elts.append(argument_item_object)
        return arguments_array_object

    def create_import_ast(self):
        temp_import_array = []
        # Start with the General Imports that are of the style import blah, and import blah as halb
        for module in self.module_imports.get("general", []):
            temp_import = copy.deepcopy(skeleton.IMPORT_SETUP)
            temp_item = copy.deepcopy(skeleton.IMPORT_ITEM)
            temp_item.name = module.get("name", "")
            temp_import.names.append(temp_item)
            temp_import_array.append(temp_import)

        # Continue on to the imports that are of the style from blah import pants, or, dont, im, not, your, dad
        for module_name, module_values in self.module_imports.get("import_from").items():
            temp_import = copy.deepcopy(skeleton.IMPORT_FROM_SETUP)
            temp_import.module = module_name
            for item in module_values:
                temp_item = copy.deepcopy(skeleton.IMPORT_ITEM)
                temp_item.name = item.get("name", "")
                temp_import.names.append(temp_item)
            temp_import_array.append(temp_import)
        return temp_import_array

    def create_bonus_class_ast_list(self):
        return self.found_classes

    def create_bonus_function_ast_list(self):
        return self.found_functions

    def create_execute_ast(self):
        exploit_function = copy.deepcopy(skeleton.EXPLOIT_FUNCTION_DEFINITION)
        if self.module_handle:
            ## Remove all of the existances of Class definitions, Function definitions, imports, variable instantiation for identified variables
            blix_handle = PhYtographer_blix(variables_to_remove=self.module_argument_names)
            blix_result = blix_handle.visit(self.module_handle.parsed_ast_handle)

            ## Update identified variables to use self.variable_name
            classification_handle = PhYtography_classifyer(variables_to_classify=self.module_argument_names)
            classification_result = classification_handle.visit(blix_result)

            # Remove the if Main section and save some of the values for future processing
            demainer_handle = PhYtographer_demainer()
            demainer_result = demainer_handle.visit(classification_result)

            remainer_handle = PhYtographer_remainer(new_main=demainer_result.body,
                                                    functions_by_name=self.module_functions_by_name)
            remainer_result = remainer_handle.visit(demainer_result)

            # This should in theory remove the functions from the bonus functions
            for function in self.found_functions:
                if function.name in remainer_handle.function_names_to_delete:
                    self.found_functions.remove(function)

            exploit_function.body = remainer_result.body

            # Return a list containing the body of this converted module Until we get the partial result built.
        return exploit_function


class TestVisitor(ast.NodeVisitor):
    def __init__(self):
        pass

    def visit_Call(self, node):
        print(ast.dump(node))


def main():
    directory_for_running = "exploitdb\\exploits"
    maker_handle = PhYtoMaker(directory=directory_for_running)
    print(len(maker_handle.find_python_files()))
    print(len(maker_handle.find_not_python_files()))

    # dektol_handle = Dektol("playground.py")
    # print(dektol_handle.get_pretty_source())
    dektol_handle = Dektol("44422.py")

    # tv = TestVisitor()
    # tv.visit(dektol_handle.create_whole_file_ast())

    with open("phyto/testfile.py", "w") as test_write:
        test_write.write(dektol_handle.get_pretty_source())


if __name__ == "__main__":
    main()

# python -m greentreesnakes.astpp exploitdb/exploits/java/local/44422.py
