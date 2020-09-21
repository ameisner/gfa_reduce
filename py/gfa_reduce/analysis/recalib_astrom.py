from .asterisms import pattern_match, gaia_cat_for_exp
import numpy as np
import astropy.io.fits as fits
from multiprocessing import Pool
import time

# run astrometric calibration given a catalog with the centroids and
# an initial guess (SKYRA, SKYDEC) of the field of view center
# mainly going to be a wrapper for asterisms.pattern_match

def recalib_astrom(cat, fname_raw, mjd=None, h=None, mp=False):
    # cat should be the catalog for an entire exposure

    if cat is None:
        return None
        
    extnames = np.unique(cat['camera'])

    if h is None:
        try:
            h = fits.getheader(fname_raw, extname='GFA')
        except:
            h = fits.getheader(fname_raw, extname='GUIDER')

    gaia = gaia_cat_for_exp(h['SKYRA'], h['SKYDEC'], mjd=mjd)
    # conserve memory
    gaia = gaia[['ra', 'dec']] # only columns needed for pattern matching

    arcmin_max = 6.0
    print('astrometry search using ' + '{:.1f}'.format(arcmin_max) + ' arcminute radius')
    args = []
    for extname in extnames:
        _cat = cat[(cat['camera'] == extname) & (cat['sig_major_pix'] > 1.0) & (cat['min_edge_dist_pix'] > 3)] # 3 is a fairly arbitrary guess
        if len(_cat) < 2:
            _cat = cat[cat['camera'] == extname]
        args.append((_cat, h['SKYRA'], h['SKYDEC'], extname, gaia, arcmin_max))

    t0 = time.time()
    if not mp:
        result = []
        for tup in args:
            result.append(pattern_match(*tup))
    else:
        print('Running astrometric pattern matching for all guide cameras in parallel...')
        nproc = len(args)
        assert(nproc <= 6)
        p = Pool(nproc)
        result = p.starmap(pattern_match, args)
    dt = time.time()-t0

    print('time taken to astrometrically recalibrate all cameras:  ', dt, ' seconds')
        
    return result
