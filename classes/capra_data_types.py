# Defines custom data types for capra. Currently all are only used in conjunction
# with the projector

class Picture:
    """Defines object which hold a row from the database table 'pictures'"""

    def __init__(self, picture_id, time, year, month, day, minute, dayofweek, hike_id, index_in_hike, 
                 altitude, altrank_hike, altrank_global, altrank_global_h,
                 color_hsv, color_rgb, colorrank_hike, colorrank_global, colorrank_global_h,
                 colors_count, colors_rgb, colors_conf,
                 camera1, camera2, camera3, cameraf, created, updated):
        self.picture_id = picture_id
        self.time = time
        self.year = year
        self.month = month
        self.day = day
        self.minute = minute
        self.dayofweek = dayofweek

        self.hike_id = hike_id
        self.index_in_hike = index_in_hike

        self.altitude = altitude
        self.altrank_hike = altrank_hike
        self.altrank_global = altrank_global
        self.altrank_global_h = altrank_global_h

        self.color_hsv = color_hsv
        self.color_rgb = color_rgb
        self.colorrank_hike = colorrank_hike
        self.colorrank_global = colorrank_global
        self.colorrank_global_h = colorrank_global_h
        self.colors_count = colors_count
        self.colors_rgb = colors_rgb
        self.colors_conf = colors_conf

        self.camera1 = camera1
        self.camera2 = camera2
        self.camera3 = camera3
        self.cameraf = cameraf

        self.created = created
        self.updated = updated

    def print_obj_mvp(self):
        print('({id}, {t}, {yr}, {mth}, {day}, {min}, {dow}, {hike_id}, {index}, {alt}, {altr}, {hsv}, {rgb}, {crh}, {crg}, {c1}, {c2}, {c3}, {cf})\
            '.format(id=self.picture_id, t=self.time, yr=self.year, mth=self.month, day=self.day,
                     min=self.minute, dow=self.dayofweek, hike_id=self.hike_id, index=self.index_in_hike,
                     alt=self.altitude, altr=self.altrank_global, hsv=self.color_hsv, rgb=self.color_rgb,
                     crh=self.colorrank_hike, crg=self.colorrank_global, c1=self.camera1, c2=self.camera2, c3=self.camera3, cf=self.cameraf))

    def print_obj(self):
        print('({id}, {t}, {alt}, {hike_id}, {index}, {c1}, {c2}, {c3}, {cf})\
            '.format(id=self.picture_id, t=self.time, alt=self.altitude,
                     hike_id=self.hike_id, index=self.index_in_hike,
                     c1=self.camera1, c2=self.camera2, c3=self.camera3, cf=self.cameraf))


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
