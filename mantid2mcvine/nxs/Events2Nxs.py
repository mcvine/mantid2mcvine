#!/usr/bin/env python
#
#   Jiao Lin
#


"""
This module helps creating "processed" nexus file.

"processed" nexus file is created by mantid. it is
actually a mantid workspace file.

"""



class Event2Nxs:

    def __init__(
            self,
            nxs_template,
            npixels = 163*8*128,
            nmonitors = 2,
    ):
        self.nxs_template = nxs_template
        self.npixels = npixels
        self.nmonitors = nmonitors
        return

    def run(self, eventfile, nxsfile, tofbinsize=0.1):
        """tofbinsize: in microsecond
        """
        print("Converting %s to %s" % (eventfile, nxsfile))
        from mccomponents.detector.event_utils import readEvents
        events = readEvents(eventfile)
        self.write(events, tofbinsize, nxsfile)
        return

    def write(self, events, tofbinsize, nxsfile):
        # tofbinsize must be in the unit of microsecond
        data = self.convert(events)
        data['tofbinsize'] = tofbinsize
        self._write(nxsfile, **data)
        return

    def convert(self, events):
        """convert simulated events to data to be written
        to "processed" nexus file
        """
        events.sort(order='pixelID')
        # !!!!! spectrum number for pixel #0 is 1+nmonitors.
        # !!!!! You can see this by Right click nxs file, show detectors.
        pixelids = events['pixelID'] + self.nmonitors + 1
        hist, bin_edges = np.histogram(
            pixelids,
            bins=np.arange(-0.5, self.nmonitors+self.npixels+1.5),
            )
        indices = np.cumsum(hist)
        nevents = len(events)
        pulse_time = np.zeros(nevents)
        tof = events['tofChannelNo'] # XXX: tof unit?
        weights = events['p']
        return {
            'indices': indices,
            'pulse_time': pulse_time,
            'tof': tof,
            'weights': weights,
            }

    def _write(
            self,
            path,
            indices=None, pulse_time=None,
            tof=None, tofbinsize=None,
            weights=None
    ):
        """write "processed" nexus file given relevant data
        """
        import shutil
        shutil.copyfile(self.nxs_template, path)
        import time; time.sleep(0.5)
        import h5py
        with h5py.File(path, 'a') as f:
            e = f['mantid_workspace_1']['event_workspace']
            e['indices'] = indices
            e['pulsetime'] = pulse_time
            tofarr = e['tof'] = np.array(tof, dtype="double") * tofbinsize
            e['weight'] = np.array(weights, dtype='float32')
            e['error_squared'] = np.array(weights, dtype='float32')**2
            e['axis1'][:] = np.min(tofarr)-100, np.max(tofarr)+100
            f.close()
        return


import numpy as np, os


# End of file 
