import java.io.File;
import java.util.Arrays;
import java.util.Map;
import java.util.LinkedHashMap;

// processing.io only works on Raspberry Pi, comment out for PC
import processing.io.*;


// Adjustables
File IMG_DIR = new File("/home/pi/Desktop/pics_DELETEME2"); // Obv.
String IMG_EXT = ".jpg"; // Include dot and keep to lowercase.
int FRAMERATE = 24;
float TIMELAPSE_FRAMERATE = 0.5; // Photos per second
int PIN_ENCODER_CLK = 17; // Watch out: Sometimes the pins on the board are broken.
int PIN_ENCODER_DT = 13;
int CACHESIZE = 48; // Number of images to cache. Must be divisible by 4.

//// Magic sauce
// Coefficient for controlling advance by encoder (or keyboard).
float gain = 0.1;
// Coefficient for deceleration to base velocity.
float brake = 0.08;
// Noise factor, makes blend "grainy." Higher noise = better performance. Must be >= 1.
float blendNoise = 16;

//// Set up
// Index of images to show.
// For example: If x = 1.23, a blend comprising 23% image 1 and 77% image 2 will be shown.
float x = 0;
// This displays photos at the same rate they were taken.
float vbase = TIMELAPSE_FRAMERATE / float(FRAMERATE); 
// v (velocity) is rate of change in x.
float v = vbase;
// Misc. prep.
int encoder_prev = 0;
File[] files = IMG_DIR.listFiles();
LinkedHashMap<String, PImage> cache;


void setup() {
  println("Java version:", System.getProperty("java.version"));
  println("Evidence of goat domestication dates back more than 8,500 years.");  

  // Rotary encoder setup
  GPIO.pinMode(PIN_ENCODER_DT, GPIO.INPUT_PULLUP);
  GPIO.pinMode(PIN_ENCODER_CLK, GPIO.INPUT_PULLUP);
  GPIO.attachInterrupt(PIN_ENCODER_CLK, this, "updateEncoder", GPIO.CHANGE);

  // Load up all images in directory into an array
  Arrays.sort(files);

  size(405, 720);
  //size(800, 600);
  //fullScreen();

  frameRate(FRAMERATE);

  // Set up cache to delete oldest entry if full
  cache = new LinkedHashMap<String, PImage>() {
    @Override
      protected boolean removeEldestEntry (final Map.Entry eldest) {
      return size() > CACHESIZE;
    }
  };
}


void draw() {
  // Loop (keep x within array bounds)
  if (x > files.length - 1) x = 0;
  if (x < 0) x = files.length - 1;

  // Decompose x into two int indexes and a proportion.
  // Acknowledge the possibility that v might be negative, i.e. going backwards.
  int i0  = (v > 0) ? floor(x) : ceil(x);
  int i1  = (v < 0) ? floor(x) : ceil(x);
  float p = (v > 0) ? x - floor(x) : ceil(x) - x;
  p = sigmoid(p); // Add flair.

  // Update cache
  for (int idx_cache = 0; idx_cache < CACHESIZE; idx_cache++) {
    // Go back a little, cache images before the current one
    int idx_files = i0 + idx_cache - CACHESIZE / 4;
    while (idx_files < 0) idx_files += files.length;
    while (idx_files >= files.length) idx_files -= files.length;
    // Avoid trying to read non-image files in directory etc.
    // This part needs to be updated.
    if (files[idx_files].getName().toLowerCase().endsWith(IMG_EXT.toLowerCase())
      && !files[idx_files].getName().startsWith(".")) {
      String path = files[idx_files].getAbsolutePath();
      if (!cache.containsKey(path)) {
        cache.put(path, requestImage(path));
        println("Cached:", path);
      }
    }
  }

  // Blend two images
  String path0 = files[i0].getAbsolutePath();
  String path1 = files[i1].getAbsolutePath();
  loadPixels();
  int pxLen = pixels.length;
  if (cache.containsKey(path0) && cache.containsKey(path1)) {
    PImage img0 = cache.get(path0);
    PImage img1 = cache.get(path1);
    if (img0.height > 0 && img1.height > 0) {
      for (int loc = 0; loc < pxLen; loc += random(1, blendNoise)) {
        pixels[loc] = lerpColor(img0.pixels[loc], img1.pixels[loc], p);
      }
    } else println(millis(), ": Caching in progress:", i0, i1);
  } else println(millis(), ": Not cached:", i0, i1);

  updatePixels();

  // Advance
  x += v;
  // Brake
  v -= (v - vbase) * brake;

  // Debug
  //println(i0, i1, p);
  //println(frameRate, "fps");
  //println("v: ", v);
  //println(cache.size());
}


//void keyPressed() {
//  // This is for testing on PC
//  if (keyCode == RIGHT) x += gain;
//  if (keyCode == LEFT) x -= gain;
//}


void updateEncoder(int pin) {
  // https://gist.github.com/Arty2/ab77038addb7f40163ba
  int clk = GPIO.digitalRead(PIN_ENCODER_CLK);
  int dt = GPIO.digitalRead(PIN_ENCODER_DT);

  int encoded = (clk << 1) | dt;
  int sum = (encoder_prev << 2) | encoded;

  if (sum == unbinary("1101") || sum == unbinary("0100") || sum == unbinary("0010") || sum == unbinary("1011")) {
    x += gain;
  }
  if (sum == unbinary("1110") || sum == unbinary("0111") || sum == unbinary("0001") || sum == unbinary("1000")) { 
    v -= gain;
  }

  encoder_prev = encoded;

  // Debug
  //println(clk, dt, Integer.toBinaryString(encoded));
  //println(frameRate, "fps");
}


float sigmoid(float x) {
  // google.com/search?q=sigmoid+function
  return 1.0/(1.0 + exp(-10.0 * (x - 0.5)));
}
