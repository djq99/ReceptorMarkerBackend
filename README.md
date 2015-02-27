Introduction
============
This repository contains the files to create a virtual machine (VM) running the
remote analytical server for [receptormarker.com][rm]. This server performs the
bulk of the analysis for ReceptorMarker using R (through Rserve) and Python
(with NumPy). It also generates and hosts many of the visualizations loaded by
ReceptorMarker.

The purpose of having a separate analytical server is to prevent the
Django-based frontend from slowing down when heavy analyses are being performed.
This separation also allows the analytical server to scale if needed, without
bringing the frontend up on a more powerful machine when it is not necessary,
given that the frontend probably won't ever require much horsepower.

The files found here are the same as those used on the live site, with the
exception of some configuration files, which are excluded for security purposes,
and some setup functions, which are omitted in order to keep the files in this
repository concise for newcomers.

[rm]: http://receptormarker.com "ReceptorMarker Homepage"

Installation
============
System Requirements: 2GB RAM Min. and 3GB Free HD Space

Install the following:

  * VirtualBox: https://www.virtualbox.org/wiki/Downloads
  * Vagrant: https://www.vagrantup.com/downloads
  * Fabric: http://www.fabfile.org/installing.html

It is likely that you already have Python, which Fabric requires. If you are
unsure, open Terminal and run `python`.

You also need to have an SSH key, since it will be used when setting up your VM
with Vagrant. See the GitHub instructions for [checking for and creating an SSH
key][ghssh]. You do not need to go through Step 3 and 4 in their instructions.
If you find a key named `id_rsa` in Step 1 then you can skip everything - you
already have an SSH key.

[ghssh]: https://help.github.com/articles/generating-ssh-keys/

The analytical server that this repo creates is only half of the ReceptorMarker
site. There is another repo that we will need to use later to bring up a
frontend. No need to worry about it now, but with that in mind you should first
create a folder that will hold both of these repos (this one, and the one we
will use later). Something like *receptormarker* is appropriate for this folder
name. Within that folder, clone this repo. So you should end up with this folder
structure somewhere on your hard drive:    

|-- *receptormarker*  
| &nbsp;&nbsp;
    |-- *ReceptorMarkerBackend*  
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        |-- a bunch of files and folders from this repo

1. You just performed this step: clone the repo.  
2. Install [Vagrant][vag] and [VirtualBox][vb].
2. `cd` into *ReceptorMarkerBackend* and run `vagrant up`. This will boot up a
   VM that runs Ubuntu Server. It will live at local IP address 66.66.66.10. The
VM's configuration comes from **Vagrantfile**.
3. Your VM server doesn't have any packages installed on it. Run `fab
vagrant setup_vagrant` to install the required packages. This could take 5-20
mins depending on the spped of your computer and internet connection.  

Keep an eye out for warnings in case you need to debug. The only one you'll
likely see is `System call failed: cannot allocate memory`. If you see this,
first try to re-run the setup command once it's done doing its thing, and if
that doesn't work then edit **Vagrantfile** and change the 1536MB in the line
`vb.customize ["modifyvm", :id, "--memory", "1536"]` to something higher. 

[vag]: https://www.vagrantup.com/downloads.html "VagrantUp Downloads"
[vb]: https://www.virtualbox.org/wiki/Downloads "VirtualBox Downloads"

## Verifying the install
You should now have an Ubuntu Server running R (via [Rserve][rs]), Python with
NumPy, and maybe some other cool things that the site leverages. The ability to
execute R commands on the remote server is critical. You can test this by
installing pyRserve (a Python client for Rserve) on your local computer, opening
a Python shell, and connecting to the server:  

```python
pip install pyRserve  # Install pyRserve if it is not installed yet
python  # Start the Python shell
>>> import pyRserve
>>> conn = pyRserve.connect(host='66.66.66.10')  # Attempt the connection to
>>> Rserve at the VM's IP
>>> conn
<Handle to Rserve on 66.66.66.10:6311>
# evaluate something in R
>>> conn.eval("2+2")
4.0
# list loaded R packages
>>> conn.eval("libraries()")
array(['httr', 'ape', 'muscle', 'seqinr', 'ade4', 'stats', 'graphics',
'grDevices', 'utils', 'datasets', 'methods', 'base'], dtype='S9')
```

Notice that what you are getting back from the call to Rserve is a NumPy array.
See the [pyRserve][pyr] manual for more information on this topic.

[rs]: http://www.rforge.net/Rserve/ "Rserve - TCP/IP server for R"
[pyr]: http://pythonhosted.org//pyRserve/ "pyRserve Documentation"

Commands Guide
==============
`vagrant up` = boot the VM  
`vagrant halt` = shutdown the VM  
`fab vagrant setup_vagrant` = install any new packages to the VM  

Next Steps
==========
Once the analytical server running properly, head over to
[ReceptorMarkerFrontend][rmf] to get the repo for the frontend server. That repo
contains all the webserver and Django files and the components for the site's
user interface.

[rmf]: https://github.com/nsh87/ReceptorMarkerFrontend "ReceptorMarkerFrontend"

Contributing
============
The ReceptorMarkerFrontend Wiki is the canonical location for documentation
about contributing, local development, accessing user-uploaded files, and
information about other files and folders in the VMs. Some useful links:

* [Backend (Analytical) Server][bas] - contains info about the
  using ReceptorMarkerBackend VM for development purposes 
* [Running an Analysis on the Analytical Server][raa] - info about connecting to
  the backend server, connecting a Django app to an Rscript
* [Local Development][ld] - general info about local development, common
  commands

If you are going to do develop any analyses for ReceptorMarker you should check
out the Wiki.

[bas]: https://github.com/nsh87/ReceptorMarkerFrontend/wiki/Backend-(Analytical)-Server
[raa]: https://github.com/nsh87/ReceptorMarkerFrontend/wiki/Running-an-Analysis-on-the-Analytical-Server
[ld]: https://github.com/nsh87/ReceptorMarkerFrontend/wiki/Local-Development
