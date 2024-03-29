import treecorr, itertools, pickle, os, regions
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from astropy.io import ascii
from astropy.coordinates import SkyCoord, Angle
from astropy.io import fits
from astropy.wcs import WCS
from sklearn.cluster import KMeans
from astropy.table import Table, vstack
class ExclusionZones():
    '''
    A class to generate randoms for a data set, and sanitize them so
    no randoms are generated inside masked regions
    '''
    def __init__(self, field, subfield, basePath='/global/homes/i/ihasan/shear_gp/data_access/'):
        self.basePath = basePath
        self.field = field
        self.subfield = subfield
        self.exRegPath = os.path.join(self.basePath, 'regfiles',self.field+self.subfield+'R.all.2009.reg')
        self.edgeRegPath = os.path.join(self.basePath, 'regfiles',self.field+self.subfield+'.edge.reg')
        self.imagePath = os.path.join(self.basePath, 'WCS',self.field + self.subfield + 'wcs.fits')
        self.wcs = self._getWCS(self.imagePath)
        self.regionList = []
        try:
            self.regionList += self._parseExReg(self.exRegPath)
        except:
            print("problem reading file %s " % self.exRegPath)
            pass
        try:
            self.regionList += self._parseEdgeReg(self.edgeRegPath)
        except:
            print("problem reading file %s " % self.edgeRegPath)
            pass

        if len(self.regionList) == 0:
            print("WARNING: No region files found")

    def _getWCS(self,filename):
        hdu = fits.open(filename)
        hdu.close()
        w = WCS(hdu[0].header)
        return w
    
    def _readCenterReg(self,filename):
        cntReg = regions.read_ds9(filename)
        return cntReg

    def _parseExReg(self,filename):

        with open(filename,'r') as f:
            lines = f.readlines()

        reglist = []

        for line in lines:
            if not line.startswith('#'):
                if line.startswith('circle'):
                    baseLine = line.partition('# color=green pos=')
                    x, y, r = baseLine[0][baseLine[0].find('(') +1 : baseLine[0].find(')')].split(',')
                    ra, dec = baseLine[-1][baseLine[-1].find('(') +1 : baseLine[-1].find(')')].split(',')
                    circ = regions.CircleSkyRegion(center=SkyCoord(np.float(ra), np.float(dec), unit='deg'),
                                 radius=Angle(.265*np.float(r), 'arcsec'))
                    reglist.append(circ)

                elif line.startswith('box'):
                    baseLine = line.partition('# color=green ')
                    x, y, w, h = baseLine[0][baseLine[0].find('(') +1:baseLine[0].find(')')].split(',')
                    ra, dec = baseLine[-1].rstrip().split()
                    ra = np.float(ra[3:])
                    dec = np.float(dec[4:])
                    rec = regions.RectangleSkyRegion(center=SkyCoord(ra, dec, unit='deg'),
                                width=Angle(.265*np.float(w), 'arcsec'),
                                height=Angle(.265*np.float(h), 'arcsec'),
                                angle=Angle(270, 'deg'))
                    reglist.append(rec)

        return reglist
    
    def _parseEdgeReg(self,filename):
        pixRegions = regions.read_ds9(filename)
        if type(pixRegions[0]) == regions.shapes.rectangle.RectanglePixelRegion:
            skyRegions = [r.to_sky(self.wcs) for r in pixRegions]
        else:
            skyRegions = pixRegions
        return skyRegions
    
    def flagPoints(self, ra, dec, unit='rad'):
        containsList = [i.contains(SkyCoord(ra, dec, unit=unit), self.wcs) for i in self.regionList]
        #tells you indx of ra dec coords that fall inside any regions
        pointMask = np.where(~np.any(containsList, axis=0))
        
        ra_clean, dec_clean = ra[pointMask], dec[pointMask]
        return ra_clean, dec_clean

    def interiorPoints(self, ra, dec, unit):
        containsMask = self.regionCenter.contains(SkyCoord(ra, dec, unit=unit), self.wcs)
        #only keep points inside the center region
        #were cutting out any points that land in gutters here
        return containsMask

def byFields(table, field):
    '''
    helper function to return a table of a particular field only
    '''
    mask = table['subfield'].str.contains(field)
#    subfield_vals = table['subfield']
#    field_vals = np.array([i[:2] for i in subfield_vals ] )
#    mask = field_vals == field
    return table[mask]

