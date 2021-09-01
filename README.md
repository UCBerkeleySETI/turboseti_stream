# turboseti_stream

This is a project to enable turbo_seti to accept data in a streaming fashion, i.e. straight from memory, instead of reading a Filterbank or HDF5 file from disk. 
This is especially useful for real-time pipelines where data must be analysed as it is being recorded.

The immediate aim of this project is to integrate into a GNU Radio block. Thus, we are able to perform SETI searches from a Gnu Radio flowgraph.

## Requirements
- [turbo_seti] (https://github.com/UCBerkeleySETI/turbo_seti)
- [setigen] (https://github.com/bbrzycki/setigen)
- [Gnu Radio] (https://www.gnuradio.org/)

## Example Usage

```
from turboseti_stream import DopplerFinder

clancy = DopplerFinder(filename="DAT_LOG_FILENAME",
                       out_dir="/datax/scratch/turboseti_stream/",
                       source_name="luyten",
                       src_raj=7.456805, 
                       src_dej=5.225785,
                       tstart=59423.2, 
                       tsamp=1, 
                       n_ints_in_file=16,
                       n_fine_chans=2**20,
                       n_coarse_chan=1,
                       f_start=3000,
                       f_stop=3100,
                       snr=42.0,
                       min_drift=0.01,
                       max_drift=4.0)
 
# Streamed data (E.g. GNU Radio):
clancy.find_ET(spectra_supplied_by_a_gnu_radio_function)

# Developer unit testing from a Filterbank file or HDF5 file:
clancy.find_ET_from_file("/path-to-synthetic-gnu-radio-data.fil")
```

For further Python examples, see [here](https://github.com/youais/gr-turboseti/blob/master/examples/python_script_tests/turboseti_multiprocessing_test.py).

For examples of .grc flowgraphs containing blocks using turboseti_stream, see [here](https://github.com/youais/gr-turboseti/tree/master/examples/example_flowgraphs).
