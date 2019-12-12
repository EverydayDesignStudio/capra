# projector_java

Prototype Java/Processing implementation for the projector.

Implements image cache using a Java LinkedHashMap (see: [geeksforgeeks.org/linkedhashmap-class-java-examples](https://www.geeksforgeeks.org/linkedhashmap-class-java-examples/)) and Processing `requestImage()` (see: [processing.org/reference/requestImage_](https://processing.org/reference/requestImage_.html)).

To dos:

- Currently only reads one directory, in the preamble (before `setup()`). To switch between different hikes / image sets, this should be moved elsewhere. (Though most probably will still require initialization in preamble.)
- Images must be standardized wrt size. Resizing online is not an option, it's too slow.
- Consider: Using an external circuit to handle encoder counting. This can then be read via polling, rather than an interrupt. (Maybe: https://www.sparkfun.com/products/15036)
- When building cache: update the code that verifies file type etc. Very important since currently only works for one photo stream, but Capra will have 3 streams (3 cameras).
- Going backwards is problematic. Unclear if bug or hardware limitation. Possible bug locations: sorting by file names, building cache, blend/display. Possible fix: maintain 2 caches (forward and backward), decide which one to use based on `signum(v)` (i.e. `java.lang.Math.signum()`).
