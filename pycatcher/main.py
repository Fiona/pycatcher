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
	'delay' : 60,
	# List of filters to apply to the images
	'filters' : []
}

img_counter = 1

currently_paused = False

filter_instances = {}

	
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
		 die("Failed taking screenshot")

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

	for filter_name in config['filters']:
		final_screengrab = filter_instances[filter_name].apply_filter(final_screengrab, config)

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

	print "Saved as %s \n" % try_file


def thread_through():
	""" Used for threading the screenshot taking mechanism so we can get input
	And still be lazy with time.sleep() """
	global currently_paused

	#time.sleep(config['delay'])
	
	while True:
		if currently_paused == False:
			take_image()
			time.sleep(config['delay'])


def load_configuration(filename):
	""" Overrides the configuration values within the defined file """
	config_mod = __import__(filename)
	config.update(config_mod.config)


def parse_command(command):
	pass


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

	# load any overriding filter configs
	for filter_name in config['filters']:
		fil = __import__("filters." + filter_name)
		filter_instances[filter_name] = fil.__dict__[filter_name].image_filter()
		
		filter_config = filter_instances[filter_name].config

		for k in filter_config:
			if k not in config:
				config[k] = filter_config[k]
			

	print "---------------------------"
	print "PyCatcher -----------------"
	print "---------------------------"
	print "By Fiona Burrows ----------"
	print "---------------------------"
	print "<fiona@myrmidonprocess.com-\n"

	print "* Hit enter to pause capturing and/or enter a command.\n"
	print "* Using configuration file at %s.py" % options.config_filename
	print "* Starting capture thread... \n"
	
	import thread
	thread.start_new_thread(thread_through, ())

	global currently_paused
	
	while True:
		get_input = raw_input("")
		currently_paused = True
		
		get_command = raw_input("* Paused...\n* Please enter a command. (exit to close PyCatcher or nothing to continue.)\n: ")

		if get_command in ["exit", "quit", "q"]:
			break

		if get_command != "":
			parse_command(get_command)

		currently_paused = False
		
		print "* Unpaused...\n"
		
	sys.exit("Quit!")
	

if __name__ == "__main__":
	main()

