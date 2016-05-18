#!/usr/bin/env python
# encoding: utf-8

import numpy as np
from pylab import imshow, show, colorbar, figure
from pyhdf.SD import SD, SDC
from luts import Idx
from os import remove
from os.path import exists


class Level2(object):
    def __init__(self, list_datasets=[
            'Rtoa', 'Rprime', 'Rnir', 'bitmask', 'logchl', 'niter']):
        self.list_datasets = list_datasets
        self.shape = None

    def init(self, level1):
        self.shape = level1.shape

class Level2_HDF(Level2):
    def __init__(self, filename, overwrite=False, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        if exists(filename):
            if overwrite:
                print 'Removing file', filename
                remove(filename)
            else:
                raise IOError('File "{}" exists'.format(filename))

        self.filename = filename
        self.hdf = SD(filename, SDC.WRITE | SDC.CREATE)
        self.sdslist = {}

        self.typeconv = {
                    np.dtype('float32'): SDC.FLOAT32,
                    np.dtype('float64'): SDC.FLOAT64,
                    np.dtype('uint16'): SDC.UINT16,
                    np.dtype('uint32'): SDC.UINT32,
                    }

    def write(self, block):

        (yoff, xoff) = block.offset
        (hei, wid) = block.size

        for d in self.list_datasets:
            if d not in self.sdslist:
                dtype = self.typeconv[block[d].dtype]
                print 'creating dataset {} of shape {} and type {}'.format(
                        d, self.shape, dtype)
                self.sdslist[d] = self.hdf.create(d, dtype, self.shape)

        self.sdslist[d][yoff:yoff+hei,xoff:xoff+wid] = block[d][:,:]

    def finish(self):
        for name, sds in self.sdslist.items():
            print 'closing dataset', name
            sds.endaccess()
        self.hdf.end()


class Level2_NETCDF(Level2):
    def __init__(self, filename, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        pass

    def write(self, block):
        pass

class Level2_Memory(Level2):
    '''
    Just store the product in memory
    '''
    def write(self, block):

        assert self.shape is not None

        (yoff, xoff) = block.offset
        (hei, wid) = block.size

        for d in self.list_datasets:

            data = block.__dict__[d]

            if data.ndim == 2:
                if d not in self.__dict__:
                    self.__dict__[d] = np.zeros(self.shape, dtype=data.dtype)
                self.__dict__[d][yoff:yoff+hei,xoff:xoff+wid] = data[:,:]

            elif data.ndim == 3:
                if d not in self.__dict__:
                    self.__dict__[d] = np.zeros(((len(block.bands),)+self.shape), dtype=data.dtype)
                self.__dict__[d][:,yoff:yoff+hei,xoff:xoff+wid] = data[:,:,:]

            else:
                raise Exception('Error')

    def finish(self):
        pass


def contrast(x, max=1.):
    ''' stretch the contrast using a custom function '''
    R = np.sin(x/max*np.pi/2)**0.5
    R[R>max]=np.NaN
    return R

def RGB(data):
    figure()
    shp = (data.shape[1], data.shape[2], 3)
    RGB = np.zeros(shp)
    R = data[Idx(680, round=True), :, :]
    G = data[Idx(550, round=True), :, :]
    B = data[Idx(460, round=True), :, :]
    RGB[:,:,0] = contrast(R/np.amax(R[~np.isnan(R)]))
    RGB[:,:,1] = contrast(G/np.amax(G[~np.isnan(G)]))
    RGB[:,:,2] = contrast(B/np.amax(B[~np.isnan(B)]))
    imshow(RGB, interpolation='nearest')
    colorbar()

