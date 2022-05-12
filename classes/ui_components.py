#!/usr/bin/env python3

# Various helper UI classes for easier development of PyQt5 applications

# Imports
from sqlite3.dbapi2 import Error
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PIL import Image

from classes.capra_data_types import Picture

# TODO - add rotatable widget container

# UI Super Classes
# -----------------------------------------------------------------------------


# TODO - figure out how to merge these two widget types together
class UIWidget(QWidget):
    """Super class for QWidgets that will be placed inside other widgets, not directly on MainWindow"""
    def __init__(self) -> None:
        super().__init__()
    # def __init__(self, window):
    #     super().__init__(window)

        self.anim = QPropertyAnimation()
        self.fadeEffect = QGraphicsOpacityEffect()
        # self.canRepaint = True

    def fadeOut(self, duration: int):
        """Fades out the label over passed in duration (milliseconds)"""
        self.setGraphicsEffect(self.fadeEffect)
        self.anim = QPropertyAnimation(self.fadeEffect, b"opacity")
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setDuration(duration)
        self.anim.start()
        self.update()

    def show(self):
        '''UIWdiget superclass method'''
        self.anim.stop()
        self.fadeEffect.setOpacity(1.0)

    def myHide(self):
        '''UIWdiget superclass method'''
        self.fadeEffect.setOpacity(0.0)

    # def setCanRepaint(self):
    #     self.canRepaint = True

    # def setCanNotRepain(self):
    #     self.canRepaint = False


class UIWindowWidget(QWidget):
    """Super class for widgets that are directly fullscreen on the MainWindow, provides universal animations"""
    def __init__(self, window):
        super().__init__(window)

        self.anim = QPropertyAnimation()
        self.fadeEffect = QGraphicsOpacityEffect()
        self.fadeEffect.setOpacity(0.0)
        self.setGraphicsEffect(self.fadeEffect)
        # self.canRepaint = True

        # self._opacity = QGraphicsOpacityEffect()
        # helpImage.setGraphicsEffect(self._opacity)

    def fadeOut(self, duration: int):
        """Fades out the widget over passed in duration (milliseconds)"""
        self.setGraphicsEffect(self.fadeEffect)
        self.anim = QPropertyAnimation(self.fadeEffect, b"opacity")
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setDuration(duration)
        self.anim.start()
        self.update()

    def fadeIn(self, duration: int):
        """Fades in the widget over passed in duration (milliseconds)"""
        self.setGraphicsEffect(self.fadeEffect)
        self.anim = QPropertyAnimation(self.fadeEffect, b"opacity")
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setDuration(duration)
        self.anim.start()
        self.update()

    def myShow(self):
        self.show()
        self.anim.stop()
        self.fadeEffect.setOpacity(1.0)

    def opacityHide(self):
        '''UIWindowWidget superclass method'''
        self.fadeEffect.setOpacity(0.0)
        self.setGraphicsEffect(self.fadeEffect)
        self.hide()


class UILabel(QLabel):
    """Super class for universal animations of
    QLabels that are placed directly onto the window"""
    def __init__(self, window):
        super().__init__(window)

        self.anim = QPropertyAnimation()
        self.fadeEffect = QGraphicsOpacityEffect()

    def fadeOut(self, duration: int):
        """Fades out the label over passed in duration (milliseconds)"""
        self.setGraphicsEffect(self.fadeEffect)
        self.anim = QPropertyAnimation(self.fadeEffect, b"opacity")
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setDuration(duration)
        self.anim.start()
        self.update()

    def show(self):
        self.anim.stop()
        self.fadeEffect.setOpacity(1.0)

    def opacityHide(self):
        self.anim.stop()
        self.fadeEffect.setOpacity(0.0)


# UI Text & Image Components
# -----------------------------------------------------------------------------

# Labels for the information at the top of the screen
# Inherits from UILabel so it comes ready for animation
class UILabelTop(UILabel):
    def __init__(self, window, text: str, alignment):
        UILabel.__init__(self, window)  # works
        # super().__init__(window)  # works

        self._text = text
        self.setText(self._text)

        self.resize(1280, 200)
        # self.setAlignment(Qt.AlignLeft)
        self.setAlignment(alignment)
        self.setMargin(35)
        # self.setIndent(100)

        self.setFont(QFont('Atlas Grotesk', 24, 400))
        self.setStyleSheet("color: rgba(255,255,255,255)")
        self.setGraphicsEffect(UIEffectTextDropShadow())

    def setPrimaryText(self, text):
        self.setText(str(text))


