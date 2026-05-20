working_memory = {}


def remember_working(key, value):
    working_memory[key] = value


def get_working(key, default=None):
    return working_memory.get(key, default)


def clear_working():
    working_memory.clear()