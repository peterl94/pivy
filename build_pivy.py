#!/usr/bin/env python

###
# Copyright (C) 2002-2004, Tamer Fahmy <tamer@tammura.at>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

###
# Pivy configure, build and install script.
#

###
# FIXME: this unmaintainable completely waste of time ugly duck script was
#   inspired by the devil himself. try to get rid of it asap and make
#   use of distutils instead like anyone else not from hell.
#   20040103 tamer.
#

"""Pivy is an Open Inventor binding for Python. Open Inventor is an object
oriented 3D toolkit which presents a programming model based on a 3D scene
database. It was developed by Silicon Graphics.

The binding has been interfaced to Coin - a 3D graphics library with an C++
Application Programming Interface based on the Open Inventor 2.1 API.

Pivy has been developed by Tamer Fahmy and is made available under a
BSD-style license.
"""

import getopt, os, sys
# from distutils.core import setup
# from distutils.extension import Extension
import distutils.sysconfig

VERSION = "0.3a"

PIVY_SNAKES = r"""
                        _____
                    .-'`     '.                                     
                 __/  __       \                                   
                /  \ /  \       |    ___                          
               | /`\| /`\|      | .-'  /^\/^\                   
               | \(/| \(/|      |/     |) |)|                     
              .-\__/ \__/       |      \_/\_/__..._             
      _...---'-.                /   _              '.               
     /,      ,             \   '|  `\                \           
    | ))     ))           /`|   \    `.       /)  /) |             
    | `      `          .'       |     `-._         /               
    \                 .'         |     ,_  `--....-'               
     `.           __.' ,         |     / /`'''`                     
       `'-.____.-' /  /,         |    / /                           
           `. `-.-` .'  \        /   / |                           
             `-.__.'|    \      |   |  |-.                         
                _.._|     |     /   |  |  `'.                       
          .-''``    |     |     |   /  |     `-.                    
       .'`         /      /     /  |   |        '.                  
     /`           /      /     |   /   |\         \               
    /            |      |      |   |   /\          |               
   ||            |      /      |   /     '.        |                
   |\            \      |      /   |       '.      /              
   \ `.           '.    /      |    \        '---'/               
    \  '.           `-./        \    '.          /                
     '.  `'.            `-._     '.__  '-._____.'--'''''--.         
       '-.  `'--._          `.__     `';----`              \       
          `-.     `-.          `.''```                     ;        
             `'-..,_ `-.         `'-.                     /         
                    '.  '.           '.                 .'          
                                                                    
                                                                    
                        ~~~ HISSSSSSSSSS ~~~
                  Welcome to build_pivy.py v%s!
             Building Pivy has never been so much fun!

""" % VERSION


CXX = "g++"
ELF_OPTS = "-shared -fPIC -O2"
DARWIN_OPTS = "-bundle -bundle_loader %s" % sys.executable

SWIG = "swig"
SWIG_SUPPRESS_WARNINGS = "-w302,306,307,312,389,362,503,509,510"
SWIG_PARAMS = "-c -v -c++ -python -includeall " + \
              "-D__PIVY__ -I. -Ifake_headers -I%s %s -o %s_wrap.cxx %s.i"

SOGUI = ['SoQt', 'SoXt', 'SoGtk']
MODULES = {'pivy'  : ('_pivy.so',  'coin-config'),
           'SoQt'  : ('_soqt.so',  'soqt-config'),
           'SoXt'  : ('_soxt.so',  'soxt-config'),
           'SoGtk' : ('_sogtk.so', 'sogtk-config')}

SUPPORTED_SWIG_VERSIONS = ['1.3.19']
SWIG_COND_SYMBOLS = []
CXX_INCS = "-I" +  distutils.sysconfig.get_python_inc() + " "
CXX_LIBS = "-lswigpy" + " "

config_log = None

def write_log(msg):
    "outputs messages to stdout and to a log file."
    sys.stdout.write(msg)
    config_log.write(msg)

def do_os_popen(cmd):
    "returns the output of a command in a single line."
    fd = os.popen(cmd)
    lines = fd.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].strip()
    lines = " ".join(lines)
    fd.close()
    return lines

