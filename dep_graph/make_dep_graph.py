import argparse
import glob
import json
import os
import string
import subprocess
import sys
from collections import defaultdict


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
        'other_dependencies': list(sorted(other_dependencies)),
        'depth': None
    }
    return dependencies


def print_dependencies(graph, f_filter=None):
    if f_filter is not None:
        graph = {k: graph[k] for k in f_filter}
    print(json.dumps(graph, indent=2))
    print('Graph size: ', len(graph))


DOTFILE_TEMPLATE = """
digraph dependency_graph {
    /* top-level graph settings */
    size="1000,1000";
    %s 
    node [shape=record];
    # splines="compound";
    # concentrate=true;
    /* the depth graph */
    %s
    /* the labels */
%s
    /* the edges */
%s
    /* ranks */
%s
}
"""
DOTFILE_LABEL_TEMPLATE = '    {symbol} [label="{label}"] ;'
DOTFILE_EDGE_TEMPLATE = '    {symbol1} -> {symbol2} ;'
DOTFILE_EDGE_HIGHLIGHT_TEMPLATE = '    {symbol1} -> {symbol2} [color=blue,weight=2] ;'


def get_dotfile_ranks(graph, symbol_map, max_depth, filtered_dependencies):
    ranks = []
    for d in range(max_depth + 1):
        level = 'depth{}'.format(d)
        equal_ranks = [level]
        for key in [k for k, v in graph.items() if v['depth'] == d]:
            if key not in filtered_dependencies:
                continue
            equal_ranks.append(symbol_map[key])
        ranking = "    {rank = same; %s }" % '; '.join(equal_ranks)
        ranks.append(ranking)
    return ranks


def get_dotfile_content(graph, ignore_depths=False, filtered_dependencies=None):
    symbol_map = get_dotfile_symbol_map(graph)
    if ignore_depths:
        depths = ''
        ranks = []
        ranksep = ''
    else:
        ranksep = 'ranksep=2;'
        try:
            max_depth = max(filter(None, [d['depth'] for d in graph.values()]))
        except ValueError:
            depths = ''
            ranks = []
        else:
            depths = ' -> '.join(['depth{}'.format(d) for d in range(max_depth+1)]) + ' [style=dotted];'
            ranks = get_dotfile_ranks(graph, symbol_map, max_depth, filtered_dependencies)
    edges, labels = get_dotfile_edges_labels(graph, symbol_map, filtered_dependencies, ignore_depths)
    content = DOTFILE_TEMPLATE % (ranksep, depths, '\n'.join(labels), '\n'.join(edges), '\n'.join(ranks))
    return content


def get_dotfile_symbol_map(graph):
    symbols = ['{}{}'.format(letter, number) for letter in string.ascii_lowercase for number in range(10)]
    if len(graph) >= len(symbols):
        print("ERROR: NOT ENOUGH SYMBOLS FOR DEP GRAPH")
        sys.exit(1)
    symbol_map = {k: symbols[index] for index, k in enumerate(graph)}
    return symbol_map


def get_dotfile_edges_labels(graph, symbol_map, filtered_dependencies, ignore_depths):
    labels = []
    edges = []
    for key, data in graph.items():
        if filtered_dependencies is not None and key not in filtered_dependencies:
            continue
        symbol = symbol_map[key]
        labels.append(DOTFILE_LABEL_TEMPLATE.format(symbol=symbol, label=key))
        for v in data.get('internal_dependencies', []):
            if filtered_dependencies is not None and v not in filtered_dependencies:
                continue
            try:
                if not ignore_depths and graph[v]['depth'] <= data['depth']:
                    print('WARN: skipping edge to previous or adjacent layer: {} -> {}'.format(key, v))
                    continue
            except TypeError:
                pass
            target = symbol_map[v]
            edge = DOTFILE_EDGE_TEMPLATE.format(symbol1=symbol, symbol2=target)
            edges.append(edge)
    return edges, labels


def get_filtered_dependencies(graph, f_filter):
    filtered_dependencies = set()
    for key, data in graph.items():
        if key not in f_filter:
            continue
        filtered_dependencies.add(key)
        for v in data.get('internal_dependencies', []):
            filtered_dependencies.add(v)
    return filtered_dependencies


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file-filter')
    parser.add_argument('--ignore-depths', default=False, action='store_true')
    parser.add_argument('--trace-depth', default=1, type=int)
    parser.add_argument('--dot-file', default='graph.dot')
    parser.add_argument('--png-file', default='graph.png')
    parser.add_argument('--source-dir', default=os.path.join(os.pardir, 'solvers'))
    parser.add_argument('--output-dir', default='out')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    max_depth = args.trace_depth
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

    filtered_dependencies = set_graph_depths(graph, max_depth, file_filter)
    print_dependencies(graph, f_filter=filtered_dependencies)

    dot_file = os.path.join(args.output_dir, args.dot_file)
    content = get_dotfile_content(
        graph,
        args.ignore_depths,
        filtered_dependencies=filtered_dependencies)
    with open(dot_file, 'w') as f:
        f.write(content)
    print('Wrote: {}'.format(dot_file))

    png_file = os.path.join(args.output_dir, args.png_file)
    subprocess.check_call('dot -Tpng {} > {}'.format(dot_file, png_file), shell=True)
    print('Wrote: {}'.format(png_file))


def set_graph_depths(graph, max_depth, file_filter):
    if file_filter is not None:
        for k, v in graph.items():
            if k in file_filter:
                print(k)
                v['depth'] = 0
                for dep in graph[k]['internal_dependencies']:
                    if graph[dep]['depth'] is None:
                        graph[dep]['depth'] = 1
    if file_filter is not None:
        filtered_dependencies = get_filtered_dependencies(graph, file_filter)
    else:
        filtered_dependencies = None
    if max_depth > 1 and file_filter is not None:
        for depth in range(2, max_depth + 1):
            prev_depth_filenames = [k for k, v in graph.items() if v['depth'] == depth - 1]
            for prev_depth_filename in prev_depth_filenames:
                for dep in graph[prev_depth_filename]['internal_dependencies']:
                    if graph[dep]['depth'] is None:
                        graph[dep]['depth'] = depth
                        filtered_dependencies.add(dep)
    return filtered_dependencies


if __name__ == '__main__':
    main()
