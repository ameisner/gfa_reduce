from ci_reduce.image import CI_image
from ci_reduce.exposure import CI_exposure
import ci_reduce.common as common
import astropy.io.fits as fits
import os

# in the context of this file, "image" and "exposure" generally refer to 
# CI_image and CI_exposure objects

def load_image_from_hdu(hdu):
    return CI_image(hdu.data, hdu.header)

def load_image_from_filename(fname, extname):
    assert(os.path.exists(fname))

    assert(common.is_valid_image_extname(extname))

    data, header = fits.getdata(fname, extname=extname, header=True)
    return CI_image(data, header)

def load_exposure(fname):
    assert(os.path.exists(fname))

    par = common.ci_misc_params()

    hdul = fits.open(fname)

    dummy_fz_header = None

    for hdu in hdul:
        if (hdu.header['EXTNAME']).strip() == par['fz_dummy_extname']:
            dummy_fz_header = hdu.header
            hdul.remove(hdu)

    imlist = [load_image_from_hdu(hdu) for hdu in hdul]

    return CI_exposure(imlist, dummy_fz_header=dummy_fz_header)
