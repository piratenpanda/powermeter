#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Benjamin Grimm-Lebsanft"
__copyright__ = "Copyright 2016, Benjamin Grimm-Lebsanft"
__license__ = "Public Domain"
__version__ = "1.2.0"
__email__ = "benjamin@lebsanft.org"
__status__ = "Production"

import serial, time, sys, random, matplotlib, decimal, logging, os
#import visa
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from decimal import *

### global data storage for later use in plots (1 day in seconds)

data1 = []
data2 = []
#rm = visa.ResourceManager('@py')
#list_of_insts = rm.list_resources()

### Real serial thread 1

class Worker(QObject):
    finished = pyqtSignal(float)

    def __init__(self):
        print("Serial thread init")
        super().__init__()
        self.ser = serial.Serial("/dev/ttyACM0", timeout=1, xonxoff=True)
        #if(len(list_of_insts)>=1):
            #self.my_test_inst = rm.open_resource(list_of_insts[0])


    def work(self):
        print("Worker work")
        while(True):
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.write(bytearray("pw?\r\n",'ascii'))
            power = self.ser.readline().decode("utf-8").lstrip().rstrip()
            powermW = float(power) * 1000            
            
            #response = self.my_test_inst.query('READ?').split(",")
            roundedpowermW = (float("{0:.6f}".format(powermW)))
            self.finished.emit(roundedpowermW)
            time.sleep(0.1)
			
class Worker2(QObject):
    finished2 = pyqtSignal(float)

    def __init__(self):
        print("Serial thread init")
        super().__init__()
        self.ser = serial.Serial("/dev/ttyACM0", timeout=1, xonxoff=True)

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
    loggingStopped = pyqtSignal(str)

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
        self.loggingStopped.emit("1")
        self.is_Logging = False

class MyMplCanvas(FigureCanvas):

    ### set matplotlib settings here

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.patch.set_alpha(0.0)
        self.axes = fig.add_subplot(111)

        ### We want the axes cleared every time plot() is called

        self.axes.hold(True)

        self.compute_initial_figure()

        ### init FigureCanvas

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Fixed,
                                   QSizePolicy.Fixed)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    display_length = 200
    ### use a QTimer to update the graph each second

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(10)


    ### plot data1 in red, max and min values used for y limits with a 10% offset.
    ### also the range can now be set dynamically.

    def update_figure(self):

        self.axes.plot(data1, 'r')
        self.axes.set_xlim(len(data1)-self.display_length,len(data1))
        #self.ymin = float(min(data1[len(data1)-self.display_length:len(data1)]))-0.1*min(data1[len(data1)-self.display_length:len(data1)])
        #self.ymax = float(max(data1[len(data1)-self.display_length:len(data1)]))+0.1*max(data2[len(data1)-self.display_length:len(data1)])
        #self.axes.set_ylim(self.ymin,self.ymax)        
        self.draw()

