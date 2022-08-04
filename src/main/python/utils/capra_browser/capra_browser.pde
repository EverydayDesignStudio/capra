// Little script to check out what the three photos of Capra look like stacked up

int index;        // number of photo-trio to display
int pr_index;     // previous displayed index
PImage photo;     // the photo to display  
String datapath;  // the path to the folder
String photopath; // for some reason this is a separate variable

void setup()
{
  size(427, 780);
  background(0);
  datapath = initialisePath();
  index = 1;
  pr_index = 0;
}

void draw()
{
  photopath = datapath + str(index);
  if (index != pr_index) // If  the index is different from the last time (saves processing power)
  {
    background(0);
    for (int i = 1; i < 4 ; i++) // Between cam 1 through cam 3 do:
    {
      try 
      { 
        photo = loadImage(photopath + "_cam" + str(i) + ".jpg");
        if (photo.width > 0) // If the photo isn't a zero kB file
        {
          photo.resize(427, 240);
          image(photo, 0, (i-1) * 240);
        }
      }
      catch (NullPointerException e) // In case photos are missing, don't trip
      {
        println("nullpointer @ " + str(index));
        println(e);
      }
    }
    fill(255);
    text(str(index), 20, 750);
    pr_index = index;
  }
  
  
}


void mouseWheel(MouseEvent event) {
  float e = event.getCount();
  println("wheel: " + str(e));
  
  index += 10 * int(e);
  if (index < 1)
  {
    index = 1;
  }
  println(int(index));
}


void keyPressed()
{
  println("keyPressed");
  if (key == CODED)
  {
    if (keyCode == LEFT)
    {
      index -= 1;
      if (index < 1)
      {
        index = 1;
      }
    }
    
    if (keyCode == RIGHT)
    {
      index += 1;
      if (index > 9000) // arbitrary upper level
      {
        index = 9000;
      }
    }
  }
  println(index);
}


String initialisePath()
{
  String _datapath = dataPath("");
  String[] splitpath = split(_datapath, '/');
  _datapath = "";
  for (int i = 1; i < splitpath.length - 2; i++)
  {
    _datapath = _datapath + "/" + splitpath[i];
  }
  _datapath = _datapath + "/";
  return _datapath;  
}
