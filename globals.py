def init():

    # *** Explorer -> Projector
    # *** Collector -> Camera

    # Transfer
    # --------------------------------------------------------------------------

    # IP Addresses
    # TODO: determine statis IP addrs for the camera and the projector
    global IP_ADDR_PROJECTOR
    # IP_ADDR_PROJECTOR = '192.168.0.127'
    IP_ADDR_PROJECTOR = '192.168.123.193'
    # IP_ADDR_PROJECTOR = '192.168.1.193'

    global IP_ADDR_CAMERA
    # IP_ADDR_CAMERA = '192.168.0.149'
    IP_ADDR_CAMERA = '192.168.123.100'
    # IP_ADDR_CAMERA = '192.168.1.100'

    # Databases
    global DBNAME_MASTER
    DBNAME_MASTER = "capra_projector.db"

    global DBNAME_TRANSFER_ANIMATION
    DBNAME_TRANSFER_ANIMATION = "capra_transfer_animation.db"

    global DBNAME_CAMERA
    # DBNAME_CAMERA = "capra_camera.db"
    # TODO: change this
    DBNAME_CAMERA = "capra_camera_test.db"
    global DBNAME_CAMERA_BAK
    DBNAME_CAMERA_BAK = "capra_camera_test_bak.db"

    # Paths
    global DATAPATH_CAMERA
    DATAPATH_CAMERA = '/home/pi/capra-storage/'

    global DATAPATH_PROJECTOR
    # TODO: update existing projector path by adding an extra slash '/'
    DATAPATH_PROJECTOR = '/media/pi/capra-hd/'

    global CAPRAPATH_PROJECTOR
    CAPRAPATH_PROJECTOR = '/home/pi/capra/'

    global PATH_CAMERA_DB
    PATH_CAMERA_DB = DATAPATH_CAMERA + DBNAME_CAMERA

    global PATH_PROJECTOR_DB
    PATH_PROJECTOR_DB = DATAPATH_PROJECTOR + DBNAME_MASTER

    global PATH_TRANSFER_ANIMATION_DB
    PATH_TRANSFER_ANIMATION_DB = DATAPATH_PROJECTOR + DBNAME_TRANSFER_ANIMATION

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

    # Projector
    # --------------------------------------------------------------------------

    # Projector Pins
    global PROJ_UART
    PROJ_UART = 14          # BOARD - 8 (used to be RGB1_BLUE)

    global HALL_EFFECT_PIN
    HALL_EFFECT_PIN = 26    # BOARD - 37
    global BUTT_MODE
    BUTT_MODE = 20          # BOARD - 38
    global BUTT_PLAY_PAUSE
    BUTT_PLAY_PAUSE = 5     # BOARD - 29
    global BUTT_PREV        # Eagle says this is NEXT
    BUTT_PREV = 6           # BOARD - 31
    global BUTT_NEXT        # Eagle says this is PREV
    BUTT_NEXT = 13          # BOARD - 33
    global BUTT_OFF
    BUTT_OFF = 4            # BOARD - 7
    global BUTT_ON
    BUTT_ON = 3             # BOARD - 5

    global ACCEL_SCL
    ACCEL_SCL = 3           # BOARD - 5
    global ACCEL_SDA
    ACCEL_SDA = 2           # BOARD - 3

    global BUTT_ENC1
    BUTT_ENC1 = 25          # BOARD - 22
    global ENC1_A
    ENC1_A = 23             # BOARD - 16
    global ENC1_B
    ENC1_B = 24             # BOARD - 18

    global NEO1
    NEO1 = 18               # BOARD - 12
    global WHITE_LED1
    WHITE_LED1 = 21         # BOARD - 40
    global WHITE_LED2
    WHITE_LED2 = 16         # BOARD - 36
    global WHITE_LED3
    WHITE_LED3 = 19         # BOARD - 35

    global RGB1_RED
    RGB1_RED = 15           # BOARD - 10
    global RGB1_GREEN
    RGB1_GREEN = 17         # BOARD - 11

    global RGB2_RED
    RGB2_RED = 7            # BOARD - 26
    global RGB2_GREEN
    RGB2_GREEN = 8          # BOARD - 24
    global RGB2_BLUE
    RGB2_BLUE = 11          # BOARD - 23

    # Projector Status and Settings
    global HALL_EFFECT
    global PREV_HALL_VALUE
    HALL_EFFECT = None
    PREV_HALL_VALUE = False
    global HALL_BOUNCE_LIMIT
    global HALL_BOUNCE_TIMER
    HALL_BOUNCE_LIMIT = 3000    # in milliseconds
    HALL_BOUNCE_TIMER = None

    global FILENAME
    global FILENAME_ROTATED
    FILENAME = "[!\.]*_cam[1-3].jpg"
    FILENAME_ROTATED = "[!\.]*_cam2r.jpg"

    # Camera
    # --------------------------------------------------------------------------

    # Camera Storage
    global DB
    DB = '/home/pi/capra-storage/capra_camera.db'

    global DIRECTORY
    DIRECTORY = '/home/pi/capra-storage/'

    # Camera Pins
    global BUTTON_PLAYPAUSE
    BUTTON_PLAYPAUSE = 17   # BOARD - 11
    global BUTTON_OFF
    BUTTON_OFF = 25         # BOARD - 22
    global SEL_1
    SEL_1 = 22              # BOARD - 15
    global SEL_2
    SEL_2 = 23              # BOARD - 16
    global LED_RED
    LED_RED = 13            # BOARD - 33
    global LED_GREEN
    LED_GREEN = 26          # BOARD - 37
    global LED_BLUE
    LED_BLUE = 14           # BOARD - 8
    global PIEZO
    PIEZO = 12              # BOARD - 32
    global LDO
    LDO = 6                 # BOARD - 31

    # Camera Settings
    global SEALEVEL_PRESSURE
    SEALEVEL_PRESSURE = 101500
    global CAM_RESOLUTION
    CAM_RESOLUTION = (1280, 720)
    global NEW_HIKE_TIME
    # NEW_HIKE_TIME = 10800   # 3 hours
    # NEW_HIKE_TIME = 9000    # 2.5 hours
    NEW_HIKE_TIME = 3600      # 1 hour
    global CAM_INTERVAL
    CAM_INTERVAL = 5        # 5 seconds
