#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Benjamin Grimm-Lebsanft"
__copyright__ = "Copyright 2016, Benjamin Grimm-Lebsanft"
__license__ = "Public Domain"
__version__ = "1.0.1"
__email__ = "benjamin@lebsanft.org"
__status__ = "Production"

import serial, time, sys, random, matplotlib, decimal, logging, os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from decimal import *

### global data variables for later use in plots

data1 = [0] * 600
data2 = [0] * 600


### Real serial thread 1

class Worker(QObject):
    finished = pyqtSignal(float)

    def __init__(self):
        print("Serial thread init")
        super().__init__()
        self.ser = serial.Serial("COM6", timeout=1, xonxoff=True)

    def work(self):
        print("Worker work")
        while(True):
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.write(bytearray("pw?\r\n",'ascii'))
            power = self.ser.readline().decode("utf-8").lstrip().rstrip()
            powermW = float(power) * 1000
            roundedpowermW = (float("{0:.3f}".format(powermW)))
            self.finished.emit(roundedpowermW)
			
class Worker2(QObject):
    finished2 = pyqtSignal(float)

    def __init__(self):
        print("Serial thread init")
        super().__init__()
        self.ser = serial.Serial("COM7", timeout=1, xonxoff=True)

    def work(self):
        print("Worker work")
        while(True):
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.write(bytearray("pw?\r\n",'ascii'))
            power = self.ser.readline().decode("utf-8").lstrip().rstrip()
            powermW = float(power) * 1000
            roundedpowermW = (float("{0:.3f}".format(powermW)))
            self.finished2.emit(roundedpowermW)


### Dummy serial thread 1

class DummySerial1(QObject):
    finished = pyqtSignal(float)

    def __init__(self):
        print("Dummy serial thread 1 init")
        super().__init__()

    def work(self):
        print("Dummy serial 1 working")
        while(True):
            roundedpowermW = (float("{0:.3f}".format(random.random())))
            self.finished.emit(roundedpowermW)
            time.sleep(1)

### Dummy serial thread 2

class DummySerial2(QObject):
    finished2 = pyqtSignal(float)

    def __init__(self):
        print("Dummy serial thread 2 init")
        super().__init__()


    def work(self):
        print("Dummy serial 2 working")
        while(True):
            roundedpowermW = (float("{0:.3f}".format(random.random())))
            self.finished2.emit(roundedpowermW)
            time.sleep(1)

### Logging thread

class Logger(QObject):
    logging = pyqtSignal(str)

    def __init__(self):
        print("Logging thread init")
        super().__init__()
        self.is_Logging = True

    def work(self):
        print("Logger working")
        while(self.is_Logging):
            self.logging.emit("1")
            time.sleep(1)

    def stop(self):
        print("Logger stopping")
        self.is_Logging = False

class MyMplCanvas(FigureCanvas):

    ### set matplotlib settings here

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.patch.set_alpha(0.0)
        self.axes = fig.add_subplot(111)

        ### We want the axes cleared every time plot() is called

        self.axes.hold(False)

        ### We want the axes background to be non intrusive

        self.axes.set_alpha(0)

        self.compute_initial_figure()

        ### init FigureCanvas

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    ### use a QTimer to update the graph each second

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    ### plot data1 in red

    def update_figure(self):

        self.axes.plot(data1, 'r')
        self.draw()

