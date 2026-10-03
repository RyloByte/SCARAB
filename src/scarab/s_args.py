__author__ = 'Ryan J McLaughlin'

import argparse
from argparse import RawTextHelpFormatter


class ScarabArgumentParser(argparse.ArgumentParser):
    """
    A base argparse ArgumentParser for SCARAB with functions to furnish with common arguments.
    This standardizes the interface for a unified aesthetic across all sub-commands
    """

    def __init__(self, **kwargs):
        """
        Instantiate the argparse argument-parser and create three broad argument groups:
            reqs - for the required parameters
            optopt - for the optional parameters
            miscellany - for the miscellaneous parameters that are module agnostic,
            for example verbose, help, num_threads
        :param kwargs:
        """
        super(ScarabArgumentParser, self).__init__(add_help=False,
                                                  formatter_class=RawTextHelpFormatter,
                                                  **kwargs
                                                  )
        self.reqs = self.add_argument_group("Required parameters")
        self.seqops = self.add_argument_group("Sequence operation arguments")
        self.optopt = self.add_argument_group("Optional options")
        self.miscellany = self.add_argument_group("Miscellaneous options")

        self.miscellany.add_argument("-v", "--verbose", action="store_true", default=False,
                                     help="Prints a more verbose runtime log")
        self.miscellany.add_argument("-h", "--help",
                                     action="help",
                                     help="Show this help message and exit")

    def parse_args(self, args=None, namespace=None):
        args = super(ScarabArgumentParser, self).parse_args(args=args, namespace=namespace)

        if hasattr(args, 'mg_file'):
            for name in ('max_contig_len', 'min_len', 'kmer_size', 'nthreads'):
                try:
                    value = int(getattr(args, name))
                except (ValueError, TypeError):
                    self.error(f'{name} must be an integer')
                if value < 1: self.error(f'{name} must be positive')
                setattr(args, name, value)
            try:
                args.overlap_len = int(args.overlap_len)
                args.jaccard = float(args.jaccard)
            except (ValueError, TypeError):
                self.error('overlap_len must be an integer and jaccard a number')
            if not 0 <= args.overlap_len < args.max_contig_len:
                self.error('overlap_len must be nonnegative and smaller than max_contig_len')
            if args.min_len > args.max_contig_len:
                self.error('min_len must not exceed max_contig_len')
            if not 0 <= args.jaccard <= 1: self.error('jaccard must be between 0 and 1')
            import re
            if not re.fullmatch(r'[1-9][0-9]*[mMgG]', args.dedupe_memory):
                self.error('dedupe_memory must be a positive integer followed by m or g')
            if args.auto_params not in ('algo_defaults', 'majority_rule', 'best_cluster', 'best_match'):
                self.error('Unknown autoopt method')
            if sum(bool(getattr(args, x)) for x in ('vr_params','r_params','s_params','vs_params')) > 1:
                self.error('Select only one relaxed/strict preset')
            for name in ('denovo_min_clust','anchor_min_clust','denovo_min_samp','anchor_min_samp'):
                value = getattr(args, name)
                if value is not None:
                    try: value = int(value)
                    except ValueError: self.error(f'{name} must be an integer')
                    if value < (2 if name.endswith('clust') else 1): self.error(f'{name} is too small')
                    setattr(args, name, value)
            if args.nu is not None:
                try: args.nu = float(args.nu)
                except ValueError: self.error('nu must be numeric')
                if not 0 < args.nu <= 1: self.error('nu must be in (0,1]')
            if args.gamma is not None and args.gamma not in ('scale','auto'):
                try: args.gamma = float(args.gamma)
                except ValueError: self.error('gamma must be scale, auto, or a positive number')
                import math
                if not math.isfinite(args.gamma) or args.gamma <= 0: self.error('gamma must be positive and finite')
        return args

    def add_recruit_args(self):
        self.reqs.add_argument("-m", "--metag", required=True, dest="mg_file",
                               help="Path to a metagenome assembly [FASTA format only]."
                               )
        self.reqs.add_argument("-l", "--metaraw", required=True, dest="mg_raw_file_list",
                               help="Text file containing paths to raw FASTQ files for samples.\n"
                                    "One file per line, supports interleaved and separate PE reads.\n"
                                    "For separate PE files, both file paths on one line sep by [tab].\n"
                               )
        self.reqs.add_argument("-o", "--output-dir", required=True, dest="save_path",
                               help="Path to directory for all outputs."
                               )
        self.reqs.add_argument("-s", "--trusted-contigs", required=False, dest="trust_path",
                               default=False, help="Path to reference FASTA file or directory "
                                                   "containing only FASTA files."
                               )
        self.optopt.add_argument("--autoopt", dest="auto_params", default='algo_defaults',
                                 help="select which automatic optimization algorithm parameter set to use,\n"
                                      "[algorithm default], majority_rule, best_cluster, best_match."
                                 )
        self.optopt.add_argument("--very_relaxed", action='store_const', const="very_relaxed",
                                 dest="vr_params",
                                 help="parameter-set that maximizes recall at approximately strain-level"
                                 )
        self.optopt.add_argument("--relaxed", action='store_const', const="relaxed",
                                 dest="r_params",
                                 help="parameter-set that maximizes recall at substrain-level."
                                 )
        self.optopt.add_argument("--strict", action='store_const', const="strict",
                                 dest="s_params",
                                 help="parameter-set that maximizes precision at approximately strain-level."
                                 )
        self.optopt.add_argument("--very_strict", action='store_const', const="very_strict",
                                 dest="vs_params",
                                 help="parameter-set that maximizes precision at substrain-level."
                                 )
        self.optopt.add_argument("--denovo_min_clust", required=False, dest="denovo_min_clust",
                                 help="minimum cluster size for De Novo HDBSCAN clustering."
                                 )
        self.optopt.add_argument("--anchor_min_clust", required=False, dest="anchor_min_clust",
                                 help="minimum cluster size for Anchored HDBSCAN clustering."
                                 )
        self.optopt.add_argument("--denovo_min_samp", required=False, dest="denovo_min_samp",
                                 help="minimum sample number for De Novo HDBSCAN clustering."
                                 )
        self.optopt.add_argument("--anchor_min_samp", required=False, dest="anchor_min_samp",
                                 help="minimum sample number for De Anchored HDBSCAN clustering."
                                 )
        self.optopt.add_argument("--nu", required=False, dest="nu",
                                 help="nu setting for Anchored OC-SVM clustering."
                                 )
        self.optopt.add_argument("--gamma", required=False, dest="gamma",
                                 help="gamma setting for Anchored OC-SVM clustering."
                                 )
        self.optopt.add_argument("--max_contig_len", required=False, default=10000,
                                 dest="max_contig_len",
                                 help="Max subcontig length in basepairs [10000]."
                                 )
        self.optopt.add_argument("--overlap_len", required=False, default=2000,
                                 dest="overlap_len",
                                 help="subcontig overlap in basepairs [2000]."
                                 )
        self.optopt.add_argument("--min_len", required=False, default=2000,
                                 dest="min_len",
                                 help="minimum length of contigs to include in basepairs [2000]."
                                 )
        self.optopt.add_argument("--kmer_size", required=False, default=201,
                                 dest="kmer_size",
                                 help="kmer length to use for minhash step [201]."
                                 )
        self.optopt.add_argument("--jaccard", required=False, default=1.0,
                                 dest="jaccard",
                                 help="minimum jaccard index to ID contigs as trusted [1.0]."
                                 )
        self.optopt.add_argument("--pacbio", required=False, default=False,
                                 action="store_true",
                                 help="Set if raw reads are PacBio Hifi [False]"
                                 )
        self.miscellany.add_argument("-t", "--num_threads", required=False, default=1,
                                     dest="nthreads",
                                     help="Number of threads [1]."
                                     )
        self.miscellany.add_argument("--dedupe_memory", default="4g",
                                     help="BBTools Java heap limit, e.g. 4g or 512m [4g].")
        self.miscellany.add_argument("--force", required=False, default=False,
                                     action="store_true",
                                     help="Preserve existing output in a sibling backup and start a fresh run [False]"
                                     )
        return
