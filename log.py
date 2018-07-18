import inspect
import threading

ADD_TAGS = False
DEBUG = False


def log(*args, **kwargs):
    if not DEBUG:
        return

    if not ADD_TAGS:
        print(*args, **kwargs)
        return

    inspection_stack = inspect.stack()[1]
    calling_module = inspection_stack[1]
    calling_func = inspection_stack[3]
    thread_name = threading.current_thread().name

    pre = ''
    pre += "[%s]" % thread_name
    pre += "[%s]" % (calling_module[calling_module.rfind("\\") + 1:])
    pre += "[%s]" % calling_func

    print(pre, *args, **kwargs)
