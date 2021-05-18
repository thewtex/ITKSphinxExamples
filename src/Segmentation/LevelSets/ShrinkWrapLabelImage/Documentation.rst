Shrink Wrap Label Image
================================

.. index::
   single: NarrowBandCurvesLevelSetImageFilter

Synopsis
--------


Shrink wrap structures in a label image that may have cracks or holes on its boundaries.


Results
-------

.. figure:: cthead1.png
  :scale: 50%
  :alt: Input image

  Input image

.. figure:: OutputBaseline.png
  :scale: 50%
  :alt: Output image

  Output image


Code
----

C++
...

.. literalinclude:: Code.cxx
   :language: c++
   :lines: 18-

Python
......

.. literalinclude:: Code.py
   :language: python
   :lines: 1,16-


Classes demonstrated
--------------------

.. breathelink:: itk::NarrowBandCurvesLevelSetImageFilter
