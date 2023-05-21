import mouse
import json
import threading
import sys
from datetime import datetime
from time import sleep

from tkinter import *
import tkinter as tk
from tkinter import ttk

# image manipulation and template matching
from PIL import ImageGrab, ImageOps
import cv2

# system tray
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

END = False



# infinite loop that breaks when END = True
def main(cfg):
    
    maxSpeed = cfg["maxSpeed"]
    while not END:
        now = datetime.now().second
        find(cfg)
        # prevents loop from occuring more than maxSpeed
        now2 = datetime.now().second
        dif = abs(now - now2)
        if dif < maxSpeed:
            sleep(maxSpeed - dif)


# loads json and places in config object then returns
def loadConfig():
    f = open("settings.json")
    config = json.load(f)
    return config


def find(config):
    # Takes screenshots makes it grayscale and saves
    img = ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=False, xdisplay=None)
    modImg = ImageOps.grayscale(img)
    modImg.save("screen.png")

    # loads images
    img = cv2.imread('screen.png')
    template = cv2.imread('skip.png')
    temp2 = None
    if config["doubleCheck"]:
        temp2 = cv2.imread('skip2.png')
    h, w = template.shape[:2]

    found = None

    # loops through each size and checks for template(s) skip button(s)
    for size in config["sizes"]:
        width = int(img.shape[1] * size)
        height = int(img.shape[0] * size)
        dim = (width, height)
        resized = cv2.resize(img, dim)
        r = img.shape[1] / float(resized.shape[1])

        if resized.shape[0] < h or resized.shape[1] < w:
            break

        res = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)

        _, maxVal, _, maxLoc = cv2.minMaxLoc(res)

        if config["doubleCheck"]:
            res2 = cv2.matchTemplate(resized, temp2, cv2.TM_CCOEFF_NORMED)
            _, maxVal2, _, maxLoc2 = cv2.minMaxLoc(res2)
            if maxVal2 > maxVal:
                maxVal, maxLoc = maxVal2, maxLoc2

        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)

    maxVal, maxLoc, r = found

    # if maxVal is greater than threshold move mouse to middle of button and click
    if maxVal >= config["threshold"]:
        startX, startY = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        endX, endY = (int((maxLoc[0] + w) * r), int((maxLoc[1] + h) * r))

        if config["mouseReturn"]:
            old = mouse.get_position()
            mouse.move((startX + endX) / 2, (startY + endY) / 2)
            mouse.click()
            mouse.move(old[0], old[1])
        else:
            mouse.move((startX + endX) / 2, (startY + endY) / 2)
            mouse.click()

        cv2.rectangle(img, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv2.imwrite('result.png', img)


# ends
def end():
    global END
    END = True
    sys.exit()


if __name__ == "__main__":
    cfg = loadConfig()

    if cfg["systemTray"]:
        app = QApplication([])
        app.setQuitOnLastWindowClosed(False)
        app.setFont(QFont("Arial"))

        # Adding an icon
        icon = QIcon("icon.png")

        # Adding item on the menu bar
        tray = QSystemTrayIcon()
        tray.setIcon(icon)
        tray.setVisible(True)

        # Creating the options
        menu = QMenu()
        menu.setFont(QFont("Arial", 12))
        quit = QAction("Quit")
        quit.triggered.connect(end)
        menu.addAction(quit)

        # Adding options to the System Tray
        tray.setContextMenu(menu)

        thread = threading.Thread(target=main, args=[cfg])
        thread.start()

        app.exec()
    else:
        main(cfg)

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master

# initialize tkinter
root = Tk()
app = Window(root)

# set window title
root.wm_title("Youtube skip adder ")


exit_button = ttk.Button(
    root,
    text='Exit',
    command=lambda: root.quit()
)

exit_button.pack(
    ipadx=5,
    ipady=5,
    expand=True
)
exit_button = ttk.Button(
    root,
    text='Exit',
    command=lambda: root.quit()
)

btn = Button(root, text = 'Click me !', bd = '5', command = root.destroy)
btn.pack(side = 'top')
button=Button(root, text="start", command =lambda: main)
button.pack()
# show window
root.mainloop()
