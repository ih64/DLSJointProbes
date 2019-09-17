import numpy as np
from os.path import join, exists
import pandas as pd
import yaml
import treecorr

class io():
    def __init__(self, realization, rand_root='/home/ishasan/DLS_randoms_4096'):
        self.flask_rand = join(rand_root,'rand_4096_{}.dat'.format(realization))
    
#    def __init__(self, realization,  filename='config.yaml'):
#        self.realization = realization
#        # sanatize the yaml file
#        config_keys = ['out_path', 'random_path', 'random_prefix']
#        with open(filename,'r') as f:
#            config = yaml.load(f)
#            self.flask_dict = config['flask']
#            self.flask_rand = self.flask_dict['flask_rand']
#            assert exists(self.flask_dict['flask_rand']), 'cant find the flask random catalog'
            # TODO
            # fragile
            
            
    def setup_FLASK_cats(self, cat_path):
        '''
        quick messy helper to make the flask source
        lens and random catalogs
        '''
#        names = ['alpha', 'delta','z', 'e1','e2','z_bin', 'pixel'] 
        flask_cat = pd.read_csv(cat_path, index_col=0)

        lens_mask = flask_cat['z_bin'].isin([1,2,3])
        lens_table = flask_cat[lens_mask]
        
        source_mask = flask_cat['z_bin'].isin([4,5,6])
        source_table = flask_cat[source_mask]

        randoms = pd.read_csv(self.flask_rand, index_col=0)
        # TODO fragile, make text files have the right column names
        randoms = randoms.rename(columns={'ra':'alpha', 'dec':'delta'})
        randoms = self.df_to_corr(randoms, shears=False)
        # fragile
        return {'lens':lens_table, 'source':source_table, 'rand':randoms}

    def df_to_corr(self, table, shears=False):
        """
        turn an pd dataframe into a treecorr catalog
        anticipating certain format form astropy catalog
        shape catalogs should be weigheted by shape noise
        position catalogs should not
        """
        if shears:
            cat = treecorr.Catalog(ra=table['alpha'].values, dec=table['delta'].values,
                                   ra_units='deg', dec_units='deg', g1=table['e1'], g2=table['e2'],
                                   w = np.ones(len(table)) * .12**-2)

        else:
            cat = treecorr.Catalog(ra=table['alpha'].values, dec=table['delta'].values,
                                   ra_units='deg', dec_units='deg')

        return cat


    def write_corrs(self, out_name, corr, outpath):
        '''
        quick function to write outputs of correlation functions
        '''
        df = pd.DataFrame(data=corr)
        output_path = join(outpath, out_name)
        df.to_csv(output_path)
        print('writing to {}'.format(output_path))
        return