# Compound QWidget that holds two QLabels for the middle UI
class UILabelTopCenter(QWidget):
    def __init__(self, window, primaryText: str, secondaryText: str, *args, **kwargs):
        # super(QWidget, self).__init__(window, *args, **kwargs)
        super().__init__(window, *args, **kwargs)

        self.resize(1280, 110)
        self.move(0, 15)
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignHCenter)
        # layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.label1 = QLabel(primaryText)
        self.label1.setFont(QFont('Atlas Grotesk', 48, 500))
        self.label1.setStyleSheet("color: rgba(255,255,255,255)")
        self.label1.setGraphicsEffect(UIEffectTextDropShadow())
        self._label1_opacity = QGraphicsOpacityEffect()
        self._label1_opacity.setOpacity(1.0)
        self.label1.setGraphicsEffect(self._label1_opacity)

        self.label2 = QLabel(secondaryText)
        self.label2.setFont(QFont('Atlas Grotesk', 30, 400))
        self.label2.setStyleSheet("color: rgba(255,255,255,225)")
        self.label2.setGraphicsEffect(UIEffectTextDropShadow())
        self._label2_opacity = QGraphicsOpacityEffect()
        self._label2_opacity.setOpacity(1.0)
        self.label2.setGraphicsEffect(self._label2_opacity)

        self.animGroupFadeOut = QParallelAnimationGroup(self)
        self._setupHideAnimation()

        # TESTING - uncomment to see clear background on the components
        # palette = self.palette()
        # palette.setColor(QPalette.Window, QColor('pink'))
        # self.label1.setAutoFillBackground(True)
        # self.label1.setPalette(palette)
        # self.label2.setAutoFillBackground(True)
        # self.label2.setPalette(palette)

        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)

    def setPrimaryText(self, text):
        self.label1.setText(str(text))

    def setSecondaryText(self, text):
        self.label2.setText(text)

    def show(self):
        self.animGroupFadeOut.stop()
        self._label1_opacity.setOpacity(1.0)
        self._label2_opacity.setOpacity(1.0)

    def opacityHide(self):
        self.animGroupFadeOut.stop()
        self._label1_opacity.setOpacity(0.0)
        self._label2_opacity.setOpacity(0.0)

    def fadeIn(self):
        print('UILabelTopCenter.fadeIn() -- NO YET IMPLEMENTED')

    def fadeOut(self):
        self.animGroupFadeOut.start()

    def _setupHideAnimation(self):
        anim1 = QPropertyAnimation(self._label1_opacity, b"opacity")
        anim1.setStartValue(1)  # opaque
        anim1.setEndValue(0)  # transparent
        anim1.setDuration(1000)

        anim2 = QPropertyAnimation(self._label2_opacity, b"opacity")
        anim2.setStartValue(1)
        anim2.setEndValue(0)
        anim2.setDuration(1000)

        self.animGroupFadeOut.addAnimation(anim1)
        self.animGroupFadeOut.addAnimation(anim2)


class UIImage(QLabel):
    '''Simple wrapper of QLabel, for easier image loading'''
    def __init__(self, path: str, *args, **kwargs):
        super(QLabel, self).__init__(*args, **kwargs)
        # QLabel.__init__(self)
        pixmap = QPixmap(path)
        self.setPixmap(pixmap)

    def update_image(self, path: str):
        """Loads new image from local storage path"""
        self.pixmap = QPixmap(path)
        # print('Is this a Pixmap?: {t}'.format(t=type(self.pixmap)))
        self.setPixmap(self.pixmap)

    # TODO - see how processing consumption for this, compares to saving locally
    def update_pixmap(self, im):
        """Accepts a raw image and utilizes image conversion to load it"""
        im = im.convert("RGBA")
        data = im.tobytes("raw", "RGBA")
        qim = QImage(data, im.size[0], im.size[1], QImage.Format_RGBA8888)

        self.pixmap = QPixmap.fromImage(qim)
        self.setPixmap(self.pixmap)

        # TODO - add a try/exception block which uses a blank pink image
        # if theres issues loading from bytes. There seems to be a problem with Python3.7.3

        # NOTE - Could easily add image effects via this function i.e. black and white

        # Due to the issues around distortion, these are left in for reference of what didn't work
        # ----------

        # RGB16 is trippy!
        # qim = QImage(data, im.size[0], im.size[1], QImage.Format_RGB16)

        # Gave weird color distortion
        # qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)

        # Inverted Colors
        # im = im.convert("CMYK")
        # print(im.format())
        # data = im.tobytes("raw", "CMYK")
        # qim = QImage(data, im.size[0], im.size[1], QImage.Format_RGBX8888)


# Semi-transparent underlay that inherits from UILabel
class UIUnderlay(UILabel):
    def __init__(self, window):
        # UILabel.__init__(self, window)  # works
        super().__init__(window)  # works
        # super(UILabel, self).__init__(window) # doesn't work

        # self.resize(1280, 720)
        # self.move(0, 0)
        self.setAlignment(Qt.AlignCenter)
        self.setGeometry(0, 0, 1280, 187)
        pixmap = QPixmap('assets/Underlay@1x.png')
        self.setPixmap(pixmap)


