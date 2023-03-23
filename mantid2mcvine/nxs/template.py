import numpy as np
import h5py
import os
import shutil


def create(idfpath, ntotpixels, outpath, workdir='.', pulse_time_end=16667., nmonitors=0, instrument_template=None):
    """create template nexus file.

    Parameters
    ----------
    idfpath : str
        path to instrument definition xml file
    ntotpixels : int
        total number of pixels
    outpath : str
        output template nexus file path
    workdir : str
        working dir to save intermediate files
    pulse_time_end : float
        end time for one pulse
    nmonitors : int
        number of monitors
    instrument_template : str, pathlib.Path
        absolute path to a processed event nexus file to serve as initial Nexus file.
        If empty, file `start.nxs` is used.
    """
    # Select the starting instrument configuration
    if bool(instrument_template):
        start = str(instrument_template)
    else:
        thisdir = os.path.dirname(__file__)
        start = os.path.join(thisdir, 'start.nxs')
    # step 1
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    step1 = os.path.join(workdir, 'step1.nxs')
    shutil.copyfile(start, step1)
    with h5py.File(step1, 'a') as f:
        ws = f['mantid_workspace_1']
        ew = ws['event_workspace']
        ew['axis1'][:] = [-1, pulse_time_end]  # TOF axis
        # del ew['axis2']
        ew['axis2'] = np.arange(1., ntotpixels+nmonitors)  # monitors then detector pixels
        attrs = ew['axis2'].attrs
        attrs['caption'] = 'Spectrum'
        attrs['label'] = ''
        attrs['units'] = 'spectraNumber'

        saved_attrs = dict(ew['indices'].attrs)
        # print saved_attrs
        saved = ew['indices'][:].copy()
        # print saved
        # print saved.dtype
        # print ew['indices'].shape
        del ew['indices']
        # monitors then detector pixels
        new_indices = np.zeros(ntotpixels+nmonitors+1, dtype='int64')
        new_indices[:saved.size] = saved[:new_indices.size]  # why?
        ew['indices'] = new_indices
        attrs = ew['indices'].attrs
        for k, v in saved_attrs.items():
            attrs[k] = v
        f.close()
        pass
    # step 2
    from mantid import simpleapi as msa
    ws = msa.Load(os.path.abspath(step1))
    step2 = os.path.join(workdir, 'step2.nxs')
    msa.LoadInstrument(Workspace=ws, Filename=os.path.abspath(idfpath), RewriteSpectraMap=True)
    msa.PreprocessDetectorsToMD(ws, OutputWorkspace="dettable")
    msa.SaveNexusProcessed(ws, Filename=os.path.abspath(step2))
    # step 3
    step3 = os.path.join(workdir, 'step3.nxs')
    shutil.copyfile(step2, step3)
    with h5py.File(step3, 'a') as f:
        ew = f['mantid_workspace_1']['event_workspace']
        del ew['indices'], ew['pulsetime'], ew['tof']
        f.close()
        pass
    shutil.copyfile(step3, outpath)
    return outpath
