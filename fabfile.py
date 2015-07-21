from fabric.api import run, sudo, env, require, settings, local, put, reboot
from fabric.contrib.files import exists
import subprocess, sys, os

### DEVELOPER IMPORTS (PRIVILEGED ACCESS) ###

try:
    this_path = os.path.dirname(__file__)
    sys.path.append(os.path.join(this_path, '..', 'ReceptorMarkerDev'))
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
INSTALL_PACKAGES = ['r-recommended=3.1.2-1trusty0',
                    'r-base=3.1.2-1trusty0',
                    'r-base-dev=3.1.2-1trusty0',
                    'libssl-dev',
                    'libgeoip-dev',
                    'git-core',
                    'python-bs4',
                    'libcurl4-openssl-dev',
                    'default-jre',
                    'libssl-dev',
                    'libxml2-dev',
                    'curl',
                    'python-numpy',
                    'python-setuptools',
                    'python-dev',
                    'build-essential',
                    'mime-support',
                    'libfuse-dev',
                    'automake',
                    'libtool']


### ENVIRONMENTS ###

def vagrant():
    """Defines the Vagrant virtual machine's environment variables. Local
    development and server will use this environment.
    """
    # Configure SSH things
    raw_ssh_config = subprocess.Popen(['vagrant', 'ssh-config'], stdout=subprocess.PIPE).communicate()[0]
    ssh_config_list = [l.strip().split() for l in raw_ssh_config.split("\n") if l]
    ssh_config = dict([x for x in ssh_config_list if x != []])
    env.hosts = ['127.0.0.1:%s' % (ssh_config['Port'])]
    env.user = ssh_config['User']
    env.key_filename = ssh_config['IdentityFile']
    env.repo = ('env.example.com', 'origin', 'master')  # Develop in master branch
    env.virtualenv, env.parent, env.branch = env.repo
    env.base = '/server'
    env.settings = 'vagrant'
    env.dev_mode = True

### ROUTINES ###

def setup_vagrant():
    """Sets up the Vagrant environment."""
    require('hosts', provided_by=[vagrant])  # Sets the environment for Fabric
    sub_add_repos()
    sub_install_packages()
    sub_build_packages()
    sudo("usermod -aG vagrant www-data") # Ad www-data to the vagrant group
    # TODO: You should probably be using a virtualenv here
    sub_install_R_packages()
    reload()


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

def ssh():
    """SSH into a given environment"""
    require('hosts', provided_by=[staging, production])
    cmd = "ssh -i {0} {1}@{2}".format(
             env.key_filename,
             env.user,
             env.hosts[0]
    )
    local(cmd)

def sub_install_packages():
    """Installs the necessary packages to get Rserve up and running."""
    # TODO: Duplicated elsewhere
    sudo('apt-get update')
    sudo('apt-get -y upgrade')
    package_str = ' '.join(INSTALL_PACKAGES)
    sudo('apt-get --force-yes install ' + package_str)
    sub_install_Rserve()
    sub_install_Biopython()

def sub_build_packages():
    """Builds necessary packages."""
    sub_build_nginx()

def sub_build_nginx():
    """Builds NginX to configure this server as a static media server for Django."""
    sudo("mkdir -p /usr/src/nginx")
    sudo("""cd /usr/src/nginx; if [ ! -e nginx-1.7.6.tar.gz ]; then
         wget 'https://github.com/openresty/headers-more-nginx-module/archive/v0.25.tar.gz' ; \
         tar xfz v0.25.tar.gz; \
         wget 'http://nginx.org/download/nginx-1.7.6.tar.gz' ; \
         tar xfz nginx-1.7.6.tar.gz; \
         cd nginx-1.7.6/; \
         ./configure --pid-path=/var/run/nginx.pid \
         --add-module=/usr/src/nginx/headers-more-nginx-module-0.25 \
         --conf-path=/etc/nginx/nginx.conf \
         --sbin-path=/usr/local/sbin \
         --user=www-data \
         --group=www-data \
         --http-log-path=/var/log/nginx/access.log \
         --error-log-path=/var/log/nginx/error.log \
         --with-http_stub_status_module \
         --with-http_ssl_module \
         --with-http_realip_module \
         --with-sha1-asm \
         --with-sha1=/usr/lib \
         --http-fastcgi-temp-path=/var/tmp/nginx/fcgi/ \
         --http-proxy-temp-path=/var/tmp/nginx/proxy/ \
         --http-client-body-temp-path=/var/tmp/nginx/client/ \
         --with-http_geoip_module \
         --with-http_gzip_static_module \
         --with-http_sub_module \
         --with-http_addition_module \
         --with-file-aio \
         --with-http_dav_module \
         --without-mail_smtp_module; make ; make install;
         fi
         """)
    sudo("mkdir -p /var/tmp/nginx; chown www-data /var/tmp/nginx")

    put("config/nginx.conf","/etc/init/nginx.conf",use_sudo=True)
    sudo("mkdir -p /server/www/media")
    copy_nginx_config()