class MyDynamicMplCanvas2(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""


    display_length = 200
    ### use a QTimer to update the graph each second

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QTimer(self)
        timer.timeout.connect(self.update_figure2)
        timer.start(10)


    ### plot data1 in green, max and min values used for y limits with a 10% offset.
    ### also the range can now be set dynamically.

    def update_figure2(self):

        self.axes.plot(data2, 'g')
        self.axes.set_xlim(len(data2)-self.display_length,len(data2))
        self.ymin = float(min(data2[len(data2)-self.display_length:len(data2)]))-0.1*min(data2[len(data2)-self.display_length:len(data2)])
        self.ymax = float(max(data2[len(data2)-self.display_length:len(data2)]))+0.1*max(data2[len(data2)-self.display_length:len(data2)])
        self.axes.set_ylim(self.ymin,self.ymax)
        self.draw()

class Powermeter(QMainWindow):

    def __init__(self, parent=None):
        
        super(self.__class__, self).__init__()
        self.form_widget = UI(self) 
        self.setCentralWidget(self.form_widget)

        ### define a three decimal macro

        self.THREEPLACES = Decimal(10) ** -3
  
        ### create a new thread for power data from power meter 1

        self.getPowerThread = QThread()
        self.getPowerData = Worker()
        self.getPowerData.finished[float].connect(self.onDataReceived)
        self.getPowerData.moveToThread(self.getPowerThread)
        self.getPowerThread.started.connect(self.getPowerData.work)
        self.getPowerThread.start() 

        ### create a new thread for power data from power meter 2

        self.getPowerThread2 = QThread()
        self.getPowerData2 = DummySerial2()
        self.getPowerData2.finished2[float].connect(self.onDataReceived2)
        self.getPowerData2.moveToThread(self.getPowerThread2)
        self.getPowerThread2.started.connect(self.getPowerData2.work)
        self.getPowerThread2.start()       

    ### Slot to receive the "onDataReceived" signal from the power meter 1 power data thread.
    ### Writes received data into the first position of data1 and drops the last element to
    ### keep data1 always the same length. Sets the text of currentPowerLabel to the received
    ### value after setting it to three decimals using the THREEPLACES macro defined above.

    @pyqtSlot(float)
    def onDataReceived(self, powervalue):
        self.form_widget.currentPowerLabel.setText("Current Power 1: " + str(Decimal(powervalue).quantize(self.THREEPLACES)) + " mW")
        data1.append(powervalue)
        if(len(data1) >= 5000):
            del data1[0]

    ### Slot to receive the "onDataReceived2" signal from the power meter 2 power data thread.
    ### Writes received data into the first position of data2 and drops the last element to
    ### keep data2 always the same length. Sets the text of currentPowerLabel2 to the received 
    ### value after setting it to three decimals using the THREEPLACES macro defined above.

    @pyqtSlot(float)
    def onDataReceived2(self, powervalue2): 
        self.form_widget.currentPowerLabel2.setText("Current Power 2: " + str(Decimal(powervalue2).quantize(self.THREEPLACES)) + " mW")
        data2.append(powervalue2)
        if(len(data2) >= 5000):
            del data2[0]

class UI(QWidget):

    ### open file selector in folder only mode to select log file folder

    def getDirectoryButtonclicked(self):
        self.logFoldername.setText("Folder where logs will be saved: " + QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly))
        if(self.logFoldername.text() != "Folder where logs will be saved: " and self.logFoldername.text() != "Folder where logs will be saved: Not set yet"):
            self.logFoldername.setStyleSheet('color: green')

    def startLoggingButtonclicked(self):

        ### add error handling for unset log folder

        if(self.logFoldername.text() == "Folder where logs will be saved: Not set yet" or self.logFoldername.text() == "Folder where logs will be saved: "):
            MessageBox = QMessageBox.warning(self,"Error:","No logging folder set yet") 
            return None

        ### add error handling for unset log file name

        if(self.logFilename.text() == "Select a filename"):
            MessageBox = QMessageBox.warning(self,"Error:","No filename set yet") 
            return None

        ### if folder name and file name is set and logging is not active,
        ### start logging thread and set button label to "Stop logging"

        if(self.logActive.text() == "Logging: Not active" and self.logFoldername.text() != "Folder where logs will be saved: Not set yet" and self.logFoldername.text() != "Folder where logs will be saved: "):
            self.logActive.setText("Logging: Active")
            self.logActive.setStyleSheet('color: green')
            self.startLoggingButton.setText("Stop logging")

            self.LoggerThread = QThread()
            self.logger = Logger()
            self.logger.logging[str].connect(self.writeLog)
            self.logger.loggingStopped[str].connect(self.stopLog)
            self.logger.moveToThread(self.LoggerThread)
            self.LoggerThread.started.connect(self.logger.work)
            self.LoggerThread.start()

        ### if logging is active, stop logging thread and set button label to "Start logging"

        elif(self.logActive.text() == "Logging: Active"):
            self.logActive.setText("Logging: Not active")
            self.logger.stop()
            self.LoggerThread.quit()
            self.logActive.setStyleSheet('color: red')
            self.startLoggingButton.setText("Start logging")

    def __init__(self, parent):

        ### create tabbed interface
        super(UI, self).__init__(parent)
        tab_widget = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()
        tab_widget.addTab(tab1, "Main")
        tab_widget.addTab(tab2, "Advanced") 

        ### add label for power meter 1 power data

        self.currentPowerLabel = QLabel(self)
        self.currentPowerLabel.setAlignment(Qt.AlignLeft)
        self.currentPowerLabel.setStyleSheet('font-size: 20pt')

        ### add label for power meter 2 power data

        self.currentPowerLabel2 = QLabel(self)
        self.currentPowerLabel2.setAlignment(Qt.AlignLeft)
        self.currentPowerLabel2.setStyleSheet('font-size: 20pt')

        ### add QLineEdit for power meter 1 display length

        self.pm1DisplayLength = QLineEdit(self)
        self.pm1DisplayLength.setAlignment(Qt.AlignLeft)
        self.pm1DisplayLength.setText(str(MyDynamicMplCanvas.display_length))
        self.pm1DisplayLength.setInputMask("99999")
        self.pm1DisplayLength.setFixedWidth(100)
        self.pm1DisplayLength.textChanged.connect(self.setpm1DisplayLength)

        ### add QLineEdit for power meter 2 display length

        self.pm2DisplayLength = QLineEdit(self)
        self.pm2DisplayLength.setAlignment(Qt.AlignLeft)
        self.pm2DisplayLength.setText(str(MyDynamicMplCanvas2.display_length))
        self.pm2DisplayLength.setInputMask("99999")
        self.pm2DisplayLength.setFixedWidth(100)
        self.pm2DisplayLength.textChanged.connect(self.setpm2DisplayLength)

        ### add label for display lenght info 1

        self.pm1DisplayLengthLabel = QLabel(self)
        self.pm1DisplayLengthLabel.setAlignment(Qt.AlignLeft)
        self.pm1DisplayLengthLabel.setText("Number of seconds displayed: ")

        ### add label for display lenght info 2

        self.pm2DisplayLengthLabel = QLabel(self)
        self.pm2DisplayLengthLabel.setAlignment(Qt.AlignLeft)
        self.pm2DisplayLengthLabel.setText("Number of seconds displayed: ")

        ### add QLineEdit for log file name

        self.logFilename = QLineEdit(self)
        self.logFilename.setText("Select a filename")
        self.logFilename.textChanged.connect(self.setLogFilename)

        ### add QLabel for log file folder

        self.logFoldername = QLabel(self)
        self.logFoldername.setText("Folder where logs will be saved: Not set yet")
        self.logFoldername.setStyleSheet('color: red')

        ### add QLabel for log file activity display

        self.logActive = QLabel(self)
        self.logActive.setText("Logging: Not active")
        self.logActive.setStyleSheet('color: red')

        ### add QPushButton for folder selector

        self.getDirectoryButton = QPushButton(self)
        self.getDirectoryButton.setText("Set logging folder")
        self.getDirectoryButton.clicked.connect(self.getDirectoryButtonclicked)

        ### add QPushButton for logging start and stop

        self.startLoggingButton = QPushButton(self)
        self.startLoggingButton.setText("Start logging")
        self.startLoggingButton.clicked.connect(self.startLoggingButtonclicked)

        ### add MyDynamicMplCanvas for power display of power meter 1

        self.PowerPlot1 = MyDynamicMplCanvas(QWidget(self))

        ### add MyDynamicMplCanvas for power display of power meter 2

        self.PowerPlot2 = MyDynamicMplCanvas2(QWidget(self))
     
        ### create Layout

        left = QVBoxLayout()
        left.addWidget(self.currentPowerLabel, 0)
        left.addWidget(self.PowerPlot1, 1)

        displaysettings1 = QHBoxLayout()

        displaysettings1.addWidget(self.pm1DisplayLengthLabel, 1)
        displaysettings1.addWidget(self.pm1DisplayLength, 1, Qt.AlignLeft)

        left.addLayout(displaysettings1, 2)

        right = QVBoxLayout()
        right.addWidget(self.currentPowerLabel2, 0)
        right.addWidget(self.PowerPlot2, 1)

        displaysettings2= QHBoxLayout()

        displaysettings2.addWidget(self.pm2DisplayLengthLabel, 1)
        displaysettings2.addWidget(self.pm2DisplayLength, 1, Qt.AlignLeft)

        right.addLayout(displaysettings2, 2)

        top = QHBoxLayout()
        top.addLayout(left, 1)    # Both sides take the same amount of space.
        top.addLayout(right, 1)

        main = QVBoxLayout()
        main.addLayout(top,0)
        main.addWidget(self.logActive, 1)
        main.addWidget(self.logFilename, 2)
        main.addWidget(self.logFoldername, 3)
        main.addWidget(self.getDirectoryButton, 4, Qt.AlignLeft)
        main.addWidget(self.startLoggingButton, 5, Qt.AlignLeft)


        ### put widgets into the QFormLayout of tab2 here
		


        ### set window title and add tab widget to main window

        self.setWindowTitle("Power meter")
        vbox = QVBoxLayout()
        vbox.addWidget(tab_widget)
        self.setLayout(main) 

    def setpm1DisplayLength(self, *args, **kwargs):

        if (self.pm1DisplayLength.text() == "" or int(self.pm1DisplayLength.text()) == 0):
            setlength = len(data1)
            self.pm1DisplayLength.setText(str(len(data1)))
        else:
            setlength = self.pm1DisplayLength.text()
        
        MyDynamicMplCanvas.display_length = int(setlength)

    def setpm2DisplayLength(self, *args, **kwargs):
        
        if (self.pm2DisplayLength.text() == "" or int(self.pm2DisplayLength.text()) == 0):
            setlength = len(data2)
            self.pm2DisplayLength.setText(str(len(data2)))
        else:
            setlength = self.pm2DisplayLength.text()
        
        MyDynamicMplCanvas2.display_length = int(setlength)

    def setLogFilename(self, *args, **kwargs):
        self.logfilename = self.logFilename.text()

    ### Slot to receive the "go" signal from the logging thread and write log file

    @pyqtSlot(str)
    def writeLog(self, logvalues):
        log = self.logFoldername.text()[33:] + "/" + self.logfilename
        logging.basicConfig(filename=log,level=logging.DEBUG,filemode="w+", format='%(asctime)s,%(message)s', datefmt='%d.%m.%Y - %H:%M:%S')
        logging.info(self.currentPowerLabel.text()[17:] + "," + self.currentPowerLabel2.text()[17:])

    ### Slot to receive the "stop" signal from the logging thread and stop all active loggers

    @pyqtSlot(str)
    def stopLog(self, logvalues):
        log = logging.getLogger()
        for hdlr in log.handlers:  # remove all old handlers
            log.removeHandler(hdlr)

def main():
    app = QApplication(sys.argv)
    Interface = Powermeter()
    Interface.show()
    Interface.setFixedSize(Interface.size());
    app.exec_()

if __name__ == "__main__":
    main()