def dumpRandoms(table, prefix, debug=False):
    fields = ('F1','F2','F3','F4','F5')
    subfields = ('p11','p12','p13','p21','p22','p23','p31','p32','p33')

    #we need to index the catalog field by field, and generate randoms
    #field by field ultimately concatenating them to make a master randoms cat

    #temporary way of dealing with fields
    #key is the field of interest, val is subtable of that field
    tableViews = {}
    for f in fields:
        tableViews[f]= {}
        tableViews[f]['galaxies'] =  byFields(table, f)
        rand_ra, rand_dec = genRandoms(tableViews[f]['galaxies']['alpha']*(np.pi/180),
            tableViews[f]['galaxies']['delta']*(np.pi/180))
        tableViews[f]['rand_ra'] = rand_ra
        tableViews[f]['rand_dec'] = rand_dec

    for f, sf in itertools.product(fields, subfields):
        ez = ExclusionZones(f, sf)
        rand_ra, rand_dec = ez.flagPoints(tableViews[f]['rand_ra'], tableViews[f]['rand_dec'], unit='rad')
        #update the rand_ra and rand_dec after they've been cleaned up
        tableViews[f]['rand_ra'] = rand_ra
        tableViews[f]['rand_dec'] = rand_dec
        print('finished %s' % f+sf)

    for f in fields:
        t = Table([tableViews[f]['rand_ra'], tableViews[f]['rand_dec']], names=('ra','dec') )
        outpath = os.path.join('catalogs','DLS_randoms',prefix,f+'randoms.csv')
        t.write(outpath, format='csv', overwrite=True)

    return

def calcProbes(table, table2=None, debug=False, n_resample=100):
    '''
    given a astropy table with ra and dec columns, compute w of theta and make a plot
    '''
    table_size = len(table)
    xi_list = []
    sig_list = []
    r_list = []

    #read in the randoms and make a master table
    fields = ('F1','F2','F3','F4','F5')
    random_tables =[ascii.read(f+'randoms.csv') for f in fields]
    master_randoms = vstack(random_tables)
    #deal with second catalog if need be
    if table2 is not None:
        cat = astpyToCorr(table)
        otherCat = astpyToCorr(table2)
        xi, sig, r, Coffset = getCrossWTheta(cat, otherCat, master_randoms['ra'],
            master_randoms['dec'])
        return {"xi":xi, "sig":sig, "r":r, "Coffset":Coffset}
    #otherwise just deal with the auto correlation
    else:
        for i in range(0,n_resample):
                resampled_idx = np.random.randint(0,table_size,table_size)
                cat = astpyToCorr(table[resampled_idx])
                #calculate w of theta given our sanitized randoms and catalog data
                xi, sig, r, Coffset = getWTheta(cat, master_randoms['ra'], master_randoms['dec'])
                xi_list.append(xi)
                sig_list.append(sig)
                r_list.append(r)

        return {"xi":xi_list, "sig":sig_list, "r":r_list, "Coffset":Coffset}

def genRandoms(ra, dec, debug=True):
    ra_min = np.min(ra)
    ra_max = np.max(ra)
    dec_min = np.min(dec)
    dec_max = np.max(dec)
    ntot = ra.size

    if debug:
        print('ra range = %f .. %f' % (ra_min, ra_max))
        print('dec range = %f .. %f' % (dec_min, dec_max))

    rand_ra = np.random.uniform(ra_min, ra_max, 7*ntot)
    rand_sindec = np.random.uniform(np.sin(dec_min), np.sin(dec_max), 7*ntot)
    rand_dec = np.arcsin(rand_sindec)
    return rand_ra, rand_dec

def astpyToCorr(table, weight=False):
    """
    turn an astropy table into a treecorr catalog
    anticipating certain format form astropy catalog
    """
    if weight:
        w = 1/(.25**2 + table['de']**2)
        cat = treecorr.Catalog(ra=table['alpha'].data, dec=table['delta'].data, w=w,
                    ra_units='deg', dec_units='deg', g1=table['e1'], g2=table['e2'])

    else:
        cat = treecorr.Catalog(ra=table['alpha'].data, dec=table['delta'].data,
                    ra_units='deg', dec_units='deg', g1=table['e1'], g2=table['e2'])
    return cat

def calcC(RR):
    NN = RR.weight
    theta = np.exp(RR.meanlogr)

    numerator = NN*np.power(theta, -.8)

    C = numerator.sum()/NN.sum()
    return C