def copy_nginx_config():
    """Copies the NginX configuration file for serving static files to Django's app server."""
    if env.dev_mode:
        put("config/nginx/dev_nginx.conf", "/etc/nginx/nginx.conf", use_sudo=True)
        put("config/nginx/dev_static_server.conf","/etc/nginx/static_server.conf", use_sudo=True)
    else:
        put("config/nginx/nginx.conf", "/etc/nginx/nginx.conf", use_sudo=True)
        if env.settings == 'production':
            put("config/nginx/static_server.conf","/etc/nginx/static_server.conf", use_sudo=True)
        else:
            put("config/nginx/stage_static_server.conf","/etc/nginx/static_server.conf", use_sudo=True)

def sub_start_processes():
    """Starts NginX."""
    sudo("start nginx")

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
    # Configure Rserve: guid and uid are for 'vagrant' user; 33MB maximum file
    # transfer; no authentication since pyRserve doesn't support it right now;
    # enable remote connections from other machines; strings are encoded as
    # utf8 before being sent to client and all strings received are assumed
    # to come as utf8; use specific port. Config file lives in config/Rserv.conf
    # on local.
    if env.settings == 'vagrant':
        local_conf = os.path.join(os.path.dirname(__file__), 'config', 'dev_Rserv.conf')
        put(local_conf, '/etc/Rserv.conf', use_sudo=True, mirror_local_mode=True)
        # Add Upstart job, one for Vagrant, one for EC2
        put('config/upstart_rserve_dev.conf', '/etc/init/rserve.conf',
            use_sudo=True)
    else:
        local_conf = os.path.join(os.path.dirname(__file__), 'config', 'Rserv.conf')
        put(local_conf, '/etc/Rserv.conf', use_sudo=True, mirror_local_mode=True)
        sudo("chown -R www-data:www-data /vagrant/project/Rserve")
        # Add Upstart job, one for Vagrant, one for EC2
        put('config/upstart_rserve.conf', '/etc/init/rserve.conf', use_sudo=True)

def sub_install_Biopython():
    """Installs Biopython."""
    sudo("easy_install -f http://biopython.org/DIST/ biopython")

def sub_start_Rserve():
    """Starts the Rserve daemon."""
    if env.settings in ('staging', 'production'):
        require('hosts', provided_by=[staging, production])
    start_cmd = sub_Rserve_start_cmd()
    run(start_cmd)

def sub_Rserve_start_cmd():
    """Cannonical location of the startup command for Rserve."""
    # TODO: Duplicated elsewhere
    return 'sudo service rserve start'
    #if env.settings == 'staging' or env.settings == 'production':
    #    return 'sudo R CMD Rserve --gui-none --no-save'
    #else:
    #    return 'R CMD Rserve --gui-none --no-save'

def sub_install_R_packages():
    """Installs any packages required to run R scripts."""
    sub_install_ape()
    sub_install_seqinr()
    sub_install_httr()
    sub_install_devtools()
    sub_install_rsqlite()
    sub_install_jsonlite()
    sub_uninstall_old_muscle()


def sub_uninstall_old_muscle():
    sudo('rm -rf /usr/local/lib/R/site-library/muscle')


def sub_install_ape():
    """Installs the package ape, a package for building phylogenies."""
    sudo('R -e "install.packages(\'ape\', '
         'repos=\'http://cran.rstudio.com/\')"')

def sub_install_seqinr():
    """Installs the seqinr package for reading and using DNA sequence
    alignments. http://cran.r-project.org/web/packages/seqinr/seqinr.pdf.
    """
    sudo('R -e "install.packages(\'seqinr\', '
         'repos=\'http://cran.rstudio.com/\')"')

def sub_install_httr():
    """Installs the httr package that provides a wrapper for RCurl.
    Mainly used for URL parsing and the like."""
    sudo('R -e "install.packages(\'httr\', '
         'repos=\'http://cran.rstudio.com/\')"')

def sub_install_devtools():
    """Installs the devtools package that allows for installing packages from
    Github. Will be used to install the 'receptormarker' package."""
    sudo('R -e "install.packages(\'devtools\', '
         'repos=\'http://cran.rstudio.com/\')"')

def sub_install_rsqlite():
    """Installs SQLite for reading and writing SQLite files."""
    sudo('R -e "install.packages(\'RSQLite\', '
         'repos=\'http://cran.rstudio.com/\')"')

def sub_install_jsonlite():
    """Installs SQLite for reading and writing SQLite files."""
    sudo('R -e "install.packages(\'jsonlite\', '
         'repos=\'http://cran.rstudio.com/\')"')

def reload():
    """Restart the server."""
    # TODO: Duplicated elsewhere
    if env.settings in ('staging', 'production'):
        require('hosts', provided_by=[staging, production])
        reboot(40)
    else:
        require('hosts', provided_by=[vagrant])
        local('vagrant reload')
