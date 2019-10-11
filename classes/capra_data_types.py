# Defines a picture object


class Picture:
    def __init__(self, picture_id, time, altitude,
                 brightness, b_rank, hue, h_rank, hue_lumosity, hl_rank,
                 hike_id, index_in_hike, camera1, camera2, camera3, camera_land):
        self.picture_id = picture_id
        self.time = time
        self.altitude = altitude

        self.brightness = brightness
        self.brightness_rank = b_rank
        self.hue = hue
        self.hue_rank = h_rank
        self.hue_lumosity = hue_lumosity
        self.hue_lomosity_rank = hl_rank

        self.hike_id = hike_id
        self.index_in_hike = index_in_hike
        self.camera1 = camera1
        self.camera2 = camera2
        self.camera3 = camera3
        self.camera_landscape = camera_land

    def print_obj(self):
        print('({id}, {t}, {alt}, {b}, {b_r}, {h}, {h_r}, {hl}, {hl_r}, {hike_id}, {index}, {c1}, {c2}, {c3}, {cl})\
            '.format(id=self.picture_id, t=self.time, alt=self.altitude,
                     b=self.brightness, b_r=self.brightness_rank, h=self.hue, h_r=self.hue_rank,
                     hl=self.hue_lumosity, hl_r=self.hue_lomosity_rank,
                     hike_id=self.hike_id, index=self.index_in_hike,
                     c1=self.camera1, c2=self.camera2, c3=self.camera3, cl=self.camera_landscape))

# Defines a hike object


class Hike:
    def __init__(self, hike_id, avg_altitude,
                 avg_brightness, avg_hue, avg_hue_lumosity,
                 start_time, end_time, pictures_num, path):
        self.hike_id = hike_id
        self.average_altitude = avg_altitude
        self.average_brightness = avg_brightness
        self.average_hue = avg_hue
        self.average_hue_lumosity = avg_hue_lumosity
        self.start_time = start_time
        self.end_time = end_time
        self.pictures_num = pictures_num
        self.path = path

    def print_obj(self):
        print('(id:{id}, alt:{alt}, bright:{br}, hue:{hue}, hue+lum:{hlum}, start:{st}, end:{et}, pictures:{n}, path:{p})\
            '.format(id=self.hike_id, alt=self.average_altitude, br=self.average_brightness,
                     hue=self.average_hue, hlum=self.average_hue_lumosity, 
                     st=self.start_time, et=self.end_time, n=self.pictures_num, p=self.path))

    def get_hike_time(self) -> float:
        return self.end_time - self.start_time
