"""
PyCatcher
By Fiona Burrows <fiona@myrmidonprocess.com>
--------
Filter file: Webcam displaying
"""

import cv, Image
from ImageDraw import Draw


class image_filter(object):

    config = {
        'width' : 100,
        'height' : 100,
        'coordinates' : (10,10),
        'border_colour' : "#fff"
        }

    camera = None

    def __init__(self):
        self.camera = cv.CaptureFromCAM(-1)
        
    
    def apply_filter(self, image, _config):
        # OpenCV sucks, it keeps all frames cached so when I query them
        # they are old frames. I delete the camera object and get a new one
        # so i can query the current frame only.
        # this is the only solution i could work out to this problem.
        del self.camera
        self.camera = cv.CaptureFromCAM(-1)

        im = cv.QueryFrame(self.camera)

        # HEY HERE IS SOMETHING REALLY FUNNY
        # OPENCV USES BGR FOR IT'S INTERNAL IMAGE FORMAT
        # WOW
        # SO STANDARD GUYS
        # FAN-FUCKING-TASTIC
        # I DIDN'T TOTALLY JUST SPEND THREE HOURS WORKING THAT OUT
        # GREAT STUFF
        # YOUR OWN EXAMPLE CODE FOR CONVERTING TO A PIL IMAGE DOESN'T TAKE THIS INTO ACCOUNT AT ALL
        # WTFFFFFFFFFFF
        pilwebcam_image = Image.fromstring("RGB", cv.GetSize(im), im.tostring()[::-1]).rotate(180)

        pilwebcam_image = pilwebcam_image.resize(
            (
            int((pilwebcam_image.size[0] / 100.0) * _config['width']),
            int((pilwebcam_image.size[1] / 100.0) * _config['height'])      
            ),
            Image.ANTIALIAS
        )

        ## Border
        drawing = Draw(pilwebcam_image)

        # top line
        drawing.line(((0,0), (pilwebcam_image.size[0], 0)), fill = _config['border_colour'])
        # left line
        drawing.line(((0,0), (0, pilwebcam_image.size[1])), fill = _config['border_colour'])
        # right line
        drawing.line(((pilwebcam_image.size[0]-1,0), (pilwebcam_image.size[0]-1, pilwebcam_image.size[1])), fill = _config['border_colour'])
        # bottow line
        drawing.line(((0, pilwebcam_image.size[1]-1), (pilwebcam_image.size[0], pilwebcam_image.size[1]-1)), fill = _config['border_colour'])

        image.paste(pilwebcam_image, (10,10))
        return image
