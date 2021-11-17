import sys
from time import sleep

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage

import rospy
from geometry_msgs.msg import Point

import cv2

from stretch_ui_main_window import Ui_StretchWindow


class MapWorker(QThread):
    map_update = pyqtSignal(QPixmap)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.capture = None
        self.thread_active = False

    def run(self):
        self.thread_active = True
        while self.thread_active:
            # TODO assign proper image file name for image we get from ROS
            updated_map = QPixmap("dummy_map.pgm")
            self.map_update.emit(updated_map)
            sleep(1)

    def stop(self):
        self.thread_active = False
        self.quit()


class VideoWorker(QThread):
    image_update = pyqtSignal(QImage)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.capture = None
        self.thread_active = False

    def run(self):
        self.thread_active = True
        self.capture = cv2.VideoCapture(0)
        while self.thread_active:
            ret, frame = self.capture.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                converted_to_qt = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
                picture = converted_to_qt.scaled(960, 540, Qt.KeepAspectRatio)
                self.image_update.emit(picture)
        self.capture.release()

    def stop(self):
        self.thread_active = False
        self.quit()


class MainWindow:
    def __init__(self):
        self.main_window = QMainWindow()
        self.ui = Ui_StretchWindow()
        self.ui.setupUi(self.main_window)

        # Set up thread for video feed
        self.video_worker = VideoWorker()
        self.video_worker.image_update.connect(self.video_frame_update)

        self.map_worker = MapWorker()
        self.map_worker.map_update.connect(self.map_frame_update)

        self.ui.PagesStackedWidget.setCurrentWidget(self.ui.page_1)

        self.ui.GraspButtonPage1.clicked.connect(self.go_to_page_2)
        self.ui.UpButtonPage1.clicked.connect(self.page_1_up)
        self.ui.LeftButtonPage1.clicked.connect(self.page_1_left)
        self.ui.RightButtonPage1.clicked.connect(self.page_1_right)
        self.ui.DownButtonPage1.clicked.connect(self.page_1_down)

        self.ui.BackButtonPage2.clicked.connect(self.go_to_page_1)
        self.ui.UpButtonPage2.clicked.connect(self.page_2_up)
        self.ui.LeftButtonPage2.clicked.connect(self.page_2_left)
        self.ui.RightButtonPage2.clicked.connect(self.page_2_right)
        self.ui.DownButtonPage2.clicked.connect(self.page_2_down)
        # TODO Implement both zooms
        self.ui.ZoomInButtonPage2.clicked.connect(self.zoom_in)
        self.ui.ZoomOutButtonPage2.clicked.connect(self.zoom_out)

        self.ui.CameraLabelPage2.mousePressEvent = self.publish_point

        self.ui.YesButtonPage3.clicked.connect(self.go_to_page_1)
        self.ui.NoButtonPage3.clicked.connect(self.go_to_page_2)

    def show(self):
        self.main_window.show()

    def go_to_page_1(self):
        self.ui.PagesStackedWidget.setCurrentWidget(self.ui.page_1)
        self.map_worker.start()
        # TODO Update image source to proper names
        self.video_worker.stop()

    def go_to_page_2(self):
        self.ui.PagesStackedWidget.setCurrentWidget(self.ui.page_2)
        self.video_worker.start()
        self.map_worker.stop()

    def go_to_page_3(self):
        self.ui.PagesStackedWidget.setCurrentWidget(self.ui.page_3)
        # TODO Add Selection to the image via opencv
        self.video_worker.stop()
        self.map_worker.stop()

    def video_frame_update(self, image):
        self.ui.CameraLabelPage2.setPixmap(QPixmap.fromImage(image))

    def map_frame_update(self, updated_map):
        self.ui.MapLabelPage1.setPixmap(updated_map)

    def page_1_up(self):
        # TODO Implement both sets of arrows properly
        print("page 1 up")

    def page_1_down(self):
        # TODO Implement both sets of arrows properly
        print("page 1 down")

    def page_1_left(self):
        # TODO Implement both sets of arrows properly
        print("page 1 left")

    def page_1_right(self):
        # TODO Implement both sets of arrows properly
        print("page 1 right")

    def zoom_in(self):
        # TODO Implement Zoom In
        print("Zoom In Pressed")

    def zoom_out(self):
        # TODO Implement Zoom Out
        print("Zoom Out Pressed")

    def publish_point(self, event):
        # TODO Implement Relative Point Calc Based on Zoom
        point_pub.publish(Point(event.x(), event.y(), 0))
        self.go_to_page_3()

    def page_2_up(self):
        # TODO Implement both sets of arrows properly
        print("page 2 up")

    def page_2_down(self):
        # TODO Implement both sets of arrows properly
        print("page 2 down")

    def page_2_left(self):
        # TODO Implement both sets of arrows properly
        print("page 2 left")

    def page_2_right(self):
        # TODO Implement both sets of arrows properly
        print("page 2 right")


if __name__ == "__main__":
    point_pub = rospy.Publisher("selected_point", Point, queue_size=10)
    rospy.init_node("gui_pub", anonymous=True)
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
