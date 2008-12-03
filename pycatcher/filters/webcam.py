"""
PyCatcher
By Fiona Burrows <fiona@myrmidonprocess.com>
--------
Filter file: Webcam displaying
"""

import opencv
from opencv import highgui

class image_filter(object):

	config = {
		'width' : 50,
		'height' : 50,
		'coordinates' : (10,10),
		'border_colour' : "#fff"
		}

	camera = None

	def __init__(self):
		self.camera = highgui.cvCreateCameraCapture(0)
		
	
	def apply_filter(self, image, _config):
		highgui.cvQueryFrame(self.camera)
		im = highgui.cvQueryFrame(self.camera)		
		pilwebcam_image = opencv.adaptors.Ipl2PIL(im)

		pilwebcam_image.thumbnail(
			(
			int((pilwebcam_image.size[0] / 100.0) * _config['width']),
			int((pilwebcam_image.size[1] / 100.0) * _config['height'])		
			)
		)

		## Border
		from ImageDraw import Draw
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
