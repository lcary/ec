import argparse
import datetime
import json
import os

import matplotlib.pyplot as plt


def get_timestamp_str() -> str:
    return datetime.datetime.now().strftime('%Y%m%d_T%H%M%S')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('loss_data_file', help='previous loss data file', nargs='*')
    parser.add_argument('-o', '--output-dir', default='out')
    parser.add_argument('-d', '--show-dreaming', default=False, action='store_true')
    parser.add_argument('-l', '--show-legend', default=False, action='store_true')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    files = args.loss_data_file
    os.makedirs(args.output_dir, exist_ok=True)
    fig = plt.figure()
    add_plots_to_figure(args, files)
    ts = get_timestamp_str()
    fpath = os.path.join(args.output_dir, f'performance_graph_{ts}.png')
    print(f'saving graph of model performance to {fpath}')
    fig.savefig(fpath, dpi=fig.dpi)


def add_plots_to_figure(args, files):
    start_times = []
    for filepath in files:
        with open(filepath, 'r') as infile:
            data = json.load(infile)
        plot_real_losses(data, start_times)
        if not args.show_dreaming:
            continue
        plot_dream_losses(data, start_times)
    if args.show_legend:
        plt.legend(start_times, loc='upper right')
    plt.xlabel('Number of training examples seen')
    plt.ylabel('Negative log likelihood loss')


def plot_real_losses(data, start_times):
    losses = [d['loss'] for epoch in data['records'] for d in epoch['losses'] if not d['dreaming']]
    counts = [d['count'] for epoch in data['records'] for d in epoch['losses'] if not d['dreaming']]
    plt.plot(counts, losses)
    start_times.append('Train loss (start time: {} w/out dreaming)'.format(int(data['start_timestamp'])))


def plot_dream_losses(data, start_times):
    losses = [d['loss'] for epoch in data['records'] for d in epoch['losses'] if d['dreaming']]
    if not losses:
        return
    counts = [d['count'] for epoch in data['records'] for d in epoch['losses'] if d['dreaming']]
    plt.plot(counts, losses)
    start_times.append('Train loss (start time: {} w/ dreaming)'.format(int(data['start_timestamp'])))


if __name__ == '__main__':
    main()
