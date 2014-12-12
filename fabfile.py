from fabric.api import run, sudo, env, require, settings, local, put
from fabric.contrib.files import exists
import subprocess, sys, os

### DEVELOPER IMPORTS (PRIVILEGED ACCESS) ###

try:
    this_path = os.path.dirname(__file__)
    sys.path.append(os.path.join(this_path, '..', 'ReceptorMarkerDev'))
    from fab_common_backend import *
    from rm_server_hosts import *
    from fabfile_backend import *
except ImportError:
    pass

### VARIABLES ###
# TODO: Duplicated elsewhere
# Origin of the repository
GIT_ORIGIN = 'git@github.com'
GIT_REPO = 'nsh87/ReceptorMarkerBackend'

# Packages to install
# r-base: R's core components, should get installed with --enable-R-shlib, which
#         is required by Rserve. $RHOME will be at /usr/lib/R.
# r-base-dev: Allows installing  packages from source using install.packages()
INSTALL_PACKAGES = ['r-base=3.1.2-1trusty0',
                    'r-base-dev=3.1.2-1trusty0',
                    'git-core']


### ENVIRONMENTS ###

def vagrant():
    """Defines the Vagrant virtual machine's environment variables. Local
    development and server will use this environment.
    """
    # Configure SSH things
    raw_ssh_config = subprocess.Popen(['vagrant', 'ssh-config'], stdout=subprocess.PIPE).communicate()[0]
    ssh_config = dict([l.strip().split() for l in raw_ssh_config.split("\n") if l])
    env.hosts = ['127.0.0.1:%s' % (ssh_config['Port'])]
    env.user = ssh_config['User']
    env.key_filename = ssh_config['IdentityFile']
    env.repo = ('env.example.com', 'origin', 'master')  # Develop in master branch
    env.virtualenv, env.parent, env.branch = env.repo
    env.base = '/server'
    env.settings = 'vagrant'

### ROUTINES ###

def setup_vagrant():
    """Sets up the Vagrant environment."""
    require('hosts', provided_by=[vagrant])  # Sets the environment for Fabric
    sub_add_repos()
    sub_install_packages()
    # TODO: You should probably be using a virtualenv here
    reload()  # Restarts the VM to initialize Rserve


### SUB-ROUTINES ###

def sub_add_repos():
    """Adds any repositories needed to install packages."""
    # TODO: Duplicated elsewhere
    # Add the repository for R if it hasn't been added yet
    if not exists('/etc/apt/sources.list.d/cran.list', use_sudo=True):
        sudo('sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys '
             'E084DAB9')
        run('sudo sh -c "echo \'deb http://cran.rstudio.com/bin/linux/ubuntu '
            'trusty/\' >> /etc/apt/sources.list.d/cran.list"')

def sub_install_packages():
    """Installs the necessary packages to get Rserve up and running."""
    # TODO: Duplicated elsewhere
    sudo('apt-get update')
    sudo('apt-get -y upgrade')
    package_str = ' '.join(INSTALL_PACKAGES)
    sudo('apt-get -y install ' + package_str)
    sub_install_Rserve()

def sub_get_virtualenv():
    """Fetches the virtualenv package."""
    run("if [ ! -e virtualenv-1.11.6.tar.gz ]; then wget --no-check-certificate http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.11.6.tar.gz; fi")
    run("if [ ! -d virtualenv-1.11.6 ]; then tar xzf virtualenv-1.11.6.tar.gz; fi")
    run("rm -f virtualenv")
    run("ln -s virtualenv-1.11.6 virtualenv")

def sub_make_virtualenv():
    """Makes the virtualenv."""
    sudo("if [ ! -d %(base)s ]; then mkdir -p %(base)s; chmod 777 %(base)s; fi" % env)
    run("if [ ! -d %(base)s/%(virtualenv)s ]; then python2.7 ~/virtualenv/virtualenv.py --no-site-packages %(base)s/%(virtualenv)s; fi" % env)
    sudo("chmod 777 %(base)s/%(virtualenv)s" % env)

def sub_install_Rserve():
    """Installs Rserve and configures it."""
    # Install Rserve
    # TODO: Duplicated elsewhere
    sudo('mkdir -p /usr/src/Rserve')
    sudo('''cd /usr/src/Rserve; if [ ! -f Rserve_1.8-1.tar.gz ];
    then a='http://rforge.net/Rserve/snapshot/' ; \
    b='Rserve_1.8-1.tar.gz' ; \
    wget $a$b ; \
    R CMD INSTALL Rserve_1.8-1.tar.gz;
    fi''')
    # Make Rserve working directory on local
    sudo('''cd /etc; if [ ! -f Rserv.conf ];
    then mkdir -p /vagrant/project/Rserve ; \
    fi''')
    # Add command to start Rserve on startup
    if not exists('/etc/Rserv.conf'):
        add_to_startup = ''.join(["sed -i '14i ", sub_Rserve_start_cmd(),
                                  "' /etc/rc.local"])
        sudo(add_to_startup)
    # Configure Rserve: guid and uid are for 'vagrant' user; 33MB maximum file
    # transfer; no authentication since pyRserve doesn't support it right now;
    # enable remote connections from other machines; strings are encoded as
    # utf8 before being sent to client and all strings received are assumed
    # to come as utf8; use specific port. Config file lives in config/Rserv.conf
    # on local.
    local_conf = os.path.join(os.path.dirname(__file__), 'config', 'Rserv.conf')
    put(local_conf, '/etc/', use_sudo=True, mirror_local_mode=True)

def sub_start_Rserve():
    """Starts the Rserve daemon."""
    start_cmd = sub_Rserve_start_cmd()
    run(start_cmd)

def sub_Rserve_start_cmd():
    """Cannonical location of the startup command for Rserve."""
    # TODO: Duplicated elsewhere
    return 'R CMD Rserve --vanilla --gui-none --no-save'

def reload():
    """Restart the server."""
    # TODO: Duplicated elsewhere
    if env.settings in ('staging', 'production'):
        sudo('reboot')
    else:
        local('vagrant reload --provision')
