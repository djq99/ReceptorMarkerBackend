ReceptorMarkerBackend
=====================
This repository contains the files to create a virtual machine (VM) running  the
remote analytical server for ReceptorMarker site. This server performs  the bulk
of the analysis for ReceptorMarker using R (through Rserve) and Python  (with
NumPy). It also generates and hosts many of the visualizations loaded  by
ReceptorMarker.

The purpose of having a separate analytical server is to prevent the 
Django-based frontend from slowing down when heavy analyses are being 
performed. This separation also allows the analytical server to scale if 
needed, without bringing the frontend up on a more powerful machine when it  is
not necessary, given that the frontend probably won't ever require much 
horsepower.

The files found here are the same as those used on the live site,  with the
exception of some configuration files, which are excluded for  security
purposes, and some setup functions, which are omitted in order to  keep the
files in this repository concise for newcomers.
