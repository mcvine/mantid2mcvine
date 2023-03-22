import os, shutil, contextlib
thisdir = os.path.abspath(os.path.dirname(__file__))

import mantid2mcvine as m2m

@contextlib.contextmanager
def chdir(path):
    """Sets the cwd within the context
    """
    origin = os.path.abspath(os.curdir)
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)

def powder_sim(instrument_model, out_nxs):
    "run a sim with an artificial powder sample using ARCS beam but the DEMO det system"
    workdir = os.path.abspath("work.powder-cones")
    if os.path.exists(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    with chdir(workdir):
        # create workflow
        cmd = "mcvine workflow powder --instrument=ARCS --sample=V --workdir=mysim"
        execCmd(cmd)
        # run beam sim
        beamdir = os.path.join(workdir, 'mysim', 'beam')
        with chdir(beamdir):
            cmd = "mcvine instruments arcs beam -E=70 --ncount=1e6 --nodes=2"
            execCmd(cmd)
        # scattering
        mysim = os.path.join(workdir, 'mysim')
        with chdir(mysim):
            # modify sample to sth easily recognizable in reduced spectrum
            with open('sampleassembly/V-scatterer.xml', 'wt') as ostream:
                ostream.write(scatter_xml_content)
            # run sim
            cmd = "./sss --ncount=1e6 --multiple-scattering=off --mpirun.nodes=2 --buffer_size=50000"
            execCmd(cmd)
            # convert to mantid nxsfile
            events = instrument_model.neutrons2events(
                './out/scattered-neutrons', nodes=2
            )
            simnxs = instrument_model.events2nxs(events, out_nxs)
    return

def reduce(path):
    from mantid import simpleapi as msa, mtd
    ws = msa.Load(path)
    ws1 = msa.CropWorkspace(InputWorkspace=ws, OutputWorkspace='ws1', StartWorkspaceIndex=1)
    msa.DgsReduction(
        SampleInputWorkspace=ws1,
        OutputWorkspace='reduced',
        IncidentEnergyGuess=70., UseIncidentEnergyGuess=1,
        EnergyTransferRange = [-70, 0.5, 65],
        SofPhiEIsDistribution=1, IncidentBeamNormalisation='ByCurrent',
        CorrectKiKf=1, TimeZeroGuess=20)
    reduced = mtd['reduced']
    from mcvine.instruments.ARCS.applications.nxs import getSqeHistogramFromMantidWS
    getSqeHistogramFromMantidWS(reduced, 'iqe.h5', qaxis=(0, 0.05, 3.5))
    return

def test():
    # use mantid2mcvine to add virtual instrument
    cmd = f"python {os.path.join(thisdir, 'add_demo_instrument.py')}"
    execCmd(cmd)
    # load the save instrument model
    import pickle as pkl
    instrument_model = pkl.load(open("demo_instrument_model.pkl", "rb"))
    # run powder simulation using the instrument model
    nxsfile = os.path.abspath('out_test_workflow.nxs')
    powder_sim(instrument_model, nxsfile)
    # reduce the simulated nxs file
    reduce(nxsfile)
    return

def execCmd(cmd):
    if os.system(cmd):
        raise RuntimeError(f"Failed: {cmd}")

scatter_xml_content = """<?xml version="1.0"?>

<!DOCTYPE scatterer>

<!-- mcweights: monte-carlo weights for 3 possible processes:
     absorption, scattering, transmission -->
<homogeneous_scatterer mcweights="0, 1, 0.1">

  <KernelContainer average="yes">

    <Phonon_IncoherentElastic_Kernel dw_core='0.00701434948808*angstrom**2'>
    </Phonon_IncoherentElastic_Kernel>

    <ConstantQEKernel momentum-transfer="1/angstrom" energy-transfer="10*meV"/>

    <ConstantQEKernel momentum-transfer="1.5/angstrom" energy-transfer="20*meV"/>

    <ConstantQEKernel momentum-transfer="1.5/angstrom" energy-transfer="10*meV"/>

    </KernelContainer>
</homogeneous_scatterer>
"""
