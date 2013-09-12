<!--
meta--title--Inside the Physical Dropbox
meta--created--2013-09-03
meta--modified--2013-09-03
meta--status--in progress
-->

## Looking Inside the Physical Dropbox
### The making of a simple 3d scanner

![](/scanner/header.jpg)

While interning at Dropbox this past summer, I built a "physical dropbox"---a 3d
laser scanner inside a Dropbox logo like enclosure---during Dropbox's biannual
hack week with teammates Abhishek Agrawal, Mason Liang, and Rachel Fong.  A few
weeks later, Makerbot announced the Makerbot Digitizer - a 3d scanner which
works on the same principles.  In this post, I go through the basic ideas
behind how it functions, how we built our own (although not a thorough
tutorial), and the results that we achieved.

To start out, here is a picture of the scanner hardware to see how it is laid
out:

![](/scanner/birdseye-dual.jpg)

The main features are the turntable that the mug rests on, the camera, and the
two lasers on either side.

### The Principle
At its most basic level, the scanner shoots a laser line onto an object,
captures an image, and then uses the deformation of the laser line from the
center of the image to triangulate points on the surface.  When this is done
along an entire line, we get a slice of the object.  When these slices are
generated for many small steps through a full rotation of the object, we end up
with a point cloud like this one from a scan of a mug:

<img src="/scanner/mug.jpg" width="45%"/>

So how do we actually triangulate the points?  We have a laser, camera, and
turntable.  We know the distances between each of them, along with the angle at
the intersection of the center of the cameras image and the laser line.  We
then capture an image and clean it up by removing the any part of the laser
that overshoots the object and threshold to get the brightest pixels.

![](/scanner/threshold.jpg)

From this image, we pull out a list of (u,v) image coordinates of the middle
brightest pixel.

We process these coordinates into a 3d points using two lines of
trigonometry---the only real math in the process.  For every (u, v) pair at
a current turntable rotation of Ɵ, we generate an (x, y, z) point as:

+ x = u * cos(Ɵ)
+ y = v
+ z = -u * sin (Ɵ)


### Implementation

Now comes the actual implementation.  I am not going to go into the details of
every part, but we built our scanner using:

Hardware:

+ Laptop
+ arduino mega
+ off the shelf webcam (hd)
+ two laser modules
+ glass stirring rods to spread the laser into a line
+ stepper motor
+ stepper controller
+ wood, screws, and felt
+ Lots of batteries to power the motors and lasers

Software:

+ Python 2.7
+ opencv for capturing and lowlevel processing of images
+ numpy for speeding up image processing

The arduino controls the lasers and stepper motor, and the laptop signals to
the arduino and manages capturing images.

We originally alternated taking pictures and having the motor take a step, but
this took much longer than necessary.  Instead, we have the motor do a full
rotation while the camera takes pictures as fast as it can.  The motor signals
when it is done, and we process the images with the assumption that the motor
turned at a uniform rate.  In practice, we found that we usually captured 226
images per rotation in much less time than 30 seconds per laser.

Here is a video showing a scan in progress.  We added a second laser to
increase scan quality, and we scanned with one laser at a time to avoid dealing
with determining which laser line is which.

<iframe src="https://www.facebook.com/video/embed?video_id=10100102584262122"
width="100%" height="400" frameborder="0"></iframe>

The resulting pointclouds are output in the ply format, which can be viewed
in most modelling programs.  We found that
[**meshlab**](http://meshlab.sourceforge.net/) worked well.

Our code can be found [**here**](https://github.com/dmrd/physical-dropbox). Overall,
the code is fairly modular, but it became significantly more messy when we
decided to add the second laser at 2am on the Friday.  The system is entirely
commandline based, and a scan is initated by running:

    python controller.py scan_and_process scan_name 1 dual

This captures images of 1 rotation with both lasers and processes them.  The
controller can also only capture, only process, or only one laser if desired.

### Results

Here are more example scans that we made while building the scanner:

<img src="/scanner/duck.jpg" width="45%"/>

### Comparing to the Digitizer

#### Accuracy
From looking at scans, it appears that the makerbot scanner has much higher
accuracy.  Overall, this is expected since our mountings and calibrations were
inexact at best.  The accuracy would likely be dramatically improved by
machining or 3d printing a mount that precisely controlled the distance and
angle between the camera and lasers.  Additionally, we did not calibrate our
camera to account for distortions.


#### Daylight
The Makerbot Digitizer also appears to have hardware to support scanning in
daylight.  My suspicion is some sort of polarized filter, but it is also
possible that increasing the power on our lasers would make it work in light.
Please let me know if you are aware of how this works.


#### Nondiffuse surfaces
One universal weakness of this technique is that it does not work with
reflective objects. Makerbot even has a tutorial on how to scan reflective
objects by coating them in a diffuse powder.  You can see a result of this
effect in some of our scans where the reflective Dropbox name on the mug is
visible because the points were not filled in:

<!-- IMAGE -->

#### Resulting meshes
You may notice that our scanner ouputs a pointcloud rather than a filled mesh.
While we tried various techniques and libraries to triangulate the point cloud
into a mesh, we found that most automated approaches produced jagged and
irregular meshes.  The best strategy was to meshify the output in an external
tool such as meshlab.  Similarly, we also did not attempt to texture the output
since it would require a fully integrate images -> mesh pipeline (although one
can store color per vertex rather than as a texture).


### Improvements & Other techniques

It is possible to improve mesh quality even more by using additional lasers.
An alternative that does not require multiple lasers is using a single laser
and grating to split it into many beams.  Laser scanning as presented here,
however, is just one way of scanning objects.  There are many of methods for
_active optical scanning_, e.g. systems in which we introduce extra light into
the scene.  This is in contrast to passive optical techniques such as using the
difference between multiple cameras.

Other active techniques include

+ Structured light scanning in which a structured pattern, such as a grid of
dots for the Kinect, is projected onto the surface and the deformation
observed.
+ Time of flight scanners use the time for a beam of light to bounce off an
object and return to the scanner to calculate depth.
+ Light diffusion

The details of these techniques are interesting, but that's a topic for another day.

### Resources
If you are curious about other similar 3d scanners, take a look at
[**pylatscan**](https://www.github.com/mvhenten/pylatscan).  It includes blueprints to
build a more polished scanner, along with code.  I have not used it, but it
appears to be fairly well documented.

Another good resource for understanding different techniques is [**this SIGGRAPH
course on 3D scanning**](http://mesh.brown.edu/byo3d/slides.html)

Lastly, the [**Wikipedia article on 3d
scanning**](http://en.wikipedia.org/wiki/3D_scanner) is a fairly thorough
overview of many different techniques and their uses.
