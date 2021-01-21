#!/usr/bin/env python3

# Various helper UI classes for easier development of PyQt5 applications

# Imports
# from projector_slideshow import *

from sqlite3.dbapi2 import Error
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PIL import Image, ImageQt  # Pillow image functions
# from PIL.ImageQt import ImageQt

import sys
import time


# UI Components
# -----------------------------------------------------------------------------

# Super classes for universal animations
class UILabel(QLabel):
    def __init__(self, window):
        # super(QLabel, self).__init__(window)  # original
        # QLabel.__init__(self, window)  # also works
        super().__init__(window)  # works
        # self.fadeEffect = QGraphicsOpacityEffect()
        # self.setGraphicsEffect(self.fadeEffect)
        # print(self.fadeEffect.opacity())

        # self._setupAnimation()

        print('UILabel was initialized ')

        self.anim = QPropertyAnimation()

        self.myTimer = QTimer()
        self.myTimer.setInterval(1000)
        self.myTimer.setSingleShot(True)
        self.myTimer.timeout.connect(self._doAnimation)

        self.fadeEffect = QGraphicsOpacityEffect()

        # m_myLongTimer->setInterval(360000);
        # m_myLongTimer->setSingleShot(true);
        # connect(m_myLongTimer, SIGNAL(timeout()), SLOT(myslot()));
        # m_myLongTimer->start();

        # self.anim = QPropertyAnimation(self.fadeEffect, b"opacity")


        # QLabel.__init__(self, mainWindow)

        # UILabel.__init__(self, window)  # works
        # super().__init__(window)  # works

        # print('UILabel superclass was called')
        # print(dir(self))

        # self.opacityEffect = QGraphicsOpacityEffect()
        # self.opacityEffect.setOpacity(1.0)
        # self.setGraphicsEffect(self.opacityEffect)
        # self.anim = QPropertyAnimation(self.opacityEffect, b"opacity")
        # self.anim.setStartValue(1)
        # self.anim.setEndValue(0)
        # self.anim.setDuration(1000)

    # def _setupAnimation(self):
    #     self.fadeEffect = QGraphicsOpacityEffect()
    #     self.setGraphicsEffect(self.fadeEffect)
    #     self.anim = QPropertyAnimation(self.fadeEffect, b"opacity")
    #     self.anim.setStartValue(1)
    #     self.anim.setEndValue(0)
    #     self.anim.setDuration(1000)

    # This works, but I need to move this stuff into the main function
    def doAnimation(self):
        # QTimer.singleShot(1000, self._doAnimation)
        self.myTimer.start(1000)

    def _doAnimation(self):
        # print('do animation')
        # print(self.fadeEffect.opacity())

        self.setGraphicsEffect(self.fadeEffect)
        self.anim = QPropertyAnimation(self.fadeEffect, b"opacity")
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setDuration(1000)
        self.anim.start()
        self.update()

    def show2(self):
        self.myTimer.stop()
        self.anim.stop()
        self.fadeEffect.setOpacity(1.0)
        # try:
        #     print('gonna try')
        #     self.fadeEffect.setOpacity(1.0)
        # except Error:
        #     print('NO FADE EFFECT')

        # print(self.fadeEffect)


    '''
    def _setupHideAnimation(self):
        anim1 = QPropertyAnimation(self._label1_opacity, b"opacity")
        # anim1 = QPropertyAnimation(fadeEffect, b"opacity")
        anim1.setStartValue(1)
        anim1.setEndValue(0)  # transparent
        anim1.setDuration(1000)

        # fadeEffect2 = QGraphicsOpacityEffect()
        # self.label2.setGraphicsEffect(fadeEffect2)
        anim2 = QPropertyAnimation(self._label2_opacity, b"opacity")
        anim2.setStartValue(1)
        anim2.setEndValue(0)  # transparent
        anim2.setDuration(1000)

        # group = QSequentialAnimationGroup(self)
        self.animGroup.addAnimation(anim1)
        self.animGroup.addAnimation(anim2)

    def _hideAnimation(self):
        self.animGroup.start()
    '''


    def show(self):
        self.anim.stop()
        self.opacityEffect.setOpacity(1.0)

    def fadeIn(self):
        self.anim.start()
        # self._showAnimation()

    def fadeOut(self):
        QTimer.singleShot(1000, self._hideAnimation)

    # def _setupHideAnimation(self):
        # self.opacityEffect.setOpacity(1.0)
        # self.anim = QPropertyAnimation(self.opacityEffect, b"opacity")

        # Transparent (0) to Opaque (1)
        # self.anim.setStartValue(1)
        # self.anim.setEndValue(0)
        # self.anim.setDuration(1000)

    def _showAnimation(self):
        self.anim.start()

        # fadeEffect = QGraphicsOpacityEffect()
        # self.setGraphicsEffect(fadeEffect)
        # self.anim = QPropertyAnimation(fadeEffect, b"opacity")
        # # self.anim = QPropertyAnimation(self.label, b"windowOpacity")

        # # Transparent (0) to Opaque (1)
        # self.anim.setStartValue(0)
        # self.anim.setEndValue(1)
        # self.anim.setDuration(1000)
        # self.anim.start()

        # self.update()

    def _hideAnimation(self):
        # fadeEffect = QGraphicsOpacityEffect()
        # self.setGraphicsEffect(self.opacityEffect)  # NOTE was commented out
        # self.anim = QPropertyAnimation(self.opacityEffect, b"opacity")  # NOTE was commented out
        # self.anim = QPropertyAnimation(self.label, b"windowOpacity")

        # Opaque (1) to Transparent (0)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setDuration(1000)
        self.anim.start()

        # self.anim.update()


