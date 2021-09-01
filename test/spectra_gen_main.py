r"""
Main program for generating synthetic Gnu Radio spectra
"""

import os
import time
from argparse import ArgumentParser
from astropy import units as u
import setigen as stg
from spectra_gen_config import ConfigObject


def sig_start(nfreq, pct):
    r""" Calcutate the signal starting frequency column number """
    return nfreq * pct / 100.0


def generate_fil_file(out_path, cfg_file):
    r"""
    Using setigen, generate a filterbank file.

    Parameters:
        out_path - Path of where to store the resultant Filterbank file (.fil).
        cfg_file - Path of configuration file to govern this generation.
    """
    print("spectra_gen_main: Begin out_path = {}".format(out_path))
    start_time = time.time()

    # Set up setigne parameters
    cfg = ConfigObject(cfg_file)

    # Instantiate a setigen Frame object
    print("spectra_gen_main: Building setigen frame")
    frame = stg.Frame(fchans=cfg.n_fine_chans * u.pixel,
                      tchans=cfg.n_ints_in_file * u.pixel,
                      df=cfg.df * u.MHz,
                      dt=cfg.dt * u.s,
                      fch1=cfg.fch1 * u.MHz,
                      ascending=(cfg.ascending))

    # Add noise to stg object.
    print("spectra_gen_main: Adding noise")
    if cfg.adding_noise:
        frame.add_noise(x_mean=cfg.noise_x_mean, noise_type="chi2")
    print("spectra_gen_main: Adding signals")

    # Signal 1 will be detected.
    signal_1_intensity = frame.get_intensity(snr=cfg.snr_1)
    frame.add_constant_signal(f_start=frame.get_frequency(sig_start(cfg.n_fine_chans,
                                                                    cfg.signal_start_1)),
                              drift_rate=cfg.drift_rate_1,
                              level=signal_1_intensity,
                              width=cfg.width_1,
                              f_profile_type="gaussian")

    # Signal 2 will be detected.
    signal_2_intensity = frame.get_intensity(snr=cfg.snr_2)
    frame.add_constant_signal(f_start=frame.get_frequency(sig_start(cfg.n_fine_chans,
                                                                    cfg.signal_start_2)),
                              drift_rate=cfg.drift_rate_2,
                              level=signal_2_intensity,
                              width=cfg.width_2,
                              f_profile_type="gaussian")

    # Signal 3 will be detected.
    signal_3_intensity = frame.get_intensity(snr=cfg.snr_3)
    frame.add_constant_signal(f_start=frame.get_frequency(sig_start(cfg.n_fine_chans,
                                                                    cfg.signal_start_3)),
                              drift_rate=cfg.drift_rate_3,
                              level=signal_3_intensity,
                              width=cfg.width_3,
                              f_profile_type="gaussian")

    # Save the frame as a Filterbank file.
    frame.save_fil(out_path)

    # Report npy characteristics
    file_size = os.path.getsize(out_path)
    print("spectra_gen_main: 2D shape = {}".format(frame.data.shape))
    print("spectra_gen_main: File size = {} MB".format(file_size / int(1e6)))
    print("spectra_gen_main: End, elapsed time = {:0.1f} s"
          .format(time.time() - start_time))


def main(args=None):
    r"""
    This is the entry point to the plotSETI executable.

    Parameters
    ----------
    args : dict

    """
    # Create an option parser to get command-line input/arguments
    parser = ArgumentParser(description="strectra_gen - Generate synthetic spectra.")

    parser.add_argument("output_fil_path", type=str,
                        help="Path to the output Filterbank file (.fil)")
    parser.add_argument("config_path", type=str,
                        help="Path to the configuration file")

    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)

    generate_fil_file(os.path.abspath(args.output_fil_path),
                      os.path.abspath(args.config_path))


if __name__ == "__main__":
    main()
