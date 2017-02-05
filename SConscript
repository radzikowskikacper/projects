# -*- mode: Python; -*- scons script
import os, platform, re, shutil


## IMPORT CONFIG

Import('env')

Import('ZAPISY_VER_MAJOR')
Import('ZAPISY_VER_MINOR')
Import('ZAPISY_VER_COMPILATION')
Import('DEBUG_FLAG')


def build_websrv_version( target, source, env):
    """Saves version of project into a file"""
    file = open(str(target[0]), 'w')
    file.write('__version__ = "' + ZAPISY_VER_MAJOR + '.' +
               ZAPISY_VER_MINOR + '.' +ZAPISY_VER_COMPILATION + '"\n')
    file.close()


def set_django_debug_flag():
   """Set django settings.DEBUG flag to the value from build_custom.ini"""
   djang_settings_path = os.path.join('settings','local.py')
   with open(djang_settings_path, 'r+') as f:
       lines = f.readlines()
       f.seek(0)
       f.truncate()
       for line in lines:
           if 'DEBUG =' in line:
               if DEBUG_FLAG:
                   line = line.replace('False','True')
               else:
                   line = line.replace('True','False')
           f.write(line)


## SCONSCRIPT WORK

# Set django debug flag
set_django_debug_flag()

# Generate file with version number
file_ver_name = 'apps/version_gen.py'
version_file = env.Command(file_ver_name, [], build_websrv_version )
env.AlwaysBuild(version_file)

env.Clean('.', 'apps/version_gen.py')

## lighttpd config files dependencies
config = 'config.py'
env.SideEffect('lighttpd.develop', config)
env.SideEffect('lighttpd.log', config)
env.SideEffect('lighttpd.pid', config)
env.SideEffect('config.pyc', config)
