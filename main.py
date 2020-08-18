"""
Web service for viewing Debian package info status files as HTML.
"""
import argparse
import collections
import sys

import dpkg_info
import web


def html_package_list(package_names):
    packages_ul = web.HTMLElement("ul")
    for package in package_names:
        package_li = web.HTMLElement("li")
        package_li.children.append(web.HTMLElement("a",
            text=package,
            attributes=['href="/packages/{:s}"'.format(package)]))
        packages_ul.children.append(package_li)

    packages_div = web.HTMLElement("div")
    packages_div.children.extend([
        web.HTMLElement("h1", text="packages"),
        packages_ul])

    return packages_div


def html_package_details(package, info, all_package_names):
    def dependency_link_if_exists(dep):
        if dep not in all_package_names:
            return web.HTMLElement("span", text=dep)
        package_href = 'href="/packages/{:s}"'.format(dep)
        return web.HTMLElement("a", text=dep, attributes=[package_href])

    package_div = web.HTMLElement("div")
    package_div.children.extend([
        web.HTMLElement("a", text="back to package list", attributes=['href="/"']),
        web.HTMLElement("h1", text=package),
        web.HTMLElement("div", text=info["description"]["short"])])

    if info["description"]["long"]:
        package_div.children.extend([
            web.HTMLElement("h2", text="description"),
            web.HTMLElement("div", text=info["description"]["long"])])

    if info["depends"]:
        depends_ul = web.HTMLElement("ul")
        for dep, *opt_deps in info["depends"]:
            li = web.HTMLElement("li")
            li.children.append(dependency_link_if_exists(dep))
            for opt_d in opt_deps:
                li.children.extend([
                    web.HTMLElement("span", text="|"),
                    dependency_link_if_exists(opt_d)])
            depends_ul.children.append(li)
        package_div.children.extend([
            web.HTMLElement("h2", text="dependencies"),
            depends_ul])

    if info["rdepends"]:
        rdepends_ul = web.HTMLElement("ul")
        for rdep in info["rdepends"]:
            li = web.HTMLElement("li")
            li.children.append(dependency_link_if_exists(rdep))
            rdepends_ul.children.append(li)
        package_div.children.extend([
            web.HTMLElement("h2", text="reverse dependencies"),
            rdepends_ul])

    return package_div


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", default="localhost", type=str)
    parser.add_argument("-p", "--port", default=8000, type=int)
    parser.add_argument("-f", "--dpkg-status-file", default="/var/lib/dpkg/status", type=str)
    args = parser.parse_args()

    package2info = dpkg_info.package_file_as_dict(args.dpkg_status_file)
    all_package_names = set(package2info.keys())

    def index_route():
        content = web.render_page(
                "base_template.html",
                html_package_list(package2info.keys()))
        return web.Response(200, content)

    def package_route(package_name):
        if package_name not in package2info:
            return web.error_response(404, "package '{}' not found".format(package_name))
        content = web.render_page(
                "base_template.html",
                html_package_details(package_name, package2info[package_name], all_package_names))
        return web.Response(200, content)

    with web.http_server(args.address, args.port) as server:
        server.route_handler.add("/", index_route)
        server.route_handler.add("/packages/{}", package_route)
        print("Starting server, listening on '{}:{}'".format(args.address, args.port))
        server.serve_forever()
