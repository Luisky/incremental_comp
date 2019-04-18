#!/bin/python

import subprocess, os, tarfile, shutil
import MySQLdb
from bz2 import decompress


LINUX_DIR = "linux-4.13.3"
LINUX_TAR =  LINUX_DIR + ".tar.xz"
MAKE_J4 = "make -j4"

def init():

    if not os.path.isdir(LINUX_DIR):
        tar = tarfile.open(LINUX_TAR, "r:xz")
        tar.extractall()
        tar.close()

    os.chdir("/home/luisky/dev/M1_SSR/incremental_compilation/linux-4.13.3")
    if not os.path.isfile(".config"):
        str_make_tinyconfig = "KCONFIG_ALLCONFIG=../tuxml.config make tinyconfig".format()
        subprocess.call(args=str_make_tinyconfig, shell=True)

    subprocess.call(args=MAKE_J4, shell=True)

    os.chdir("..")
    return
    

def get_cid_data(cids=10):
    
    socket = MySQLdb.connect(host="148.60.11.195", user="script2", passwd="ud6cw3xNRKnrOz6H", database="IrmaDB_prod")
    cursor = socket.cursor()


    query = "SELECT cid, core_size, config_file FROM Compilations  WHERE core_size > 0 ORDER BY cid DESC LIMIT {}".format(cids)
    cursor.execute(query)

    compilations = cursor.fetchall()

    return compilations


if __name__ == "__main__":
    
    init()
    comp_data = get_cid_data()

    res_file = open("res_file", "w+")
    res_file.write("cid, core_size, core_size_inc\n")

    core_sizes = []

    for row in comp_data:

        hit = True
        for core in core_sizes:
            if row[1] == core:
                hit = False

        if hit is True:
            shutil.copytree(LINUX_DIR, str(row[0]))
            os.chdir(str(row[0]))

            f = open(str(row[0]),"wb+")
            f.write(row[2])
            f.close()

            data = decompress(row[2]).decode('ascii')
            f = open(".config", "w+")
            f.write(data)
            f.close()

            subprocess.call(args=MAKE_J4, shell=True)
            size = os.path.getsize("vmlinux")

            res_string = "{}, {}, {}\n".format(str(row[0]), str(row[1]), str(size))
            res_file.write(res_string)

            core_sizes.append(row[1])

            os.chdir("..")
            shutil.rmtree(str(row[0]))
            