class UIModeOverlay(QLabel):
    '''Old version of Mode -- No longer used'''
    def __init__(self, window, path: str, *args, **kwargs):
        super(QLabel, self).__init__(window, *args, **kwargs)
        # QLabel.__init__(self, window)

        self.resize(1280, 720)
        # self.move(0, 0)
        self.setAlignment(Qt.AlignCenter)
        # self.setStyleSheet("border: 3px solid pink; background-color: rgba(0, 0, 0, 100);")
        self.setStyleSheet("background-color: rgba(0, 0, 0, 25);")

        fadeEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(fadeEffect)
        anim1 = QPropertyAnimation(fadeEffect, b"opacity")
        anim1.setEasingCurve(QEasingCurve.InCubic)
        anim1.setStartValue(0)
        anim1.setEndValue(0)
        anim1.setDuration(50)
        anim1.start()

    def setTime(self):
        # print('UIModeOverlay.setTime()')
        pixmap = QPixmap('assets/Time@1x.png')
        self.setPixmap(pixmap)
        self._doAnimation()

    def setAltitude(self):
        # print('UIModeOverlay.setAltitude()')
        pixmap = QPixmap('assets/Altitude@1x.png')
        self.setPixmap(pixmap)
        self._doAnimation()

    def setColor(self):
        # print('UIModeOverlay.setColor()')
        pixmap = QPixmap('assets/Color@1x.png')
        self.setPixmap(pixmap)
        self._doAnimation()

    def _doAnimation(self):
        fadeEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(fadeEffect)

        anim1 = QPropertyAnimation(fadeEffect, b"opacity")
        anim1.setEasingCurve(QEasingCurve.InCubic)
        anim1.setStartValue(0)
        anim1.setEndValue(1)
        anim1.setDuration(750)

        anim2 = QPropertyAnimation(fadeEffect, b"opacity")
        anim2.setEasingCurve(QEasingCurve.OutCubic)
        anim2.setStartValue(1)
        anim2.setEndValue(0)
        anim2.setDuration(750)

        group = QSequentialAnimationGroup(self)
        group.addAnimation(anim1)
        group.addPause(2000)
        group.addAnimation(anim2)
        # group.addAnimation(anim1)
        group.start()

        # self.anim = QPropertyAnimation(self.label, b"geometry")
        # self.anim.setDuration(400)
        # self.anim.setStartValue(QRect(0, 720, 1280, 110))
        # self.anim.setEndValue(QRect(0, 610, 1280, 110))
        # self.anim.start()


# UI Fullscreen Components
# -----------------------------------------------------------------------------
class UIHelpMenu(QWidget):
    '''Help Menu overlay that shows Mac/Windows controls
    Remember to pass in MainWindow as a parameter'''
    def __init__(self, window: QMainWindow):
        super().__init__(window)

        self.resize(window.width(), window.height())
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        helpImage = UIImage('assets/help-menu@2x.png')
        self.layout.addWidget(helpImage)

        self._opacity = QGraphicsOpacityEffect()
        self._opacity.setOpacity(0.0)
        helpImage.setGraphicsEffect(self._opacity)

        self._setupHideAnimation()
        self._setupShowAnimation()

        self._status = 0

    def _setupHideAnimation(self):
        anim1 = QPropertyAnimation(self._opacity, b"opacity")
        anim1.setStartValue(1)  # opaque
        anim1.setEndValue(0)  # transparent
        anim1.setDuration(500)

        self.animGroupFadeOut = QParallelAnimationGroup(self)
        self.animGroupFadeOut.addAnimation(anim1)

    def _setupShowAnimation(self):
        anim1 = QPropertyAnimation(self._opacity, b"opacity")
        anim1.setStartValue(0)  # opaque
        anim1.setEndValue(1)  # transparent
        anim1.setDuration(0)

        self.animGroupFadeIn = QParallelAnimationGroup(self)
        self.animGroupFadeIn.addAnimation(anim1)

    def fadeOut(self):
        self.animGroupFadeOut.start()

    def fadeIn(self):
        self.animGroupFadeOut.stop()
        self.animGroupFadeIn.start()

    def toggleShowHide(self):
        self._opacity.setOpacity(1.0)
        self._status = (self._status + 1) % 2

        if self._status:
            self.show()
        else:
            self.hide()

    def toggleShowHideWithFade(self):
        self._status = (self._status + 1) % 2

        if self._status:
            self.fadeIn()
        else:
            self.fadeOut()


# UI Top Components
# -----------------------------------------------------------------------------
class UIScope(UIWindowWidget):
    '''Shows the Scope in the top left for both Landscape and Portrait'''
    def __init__(self, window: QMainWindow):
        super().__init__(window)

        self.resize(window.width(), window.height())
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        self.scopeImage = UIImage('assets/scope-hikes@2x.png')
        # scopeImage.setGeometry(0, 610, 1280, 110)
        self.layout.addWidget(self.scopeImage)

        self._status_scope = 1  # 0 - Archive; 1 - Hikes
        self._status_visibility = 1  # 0 - hidden; 1 - visible

        # self.label = QLabel("HOWDY", self)
        # bottomImg = QPixmap("bottom.png")
        # self.label.setPixmap(bottomImg)
        # self.label.setAlignment(Qt.AlignCenter)
        # self.label.setGeometry(0, 610, 1280, 110)

        # self._opacity = QGraphicsOpacityEffect()
        # self._opacity.setOpacity(0.0)
        # helpImage.setGraphicsEffect(self._opacity)

        # self._setupHideAnimation()
        # self._setupShowAnimation()

        # self._status = 0

    def setScopeHikes(self):
        self.scopeImage.update_image('assets/scope-hikes@2x.png')

    def setScopeArchive(self):
        self.scopeImage.update_image('assets/scope-archive@2x.png')

    def toggleScope(self):
        self._status_scope = (self._status_scope + 1) % 2
        if self._status_scope:  # 1 - Hikes
            self.scopeImage.update_image('assets/scope-hikes@2x.png')
        else:
            self.scopeImage.update_image('assets/scope-archive@2x.png')

    # def toggleShowHide(self):
    #     self._status = (self._status + 1) % 2

    #     if self._status:
    #         self.show()
    #     else:
    #         self.hide()


