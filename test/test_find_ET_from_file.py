r""" Test with synthetic data"""

import logging
from turboseti_stream import DopplerFinder


from datafiles import TEMPDIR, SYNTH_FILE, CFG_FILE, MAX_DRIFT_RATE, MIN_SNR
from spectra_gen_main import generate_fil_file
from spectra_gen_config import ConfigObject


def test_find_ET_from_file():
    
    # Generate the Filterbank file.
    generate_fil_file(SYNTH_FILE, CFG_FILE)
    
    # Define observation parameters
    cfg = ConfigObject(CFG_FILE)
    n_fine_chans = cfg.n_fine_chans # setigen fchans
    f_start = cfg.fch1 # MHz, setigen fch1
    foff = cfg.df # MHz, setigen df
    f_stop = f_start + (n_fine_chans - 1) * foff # MHz
    ntime = cfg.n_ints_in_file # seconds, setigen tchans
    tsamp = cfg.dt # seconds, setigen dt
    mjd = 59423.2 # Modified Julian Date
    
    
    print("test_find_ET_from_file: Clancy is being initialised")
    clancy = DopplerFinder(filename=SYNTH_FILE,
                           source_name="SYNTHETIC",
                           out_dir=TEMPDIR,
                           max_drift=MAX_DRIFT_RATE,
                           snr=MIN_SNR,
                           log_level_int=logging.INFO,
                           src_raj=7.456805,
                           src_dej=5.225785,
                           tstart=mjd,
                           tsamp=tsamp,
                           f_start=f_start,
                           f_stop=f_stop,
                           n_fine_chans=n_fine_chans,
                           n_ints_in_file=ntime)
    
    print("test_find_ET_from_file: Clancy is searching for ET")
    clancy.find_ET_from_file(SYNTH_FILE)


if __name__ == "__main__":
    test_find_ET_from_file()