def check_cmd_exists(cmd):
    "returns the path of the specified command if it exists."
    write_log("Checking for %s..." % cmd)
    for path in os.environ['PATH'].split(':'):
        if os.path.exists(os.path.join(path, cmd)):
            write_log("'%s'\n" % os.path.join(path, cmd))
            return 1
    write_log("not found.\n")
    return 0

def check_python_version():
    "checks the Python version."
    write_log("Python version...%s\n" % sys.version.split(" ")[0])
    if int(sys.version[0]) < 2:
        write_log("Pivy only works with Python versions >= 2.0.\n")
        sys.exit(1)

def check_coin_version():
    "checks the Coin version."
    if not check_cmd_exists("coin-config"):
        sys.exit(1)
    write_log("Coin version...")
    version = do_os_popen("coin-config --version")
    if not version.startswith('2.1'):
        write_log("Warning: Pivy has only been tested with Coin "
                  "versions 2.1.x.\n")
    write_log("%s\n" % version)

def check_gui_bindings():
    "checks for availability of SoGui bindings and removes the not available ones."
    global MODULES

    for gui in SOGUI:
        gui_config_cmd = MODULES[gui][1]
        if not check_cmd_exists(gui_config_cmd):
            del MODULES[gui]
        else:
            write_log("Checking for %s version..." % gui)
            version = do_os_popen("%s --version" % gui_config_cmd)
            write_log("%s\n" % version)

def get_coin_features():
    "sets the global variable SWIG_COND_SYMBOLS needed for conditional " + \
    "wrapping"
    global SWIG_COND_SYMBOLS

    write_log("Checking for Coin features...")
    if not os.system("coin-config --have-feature 3ds_import"):
        SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_3DS_IMPORT")
        write_log("3ds import ")

    if not os.system("coin-config --have-feature vrml97"):
        SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_VRML97")
        write_log("vrml97 ")

    if not os.system("coin-config --have-feature sound"):
        SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_SOUND")
        write_log("sound ")

    if not os.system("coin-config --have-feature superglu"):
        SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_SUPERGLUE")
        write_log("superglu ")

    if not os.system("coin-config --have-feature threads"):
        SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_THREADS")
        write_log("threads ")

    if not os.system("coin-config --have-feature threadsafe"):
        SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_THREADSAFE")
        write_log("threadsafe ")

    write_log("\n")

def check_compiler_version(compiler):
    "checks for the compiler version."
    if not check_cmd_exists(compiler):
        sys.exit(1)
    fd = os.popen("%s --version" % compiler)
    for line in fd.readline():
        write_log(line)
    fd.close()
    
def check_swig_version(swig):
    "checks for the swig version."
    if not check_cmd_exists(swig):
        sys.exit(1)
    write_log("Checking for SWIG version...")        
    fd = os.popen("%s -version 2>&1" % swig)
    version = fd.readlines()[1].strip().split(" ")[2]
    fd.close()
    write_log("%s\n" % version)
    if not version in SUPPORTED_SWIG_VERSIONS:
        write_log("Warning: Pivy has only been tested with the following" + \
                  "SWIG versions: %s.\n" % " ".join(SUPPORTED_SWIG_VERSIONS))

def configure():
    "configures Pivy"
    write_log(PIVY_SNAKES)
    write_log("Platform...%s\n" % sys.platform)
    check_python_version()
    check_coin_version()
    if SOGUI: check_gui_bindings()
    get_coin_features()
    check_compiler_version(CXX)
    check_swig_version(SWIG)

