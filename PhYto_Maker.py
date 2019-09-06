import os
import re
import ast
import astor
import copy
import autopep8
from pprint import pprint
import phyto.module_skeleton
import phyto.phytographer


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

    def delete_not_python_files(self):
        for file_path_and_name in self.find_not_python_files():
            os.remove(file_path_and_name)




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


class Dektol:
    def __init__(self, file_name=""):
        self.file_name = file_name
        # We really should be calling 2to3 here and working off of modified code.
        self.file_data = self.get_file_data()
        self.parsed_ast_handle = ast.parse(self.file_data)

        self.raw_imports = []
        self.imported_modules = []

        phytographer = phyto.phytographerPhYtographer_assistant()
        phytographer.visit(self.parsed_ast_handle)

        arg_parse_theif = phyto.phytographerPhYtographer_argparse()
        arg_parse_theif.visit(self.parsed_ast_handle)
        print(arg_parse_theif.found_arguments)
        print(arg_parse_theif.found_parsed_argument_handles)

        self.module_arguments = {"argparse": arg_parse_theif.found_arguments,
                                 "found": phytographer.possible_variables()}
        # "quick" one-liner to pull all of the variable names from the module_arguments found during argparse and phytographer tree searches
        self.module_argument_names = [
            *[argument.get("static", [])[-1].lstrip('-').replace('-', '_') for argument in
              self.module_arguments.get("argparse", [])],
            *list(self.module_arguments.get("found", {}).keys())]

        self.module_imports = phytographer.stats.get("import_info", {})
        self.import_array = []  # This is an output section
        self.found_classes = phytographer.found_classes
        self.found_functions = phytographer.found_functions
        self.module_functions_by_name = phytographer.found_functions_by_name

    def get_file_data(self):
        file_handle = open(self.file_name, "r", encoding="ISO-8859-1")
        file_data = file_handle.read()
        file_handle.close()
        return file_data

    def get_ugly_source(self):
        return astor.to_source(self.create_whole_file_ast())

    def get_pretty_source(self):
        return autopep8.fix_code(self.get_ugly_source(), options={"experimental": True, "aggressive": 2})

    def create_whole_file_ast(self):
        whole_file = copy.deepcopy(phyto.module_skeleton.BASE_FILE)
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
        module_copy = copy.deepcopy(phyto.module_skeleton.MODULE_DEFINITION)
        module_copy.body.append(self.create_variable_block_ast())
        module_copy.body.append(self.create_execute_ast())
        module_copy.body.append(self.create_help_block_ast())
        return module_copy

    def create_help_block_ast(self):
        help_copy = copy.deepcopy(phyto.module_skeleton.HELP_FUNCTION_DEFINITON)
        help_copy.body[0].value.args[
            0].s = "This is the new help string, it will eventually be ALL OF THE COMMENTS SHOVED IN HERE"
        return help_copy

    def create_variable_block_ast(self):
        # deepcopy the variable definition block.
        arguments_array_object = copy.deepcopy(phyto.module_skeleton.ARGUMENTS_ARRAY)

        for argument_name, argument_values in self.module_arguments.get("found", {}).items():
            if isinstance(argument_values.get("current_value"), (int, float)):
                argument_item_object = copy.deepcopy(phyto.module_skeleton.ARGUMENTS_ARRAY_INT_ARGUMENT)
                argument_item_object.values[4].n = argument_values.get("current_value")
            else:
                argument_item_object = copy.deepcopy(phyto.module_skeleton.ARGUMENTS_ARRAY_STRING_ARGUMENT)
                argument_item_object.values[4].s = argument_values.get("current_value")
            argument_item_object.values[0].s = argument_name
            arguments_array_object.body[0].value.elts.append(argument_item_object)

        for argument in self.module_arguments.get("argparse", []):
            argument_replacements = {"type": {"location": 1, "call": "s"}, "nargs": {"location": 2, "call": "s"},
                                     "help": {"location": 3, "call": "s"}}
            if isinstance(argument.get("keyword", {}).get("default", ""), (int, float)):
                argument_item_object = copy.deepcopy(phyto.module_skeleton.ARGUMENTS_ARRAY_INT_ARGUMENT)
                argument_replacements["default"] = {"location": 4, "call": "n"}
            elif isinstance(argument.get("keyword", {}).get("default", ""), bool):
                argument_item_object = copy.deepcopy(phyto.module_skeleton.ARGUMENTS_ARRAY_BOOL_ARGUMENT)
                argument_replacements["default"] = {"location": 4, "call": "value"}
            else:
                argument_item_object = copy.deepcopy(phyto.module_skeleton.ARGUMENTS_ARRAY_STRING_ARGUMENT)
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
            temp_import = copy.deepcopy(phyto.module_skeleton.IMPORT_SETUP)
            temp_item = copy.deepcopy(phyto.module_skeleton.IMPORT_ITEM)
            temp_item.name = module.get("name", "")
            temp_import.names.append(temp_item)
            temp_import_array.append(temp_import)

        # Continue on to the imports that are of the style from blah import pants, or, dont, im, not, your, dad
        for module_name, module_values in self.module_imports.get("import_from").items():
            temp_import = copy.deepcopy(phyto.module_skeleton.IMPORT_FROM_SETUP)
            temp_import.module = module_name
            for item in module_values:
                temp_item = copy.deepcopy(phyto.module_skeleton.IMPORT_ITEM)
                temp_item.name = item.get("name", "")
                temp_import.names.append(temp_item)
            temp_import_array.append(temp_import)
        return temp_import_array

    def create_bonus_class_ast_list(self):
        return self.found_classes

    def create_bonus_function_ast_list(self):
        return self.found_functions

    def create_execute_ast(self):
        exploit_function = copy.deepcopy(phyto.module_skeleton.EXPLOIT_FUNCTION_DEFINITION)
        ## Remove all of the existances of Class definitions, Function definitions, imports, variable instantiation for identified variables
        blix_handle = phyto.phytographer.PhYtographer_blix(variables_to_remove=self.module_argument_names)
        blix_result = blix_handle.visit(self.parsed_ast_handle)

        ## Update identified variables to use self.variable_name
        classification_handle = phyto.phytographer.PhYtography_classifyer(
            variables_to_classify=self.module_argument_names)
        classification_result = classification_handle.visit(blix_result)

        # Remove the if Main section and save some of the values for future processing
        demainer_handle = phyto.phytographer.PhYtographer_demainer()
        demainer_result = demainer_handle.visit(classification_result)

        remainer_handle = phyto.phytographer.PhYtographer_remainer(new_main=demainer_result.body,
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
    dektol_handle = Dektol("argv_example.py")

    # tv = TestVisitor()
    # tv.visit(dektol_handle.create_whole_file_ast())

    with open("phyto/testfile.py", "w") as test_write:
        test_write.write(dektol_handle.get_pretty_source())


if __name__ == "__main__":
    main()

# python -m greentreesnakes.astpp exploitdb/exploits/java/local/44422.py
