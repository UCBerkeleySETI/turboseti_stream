r""" Testspectra_gen functions"""

import configparser
import pytest


from datafiles import TEMPDIR, CFG_FILE
from spectra_gen_main import main
import spectra_gen_config as sgc


def test_spectra_gen_main():
    fil_file = TEMPDIR + "rubbish.fil"
    args = [fil_file, CFG_FILE]
    main(args)


def test_spectra_gen_cfg():
    config = configparser.ConfigParser()
    config.read(CFG_FILE)
    with pytest.raises(SystemExit):
        sgc.get_config_string(config, "StrangeSection", "RaspberryPi4")
    with pytest.raises(SystemExit):
        sgc.get_config_string(config, "main", "RaspberryPi4")
    with pytest.raises(SystemExit):
        sgc.get_config_boolean(config, "StrangeSection", "ascending")
    with pytest.raises(SystemExit):
        sgc.get_config_boolean(config, "main", "RaspberryPi4")
    with pytest.raises(SystemExit):
        sgc.get_config_int(config, "StrangeSection", "n_fine_chans")
    with pytest.raises(SystemExit):
        sgc.get_config_int(config, "main", "RaspberryPi4")
    with pytest.raises(SystemExit):
        sgc.get_config_float(config, "StrangeSection", "drift_rate_1")
    with pytest.raises(SystemExit):
        sgc.get_config_float(config, "signal_1", "RaspberryPi4")
