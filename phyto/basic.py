import argparse
import importlib


class CombineAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(CombineAction, self).__init__(option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, " ".join(values))

class Exploit():
    def __init__(self, provided_argument_string):
        module_argument_parser = argparse.ArgumentParser(description=self.help())

        for argument in self.global_arguments():
            module_argument_parser.add_argument("--{field}".format(field=argument.get("name", "missing_name")),
                                                type=argument.get("type", str),
                                                nargs=argument.get("nargs", "+"),
                                                action=CombineAction,
                                                default=argument.get("default", ""),
                                                help=argument.get("help", "You need a {name}".format(
                                                    name=argument.get("name", "missing_name"))))

        parsed_module_arguments = module_argument_parser.parse_args(provided_argument_string)
        self.__dict__.update(parsed_module_arguments.__dict__)

    def exploit_arguments(self):
        return []

    def global_arguments(self):
        # local_arguments is a function that is pulled from the class that is using this as a super class
        return self.local_arguments() + self.exploit_arguments()