def getWTheta(cat, rand_ra, rand_dec):
    """
    calculate the angular two point correlation function using the landay-sazlay estimator

    note: rand_ra and rand_dec should sample the same space on the sky as the data
        to accurately calculate w of theta
    
    parameters
    cat: treecorr catalog of galaxies we will calculate w of theta for.
    rand_ra: numpy array. uniformly random sampled coordinates in RA space. 
    rand_dec: numpy array. uniformly random sampled coordinates in DEC space

    returns:
    xi: numpy array. the angular two point correlation function
    sig: numpy array. xi's std dev noise estimated from treecor. underestimated error 
    r: numpy array of angular bins xi is calculated for
    """

    dd = treecorr.NNCorrelation(min_sep=0.1, max_sep=80, nbins=15, sep_units='arcmin')
    dd.process(cat)
    rand = treecorr.Catalog(ra=rand_ra, dec=rand_dec, ra_units='radians', dec_units='radians')
    rr = treecorr.NNCorrelation(min_sep=0.1, max_sep=80, nbins=15, sep_units='arcmin')
    rr.process(rand)

    r = np.exp(dd.meanlogr)

    dr = treecorr.NNCorrelation(min_sep=0.1, max_sep=80, nbins=15, sep_units='arcmin')
    dr.process(cat, rand)

    xi, varxi = dd.calculateXi(rr, dr)
    sig = np.sqrt(varxi)

    Coffset = calcC(rr)
    return xi, sig, r, Coffset

def getCrossWTheta(cat, cat2, rand_ra, rand_dec):
    """
    calculate the angular two point correlation function using the landay-sazlay estimator

    note: rand_ra and rand_dec should sample the same space on the sky as the data
        to accurately calculate w of theta
    
    parameters
    cat: treecorr catalog of galaxies we will calculate w of theta for.
    rand_ra: numpy array. uniformly random sampled coordinates in RA space. 
    rand_dec: numpy array. uniformly random sampled coordinates in DEC space

    returns:
    xi: numpy array. the angular two point correlation function
    sig: numpy array. xi's std dev noise estimated from treecor. underestimated error 
    r: numpy array of angular bins xi is calculated for
    """

    dd = treecorr.NNCorrelation(min_sep=0.1, max_sep=80, nbins=15, sep_units='arcmin')
    dd.process(cat, cat2)
    rand = treecorr.Catalog(ra=rand_ra, dec=rand_dec, ra_units='radians', dec_units='radians')
    rr = treecorr.NNCorrelation(min_sep=0.1, max_sep=80, nbins=15, sep_units='arcmin')
    rr.process(rand)

    r = np.exp(dd.meanlogr)

    dr = treecorr.NNCorrelation(min_sep=0.1, max_sep=80, nbins=15, sep_units='arcmin')
    dr.process(cat, rand)

    rd = treecorr.NNCorrelation(min_sep=0.1, max_sep=80, nbins=15, sep_units='arcmin')
    rd.process(rand, cat2)

    xi, varxi = dd.calculateXi(rr, dr, rd)
    sig = np.sqrt(varxi)

    Coffset = calcC(rr)
    return xi, sig, r, Coffset

def shearBias(lens_table):
    """
    calculate the shear muliplicative bias
    James Jee has a way of using the R band magnitude
    as a proxy for m
    """
    mb = 6*(10**-4) * np.sign(lens_table['r'] - 20) * np.abs(lens_table['r'] - 20)**3.26 + 1.036
    lens_table['e1'] *= mb
    lens_table['e2'] *= mb
    return lens_table

def shapeCut(source_table):
    '''make draconian cuts to shape catalog'''
    mask = source_table['de'] < .1
    mask &= np.sqrt(source_table['e2']**2 + source_table['e1']**2) < .6
    mask &= source_table['flux_radius'] > 1.8
    mask &= source_table['flux_radius'] < 5
    mask &= np.sqrt( 1 - np.square(source_table['b']) / np.square(source_table['a'])) < .9
    mask &= source_table['b'] < 3
    
    return source_table[mask]

