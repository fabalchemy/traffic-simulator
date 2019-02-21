import tkinter as tk
import random
from math import cos, sin

W, H = 500, 300
marge = 5000

class Map(tk.Canvas):
    def __init__(self, master, width, height, background):
        # Initialize a canvas
        tk.Canvas.__init__(self, master=master, width=width, height=height, background=background)
        self.configure(scrollregion=(-marge, -marge, marge, marge))
        self.create_rectangle(-50,-50,W-1, H-1, tags="container")

        # Enable scrolling with the mouse:
        self.bind("<ButtonPress-1>", self.scroll_start)
        self.bind("<B1-Motion>", self.scroll_move)

        # Keep track of the current scale to make correct operations when zoomed in or out
        self.current_scale = 1
        self.configure(xscrollincrement=1)
        self.configure(yscrollincrement=1)

    def scroll_start(self, event):
        # Save the current position of the map
        self.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        # Move the map accordingly to the new event position
        self.scan_dragto(event.x, event.y, gain=2)

    def zoom(self, event):
        # Zoom in if the user scrolls up, zoom out otherwise
        factor = 2 if event.delta < 0 else .5

        # Scale every object on the canvas by (factor)
        self.scale("all", 0,0 , factor, factor)
        self.current_scale *= factor
        marge = self.current_scale * 5000

        # Reconfiguration for the scrollbars
        self.configure(scrollregion=(-marge, -marge, marge, marge))
        x,y = self.canvasx(event.x), self.canvasy(event.y)

        self.xview_scroll(int(x*(factor-1)), "units")
        self.yview_scroll(int(y*(factor-1)), "units")

class Container(tk.Frame):
    def __init__(self, root):
        # Initialize a Frame
        tk.Frame.__init__(self, root)
        # Initialize the canvas representating the map
        self.map = Map(self, W, H, "SeaGreen2")
        self.map.create_rectangle(-50,-50,W-1, H-1, tags="container")

        # Setting up scrollbars to be able to move the map in the window
        self.xsb = tk.Scrollbar(self, orient="horizontal", command=self.map.xview)
        self.ysb = tk.Scrollbar(self, orient="vertical", command=self.map.yview)
        self.map.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)

        # Place the canvas and scrollbars in their correct positions
        # Using a grid system to sustain further modifications of the layout
        self.xsb.grid(row=1, column=0, sticky="ew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.map.grid(row=0, column=0, sticky="nsew")
        #
        # # Allows the canvas to expand as much as it can
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


# DEBUG: Fonctions pour tester le comportement
def clavier(event):
    global car_angle, a
    if event.char == "w":
        map.zoom(event)
    e = map.current_scale
    dist = 1
    if event.char == "z": #haut
        map.move("car", dist*e*cos(car_angle), -dist*e*sin(car_angle))
    if event.char == "s": #bas
        map.move("car", -dist*e*cos(car_angle), dist*e*sin(car_angle))
    if event.char == "q": #gauche
        map.move("car", -dist*e*sin(car_angle), -dist*e*cos(car_angle))
    if event.char == "d": #droite
        map.move("car", dist*e*sin(car_angle), dist*e*cos(car_angle))

    if event.char == "x":
        car_angle = 2*3.1415/random.randint(1, 10)
        dx = sin(car_angle)*w/2
        dy = cos(car_angle)*w/2
        dxb = l*cos(car_angle)
        dyb = l*sin(car_angle)
        print(x+dx, y+dy, x-dx, y-dy, x-dxb-dx, y+dyb-dy, x-dxb+dx, y+dyb+dy)
        map.coords(a, x+dx, y+dy, x-dx, y-dy, x-dxb-dx, y+dyb-dy, x-dxb+dx, y+dyb+dy)

    if event.char == " ":
        e = map.current_scale
        for n in range(50):
            x0 = random.randint(0, W-10) * e
            y0 = random.randint(0, H-10) * e
            x1 = x0 + random.randint(50, 100) * e
            y1 = y0 + random.randint(50,100) * e
            color = ("red", "orange", "yellow", "green", "blue")[random.randint(0,4)]
            map.create_rectangle(x0,y0,x1,y1, outline="grey26", fill=color)

def draw_cross(cross):
    (x,y) = cross.coords
    map.create_oval(x-2.5, y-2.5, x+2.5, y+2.5, fill="black")

def draw_road(road):
    (l, w) = (road.length, road.width)
    ang = road.angle
    (x,y) = road.cross1.coords
    dx = sin(ang)*w/2
    dy = cos(ang)*w/2
    dxb = l*cos(ang)
    dyb = l*sin(ang)
    a = map.create_polygon(x+dx, y+dy, x-dx, y-dy, x+dxb-dx, y-dyb-dy, x+dxb+dx, y-dyb+dy, fill="grey26", tag="road")
    # a = map.canvas.create_polygon(x+dx, y+dy, x-dx, y-dy, x-dxb-dx, y+dyb-dy, x-dxb+dx, y+dyb+dy, fill="black", tag="road")


# Create a window
root = tk.Tk()
# Create a map to display
container = Container(root)
# Put it inside the window
container.pack(fill="both", expand=True)

map = container.map

# DEBUG: Test pour afficher une voiture
# map.canvas.create_rectangle(10, 10, 10+5, 10+2, fill = "red", tag="car")
car_pos = (x,y) = (15,20)
car_angle = 3.1415/6 #rad
car_geom = (l, w) = (4, 2)

dx = sin(car_angle)*w/2
dy = cos(car_angle)*w/2
dxb = l*cos(car_angle)
dyb = l*sin(car_angle)
a = map.create_polygon(x+dx, y+dy, x-dx, y-dy, x-dxb-dx, y+dyb-dy, x-dxb+dx, y+dyb+dy, fill="red", tag="car")
#############

# Event-listeners
root.bind("<MouseWheel>", map.zoom)
root.bind("<KeyPress>", clavier)

def update():
    after(100, update())

def start():
    root.mainloop()
