<!--
meta--title--Inside the Physical Dropbox
meta--created--2013-09-03
meta--modified--2013-09-03
meta--status--in progress
-->

## Looking Inside the Physical Dropbox
<!--### The making of a simple 3d scanner-->

[me presenting]

While interning at Dropbox this past summer, I built a "physical dropbox"--a 3d
laser scanner inside a Dropbox logo like enclosure--over Dropbox's biannual
hack week with teammates Abhishek Agrawal, Mason Liang, and Rachel Fong.  A few
weeks later, Makerbot announced the Makerbot Digitizer - a 3d scanner which
works on the same principles.  In this post, I go through the basic ideas
behind how it functions and how we built our own.

To start out, here is a picture of the scanner to see how it is layed out.

[PICTURE]

## The Principle
At its most basic level, the scanner shoots a laser line onto an object,
captures an image, and then uses the deformation of the laser line from the
center of the image to triangulate points on the surface.  When this is done
along an entire line, we get a slice of the object.  When these slices are
generated for many small steps through a full rotation of the object, we end up
with a point cloud.

[a cup - about as basic as you get - a point cloud ]

So how do we actually triangulate the points?  We have a laser, camera, and
turntable.  We know the distances between each of them, along with the angle
at the intersection of the center of the cameras image and the laser line.  We
then capture an image like this:

[GREEN LASER]

Clean up the image by removing the any part of the laser that overshoots the
object and threshold to get the brightest pixels.

[WHITE LINES]

From this image, we pull out a list of (u,v) image coordinates of the middle
brightest pixel.

Now comes the only real math with two lines of trigonometry to process this
list.

For every (u, v) pair at a current turntable rotation of theta, we generate an (x, y, z) point by
x = u * cos(theta)
y = v
z = -u * sin (theta)


## Implementation

Now for the actual implementation.  I am not going to go into the details of
every part, but we built our scanner using:

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


The resulting pointclouds are output in the ply format, which can be viewed
in most modelling programs.  We found the meshlab worked well.

Our code can be found at [here](github.com/dmrd/physical-dropbox). Overall,
the code is fairly modular, but it became significantly more messy when we
decided to add the second laser at 2am on the Friday.

## Finished Product

Here are more example scans that we made while building the scanner:

[pics]

## Comparing to the Digitizer

### Accuracy
From looking at scans, it appears that the makerbot scanner has much higher
accuracy.  Overall, this is expected since our mountings and calibrations were
inexact at best.  The accuracy would likely be dramatically improved by
machining or 3d printing a mount that precisely controlled the distance and
angle between the camera and lasers.  Additionally, we did not calibrate our
camera to account for distortions, instead assuming an orthographic projection


### Light
The Makerbot Digitizer also appears to have hardware to support scanning in
daylight.  My suspicion is some sort of polarized filter, but it is also
possible that increasing the power on our lasers would make it work in light.
Please let me know if you are aware of how this works.


### Nondiffuse surfaces
One universal weakness of this technique is that it does not work with
reflective objects. Makerbot even has a tutorial on how to scan reflective
objects by coating them in a diffuse powder.  You can see a result of this
effect in some of our scans where the reflective Dropbox name on the mug is
visible because the points were not filled in:

### Resulting meshes
You may notice that our scanner ouputs a pointcloud rather than a filled mesh.
While we tried various techniques and libraries to triangulate the point cloud
into a mesh, we found that most automated approaches produced jagged and
irregular meshes.  The best strategy was to meshify the output in an external
tool such as meshlab.  Similarly, we also did not attempt to texture the output
since it would require a fully integrate images -> mesh pipeline (although one
can store color per vertex rather than as a texture).


## Improvements & Other techniques

It is possible to improve mesh quality even more by using additional lasers.
Alternatively, one can use a single laser and grating to split it into many
beams.

This technique was used to scan _David_ with some variation (not rotating).

Laser scanning as presented here is just one way of scanning objects.  There
are many of methods for _active optical scanning_, e.g. systems in which we
introduce extra light into the scene.  This is in contrast to optical
techniques such as using the difference between multiple cameras.

Other techniques include structured light scanning, time of flight scanners,
and light diffusion whatevers-----.  The details of these techniques are
interesting, but that's a topic for another day.

## Resources
If you are curious about other similar 3d scanners, take a look at
[pylatscan](https://github.com/mvhenten/pylatscan).  It includes blueprints to
build a more polished scanner, along with code.  I have not used it, but it
appears to be fairly well documented.

Another good resource for understanding different techniques is [this SIGGRAPH
course on 3D scanning](http://mesh.brown.edu/byo3d/slides.html)