# UI Time, Color, Altitude Components
# -----------------------------------------------------------------------------
class UIContainer(QWidget):
    def __init__(self, window, layout, alignment, *args, **kwargs):
        super().__init__(window, *args, **kwargs)

        self.resize(window.width(), window.height())
        self.layout = layout
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(alignment)

        # layout.setSpacing(5)
        # self.timebar = TimeBar(QColor(62, 71, 47), 75, True)
        # self.timebar.setGraphicsEffect(UIEffectDropShadow())
        # self.layout.addWidget(self.timebar)

        self.setLayout(self.layout)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)

        # grab width & height of the whole painter
        w = painter.device().width()
        h = painter.device().height()

        # TESTING
        # brush.setColor(QColor(9, 24, 94, 100))
        # rect = QRect(0, 0, w, h)
        # painter.fillRect(rect, brush)


class PortraitTopLabel(UIWidget):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text
        self.setFixedHeight(720)
        self.setFixedWidth(250)

    def setText(self, str):
        self.text = str
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # bg
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)

        painter.translate(painter.device().width(), 0)
        painter.rotate(90)

        # text
        pen = QPen()
        pen.setColor(QColor('white'))
        painter.setPen(pen)
        font = QFont()
        font.setFamily('Atlas Grotesk')
        font.setBold(True)
        font.setPointSize(24)
        painter.setFont(font)

        rec = QRect(QPoint(300, 50), QSize(100, 25))
        painter.drawText(rec, 0, self.text)
        # painter.drawText(pt, "Starting")
        # painter.drawText(200, 20, 0, "Starting")

        painter.end()


class ColorPaletteNew(QWidget):
    def __init__(self, window: QMainWindow, visible: bool, colorList: list, confidentList: list) -> None:
        super().__init__(window)

        self.resize(window.width(), window.height())
        # self.layout = QVBoxLayout()
        # self.layout.setContentsMargins(100, 100, 50, 50)
        # self.layout.setAlignment(Qt.AlignHCenter)
        # self.setLayout(self.layout)

        # Width & Height = 160 x 40
        self.setFixedHeight(100)
        self.setFixedWidth(1280)
        self.colorList = colorList
        self.confidentList = confidentList
        self.isVisible = visible

    def paintEvent(self, e):
        # print('painting Color Palette')
        # print(self.previousInFocusChain())
        if self.isVisible:
            painter = QPainter(self)
            brush = QBrush()
            brush.setStyle(Qt.SolidPattern)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)

            # bg - for testing
            # brush.setColor(QColor(9, 24, 94, 150))
            # rect = QRect(0, 0, painter.device().width(), painter.device().height())
            # painter.fillRect(rect, brush)

            # grab width & height of the whole painter
            widgetw = painter.device().width()
            widgeth = painter.device().height()

            brush.setColor(QColor(0, 0, 0, 150))
            # rect = QRect(0, 0, widgetw, widgeth)
            # rect = QRect(1280/2 - 160, 60, 160, 40)
            # painter.fillRect(rect, brush)

            total = sum(self.confidentList)
            x = 1280/2 - 160/2
            for i, color in enumerate(self.colorList):
                brush.setColor(color)
                perc = self.confidentList[i]
                # w = round((perc / total) * widgetw, 0)
                # rect = QRect(x, 0, w, widgeth)

                w = round((perc / total) * 160, 0)
                rect = QRect(x, 30, w, 40)
                x += w
                painter.fillRect(rect, brush)

    def trigger_refresh(self, visible: bool, colorList: list, confidentList: list):
        self.colorList = colorList
        self.confidentList = confidentList
        self.isVisible = visible
        self.update()


class ColorPalette(UIWidget):
    def __init__(self, colorList: list, confidentList: list, visible: bool) -> None:
        super().__init__()

        self.setFixedHeight(40)
        self.setFixedWidth(160)

        self.colorList = colorList
        self.confidentList = confidentList
        self.visible = visible

    def paintEvent(self, e):
        # if self.canRepaint == False:
        #     return

        # print('painting Color Palette')
        # print(self.previousInFocusChain())
        if self.visible:
            painter = QPainter(self)
            brush = QBrush()
            brush.setStyle(Qt.SolidPattern)
            painter.setRenderHint(QPainter.HighQualityAntialiasing)

            # grab width & height of the whole painter
            widgetw = painter.device().width()
            widgeth = painter.device().height()

            brush.setColor(QColor(0, 0, 0, 150))
            rect = QRect(0, 0, widgetw, widgeth)
            painter.fillRect(rect, brush)

            total = sum(self.confidentList)
            x = 0
            for i, color in enumerate(self.colorList):
                brush.setColor(color)
                perc = self.confidentList[i]
                w = round((perc / total) * widgetw, 0)
                rect = QRect(x, 0, w, widgeth)
                x += w
                painter.fillRect(rect, brush)

        # self.canRepaint = False

    def trigger_refresh(self, colorList: list, confidentList: list, visible: bool):
        # self.canRepaint = True
        self.colorList = colorList
        self.confidentList = confidentList
        self.visible = visible
        self.update()


