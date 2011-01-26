
Description:

This is a simple Python script to export data from Akregator, KDE's default
RSS aggregator.  Akregator currently uses the Metakit which is a fast
database toolkit but it has a limitation as implemented with Akregator. 
After a few years of happily collecting RSS feeds, I noticed my system
becoming unstable and my system log filling up with "Too many open files"
errors.

The problem comes from the fact that Akregator stores each RSS channel in a
file and it leaves these files open while running.  With many hundreds
(thousands?) of RSS feeds, this can be problematic.  Of course, you can
adjust the upper limit of open files in the kernel but this isn't really a
good solution for what should be just a lightweight tool running in the
background.

This tool was my solution of recovering 4GB worth of years of RSS feeds from
Akregator when transitioning to a new tool.  I haven't touched this script
in well over a year but should still work.

Hope this is helpful for some.

Contact:

paul@stratofex.com

Requirements:

	You will need the Metakit library and Python bindings. 
	Unfortunately, these are not generally provided even by many popular
	distros so you may have to build these yourself.

		http://en.wikipedia.org/wiki/Metakit
                http://www.equi4.com/metakit/



