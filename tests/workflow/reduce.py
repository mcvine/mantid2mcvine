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

if __name__ == '__main__':
    import sys
    reduce(sys.argv[1])