class AltitudeGraph(UIWidget):
    '''Altitude Graph which builds a graph of points from list of altitude values.'''
    def __init__(self, isAltMode: bool, altitudeList: list, percent: float, currentAlt: float) -> None:
        super().__init__()
        self.setFixedHeight(180)
        self.bgcolor = QColor('#ff00ff')

        self.altitudeList = altitudeList
        self.isAltMode = isAltMode
        self.percent = percent
        self.currentAlt = currentAlt

        self.indicatorSelected = QImage('assets/indicator-selected.png')

    def paintEvent(self, e):
        # print('painting Altitude Graph')

        DOT_DIAM = 5
        IND_DIAM = DOT_DIAM + 5

        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        W = painter.device().width()
        H_PAD = 46
        H_PAD_HALF = H_PAD/2
        # puts padding on the drawable space, so indicator isn't cut off on top or bottom
        H = painter.device().height() - H_PAD
        # print(f"H = {H}")

        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        pen = QPen()

        # bg - for testing
        # brush.setColor(QColor(9, 24, 94, 150))
        # rect = QRect(0, 0, painter.device().width(), painter.device().height())
        # painter.fillRect(rect, brush)

        # Setup for painting the dots
        pen.setWidth(1)
        pen.setColor(QColor(255, 255, 255, 150))
        painter.setPen(pen)

        brush.setStyle(Qt.SolidPattern)
        brush.setColor(QColor(255, 255, 255, 150))
        painter.setBrush(brush)

        STEP = W / len(self.altitudeList)
        FIRST_STEP = STEP/2 - DOT_DIAM/2
        MINV = min(self.altitudeList)
        MAXV = max(self.altitudeList)

        # Draw the Graph
        i = 0
        for a in self.altitudeList:
            x = FIRST_STEP + (STEP * i)
            y = H + H_PAD_HALF - DOT_DIAM - ((a - MINV)/(MAXV-MINV))*(H-DOT_DIAM)  # used to be round
            painter.drawEllipse(x, y, DOT_DIAM, DOT_DIAM)
            i += 1

        # Draw the Indicator
        # just increasing the border instead of the IND_DIAM fixes weird
        # rounding issues between the y of the Graph and y of the Indicator
        pen.setWidth(4)
        pen.setColor(QColor(255, 255, 255))
        painter.setPen(pen)
        brush.setColor(QColor(255, 255, 255))
        painter.setBrush(brush)

        x = (self.percent * W)
        if len(self.altitudeList) < 128:  # if less than 128, starting step needs to be adjusted to align properly
            x = (self.percent * W) - (STEP/2)
        y = H + H_PAD_HALF - IND_DIAM - ((self.currentAlt - MINV)/(MAXV-MINV))*(H-IND_DIAM)

        if self.isAltMode:
            rect = QRectF(x - 48/2, y-(54/2 - IND_DIAM/2), 48, 54)
            painter.drawImage(rect, self.indicatorSelected)
        painter.drawEllipse(x - IND_DIAM/2, y, IND_DIAM, IND_DIAM)

    def trigger_refresh(self, isAltMode: bool, altitudeList: list, percent: float, currentAlt: float):
        self.altitudeList = altitudeList
        self.isAltMode = isAltMode
        self.percent = percent
        self.currentAlt = currentAlt
        self.update()


