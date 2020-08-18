"""
Debian package info status file parser.
"""
import collections


def parse_file_sections(status_file_path):
    section = ''
    with open(status_file_path) as status_file:
        for line in status_file:
            if line.startswith('#'):
                continue
            if not line.rstrip():
                yield section
                section = ''
            else:
                section += line
    if section:
        yield section


def next_end(section, start):
    end = section.find('\n', start)
    return len(section) if end == -1 else end


def field_start_end(section, key):
    key += ": "
    start = section.find(key)
    if start < 0:
        return -1, 0
    start += len(key)
    return start, next_end(section, start)


def parse_name(section):
    start, end = field_start_end(section, "Package")
    return section[start:end]


def strip_version(dep):
    return dep if '(' not in dep else dep[:dep.find('(')].strip()


def parse_depends(section):
    start, end = field_start_end(section, "Depends")
    if start < 0:
        return []

    all_deps = section[start:end].split(',')
    unique_deps = []
    seen_deps = set()

    for opt_deps in all_deps:
        unique_opt_deps = []
        for opt_dep in opt_deps.split("|"):
            opt_dep = strip_version(opt_dep.strip())
            if opt_dep not in seen_deps:
                seen_deps.add(opt_dep)
                unique_opt_deps.append(opt_dep)
        if unique_opt_deps:
            unique_deps.append(unique_opt_deps)

    return unique_deps


def parse_description(section):
    start, end = field_start_end(section, "Description")
    short_desc = section[start:end]
    if not short_desc:
        return '', ''

    long_desc = ''
    start = end + 1
    while start < len(section) and section[start] in " \t":
        end = next_end(section, start)
        line = section[start:end]
        long_desc += '\n' if line.strip() == '.' else line
        start = end + 1

    return short_desc.strip(), long_desc.strip()


def package_file_as_dict(dpkg_status_file):
    package2info = collections.OrderedDict()

    for section in parse_file_sections(dpkg_status_file):
        short_desc, long_desc = parse_description(section)
        package2info[parse_name(section)] = {
            "depends": parse_depends(section),
            "rdepends": [],
            "description": {"short": short_desc, "long": long_desc}}

    for package, info in package2info.items():
        for opt_deps in info["depends"]:
            for dep in opt_deps:
                if dep in package2info:
                    package2info[dep]["rdepends"].append(package)

    return package2info
