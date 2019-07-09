import argparse
import glob
import json
import os
import string
import subprocess
import sys


def collect_dependencies(ocaml_file, module_mapping):
    with open(ocaml_file, 'r') as f:
        lines = f.readlines()
    internal_dependencies = set()
    other_dependencies = set()
    for i in lines:
        if not i.startswith('open'):
            continue
        tokens = list(filter(None, i.split(' ')))
        dep = tokens[1].strip()
        if dep.lower() in module_mapping:
            internal_dependencies.add(module_mapping[dep.lower()])
        else:
            other_dependencies.add(dep)
    dependencies = {
        'internal_dependencies': list(sorted(internal_dependencies)),
        'other_dependencies': list(sorted(other_dependencies))}
    return dependencies


def print_dependencies(graph, f_filter=None):
    if f_filter is not None:
        graph = {k: graph[k] for k in f_filter}
    print(json.dumps(graph, indent=2))


DOTFILE_TEMPLATE = """
digraph dependency_graph {
    size="1000,1000";
    node [shape=record];
    # splines="compound";
    # concentrate=true;
%s
%s
}
"""
DOTFILE_LABEL_TEMPLATE = '    {symbol} [label="{label}"] ;'
DOTFILE_EDGE_TEMPLATE = '    {symbol1} -> {symbol2} ;'
DOTFILE_EDGE_HIGHLIGHT_TEMPLATE = '    {symbol1} -> {symbol2} [color=blue,weight=2] ;'


def get_dotfile_content(graph, f_filter=None):
    filtered_dependencies = get_filtered_dependencies(graph, f_filter)
    symbol_map = get_dotfile_symbol_map(graph, filtered_dependencies)
    edges, labels = get_dotfile_edges_labels(graph, symbol_map, f_filter, filtered_dependencies)
    content = DOTFILE_TEMPLATE % ('\n'.join(labels), '\n'.join(edges))
    return content


def get_dotfile_symbol_map(graph, filtered_dependencies):
    symbols = ['{}{}'.format(letter, number) for letter in string.ascii_lowercase for number in range(10)]
    if len(graph) >= len(symbols):
        print("ERROR: NOT ENOUGH SYMBOLS FOR DEP GRAPH")
        sys.exit(1)
    symbol_map = {k: symbols[index] for index, k in enumerate(graph)}
    if filtered_dependencies is not None:
        symbol_map = {k: symbol_map[k] for k in symbol_map if k in filtered_dependencies}
    return symbol_map


def get_dotfile_edges_labels(graph, symbol_map, f_filter, filtered_dependencies):
    labels = []
    edges = []
    for key, data in graph.items():
        if filtered_dependencies is not None and key not in filtered_dependencies:
            continue
        symbol = symbol_map[key]
        labels.append(DOTFILE_LABEL_TEMPLATE.format(symbol=symbol, label=key))
        if f_filter is not None and key not in f_filter:
            continue
        for v in data.get('internal_dependencies', []):
            target = symbol_map[v]
            edge = DOTFILE_EDGE_TEMPLATE.format(symbol1=symbol, symbol2=target)
            edges.append(edge)
    return edges, labels


def get_filtered_dependencies(graph, f_filter):
    if f_filter:
        filtered_dependencies = set()
        for key, data in graph.items():
            if key not in f_filter:
                continue
            filtered_dependencies.add(key)
            for v in data.get('internal_dependencies', []):
                filtered_dependencies.add(v)
    else:
        filtered_dependencies = None
    return filtered_dependencies


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file-filter')
    parser.add_argument('--dot-file', default='graph.dot')
    parser.add_argument('--png-file', default='graph.png')
    parser.add_argument('--source-dir', default=os.path.join(os.pardir, 'solvers'))
    parser.add_argument('--output-dir', default='out')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    try:
        file_filter = args.file_filter.split(',')
    except AttributeError:
        file_filter = None

    graph = {}
    ocaml_files = [f for f in glob.glob(os.path.join(args.source_dir, "*.ml"))]
    ocaml_filenames = [os.path.basename(f) for f in ocaml_files]
    module_mapping = {n[:-3].lower(): n for n in ocaml_filenames}

    for filepath in ocaml_files:
        filename = os.path.basename(filepath)
        graph[filename] = collect_dependencies(filepath, module_mapping)
    print_dependencies(graph, f_filter=file_filter)

    dot_file = os.path.join(args.output_dir, args.dot_file)
    content = get_dotfile_content(graph, f_filter=file_filter)
    with open(dot_file, 'w') as f:
        f.write(content)
    print('Wrote: {}'.format(dot_file))

    png_file = os.path.join(args.output_dir, args.png_file)
    subprocess.check_call('dot -Tpng {} > {}'.format(dot_file, png_file), shell=True)
    print('Wrote: {}'.format(png_file))


if __name__ == '__main__':
    main()