# Labels for the information at the top of the screen
class UILabelTop(UILabel):
    def __init__(self, window, text: str, alignment):
        UILabel.__init__(self, window)  # works
        # super().__init__(window)  # works

        

        # super(QLabel, self).__init__(*args, **kwargs)
        # super().__init__(window)
        # QLabel.__init__(self, window)

        
        # class B(A):
        #     def __init__(self):
        #         A.__init__(self)
        #         # super(B, self).__init__() you can use this line as well
        #         print 'B'



        print('UILabelTop being initialized')

        self._text = text
        self.setText(self._text)

        self.resize(1280, 200)
        # self.setAlignment(Qt.AlignLeft)
        self.setAlignment(alignment)
        self.setMargin(65)
        # self.setIndent(100)

        self.setFont(QFont('Atlas Grotesk', 28, 400))
        self.setStyleSheet("color: rgba(255,255,255,255)")
        self.setGraphicsEffect(UIEffectTextDropShadow())

    def setPrimaryText(self, text):
        self.setText(str(text))


class UILabelTopCenter(QWidget):
    def __init__(self, window, primaryText: str, secondaryText: str, *args, **kwargs):
        # super(QWidget, self).__init__(window, *args, **kwargs)
        super().__init__(window, *args, **kwargs)

        self.resize(1280, 150)
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

        self.animGroup = QParallelAnimationGroup(self)
        self._setupHideAnimation()

        # TESTING
        # palette = self.palette()
        # palette.setColor(QPalette.Window, QColor('gray'))
        # label1.setAutoFillBackground(True)
        # label1.setPalette(palette)
        # label2.setAutoFillBackground(True)
        # label2.setPalette(palette)

        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)

    def setPrimaryText(self, text):
        self.label1.setText(str(text))

    def setSecondaryText(self, text):
        self.label2.setText(text)

    def show(self):
        # print('show')
        # print(self.animGroup.children())
        self.animGroup.stop()
        self._label1_opacity.setOpacity(1.0)
        self._label2_opacity.setOpacity(1.0)

        # self.opacity_effect = QGraphicsOpacityEffect() 
        # self.opacity_effect.setOpacity(0.3) 
        # label.setGraphicsEffect(self.opacity_effect)

    def fadeIn(self):
        print('UILabelTopCenter.fadeIn() -- NO YET IMPLEMENTED')

    def fadeOut(self):
        QTimer.singleShot(1000, self._hideAnimation)

    def _setupHideAnimation(self):
        anim1 = QPropertyAnimation(self._label1_opacity, b"opacity")
        # anim1 = QPropertyAnimation(fadeEffect, b"opacity")
        anim1.setStartValue(1)
        anim1.setEndValue(0)  # transparent
        anim1.setDuration(1000)

        # fadeEffect2 = QGraphicsOpacityEffect()
        # self.label2.setGraphicsEffect(fadeEffect2)
        anim2 = QPropertyAnimation(self._label2_opacity, b"opacity")
        anim2.setStartValue(1)
        anim2.setEndValue(0)  # transparent
        anim2.setDuration(1000)

        # group = QSequentialAnimationGroup(self)
        self.animGroup.addAnimation(anim1)
        self.animGroup.addAnimation(anim2)

    def _hideAnimation(self):
        self.animGroup.start()


