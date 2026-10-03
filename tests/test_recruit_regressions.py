import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from scarab import utilities, clusterer, abundance_recruiter
from subprocess import CalledProcessError

class RecruitmentRegressions(unittest.TestCase):
    def test_manual_overrides_reach_effective_parameters(self):
        defaults=dict(d_min_clust=5,d_min_samp=None,a_min_clust=5,a_min_samp=None,nu=.5,gamma='scale',setting='Default')
        with patch.object(utilities,'calc_entropy'),patch.object(utilities,'run_param_match',return_value=('algo_defaults','Default',defaults)):
            _,_,params=utilities.set_clust_params(9,2,11,3,.1,'auto',None,None,None,None,'algo_defaults','unused','unused')
        self.assertEqual([params[k] for k in ('d_min_clust','d_min_samp','a_min_clust','a_min_samp','nu','gamma')],[9,2,11,3,.1,'auto'])
        self.assertEqual(defaults['d_min_clust'],5)
    def test_custom_kmer_and_minimum_similarity(self):
        original=pd.DataFrame({'sag_id':['s','s','s'],'q_contig_id':['a','b','c'],'jacc_sim':[.7,.8,.95]})
        all_hits,anchors=clusterer.trusted_hits({31:original},.8)
        self.assertEqual(list(anchors.contig_id),['b','c'])
        self.assertIn('q_contig_id',original)
        self.assertTrue(clusterer.trusted_hits(False,1)[1].empty)
    def test_mapping_failure_removes_partial_sam_and_propagates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);read=root/'sample.one.fastq';read.write_text('@r\nAC\n+\nII\n')
            with patch.object(abundance_recruiter,'Popen') as popen:
                popen.return_value.returncode=17
                with self.assertRaises(CalledProcessError):
                    abundance_recruiter.runMiniMap2(tmp,tmp,'mg',[str(read)],False,1)
            self.assertFalse((root/'sample.one.sam').exists())
    def test_paired_mapping_passes_distinct_mates_and_private_temp_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            reads=[root/'sample.R1.fastq',root/'sample.R2.fastq']
            for read in reads: read.write_text('@r\nAC\n+\nII\n')
            with patch.object(abundance_recruiter,'Popen') as popen:
                popen.return_value.returncode=0
                abundance_recruiter.runMiniMap2(tmp,tmp,'mg',list(map(str,reads)),False,2)
            command=popen.call_args.args[0]
            self.assertEqual(command[-2:],list(map(str,reads)))
            self.assertIn('--split-prefix='+str(root/'sample.R1.minimap-tmp'),command)
    def test_unanchored_path_and_noise_are_not_exported_as_a_bin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            ids=[f'c{i}_0' for i in range(25)]
            # Supply valid cached embeddings and cluster assignments, isolating
            # denoising and unanchored return behavior from UMAP fitting.
            pd.DataFrame({'subcontig_id':ids,'x':np.arange(25)}).to_csv(root/'mg.merged_emb.tsv',sep='\t',index=False)
            pd.DataFrame({'subcontig_id':ids,'label':[-1]*25,'probabilities':[0.]*25,'outlier_score':[0.]*25,'contig_id':[f'c{i}' for i in range(25)]}).to_csv(root/'mg.denovo_hdbscan.tsv',sep='\t',index=False)
            # Serial pool facade avoids requiring OS process creation in tests.
            class Pool:
                def __init__(self,**kwargs): pass
                def imap_unordered(self,fn,args): return map(fn,args)
                def close(self): pass
                def join(self): pass
            with patch.object(clusterer.multiprocessing,'Pool',Pool):
                for trusted in (False,{31:pd.DataFrame(columns=['sag_id','q_contig_id','jacc_sim'])}):
                    results=clusterer.runClusterer('mg',tmp,tmp,'unused','unused',trusted,5,None,5,None,.5,'scale',1,1)
                    self.assertTrue(results[0].empty)
                    self.assertEqual(results[1:],(False,False,False))
            self.assertEqual(len(pd.read_csv(root/'mg.denovo_noise.tsv',sep='\t')),25)

if __name__=='__main__': unittest.main()
