# Defines a picture object


class Picture:
    def __init__(self, picture_id, time, altitude, color, hike_id,
                 index_in_hike, camera1, camera2, camera3):
        self.picture_id = picture_id
        self.time = time
        self.altitude = altitude
        self.color = color
        self.hike_id = hike_id
        self.index_in_hike = index_in_hike
        self.camera1 = camera1
        self.camera2 = camera2
        self.camera3 = camera3

    def print_obj(self):
        print('({id}, {t}, {alt}, {col}, {hike_id}, {index}, {c1}, {c2}, {c3})\
            '.format(id=self.picture_id, t=self.time, alt=self.altitude,
                     col=self.color, hike_id=self.hike_id, index=self.index_in_hike,
                     c1=self.camera1, c2=self.camera2, c3=self.camera3))

# Defines a hike object


class Hike:
    def __init__(self, hike_id, average_altitude, average_color, start_time,
                 end_time, pictures_num):
        self.hike_id = hike_id
        self.average_altitude = average_altitude
        self.average_color = average_color
        self.start_time = start_time
        self.end_time = end_time
        self.pictures_num = pictures_num

    def print_obj(self):
        print('({id}, {alt}, {col}, {time_s}, {time_e}, {p})\
            '.format(id=self.hike_id, alt=self.average_altitude, col=self.average_color,
                     time_s=self.start_time, time_e=self.end_time, p=self.pictures_num))