# Simple wrapper of QLabel, for easier image loading
class UIImage(QLabel):

    # def __init__(self, *args, **kwargs):
    #     super(QLabel, self).__init__(*args, **kwargs)
    #     # QLabel.__init__(self)
    #     pixmap = QPixmap()

    def __init__(self, path: str, *args, **kwargs):
        super(QLabel, self).__init__(*args, **kwargs)
        # QLabel.__init__(self)
        pixmap = QPixmap(path)
        self.setPixmap(pixmap)

    # Utilizes local storage
    def update_image(self, path: str):
        self.pixmap = QPixmap(path)
        print('Is this a Pixmap?: {t}'.format(t=type(self.pixmap)))
        self.setPixmap(self.pixmap)

    # Utilizes image conversion
    # TODO - see how processing consumption for this, compares to saving locally
    def update_pixmap(self, im):
        im = im.convert("RGB")
        data = im.tobytes("raw", "RGB")
        # qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)  # give weird color distortion
        qim = QImage(data, im.size[0], im.size[1], QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qim)
        self.setPixmap(self.pixmap)

        # Collection of things that didn't work but it is helpful to remember
        '''
        qim = ImageQt(im)
        pix = QPixmap.fromImage(qim)
        # pix = QPixmap.fromImage(qim, flags=Qt.AutoColor)
        self.setPixmap(pix)
        '''

        '''
        # fromImage() doesn't seem to be working; the other function just builds it from path
        qim = ImageQt(image)
        qim2 = QImage(qim)
        pix = QPixmap.fromImage(qim2)
        self.setPixmap(pix)
        '''

        '''
        # self.pixmap = QPixmap(ImageQt.ImageQt(image))
        print('update_pixmpa()')
        print('Parameter input is: {t}'.format(t=type(image)))

        qtimg = ImageQt.ImageQt(image)
        print('Is this a QT Image?: {t}'.format(t=type(qtimg)))

        self.pixmap = QPixmap.fromImage(qtimg)
        print('Is this a Pixmap?: {t}'.format(t=type(self.pixmap)))

        self.setPixmap(QPixmap(self.pixmap))
        '''


class UIUnderlay(UILabel):
    def __init__(self, window):
        super(UILabel, self).__init__(window)
        # self.resize(1280, 720)
        # self.move(0, 0)
        self.setAlignment(Qt.AlignCenter)
        self.setGeometry(0, 0, 1280, 187)
        pixmap = QPixmap('assets/underlay.png')
        self.setPixmap(pixmap)

    '''
    def show(self):
        self._showAnimation()

    def hide(self):
        QTimer.singleShot(1000, self._hideAnimation)

    def _showAnimation(self):
        fadeEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(fadeEffect)
        self.anim = QPropertyAnimation(fadeEffect, b"opacity")
        # self.anim = QPropertyAnimation(self.label, b"windowOpacity")

        # Transparent (0) to Opaque (1)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setDuration(1000)
        self.anim.start()

        self.update()

    def _hideAnimation(self):
        fadeEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(fadeEffect)
        self.anim = QPropertyAnimation(fadeEffect, b"opacity")
        # self.anim = QPropertyAnimation(self.label, b"windowOpacity")

        # Opaque (1) to Transparent (0)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setDuration(1000)
        self.anim.start()

        self.update()
    '''


class UIModeOverlay(QLabel):
    def __init__(self, window, path: str, mode, *args, **kwargs):
        super(QLabel, self).__init__(window, *args, **kwargs)
        # QLabel.__init__(self, window)

        self.resize(1280, 720)
        # self.move(0, 0)
        self.setAlignment(Qt.AlignCenter)
        # self.setStyleSheet("border: 3px solid pink; background-color: rgba(0, 0, 0, 100);")
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")

        # TODO - remove this because its so janky
        fadeEffect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(fadeEffect)
        anim1 = QPropertyAnimation(fadeEffect, b"opacity")
        anim1.setEasingCurve(QEasingCurve.InCubic)
        anim1.setStartValue(0)
        anim1.setEndValue(0)
        anim1.setDuration(50)
        anim1.start()

        # pixmap = QPixmap('assets/Time@1x.png')
        # self.setPixmap(pixmap)

        # self.hide()

    def setTime(self):
        print('time')
        pixmap = QPixmap('assets/Time@1x.png')
        self.setPixmap(pixmap)
        self._doAnimation()

    def setAltitude(self):
        print('alt')
        pixmap = QPixmap('assets/Altitude@1x.png')
        self.setPixmap(pixmap)
        self._doAnimation()

    def setColor(self):
        print('color')
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
