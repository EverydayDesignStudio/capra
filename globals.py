def init():

    # *** Explorer -> Projector
    # *** Collector -> Camera

    # IP Addresses
    # TODO: determine statis IP addrs for the camera and the projector
    global IP_ADDR_PROJECTOR
    IP_ADDR_PROJECTOR = '192.168.0.???'

    global IP_ADDR_CAMERA
    IP_ADDR_CAMERA = '192.168.0.???'

    # Databases
    global DBNAME_MASTER
    DBNAME_MASTER = "capra_projector.db"

    global DBNAME_TRANSFER_ANIMATION
    DBNAME_TRANSFER_ANIMATION = "capra_transfer_animation.db"

    global DBNAME_CAMERA
    DBNAME_CAMERA = "capra_camera.db"

    # GPIOs
    global HALL_EFFECT
    HALL_EFFECT = 26

    # Paths
    global PATH_ON_CAMERA
    PATH_ON_CAMERA = '/home/pi/capra-storage/'

    global FILENAME
    global FILENAME_ROTATED
    FILENAME = "*_cam[1-3].jpg"
    FILENAME_ROTATED = "*_cam2r.jpg"

    global PATH_ON_PROJECTOR
    # TODO: update existing projector path by adding an extra slash '/'
    PATH_ON_PROJECTOR = '/media/pi/capra-hd/'

    global PATH_CAMERA_DB
    PATH_CAMERA_DB = PATH_ON_CAMERA + DBNAME_CAMERA

    global PATH_PROJECTOR_DB
    PATH_PROJECTOR_DB = PATH_ON_PROJECTOR + DBNAME_MASTER

    global PATH_TRANSFER_ANIMATION_DB
    PATH_TRANSFER_ANIMATION_DB = PATH_ON_PROJECTOR + DBNAME_TRANSFER_ANIMATION

    # Flags
    global flag_start_transfer
    flag_start_transfer = False

    global flag_run_explorer
    flag_run_explorer = False

    # Color detection
    global COLOR_CLUSTER
    COLOR_CLUSTER = 5

    global COLOR_DIMX
    COLOR_DIMX = 160

    global COLOR_DIMY
    COLOR_DIMY = 95
