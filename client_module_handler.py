import json
import types
import client_module_inspector as mi

FUNC_TYPE = mi.FUNC_TYPE


def generate_module_file(module_name, module_construct):
    file = open(module_name + ".py", "w")
    file.write(module_construct)
    file.close()


def load_module(module_name, proxy_reference):
    module = __import__(module_name)
    module.reference = proxy_reference
    return module


def compile_module(module_name, module_construct, proxy_reference):
    module = types.ModuleType(module_name)
    code = compile(module_construct, '', 'exec')

    exec(code, module.__dict__)
    module.reference = proxy_reference
    return module


def get_instance(module, class_name):
    cls = getattr(module, class_name)
    return cls()


def exec_func(module, func_name, *args):
    func = getattr(module, func_name)
    return func(*args)


def _construct_imports():
    return "import client_socket_handler as sh\nimport client_packet\nfrom log import log\nfrom queue import Queue\n"


def _construct_proxy_ref():
    return "reference = None\n"

def _construct_results_queue():
    return "results_queue = Queue()\n"


def _construct_proxy_funcs():
    result = ''

    result += "def _call_server(host_cls, func_type, func_name, *func_args):\n%s\n" % \
              '''
    func_call = str(dict(host_cls=host_cls, func_type=func_type, name=func_name, args=func_args)).replace('\\\'', '\\\"').replace('(', '[').replace(')', ']').replace(',]', ']')
    pk = client_packet.Packet(func_call, client_packet.PACKET_ID_FUNC_CALL)
    reference.send_packet(pk)
          '''
    return result


def _construct_function(func_name, func_type, func_args, host_cls=''):
    result = ''

    # TODO: add annotation inspection

    indentation_count = 0

    if func_type == FUNC_TYPE.MODULE_FUNC.value:
        indentation_count = 0
    elif func_type == FUNC_TYPE.INSTANCE_FUNC.value:
        indentation_count = 1
    elif func_type == FUNC_TYPE.CLASS_FUNC.value:
        indentation_count = 1
    elif func_type == FUNC_TYPE.PROPERTY_FUNC.value:
        indentation_count = 1
    elif func_type == FUNC_TYPE.STATIC_FUNC.value:
        indentation_count = 1

    result += "\t" * indentation_count

    result += "def %s(" % func_name

    result += ", ".join(func_args)
    result += "):\n" + "\t" * (indentation_count + 1)

    for i in range(len(func_args)):
        args = func_args[i]
        if '=' in args:
            func_args[i] = args[:args.index('=')]

    result += "_call_server(%s, %s, %s, %s)" % (
            ("\"%s\"" % host_cls), str(func_type), ("\"%s\"" % func_name), (", ".join(func_args))) + "\n" + "\t" * (indentation_count + 1)
    result += "return results_queue.get()"
    return result


def _construct_class(cls_name, func_names, func_types, func_args):
    result = ''

    result += "class %s:\n" % cls_name

    for i in range(len(func_names)):
        # TODO implement func type checking
        result += _construct_function(func_names[i], func_types[i], func_args[i], host_cls=cls_name)
        result += "\n"

    return result


def construct_module(module_data):
    module_name, module = '', ''

    data = json.loads(module_data)

    module_name = data["name"]
    classes = data["classes"]
    funcs = data["functions"]

    module += _construct_imports()
    module += "\n" * 2

    module += _construct_proxy_ref()
    module += "\n" * 2

    module += _construct_results_queue()
    module += "\n" * 2

    module += _construct_proxy_funcs()
    module += "\n" * 2

    for func_name, func_data in funcs.items():
        module += _construct_function(func_name, func_data["type"], func_data["args"])
        module += '\n' * 2

    for class_name, class_data in classes.items():
        func_names = list(class_data["functions"].keys())
        func_types = list(class_data["functions"][x]["type"] for x in func_names)
        func_args = list(class_data["functions"][x]["args"] for x in func_names)

        module += _construct_class(class_name, func_names, func_types, func_args)
        module += '\n'

        module = module.replace("\t", " " * 4)

    return module_name, module
