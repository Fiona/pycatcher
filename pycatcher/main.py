"""
PyCatcher
By Fiona Burrows <fiona@myrmidonprocess.com>
"""

import os, sys, time, gtk, Image, curses
import curses.ascii
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

currently_paused = False

stdscr = curses.initscr()

def _print(str):
	""" Helper func for curses """
	stdscr.addstr(str)
	stdscr.refresh()
	

def _die(msg):
	""" Helper func for curses """
	curses.nocbreak(); stdscr.keypad(0); curses.echo()
	curses.endwin()
	sys.exit(msg)

	
def take_image():
	""" The magic method - Captures an image and saves it out. """

	# take screenshot
	_print("Trying to take screengrab ...")
	
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
		 _die("Failed taking screenshot")

	_print("Converting to PIL image ...")

	final_screengrab = Image.frombuffer(
		"RGB",
		(img_width, img_height),
		screengrab.get_pixels(),
		"raw",
		"RGB",
		screengrab.get_rowstride(),
		1
	)

	_print("Saving image ...")

	global img_counter
	
	# Check what our filename should be
	while True:
		
		try_file = config['filename_prefix']  + ((5 - len(str(img_counter))) * "0") + str(img_counter) + ".png"
		
		if os.path.exists(config['filename_path'] + try_file) == False:
			break

		img_counter += 1

	# Save it out
	final_screengrab.save(config['filename_path'] + try_file, "PNG")

	_print("Saved as %s \n" % try_file)


def thread_through():
	""" Used for threading the screenshot taking mechanism so we can get input
	And still be lazy with time.sleep() """
	global currently_paused
	
	while True:
		if currently_paused == False:
			take_image()
			time.sleep(config['delay'])


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

	#curses.noecho()
	#curses.cbreak()
	stdscr.keypad(1)

	_print("---------------------------\n")
	_print("PyCatcher -----------------\n")
	_print("---------------------------\n")
	_print("By Fiona Burrows ----------\n")
	_print("---------------------------\n")
	_print("<fiona@myrmidonprocess.com-\n\n")

	_print("* Esc to quit, space to pause capturing.\n\n")	
	_print("* Using configuration file at %s.py \n" % options.config_filename)
	_print("* Starting capture thread... \n\n")
	
	import thread
	thread.start_new_thread(thread_through, ())

	global currently_paused
	
	while 1:
		c = stdscr.getch()
		if c == curses.ascii.ESC:
			break
		elif c == curses.ascii.SP:
			if currently_paused:
				currently_paused = False
				_print("* Unpaused\n\n")
			else:
				currently_paused = True
				_print("* Paused\n\n")

	_die("Quit!")
	

if __name__ == "__main__":
	main()

