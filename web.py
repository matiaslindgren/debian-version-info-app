"""
Tiny web framework that renders HTML content for GET requests.
"""
import collections
import http.server
import string


def render_page(base_template_path, body):
    with open(base_template_path) as base_template:
        base_content = base_template.read()
    return string.Template(base_content).substitute(body=body)


class HTMLElement:

    def __init__(self, tag, text='', attributes=None):
        self.tag = tag
        self.text = text
        self.attributes = attributes
        self.children = []

    def __str__(self):
        if self.attributes:
            res = "<{:s} {:s}>".format(self.tag, ' '.join(self.attributes))
        else:
            res = "<{:s}>".format(self.tag)
        res += '\n'.join(str(child) for child in self.children)
        res += self.text
        res += "</{:s}>".format(self.tag)
        return res


Response = collections.namedtuple("Response", ["code", "content"])


def error_response(code, msg):
    content = HTMLElement("div")
    content.children.extend([
        HTMLElement("h1", text="{:d} - error".format(code)),
        HTMLElement("p", text=msg)])
    return Response(code, render_page("base_template.html", content))


class RequestHandler(http.server.BaseHTTPRequestHandler):

    def do_response(self, response):
        self.send_response(response.code)
        self.send_header("Content-Type", "text/html; charset=UTF-8")
        self.send_header("Content-Length", len(response.content))
        self.end_headers()
        self.wfile.write(response.content.encode("utf-8"))

    def do_GET(self):
        self.protocol_version = self.request_version
        handler, args = self.server.route_handler.get(self.path)
        if handler:
            self.do_response(handler(*args))
        else:
            self.do_response(error_response(404, "'{}' not found".format(self.path)))


class RouteHandler:

    @staticmethod
    def split_path(path):
        return [p for p in path.split("/") if p]

    def __init__(self):
        self.routes = []

    def add(self, route, handler):
        self.routes.append((self.split_path(route), handler))

    def get(self, request_path):
        """
        Given a request_path, e.g. /packages/python-dev, search through all routes for a match.
        If a match is found, return (handler, args), else return (None, []).
        E.g. for route '/packages/{}', the return value would be (handler, ["python-dev"]).
        """
        request_parts = self.split_path(request_path)
        for route_parts, handler in self.routes:
            if len(route_parts) != len(request_parts):
                continue
            handler_args = []
            for route_part, request_part in zip(route_parts, request_parts):
                if route_part == "{}":
                    handler_args.append(request_part)
                    continue
                if route_part == request_part:
                    continue
                break
            else:
                return handler, handler_args
        return None, []


def http_server(address, port):
    server = http.server.ThreadingHTTPServer((address, port), RequestHandler)
    server.route_handler = RouteHandler()
    return server
