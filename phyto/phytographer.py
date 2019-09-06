import ast
import copy
import phyto.module_skeleton


class PhYtographer_classifyer(ast.NodeTransformer):
    def __init__(self, variables_to_classify=[]):
        self.variables_to_classify = variables_to_classify

        # ast.Attribute(value=ast.Name(id='self', ctx=ast.Load(), lineno=33, col_offset=15), attr='apples', ctx=ast.Load(), lineno=33, col_offset=15)
        # Name(id='tuesday', ctx=Load(), lineno=36, col_offset=0)
        # Name(id='tuesday', ctx=Store(), lineno=36, col_offset=0)

    def visit_Name(self, node):
        if node.id in self.variables_to_classify:
            new_node = copy.deepcopy(phyto.module_skeleton.VARIABLE_SELF_REPLACEMENT)
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
