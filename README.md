[![Build Status](https://github.com/mcvine/mantid2mcvine/workflows/CI/badge.svg)](https://github.com/mcvine/mantid2mcvine/actions?query=workflow%3ACI)
[![Coverage Status](https://coveralls.io/repos/github/mcvine/mantid2mcvine/badge.svg)](https://coveralls.io/github/mcvine/mantid2mcvine)

# Convert Mantid IDF to MCViNE instrument xml

First make sure the instrument name in the filename matches the "name" attribute of the "instrument" tag
in the IDF file.

```
import mantid2mcvine as m2m
```

Create a model:
```
im = m2m.InstrumentModel(
    instrument_name, beamline, mantid_idf, mcvine_idf, template_nxs,
    detsys_shape, tube_info,
    nbanks = nbanks,
    ntubesperpack = ntubesperpack,
    npixelspertube = npixelspertube,
    nmonitors = nmonitors,
    tofbinsize = tofbinsize,
    )
```

Convert model. this will
1. add mantid IDF to ~/.mantid
2. create mcvine xml
3. create template nxs used for sim.nxs generation

```
im.convert()
```

Convert simulated neutrons to simulated nxs file:
```
events = im.neutrons2events('scattered-neutrons', nodes=20)
simnxs = im.events2nxs(events, 'sim.nxs')
```

For more details, see [demo](notebooks/demo.ipynb)
