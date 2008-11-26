"""
PyCatcher
By Fiona Burrows <fiona@myrmidonprocess.com>
"""

import os, sys, time, gtk, Image
from optparse import OptionParser

config = {
	# Path to define where to save images. Relative to where the script is run.
	'filename_path' : 'images/',
	# Filenames are saved as prefix%n.png where %n is the number in the sequence.
	'filename_prefix' : 'img-',
	# Delay in seconds between each image shot
	'delay' : 60
}

img_counter = 1


def take_image():
	""" The magic method - Captures an image and saves it out. """
	
	# take screenshot
	print "Trying to take screengrab ..."
	
	try:

		img_width = gtk.gdk.screen_width()
		img_height = gtk.gdk.screen_height()
		
		screengrab = gtk.gdk.Pixbuf(
			gtk.gdk.COLORSPACE_RGB,
			False,
			8,
			img_width,
			img_height
		)

		screengrab.get_from_drawable(
			gtk.gdk.get_default_root_window(),
			gtk.gdk.colormap_get_system(),
			0, 0, 0, 0,
			img_width,
			img_height
		)

	except:
		 sys.exit("Failed taking screenshot")

	print "Converting to PIL image ..."

	final_screengrab = Image.frombuffer(
		"RGB",
		(img_width, img_height),
		screengrab.get_pixels(),
		"raw",
		"RGB",
		screengrab.get_rowstride(),
		1
	)

	print "Saving image ..."

	global img_counter
	
	# Check what our filename should be
	while True:
		
		try_file = config['filename_prefix']  + ((5 - len(str(img_counter))) * "0") + str(img_counter) + ".png"
		
		if os.path.exists(config['filename_path'] + try_file) == False:
			break

		img_counter += 1

	# Save it out
	final_screengrab.save(config['filename_path'] + try_file, "PNG")

	print "Saved as %s" % try_file


def load_configuration(filename):
	""" Overrides the configuration values within the defined file """
	config_mod = __import__(filename)
	config.update(config_mod.config)
	

def main():
	""" Main entry point """
	parser = OptionParser()

	parser.add_option("-c", "--config", dest="config_filename",
					  default="defaults",
                      help="Specify name of configuration file. [Default: %default]")

	(options, args) = parser.parse_args()

	if os.path.exists(options.config_filename + ".py") == False:
		parser.error("Configuration file not found.")

	load_configuration(options.config_filename)

	if os.path.exists(config['filename_path']) == False:
		sys.exit("Path defined in configuration does not exist.")

	while True:
		take_image()
		time.sleep(config['delay'])
	

if __name__ == "__main__":
	main()

