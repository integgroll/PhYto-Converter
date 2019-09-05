import argparse
import importlib


def main():
    argument_parser = argparse.ArgumentParser(
        description="PhYto is all about making better Python exploits, in Python 3", add_help=False)
    argument_parser.add_argument("module_name", type=str,
                                 help="Need a module name you can search for them on exploitdb")
    arguments, module_arguments = argument_parser.parse_known_args()

    module_handle = importlib.import_module("modules.{module_name}".format(module_name=arguments.module_name))
    tots_module_for_execution = module_handle.PhYtoModule(module_arguments)

    tots_module_for_execution.execute()


if __name__ == "__main__":
    main()
