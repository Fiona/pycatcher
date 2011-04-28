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
    'filters' : [],
    # filter specific config
    'filters_config' : {}

}

img_counter = 1

currently_paused = False
quit = False

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
        final_screengrab = filter_instances[filter_name].apply_filter(final_screengrab, config['filters_config'][filter_name])

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


def input_thread():
    """ Handles input. Does all the pausing. """
    global currently_paused, quit
    
    while True:
        get_input = sys.stdin.readline()
        
        if get_input == "\n" and not currently_paused:
            currently_paused = True
            print "* Paused...\n* Please enter a command. (Type exit to close PyCatcher or nothing to continue capturing.) "

        elif get_input in ["exit\n", "quit\n", "q\n"] and currently_paused:
            quit = True
            return

        elif currently_paused:
            parse_command(get_input)
            currently_paused = False
            print "* Unpaused...\n"


def image_handling_thread():
    """ Is responsible for taking images and waiting between shots. """
    global currently_paused, quit
    
    while True:
        if currently_paused == False:
            take_image()
            for x in range(config['delay']):
                if quit:
                    return
                time.sleep(1)


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
        
        if filter_name in config['filters_config']:
            filter_instances[filter_name].config.update(config['filters_config'][filter_name])
        config['filters_config'][filter_name] = filter_instances[filter_name].config

            

    print "---------------------------"
    print "PyCatcher -----------------"
    print "---------------------------"
    print "By Fiona Burrows ----------"
    print "---------------------------"
    print "<fiona@myrmidonprocess.com-\n"

    print "* Hit enter to pause capturing and/or enter a command.\n"
    print "* Using configuration file at %s.py" % options.config_filename
    print "* Starting capture thread... \n"

    from threading import Thread

    #import thread
    #thread.start_new_thread(thread_through, ())
    input_thread_handle = Thread(target=input_thread, args=())
    image_handling_thread_handle = Thread(target=image_handling_thread, args=())

    input_thread_handle.start()
    image_handling_thread_handle.start()
    
    global currently_paused, quit
    
    while True:
        if quit:
            break

    # Wait for threads to die
    input_thread_handle.join()
    image_handling_thread_handle.join()
    
    sys.exit("Quit!")
    

if __name__ == "__main__":
    main()

