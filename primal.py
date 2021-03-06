#!/usr/bin/env python2.7
# Primal scheme by Josh Quick and Andy Smith 2016
# www.github.com/aresti/primalrefactor.git

import sys
import os
import argparse
import logging

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from primal.multiplex_reporting import MultiplexReporter
from primal.smart_reporting import SMARTplexReporter

logger = logging.getLogger('Primal Log')


def multiplex(args):
    #print(args)
    scheme = MultiplexReporter(args.references, args.amplicon_length, min_overlap=args.min_overlap, max_gap=args.max_gap,
                             max_alts=args.max_alts, max_candidates=args.max_candidates, step_size=args.step_size,
                             max_variation=args.max_variation, prefix=args.prefix)
    scheme.write_bed(args.output_path)
    scheme.write_pickle(args.output_path)
    scheme.write_tsv(args.output_path)
    scheme.write_SMARTplex(args.output_path)
    scheme.write_refs(args.output_path)
    scheme.write_schemadelica_plot(args.output_path)

def smart(args):
    print(args)
    sys.exit()
    scheme = SMARTplexReporter(args.references, args.amplicon_length, max_candidates=args.max_candidates, prefix=args.prefix)
    scheme.write_bed(args.output_path)
    scheme.write_pickle(args.output_path)
    scheme.write_tsv(args.output_path)
    scheme.write_refs(args.output_path)
    scheme.write_schemadelica_plot(args.output_path)


def main():
    parser = argparse.ArgumentParser(prog='primal', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(title='[sub-commands]', dest='command')

    # Standard scheme
    parser_scheme = subparsers.add_parser('multiplex', help='Multiplex PCR scheme')
    parser_scheme.add_argument('fasta', help='FASTA file')
    parser_scheme.add_argument('prefix', help='Prefix')
    parser_scheme.add_argument('--amplicon-length', help='Amplicon length (default: %(default)i)', type=int, default=400)
    parser_scheme.add_argument('--min-overlap', help='Minimum overlap length (default: %(default)i)', type=int, default=0)
    parser_scheme.add_argument('--max-gap', help='Maximum gap to introduce before failing (default: %(default)i)', type=int, default=200)
    parser_scheme.add_argument('--max-alts', help='Maximum number of alternate primers to output (default: %(default)i)', type=int, default=2)
    parser_scheme.add_argument('--max-candidates', help='Maximum candidate primers (default: %(default)i)', type=int, default=10)
    parser_scheme.add_argument('--step-size', help='Step size when moving left or right (default: %(default)i)', type=int, default=11)
    parser_scheme.add_argument('--max-variation', help='Variation in allowed product length (default: %(default)i)', type=float, default=0.1)
    parser_scheme.add_argument('--output-path', help='Output directory to save files (default: %(default)s)', default='./')
    parser_scheme.add_argument('--force', help='Force overwrite', action="store_true")
    parser_scheme.add_argument('--debug', help='Verbose logging', action="store_true")
    parser_scheme.set_defaults(func=multiplex)

    # SMART scheme
    parser_smart = subparsers.add_parser('smart', help='SMART-plex scheme')
    parser_smart.add_argument('fasta', help='FASTA file')
    parser_smart.add_argument('prefix', help='Prefix')
    parser_smart.add_argument('--amplicon-length', help='Amplicon length (default: %(default)i)', type=int, default=400)
    parser_smart.add_argument('--max-candidates', help='Maximum candidate primers (default: %(default)i)', type=int, default=10)
    parser_smart.add_argument('--output-path', help='Output directory to save files (default: %(default)s)', default='./')
    parser_smart.add_argument('--force', help='Force overwrite', action="store_true")
    parser_smart.add_argument('--debug', help='Verbose logging', action="store_true")
    parser_smart.set_defaults(func=smart)

    # Generate args
    args = parser.parse_args()
    args.references = []
    for record in SeqIO.parse(open(args.fasta, 'r'), 'fasta'):
        args.references.append(SeqRecord(Seq(str(record.seq).replace('-', '').upper()), id=record.id, description=record.id))

    # Check directory exists
    if os.path.isdir(args.output_path) and not args.force:
        logger.error('Directory exists add --force to overwrite')
        raise IOError('Directory exists add --force to overwrite')
        sys.exit()
    if not os.path.isdir(args.output_path):
        os.mkdir(args.output_path)

    # Logging
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    fh = logging.FileHandler(os.path.join(args.output_path, '{}.log'.format(args.prefix)))
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh_formatter = logging.Formatter('%(message)s')
    sh.setFormatter(sh_formatter)
    logger.addHandler(sh)

    logger.info('Primal scheme started...)')
    for arg in vars(args):
        logger.debug('{}: {}'.format(arg, str(vars(args)[arg])))

    for r in args.references:
        logger.info('Reference: {}'.format(r.id))

    # Run
    args.func(args)


if __name__ == '__main__':
    main()