class ColorBar(UIWidget):
    '''Defines the color bar at bottom of the screen
    Accepts a list of colors, percent, and indicator color'''
    def __init__(self, isColorMode: bool, colorList: list, percent: float, indicatorColor: QColor) -> None:
        super().__init__()
        self.setFixedHeight(54)
        self.bgcolor = QColor('#ffffff')

        self.colorList = colorList
        self.isColorMode = isColorMode
        self.percent = percent
        self.indicatorColor = indicatorColor
        self.indicatorSelected = QImage('assets/indicator-selected.png')

    def paintEvent(self, e):
        # print('painting Color Bar')
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # grab width & height of the whole painter space
        W = painter.device().width()
        H = painter.device().height()

        # Set the values for the widget
        height = 20
        yline = H/2 - height/2

        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        pen = QPen()

        # bg - for testing
        # brush.setColor(QColor(9, 24, 94, 150))
        # rect = QRect(0, 0, painter.device().width(), painter.device().height())
        # painter.fillRect(rect, brush)

        x1 = 0
        boxw = W / len(self.colorList)

        for color in self.colorList:
            brush.setColor(color)
            # 'boxw' + 5 - the 5 is for extra padding to make sure the bar extends enough and doesn't leave gaps
            # sometimes for smaller hikes there's awkward gaps between color bars.
            # The other remedy was to round 'boxw', but that led to an overall net shorter ColorBar
            rect = QRect(x1, yline, boxw+5, height)
            x1 += boxw
            painter.fillRect(rect, brush)

        # Indicator
        brush.setColor(self.indicatorColor)
        painter.setBrush(brush)
        pen.setWidth(1)
        pen.setColor(self.indicatorColor)
        painter.setPen(pen)

        x1 = W * self.percent
        if len(self.colorList) < 128:  # if less than 128, the starting x needs to be adjusted to align properly
            # subtracting BOXW/2 moves the indicator back so it is centered on the respective color bar
            x1 = W * self.percent - boxw/2

        # Highlight
        if self.isColorMode:
            rect = QRectF(x1 - 48/2, H/2 - 54/2, 48, 54)
            painter.drawImage(rect, self.indicatorSelected)

        # Color Indicator
        INDH = 40
        INDW = 20
        y1 = H/2 - INDH/2
                                # x, y, w, h, radius, radius
        painter.drawRoundedRect(x1 - INDW/2, y1, INDW, INDH, 6, 6)

    def trigger_refresh(self, isColorMode: bool, colorList: list, percent: float, indicatorColor: QColor):
        # print(f'ColorBar._trigger_refresh()')
        self.colorList = colorList
        self.isColorMode = isColorMode
        self.percent = percent
        self.indicatorColor = indicatorColor
        # self.update()


class TimeBar(UIWidget):
    '''Defines the time bar at the bottom of the screen.
    There's two styles depending whether you are in Time mode or Not'''
    def __init__(self, isTimeMode: bool, bgcolor, colorBarSize: int, percent: float) -> None:
        super().__init__()
        self.setFixedHeight(70)
        self.bgcolor = bgcolor
        self.colorBarSize = colorBarSize    # the amount of discrete points in the colorbar,
                                            # so we know how to position the time bar indicator to line up
        self.percent = percent
        self.isTimeMode = isTimeMode

        self.indicator = QImage('assets/indicator-time.png')
        self.indicatorSelected = QImage('assets/indicator-time-selected.png')

    def paintEvent(self, e):
        # print('painting TimeBar')
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # grab width & height of the whole painter
        W = painter.device().width()
        H = painter.device().height()
        # print(f'TimeBar H: {H}')

        # Set the values for the widget
        lheight = 9
        yline = H/2 - lheight/2
        dotdiam = 20
        ydot = (H/2) - (dotdiam/2)

        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        pen = QPen()

        # bg - for testing
        # brush.setColor(QColor(9, 24, 94, 150))
        # rect = QRect(0, 0, painter.device().width(), painter.device().height())
        # painter.fillRect(rect, brush)

        # full line
        brush.setColor(QColor(255, 255, 255, 100))
        rect2 = QRect(0, yline, W, lheight)
        painter.fillRect(rect2, brush)
        brush.setColor(QColor(255, 255, 255))

        # If Time Mode - partial fill-line
        stepback = (W / self.colorBarSize) / 2  # Amount to move back the Time Indicator to align with
                                                # the ColorBar and AltitudeGraph Indicators

        x = W*self.percent
        if self.colorBarSize < 128:  # if less than 128, the starting x needs to be adjusted to align properly
            x = W*self.percent - stepback

        if self.isTimeMode:
            rect2 = QRect(0, yline, x, lheight)
            painter.fillRect(rect2, brush)

        # Indicator Styling
        pen.setWidth(1)
        pen.setColor(QColor(255, 255, 255))
        painter.setPen(pen)
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)

        # Circle Indicator
        # x = x - dotdiam/2 - 1
        # painter.drawEllipse(x, ydot, dotdiam, dotdiam)

        # Triangle Indicator
        # rect = QRectF(x, ydot - 7, 20, 20)
        # path = QPainterPath()
        # path.moveTo(rect.left() + (rect.width() / 2), rect.bottom())
        # path.lineTo(rect.topLeft())
        # path.lineTo(rect.topRight())
        # path.lineTo(rect.left() + (rect.width() / 2), rect.bottom())
        # painter.fillPath(path, brush)

        # Image Indicator
        rect = QRectF(x - 48/2, ydot - 25, 48, 54)
        if self.isTimeMode:
            painter.drawImage(rect, self.indicatorSelected)
        else:
            painter.drawImage(rect, self.indicator)

    def trigger_refresh(self, isTimeMode: bool, colorBarSize: int, percent: float):
        self.colorBarSize = colorBarSize
        self.percent = percent
        self.isTimeMode = isTimeMode
        self.update()


