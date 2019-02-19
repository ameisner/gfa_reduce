#!/usr/bin/env python

import argparse
import os
import ci_reduce.io as io
from datetime import datetime

if __name__ == "__main__":
    descr = 'run full ci_reduce pipeline on a CI exposure'
    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument('fname_in', type=str, nargs=1)

    parser.add_argument('--outdir', default='', type=str,
                        help='directory to write outputs in')

    args = parser.parse_args()

    print('Starting CI reduction pipeline at: ' + str(datetime.utcnow()) + 
          ' UTC')

    fname_in = args.fname_in[0]

    write_outputs = (len(args.outdir) > 0)

    assert(os.path.exists(fname_in))

    if write_outputs:
        outdir = args.outdir
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        # fail if ANY of expected outputs already exist
        io.check_image_level_outputs_exist(outdir, fname_in, gzip=True)

    exp = io.load_exposure(fname_in)

    # create data quality bitmasks
    exp.create_all_bitmasks()

    # go from "raw" images to "reduced" images
    exp.calibrate_pixels()

    # calculate sky brightness in mag per sq asec -- this should 
    # probably go somewhere else eventually

    for image in exp.images.values():
        print(image.header['EXTNAME'] + ' sky mag per square asec AB : ', 
              image.estimate_sky_mag())

    # try to write image-level outputs if outdir is specified
    if write_outputs:
        print('Attempting to write image-level outputs to directory : ' + 
              outdir)

    if write_outputs:
        # could add command line arg for turning off gzip compression
        io.write_image_level_outputs(exp, outdir, fname_in, gzip=True)

    print('Succesfully finished reducing ' + fname_in)

    print('CI reduction pipeline completed at: ' + str(datetime.utcnow()) + 
          ' UTC')
