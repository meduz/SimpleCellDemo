#!/usr/bin/env python

"""

SimpleReceptiveField.py : linking the webcam to a crude-but-adaptive neuron and
let it spike in the loudspeaker.

Laurent Perrinet, 2010. Credits: see http://invibe.net/LaurentPerrinet/SimpleCellDemo

this depends on OpenCV + numpy + pil, which intalls fine with MacPorts: {{{
sudo port install opencv +python26 +tbb
sudo port install py26-numpy py26-scipy py26-pil py26-distribute py26-pip python_select
sudo python_select python26
sudo port install py26-ipython py26-matplotlib py26-mayavi py26-pyobjc2-cocoa  # optionnally
}}}

Credits: see pysight.py and EgoViewer.py

$Id: SimpleReceptiveField.py,v 3ff3065a2f2d 2011/04/13 14:46:44 perrinet $

"""
try:
    import pyaudio
    AUDIO = True
except:
    print('Could not import pyaudio, disabling sound')
    AUDIO = False

from numpy import zeros, linspace, hstack, transpose, pi
import numpy as np
from SimpleCV import Camera, Display, Color

import numpy as np
import time
import sys

# TODO : plot histogram and membrane potential
# TODO : remove background of RF

#########################################################
#########################################################
NUM_SAMPLES = 1024
# neural parameters
spike = 255*np.ones(45) # that's a crude spike!
quant = 512
rate = 0.01
adaptive = True
sample = 5
sigma = 8.

#============================================================================
# Set up input
#============================================================================
def do_RF():

    img = cam.getImage().flipHorizontal().smooth()
    #img = img.smooth()
#     img = img.edges()
    img_np = img.getNumpy().mean(axis=2).T
    img_np /= np.sqrt(np.sum(img_np**2))
    return img, img_np

#============================================================================
# Create the model.
#============================================================================
corr = 0
voltage = 0.5
hist = np.ones(quant) / quant

def neuron(im, voltage, hist):
    if voltage > 1.: voltage = 0.
    corr = np.dot(im.ravel(), RF.ravel()) #result[0, 0]
    quantile = int(((corr+1)/2) * quant)-1
    if adaptive:
        cumhist = np.cumsum(hist)
        voltage = cumhist[quantile]
        if voltage > .9:
            if AUDIO: stream.write(spike)
            voltage = 2.

        hist[quantile] += rate
        hist /= np.sum(hist)

    else:
        if corr > .15:
            if AUDIO: stream.write(spike)

    return corr, voltage
#============================================================================
if __name__ == "__main__":

    if AUDIO:
        # open audio stream to the speakers
        p = pyaudio.PyAudio()
        # initialize loudspeaker
        stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    output=True)

    snapshotTime = time.time()
    # check if capture device is OK
    # Initialize the camera
    cam = Camera()
    print 'Camera : ', cam.getProperty("height"), cam.getProperty("width")

#     downsize = 2
#     frame = None
#     cv2.namedWindow("preview")
#     while frame is None: rval, frame = capture.read()
# 
#     cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, frame.shape[0] / downsize)
#     cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, frame.shape[1] / downsize)
#     cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FORMAT, cv.IPL_DEPTH_32F)
# 
# 
#     font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, .5, .5, thickness=3/downsize, lineType=cv.CV_AA)
#     font_ = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, .5, .5, thickness=4/downsize, lineType=cv.CV_AA)
#     font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1./downsize, 1./downsize, thickness=3./downsize, lineType=cv.CV_AA)
#     font_ = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1./downsize, 1./downsize, thickness=4./downsize, lineType=cv.CV_AA)

    print ' Startup time ', (time.time() - snapshotTime)*1000, ' ms'
    snapshotTime = time.time()

    try:
#         disp = Display()
#         cv.NamedWindow("Receptive Field", 0)
        img, RF = do_RF()
#         cv.NamedWindow("Retina", 0)
#         cv.MoveWindow("Receptive Field", 0*RF.width , 0)
#         cv.ResizeWindow("Receptive Field", 2*RF.width, 2*RF.height)
#         cv.Set(RF, 0.)
#         cv.PutText(RF, 'SimpleCellDemo', (12/downsize, 48/downsize), font, cv.RGB(0, 255, 0))
#         cv.PutText(RF, 'Press Esc to exit', (12/downsize, 96/downsize), font, cv.RGB(255, 0, 0))
#         cv.PutText(RF, 'Press r to (re)draw', (12/downsize, 144/downsize), font, cv.RGB(0, 0, 255))
#         cv.ShowImage("Receptive Field", RF)
# 
#         rval, frame = vc.read()
#         ret = cv.CreateImage(iframe.shape, cv.IPL_DEPTH_32F, 3)
#         retina(frame, ret)
#         cv.ShowImage("Retina", ret)
#         cv.ResizeWindow("Retina", 2*RF.width, 2*RF.height)
#         cv.MoveWindow("Retina", 2*RF.width, 0)

        while True:
            snapshotTime = time.time()
            img, im = do_RF()

#             rval, frame = vc.read()
            corr, Vm = neuron(im, voltage, hist)
            print corr, Vm
            backshotTime = time.time()
            fps = 1. / (backshotTime - snapshotTime)
            img.drawText("FPS:" + str(fps), 10, 10, fontsize=30, color=Color.GREEN)
            img.show()

    finally:
        # Always close the camera stream
        if AUDIO: stream.close()
#         cv.DestroyWindow("Receptive Field")
#         cv.DestroyWindow("Retina")