# Transfer Animation Components
# -----------------------------------------------------------------------------
class TimeBarTransfer(QWidget):
    '''Defines the time bar for transfer'''
    def __init__(self, window: QMainWindow, percent: float) -> None:
        super().__init__(window)

        self.resize(window.width(), window.height())

        self.setFixedHeight(70)
        self.setFixedWidth(1280)
        self.move(0, 640)

        self.colorBarSize = 1280    # the amount of discrete points in the colorbar,
                                    # so we know how to position the time bar indicator to line up
        self.percent = percent
        self.isTimeMode = True

        self.indicator = QImage('assets/indicator-time-transfer.png')

    def paintEvent(self, e):
        # print('painting TimeBar')
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # grab width & height of the whole painter
        W = painter.device().width()
        H = painter.device().height()
        # print(f'TimeBar H: {H}')

        # Set the values for the widget
        lheight = 9
        yline = H/2 - lheight/2
        dotdiam = 20
        ydot = (H/2) - (dotdiam/2)

        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        pen = QPen()

        # bg - for testing
        # brush.setColor(QColor(9, 24, 94, 150))
        # rect = QRect(0, 0, painter.device().width(), painter.device().height())
        # painter.fillRect(rect, brush)

        # full line
        brush.setColor(QColor(255, 255, 255, 150))
        rect2 = QRect(0, yline, W, lheight)
        painter.fillRect(rect2, brush)
        brush.setColor(QColor(255, 255, 255))

        # Indicator Styling
        pen.setWidth(1)
        pen.setColor(QColor(255, 255, 255))
        painter.setPen(pen)
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)

        # Image Indicator
        x = W*self.percent
        rect = QRectF(x - 48/2, ydot - 25, 48, 54)
        painter.drawImage(rect, self.indicator)

    def trigger_refresh(self, percent: float):
        self.percent = percent
        self.update()


class AltitudeGraphTransferQWidget(QWidget):
    def __init__(self, window: QMainWindow, isAltMode: bool, altitudeList: list, currentAlt: float) -> None:
        super().__init__(window)

        self.resize(window.width(), window.height())

        self.setFixedHeight(500)
        self.setFixedWidth(1280)
        self.move(0, 110)

        self.altitudeList = altitudeList
        self.isAltMode = isAltMode
        self.currentAlt = currentAlt

        self.H_PAD = 50

        self.indicatorSelected = QImage('assets/indicator-selected.png')

    def paintEvent(self, e):
        # print('painting Altitude Graph')

        DOT_DIAM = 5
        IND_DIAM = DOT_DIAM + 5

        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        W = painter.device().width()
        self.H_PAD = 0  # TODO - used to be 46, make sure this doesn't cause an issue
        H_PAD_HALF = self.H_PAD/2
        # puts padding on the drawable space, so indicator isn't cut off on top or bottom
        H = painter.device().height() - self.H_PAD
        # print(f"H = {H}")

        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        pen = QPen()

        # bg - for testing
        # brush.setColor(QColor(255, 24, 94, 150))
        # rect = QRect(0, 0, painter.device().width(), painter.device().height())
        # painter.fillRect(rect, brush)

        # Setup for painting the dots
        pen.setWidth(1)
        pen.setColor(QColor(255, 255, 255, 150))
        painter.setPen(pen)

        brush.setStyle(Qt.SolidPattern)
        brush.setColor(QColor(255, 255, 255, 150))
        painter.setBrush(brush)

        STEP = W / len(self.altitudeList)
        FIRST_STEP = STEP/2 - DOT_DIAM/2
        MINV = min(self.altitudeList)
        MAXV = max(self.altitudeList)

        # Draw the Graph
        i = 0
        for a in self.altitudeList:
            x = FIRST_STEP + (STEP * i)
            y = H + H_PAD_HALF - DOT_DIAM - ((a - MINV)/(MAXV-MINV))*(H-DOT_DIAM)  # used to be round
            painter.drawEllipse(x, y, DOT_DIAM, DOT_DIAM)
            i += 1

        # Calculate the line position
        # H-percent*H : figures out the position
        # - 2 : adjusts for the weight of the line
        y = H - ( ((self.currentAlt - MINV)/(MAXV-MINV)) * (H-4) )
        # print(H)
        self.linePosY = y
        # print("Line PosY:")
        # print(self.linePosY)

    def trigger_refresh(self, isAltMode: bool, altitudeList: list):
        self.altitudeList = altitudeList
        self.isAltMode = isAltMode
        self.update()


class ColorBarTransfer(QWidget):
    def __init__(self, window: QMainWindow, isColorMode: bool, colorList: list) -> None:
        super().__init__(window)

        self.resize(window.width(), window.height())

        self.setFixedHeight(30)
        self.setFixedWidth(1280)
        self.move(0, 640)

        self.colorList = colorList
        self.isColorMode = isColorMode  # TODO - maybe remove this during linting?

    def paintEvent(self, e):
        # print('painting Color Bar')
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # grab width & height of the whole painter space
        W = painter.device().width()
        H = painter.device().height()

        # Set the values for the widget
        height = 30
        yline = H/2 - height/2

        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        pen = QPen()

        # bg - for testing
        brush.setColor(QColor(255, 50, 50, 150))
        rect = QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        x1 = 0
        boxw = W / len(self.colorList)

        for color in self.colorList:
            brush.setColor(color)
            # 'boxw' + 5 - the 5 is for extra padding to make sure the bar extends enough and doesn't leave gaps
            # sometimes for smaller hikes there's awkward gaps between color bars.
            # The other remedy was to round 'boxw', but that led to an overall net shorter ColorBar
            rect = QRect(x1, yline, boxw+5, height)
            x1 += boxw
            painter.fillRect(rect, brush)

    def trigger_refresh(self, isColorMode: bool, colorList: list):
        # print(f'ColorBar._trigger_refresh()')
        self.colorList = colorList
        self.isColorMode = isColorMode
        self.update()


