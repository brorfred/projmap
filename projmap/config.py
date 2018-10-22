
import os
from six.moves import configparser



def regionlist():
    """return list with all reagions"""
    cfg = configparser.ConfigParser()

    basedir =  os.path.dirname(os.path.abspath(__file__))
    cfg_file_list = [os.curdir + "/map_regions.cfg",
                     os.path.expanduser("~") + "/.map_regions.cfg",
                     basedir + "/map_regions.cfg"]
    if region:
        for cfg_file in cfg_file_list:
            cfg.read(cfg_file)
            if region in cfg.sections(): break
        print ("\n\nThe region -%s- was found in \n \n   %s:\n " %
               (region,cfg_file))
        print ("and has the following options:\n")
        for key,val in cfg.items(region):
            print ("   %s:   %s" % (key,val))
    else:
        for cfg_file in cfg_file_list:
            cfg.read(cfg_file)
            if cfg.sections():
                print ("\nRegions in \n" + cfg_file + ":")
                for sect in cfg.sections():
                    desc = ""
                    if "proj.description" in cfg.options(sect):
                        desc = cfg.get(sect,'proj.description')
                    print ("   %s:   %s" % (sect,desc))
