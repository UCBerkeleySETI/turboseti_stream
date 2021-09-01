import logging
from astropy import units as u
import setigen as stg
from turboseti_stream import DopplerFinder
from datafiles import TEMPDIR


def test_find_ET():
    # Define observation parameters
    f_start = 3e3  #MHz
    BW = 1 #MHz
    tsamp=1 #seconds
    f_stop = f_start + BW
    n_fine_chans = int(1e6)
    ntime = int(60)
    mjd=59423.2
    
    
    # Define synthetic signal parameters
    snr_of_synthetic_pulse=100
    drift_rate = -2
    width = 5 #Hz
    
    print("test_find_ET: Creating synthetic signal...")
    # Create a synthetic signal
    frame = stg.Frame(fchans=n_fine_chans*u.pixel,
                      tchans=ntime*u.pixel,
                      df=BW/n_fine_chans*u.MHz,
                      dt=tsamp*u.s,
                      fch1=f_start*u.MHz)
    
    frame.add_noise(x_mean=10, noise_type='chi2')
    frame.add_signal(stg.constant_path(f_start=frame.get_frequency(index=n_fine_chans/2), #injecting exactly in middle of band
                                       drift_rate=drift_rate*u.Hz/u.s),
                              stg.constant_t_profile(level=frame.get_intensity(snr=snr_of_synthetic_pulse)),
                              stg.gaussian_f_profile(width=width*u.Hz),
                              stg.constant_bp_profile(level=1))
    
    print("test_find_ET: synthetic signal generated.")
    
    
    print("test_find_ET: Clancy is being initialised")
    clancy = DopplerFinder(filename="CH0_TIMESTAMP",
                           out_dir=TEMPDIR,
                           source_name="test", src_raj=7.456805, src_dej=5.225785,
                           tstart=mjd, tsamp=tsamp, f_start=f_start, f_stop=f_stop, n_fine_chans=n_fine_chans,
                           log_level_int=logging.INFO,
                           n_ints_in_file=ntime)
    
    print("test_find_ET: Clancy is searching for ET")
    clancy.find_ET(frame.data)


if __name__ == "__main__":
    test_find_ET()