class BackgroundColor(QWidget):
    def __init__(self, window, layout, alignment, color: QColor, *args, **kwargs):
        super().__init__(window, *args, **kwargs)

        self.resize(window.width(), window.height())
        self.layout = layout
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(alignment)
        self.setLayout(self.layout)
        self.color = color

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)

        # grab width & height of the whole painter
        w = painter.device().width()
        h = painter.device().height()

        # TESTING
        # brush.setColor(QColor(9, 24, 94, 255))
        brush.setColor(self.color)
        rect = QRect(0, 0, w, h)
        painter.fillRect(rect, brush)

    def changeColor(self, color):
        self.color = color
        self.update()


# Simple wrapper of QLabel, for a scaled center image
# class CenterImage(QLabel):
#     def __init__(self, mainWindow, path: str, *args, **kwargs):
#         # super(QLabel, self).__init__(*args, **kwargs)
#         super().__init__(mainWindow)

#         # QLabel.__init__(self, mainWindow)
#         self.resize(1280, 720)
#         pixmap = QPixmap(path)
#         pixmap = pixmap.scaledToWidth(550)
#         self.setPixmap(pixmap)

#     def updateImage(self, path: str):
#         pixmap = QPixmap(path)
#         pixmap = pixmap.scaledToWidth(550)
#         self.setPixmap(pixmap)


class TransferCenterImage(QWidget):
    '''Alternates between the 2 images for a smooth fading experience'''
    def __init__(self, window: QMainWindow, picture: Picture) -> None:
        super().__init__(window)
        self.resize(window.width(), window.height())

        # Used to cover up UI components behind it
        self._bgImg = _CenterImage(window, 'assets/black.png')

        # Alternates between the images for a smooth fading experience
        self._centerImg2 = _CenterImage(window, 'assets/black.png')
        self._centerImg1 = _CenterImage(window, picture.cameraf)

        self.currentImg = self._centerImg1

    def fadeNewImage(self, picture: Picture):
        # Create a new color bg to hide the UI elements behind the image
        hexcode = picture.color_rgb.name()
        im = Image.new("RGB", (1280, 720), hexcode)
        im.save("assets/transferBg.png")
        self._bgImg.setImage('assets/transferBg.png')

        # Fade the top two images
        if self.currentImg == self._centerImg1:
            # Change img2, fadeout img1, fadein img2, switch current to img2
            self._centerImg2.setImage(picture.cameraf)
            self._centerImg1.fadeout()
            self._centerImg2.fadein()
            self.currentImg = self._centerImg2

        elif self.currentImg == self._centerImg2:
            self._centerImg1.setImage(picture.cameraf)
            self._centerImg2.fadeout()
            self._centerImg1.fadein()
            self.currentImg = self._centerImg1

        else:
            print('ERROR fading between transfer center images')


class _CenterImage(QWidget):
    '''Defines a center image for transfer animation February 2022'''
    def __init__(self, window: QMainWindow, path: str) -> None:
        super().__init__(window)
        self.resize(window.width(), window.height())
        # self.setFixedHeight(720)
        # self.setFixedWidth(1280)
        # self.move(0, 640)

        self.image = QImage(path)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # Set the values for the widget
        rectx = (painter.device().width() / 2) - (550/2)
        recty = (painter.device().height() / 2) - (310/2)
        rect = QRectF(rectx, recty, 550, 310)
        painter.drawImage(rect, self.image)

    def setImage(self, path: str):
        self.image = QImage(path)
        self.update()

    def fadein(self):
        fadeEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(fadeEffect)
        self.anim = QPropertyAnimation(fadeEffect, b"opacity")
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setDuration(2000)
        self.anim.start()

    def fadeout(self):
        fadeEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(fadeEffect)
        self.anim = QPropertyAnimation(fadeEffect, b"opacity")
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setDuration(2000)
        self.anim.start()


# UI Effects
# -----------------------------------------------------------------------------

# Text effect used for the text at the top of the interface
class UIEffectTextDropShadow(QGraphicsDropShadowEffect):
    def __init__(self):
        super(QGraphicsDropShadowEffect, self).__init__()
        self.setBlurRadius(20)
        color = QColor(0, 0, 0, 50)  # r,g,b,a | opaque = 255
        self.setColor(color)
        self.setOffset(0, 2)


# Drop shadow for bottom UI elements
class UIEffectDropShadow(QGraphicsDropShadowEffect):
    def __init__(self):
        super(QGraphicsDropShadowEffect, self).__init__()
        self.setBlurRadius(20)
        color = QColor(0, 0, 0, 150)  # r,g,b,a | opaque = 255
        self.setColor(color)
        self.setOffset(0, 2)


# UI Testing
# -----------------------------------------------------------------------------

# Add a single color widget, great for testing purposes
class UIColor(QWidget):
    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)
