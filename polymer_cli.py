#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
A basic command line interface for Polymer
'''

import argparse
import os
from polymer.main import run_atm_corr
from polymer.level1 import Level1
from polymer.level2 import Level2
from polymer.gsw import GSW
from polymer.ancillary import Ancillary_NASA
from polymer.ancillary_era5 import Ancillary_ERA5

# Setup GDAL paths
homedir = os.path.expanduser('~')
penv = r"{}/anaconda3/envs/polymer_env".format(homedir)
# Setup GDAL paths
os.environ['PROJ_LIB'] = os.path.join(penv,r"Library/share/proj")
os.environ['GDAL_DATA'] = os.path.join(penv,r"Library/share")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='''Polymer atmospheric correction, simple command line interface.
                       To pass additional parameters, it is advised to execute the
                       function run_atm_corr in a python script''')

    parser.add_argument('input_file')
    parser.add_argument('output_file')
    parser.add_argument('-res', default='60', help='Resolution')
    parser.add_argument('-sline', default=None, help='Bounding box')
    parser.add_argument('-eline', default=None, help='Bounding box')
    parser.add_argument('-scol', default=None, help='Bounding box')
    parser.add_argument('-ecol', default=None, help='Bounding box')
    parser.add_argument('-fmt', choices=['hdf4', 'netcdf4', 'autodetect'],
                        default='autodetect',
                        help='Output file format')
    args = parser.parse_args()

    if args.fmt == 'autodetect':
        if args.output_file.endswith('.nc'):
            args.fmt = 'netcdf4'
        elif args.output_file.endswith('.hdf'):
            args.fmt = 'hdf4'
        else:
            print('Error, cannot detect file format from output file "{}"'.format(
                args.output_file))
            exit()
            
    stem = os.path.dirname(args.output_file)
    gswdir = os.path.join(stem,"GSW")
    if not os.path.exists(gswdir):
      os.mkdir(gswdir)

    ancdir = os.path.join(stem,"ancillary")
    if not os.path.exists(ancdir):
      os.mkdir(ancdir)

    tmpdir = os.path.join(stem,"temp")
    if not os.path.exists(tmpdir):
      os.mkdir(tmpdir)
      
    if args.sline is not None:
      run_atm_corr(Level1(args.input_file,ancillary=Ancillary_NASA(directory=ancdir), resolution=args.res, landmask=GSW(directory=gswdir), sline=int(args.sline), eline=int(args.eline), scol=int(args.scol), ecol=int(args.ecol)), Level2(filename=args.output_file, fmt=args.fmt, tmpdir=tmpdir), multiprocessing=-1)
    else:
      run_atm_corr(Level1(args.input_file,ancillary=Ancillary_NASA(directory=ancdir), resolution=args.res, landmask=GSW(directory=gswdir)), Level2(filename=args.output_file, fmt=args.fmt, tmpdir=tmpdir), multiprocessing=-1)

