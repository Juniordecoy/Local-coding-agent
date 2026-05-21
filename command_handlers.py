from web_tools import (
    find_text_usage,
    find_function_usage,
    trace_button,
    trace_route,
    trace_endpoint,
    trace_id,
)


def find_usage_command(user_message):
    search_text = user_message.replace("find usage ", "", 1)

    return find_text_usage(search_text)


def find_function_command(user_message):
    function_name = user_message.replace("find function ", "", 1)

    return find_function_usage(function_name)


def trace_button_command(user_message):
    button_id = user_message.replace("trace button ", "", 1)

    return trace_button(button_id)


def trace_route_command(user_message):
    route_name = user_message.replace("trace route ", "", 1)

    return trace_route(route_name)


def trace_endpoint_command(user_message):
    endpoint = user_message.replace("trace endpoint ", "", 1)

    return trace_endpoint(endpoint)

def trace_id_command(user_message):
    element_id = user_message.replace("trace id ", "", 1)

    return trace_id(element_id)