def build():
    "build all available modules"
    for module in MODULES.keys():
        module_name = MODULES[module][0]
        config_cmd = MODULES[module][1]

        sys.stdout.write("\n=== Building %s ===\n\n" % module)
        
        write_log(SWIG + " " + SWIG_SUPPRESS_WARNINGS + " " + SWIG_PARAMS %
                  (do_os_popen("coin-config --includedir"),
                   CXX_INCS + do_os_popen("%s --cppflags" % config_cmd),
                   module.lower(),
                   module.lower()) + "\n")
        if not os.system(SWIG + " " + SWIG_SUPPRESS_WARNINGS + " " + SWIG_PARAMS %
                         (do_os_popen("coin-config --includedir"),
                          CXX_INCS + do_os_popen("%s --cppflags" % config_cmd),
                          module.lower(), module.lower())):
            OPTS = ""
            if sys.platform.startswith("linux"):
                OPTS=ELF_OPTS
            elif sys.platform.startswith("darwin"):
                OPTS=DARWIN_OPTS
            sys.stdout.write("\n  +" + "-"*61 + "+\n")
            sys.stdout.write("  | The remedy against bad times is to " + \
                             "have patience with them! |\n")
            sys.stdout.write("  +" + "-"*61 + "+\n\n")
            write_log(" ".join((CXX, OPTS,
                                CXX_INCS + do_os_popen("%s --cppflags" % config_cmd),
                                CXX_LIBS + do_os_popen("%s --ldflags --libs" % config_cmd),
                                "-o %s %s_wrap.cxx" % (module_name, module.lower()))) + "\n")
            if not os.system(" ".join((CXX, OPTS,
                                       CXX_INCS + do_os_popen("%s --cppflags" % config_cmd),
                                       CXX_LIBS + do_os_popen("%s --ldflags --libs" % config_cmd),
                                       "-o %s %s_wrap.cxx" % (module_name, module.lower())))):
                write_log("Importing %s.py...\n" % module.lower())
                __import__(module.lower())
            else:
                sys.exit(1)
        else:
            sys.exit(1)
        

def cleanup():
    "cleanup method"
    if config_log:
        config_log.close()

def usage():
    "outputs a usage message"
    sys.stdout.write(os.path.basename(sys.argv[0]) + " " + VERSION + ""
                     "\nUsage: " + os.path.basename(sys.argv[0]) + " [options]"
                     "\n\nwhere options include:\n"
                     "\n--without-sogui  \tbuild without GUI bindings"
                     "\n-w, --warn       \tdon't suppress SWIG warnings"
                     "\n-h, --help       \tprint this message and exit"
                     "\n-v, --version    \tprint version and exit"
                     "\n\nPlease report bugs to <tamer@tammura.at>.\n")
    
def option_check():
    "check for options"
    global SOGUI, MODULES, SWIG_SUPPRESS_WARNINGS
    
    try:
        (options, arguments) = getopt.getopt(sys.argv[1:], "whvi",
                                             ["without-sogui", "warn", "help",
                                              "version", "install"])
        for opt in options:
            if opt[0] == "--without-sogui":
                for gui in SOGUI: del MODULES[gui]
                SOGUI = None
            elif opt[0] in ("-w", "--warn"):
                SWIG_SUPPRESS_WARNINGS = ""
            elif opt[0] in ("-h", "--help"):
                usage(); sys.exit(0)
            elif opt[0] in ("-v", "--version"):
                sys.stdout.write(os.path.basename(sys.argv[0]) + " " + \
                                 VERSION + "\n"); sys.exit(0)
            elif opt[0] in ("-i", "--install"):
                # FIXME: implement install procedure. 20040103 tamer.
                pass
                
    except getopt.error, error:
        usage()
        sys.exit(1)

if __name__ == "__main__":
    option_check()
    sys.exitfunc = cleanup
    config_log = open("config.log", 'w')
    configure()
    build()
    
###
# distutils setup
##setup(name = "Pivy",
##      version = "0.1",
##      description = "An Open Inventor Python binding",
##      long_description = __doc__,
##      author = "Tamer Fahmy",
##      author_email = "tamer@tammura.at",
##      maintainer = "Tamer Fahmy",
##      maintainer_email = "tamer@tammura.at",      
##      url = "http://pivy.tammura.at/",
##      ext_modules = [Extension("_pivy",
##                               ["pivy_wrap.cxx"],
##                               include_dirs=["/opt/qt/include"],
##                               define_macros=SWIG_COND_SYMBOLS,
##                               extra_compile_args=[pivy_incs],
##                               extra_link_args=[pivy_libs + "-lstdc++"])
##                     ],
##      py_modules = ["pivy"])