class MyDynamicMplCanvas2(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    ### use a QTimer to update the graph each second

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QTimer(self)
        timer.timeout.connect(self.update_figure2)
        timer.start(1000)

    ### plot data1 in green

    def update_figure2(self):

        self.axes.plot(data2, 'g')
        self.draw()

class Powermeter(QMainWindow):

    def __init__(self, parent=None):
        
        super(self.__class__, self).__init__()
        self.form_widget = UI(self) 
        self.setCentralWidget(self.form_widget)

        ### define a three decimal macro

        self.THREEPLACES = Decimal(10) ** -3
  
        ### create a new thread for power data from power meter 2

        self.getPowerThread = QThread()
        self.getPowerData = Worker()
        self.getPowerData.finished[float].connect(self.onDataReceived)
        self.getPowerData.moveToThread(self.getPowerThread)
        self.getPowerThread.started.connect(self.getPowerData.work)
        self.getPowerThread.start() 

        ### create a new thread for power data from power meter 2

        self.getPowerThread2 = QThread()
        self.getPowerData2 = Worker2()
        self.getPowerData2.finished2[float].connect(self.onDataReceived2)
        self.getPowerData2.moveToThread(self.getPowerThread2)
        self.getPowerThread2.started.connect(self.getPowerData2.work)
        self.getPowerThread2.start()       

    ### Slot to receive the "onDataReceived" signal from the power meter 1 power data thread.
    ### Writes recieved data into the first position of data1 and drops the last element to
    ### keep data1 always the same length. Sets the text of currentPowerLabel to the received
    ### value after setting it to three decimals using the THREEPLACES macro defined above.

    @pyqtSlot(float)
    def onDataReceived(self, powervalue):
        self.form_widget.currentPowerLabel.setText("Current Power 1: " + str(Decimal(powervalue).quantize(self.THREEPLACES)) + " mW")
        data1.append(powervalue)
        del data1[0]

    ### Slot to receive the "onDataReceived2" signal from the power meter 2 power data thread.
    ### Writes recieved data into the first position of data2 and drops the last element to
    ### keep data2 always the same length. Sets the text of currentPowerLabel2 to the received 
    ### value after setting it to three decimals using the THREEPLACES macro defined above.

    @pyqtSlot(float)
    def onDataReceived2(self, powervalue2): 
        self.form_widget.currentPowerLabel2.setText("Current Power 2: " + str(Decimal(powervalue2).quantize(self.THREEPLACES)) + " mW")
        data2.append(powervalue2)
        del data2[0]

class UI(QWidget):

    ### open file selector in folder only mode to select log file folder

    def getDirectoryButtonclicked(self):
        self.logFoldername.setText("Folder where logs will be saved: " + QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly))

    def startLoggingButtonclicked(self):

        ### add error handling for unset log folder

        if(self.logFoldername.text() == "Folder where logs will be saved: Not set yet"):
            MessageBox = QMessageBox.warning(self,"Error:","No logging folder set yet") 
            return None

        ### add error handling for unset log file name

        if(self.logFilename.text() == "Select a filename"):
            MessageBox = QMessageBox.warning(self,"Error:","No filename set yet") 
            return None

        ### if folder name and file name is set and logging is not active,
        ### start logging thread and set button label to "Stop logging"

        if(self.logActive.text() == "Logging: Not active" and self.logFoldername.text() != "Folder where logs will be saved: Not set yet"):
            self.logActive.setText("Logging: Active")
            self.startLoggingButton.setText("Stop logging")

            self.LoggerThread = QThread()
            self.logger = Logger()
            self.logger.logging[str].connect(self.writeLog)
            self.logger.moveToThread(self.LoggerThread)
            self.LoggerThread.started.connect(self.logger.work)
            self.LoggerThread.start()

        ### if logging is active, stop logging thread and set button label to "Start logging"

        elif(self.logActive.text() == "Logging: Active"):
            self.logger.stop()
            self.logActive.setText("Logging: Not active")
            self.startLoggingButton.setText("Start logging")

    def __init__(self, parent):

        ### create tabbed interface
        super(UI, self).__init__(parent)
        tab_widget = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()
        p1_vertical = QFormLayout(tab1)
        p2_vertical = QFormLayout(tab2)
        tab_widget.addTab(tab1, "Main")
        tab_widget.addTab(tab2, "Advanced") 

        ### add label for power meter 1 power data

        self.currentPowerLabel = QLabel(self)
        self.currentPowerLabel.setAlignment(Qt.AlignLeft)

        ### add label for power meter 2 power data

        self.currentPowerLabel2 = QLabel(self)
        self.currentPowerLabel2.setAlignment(Qt.AlignLeft)

        ### add QLineEdit for log file name

        self.logFilename = QLineEdit(self)
        self.logFilename.setText("Select a filename")

        ### add QLabel for log file folder

        self.logFoldername = QLabel(self)
        self.logFoldername.setText("Folder where logs will be saved: Not set yet")

        ### add QLabel for log file activity display

        self.logActive = QLabel(self)
        self.logActive.setText("Logging: Not active")

        ### add QPushButton for folder selector

        self.getDirectoryButton = QPushButton(self)
        self.getDirectoryButton.setText("Set logging folder")
        self.getDirectoryButton.clicked.connect(self.getDirectoryButtonclicked)

        ### add QPushButton for logging start and stop

        self.startLoggingButton = QPushButton(self)
        self.startLoggingButton.setText("Start logging")
        self.startLoggingButton.clicked.connect(self.startLoggingButtonclicked)

        ### add MyDynamicMplCanvas for power display of power meter 1

        self.PowerPlot1 = QWidget(self)
        l = QVBoxLayout(self.PowerPlot1)
        dc = MyDynamicMplCanvas(self.PowerPlot1)
        l.addWidget(dc)

        ### add MyDynamicMplCanvas for power display of power meter 2

        self.PowerPlot2 = QWidget(self)
        l2 = QVBoxLayout(self.PowerPlot2)
        dc2 = MyDynamicMplCanvas2(self.PowerPlot2)
        l2.addWidget(dc2)
     
        ### put widgets into the QFormLayout of tab1 here

        p1_vertical.addRow(self.currentPowerLabel, self.currentPowerLabel2)
        p1_vertical.addRow(self.PowerPlot1, self.PowerPlot2)
        p1_vertical.addRow(self.logActive)
        p1_vertical.addRow(self.logFoldername,self.getDirectoryButton)
        p1_vertical.addRow(self.logFilename,self.startLoggingButton)

        ### put widgets into the QFormLayout of tab2 here
		


        ### set window title and add tab widget to main window

        self.setWindowTitle("Power meter")
        vbox = QVBoxLayout()
        vbox.addWidget(tab_widget)
        self.setLayout(vbox) 

    ### Slot to receive the "go" signal from the logging thread and write log file

    @pyqtSlot(str)
    def writeLog(self, logvalues):
        log = self.logFoldername.text()[33:] + "/" + self.logFilename.text()
        logging.basicConfig(filename=log,level=logging.DEBUG,filemode="w+", format='%(asctime)s,%(message)s', datefmt='%d.%m.%Y - %H:%M:%S')
        logging.info(self.currentPowerLabel.text()[17:] + "," + self.currentPowerLabel2.text()[17:])

def main():
    app = QApplication(sys.argv)
    Interface = Powermeter()
    Interface.show()
    Interface.setFixedSize(Interface.size());
    app.exec_()

if __name__ == "__main__":
    main()