def getGGL(lens_table, source_table, n_resample=100, swap_test=True,
           cal_lens=True, cal_source=True, shape_cut=True):
    """
    calculate galaxy galaxy lensing

    parameters
    lens_table: astropy table of lens galaxies. must have positions and shear specified 
    source_table: astropy table of source galaxies. must have positions and shear specified
    n_resample: number of bootstrap resamplings to do. default is 100
    swap_test: calculate the tangential shear swapping lens and souces 

    returns a dictionary containing the following:
    gammat: tangential shear for each boostrap iterations. a list of n_resample
        python arrays
    gammax: tangential shear calculated after rotating sources 45 degrees
    r: mean center of radial bins
    gammat_flip: tangential shear calculated for swap test
    gammax_flip: tangential shear calculated after rotating sources 45 degrees
        calculated for the swap
    r_flip: mean center of radial bins 
    nullGGL : galaxy galaxy lens treecorr object. 
        swap shear and lens planes and calculate tangential shear
        nice null test for photo-zs
    """
    lens_tab_size = len(lens_table)
    gammat_list = []
    gammax_list = []
    r_list = []

    #calibrate the shear bias for both tables
    if cal_lens:
        lens_table = shearBias(lens_table)
    if shape_cut:
        source_table = shapeCut(source_table)
    if cal_source:
        source_table = shearBias(source_table)

    src_tab_size = len(source_table)

    #each iteration in the loop is a bootstrap resample
    for i in range(0,n_resample):
        #make new catalogs by resampling input lens and src
        lens_resamp_idx = np.random.randint(0,lens_tab_size,lens_tab_size)
        lens_corr = astpyToCorr(lens_table[lens_resamp_idx])
        src_resamp_idx = np.random.randint(0,src_tab_size,src_tab_size)
        source_corr = astpyToCorr(source_table[src_resamp_idx])
        #now make correlation functions
        GGL = treecorr.NGCorrelation(min_sep=0.1, max_sep=90, nbins=10, sep_units='arcmin')
        GGL.process(lens_corr, source_corr)
        gammat_list.append(GGL.xi)
        gammax_list.append(GGL.xi_im)
        r_list.append(np.exp(GGL.meanlogr))
    
    #option to do a one off lens source swap 
    if swap_test == False:
        return {"gammat":gammat_list, "gammax":gammax_list, "r":r_list}

    else:
        nullGGL = treecorr.NGCorrelation(min_sep=0.1, max_sep=90, nbins=10, sep_units='arcmin')
        nullGGL.process(source_corr, lens_corr)
        return {"gammat":gammat_list, "gammax":gammax_list, "r":r_list,
            "gammat_flip":nullGGL.xi, "r_flip":np.exp(nullGGL.meanlogr)}

def getRandomGGL(source_table, n_resample=100):
    '''use a catalog of randoms as lens objects
    '''
    #read in the randoms and make a master table
    fields = ('F1','F2','F3','F4','F5')
    random_tables =[ascii.read(f+'randoms.csv') for f in fields]
    master_randoms = vstack(random_tables)
    #the randoms are ~6 times bigger than the lens catalogs
    master_randoms = master_randoms[::6]

    gammat_list = []
    gammax_list = []
    r_list = []

    lens_tab_size = len(master_randoms)
    src_tab_size = len(source_table)
    
    #calibrate the shear bias
    source_table = shearBias(source_table)
    
    for i in range(0,n_resample):
        #make new catalogs by resampling input lens and src
        lens_resamp_idx = np.random.randint(0,lens_tab_size,lens_tab_size)
        src_resamp_idx = np.random.randint(0, src_tab_size, src_tab_size)
        random_cat = treecorr.Catalog(ra=master_randoms[lens_resamp_idx]['ra'].data,
            dec=master_randoms[lens_resamp_idx]['dec'].data,
            ra_units='radians', dec_units='radians')
        source_corr = astpyToCorr(source_table[src_resamp_idx])
        #now make correlation functions
        GGL = treecorr.NGCorrelation(min_sep=0.1, max_sep=90, nbins=10, sep_units='arcmin')
        GGL.process(random_cat, source_corr)
        gammat_list.append(GGL.xi)
        gammax_list.append(GGL.xi_im)
        r_list.append(np.exp(GGL.meanlogr))
    
    return {'gammat':gammat_list, "gammax":gammax_list, "r":r_list}

def makePlot(xi, sig, r):
    plt.style.use('seaborn-poster')
    plt.plot(r, xi, color='blue')
    plt.plot(r, -xi, color='blue', ls=':')
    plt.errorbar(r[xi>0], xi[xi>0], yerr=sig[xi>0], color='blue', ls='')
    plt.errorbar(r[xi<0], -xi[xi<0], yerr=sig[xi<0], color='blue', ls='')
    leg = plt.errorbar(-r, xi, yerr=sig, color='blue')

    plt.xscale('log')
    plt.yscale('log', nonposy='clip')
    plt.xlabel(r'$\theta$ (arcmin)')

    plt.legend([leg], [r'$w(\theta)$'], loc='lower left')
    plt.show()
    return

        
