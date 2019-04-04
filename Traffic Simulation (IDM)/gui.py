import tkinter as tk
from math import cos, sin, atan, sqrt

W, H = 4000, 2500
marge = 5000
dx,dy = 20,20 # Elementary move for the canvas


class Map(tk.Canvas):
    def __init__(self, master, width, height, background):
        # Initialize a canvas
        tk.Canvas.__init__(self, master=master, width=width, height=height, background=background)
        self.configure(scrollregion=(-marge, -marge, marge, marge))
        self.configure(xscrollincrement=1)
        self.configure(yscrollincrement=1)
        self.create_rectangle(-50,-50,W-1, H-1, tags="container")

        # Keep track of the current scale to make correct operations when zoomed in or out
        self.current_scale = 1

    def scroll_start(self, event):
        # Save the current position of the map
        self.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        # Move the map accordingly to the new event position
        self.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, event):
        # Zoom in if the user scrolls up, zoom out otherwise
        factor = 0
        if event.delta > 0 or event.keysym == "Up":
            factor = 2
        elif event.delta < 0 or event.keysym == "Down":
            factor = .5

        # Scale every object on the canvas by (factor)
        self.scale("all", 0,0 , factor, factor)
        self.current_scale *= factor
        marge = self.current_scale * 5000

        # Reconfiguration for the scrollbars
        self.configure(scrollregion=(-marge, -marge, marge, marge))
        x,y = self.canvasx(event.x), self.canvasy(event.y)

        self.xview_scroll(int(x*(factor-1)), "units")
        self.yview_scroll(int(y*(factor-1)), "units")

    def draw_cross(self, cross_list):
        for cross in cross_list:
            (x,y) = cross.coords
            self.create_oval(x-2.5, y-2.5, x+2.5, y+2.5, fill="grey20", outline = "grey30", tag="cross")

    def draw_road(self, road_list):
        for road in road_list:
            (l, w) = (road.length, road.width)
            ang = road.angle
            (x,y) = road.cross2.coords
            dx = sin(ang)*w/2
            dy = - cos(ang)*w/2
            dxb = -l*cos(ang)
            dyb = -l*sin(ang)
            self.create_polygon(x+dx, y+dy, x-dx, y-dy, x+dxb-dx, y+dyb-dy, x+dxb+dx, y+dyb+dy, fill="grey20", tag="road")

    def draw_vehicle(self, vehicle_list):
        for veh in vehicle_list:
            (x0,y0) = veh.origin_cross.coords
            road_width = veh.road.width
            (l, w) = (veh.length, veh.width)
            angle = veh.road.angle if (veh.origin_cross==veh.road.cross1) else (veh.road.angle + 3.1415)
            x = x0 - road_width/4 *sin(angle) + (veh.x+veh.length/2)*cos(angle)
            y = y0 + road_width/4 *cos(angle) + (veh.x+veh.length/2)*sin(angle)

            e = self.current_scale
            x = x*e
            y = y*e
            dx = sin(angle)*w/2 *e
            dy = - cos(angle)*w/2 *e
            dxb = - l*cos(angle) *e
            dyb = - l*sin(angle) *e

            points = (x+dx, y+dy, x-dx, y-dy, x+dxb-dx, y+dyb-dy, x+dxb+dx, y+dyb+dy)
            if veh.rep == None :
                veh.rep = self.create_polygon(points, fill="red", tag="car")
            else:
                self.coords(veh.rep, points)

            if veh.v < 10/3.6:
                self.itemconfig(veh.rep, fill="steel blue")
            elif veh.v < 20/3.6:
                self.itemconfig(veh.rep, fill="cyan")
            elif veh.v < 30/3.6:
                self.itemconfig(veh.rep, fill="yellow")
            elif veh.v < 40/3.6:
                self.itemconfig(veh.rep, fill="orange")
            else:
                self.itemconfig(veh.rep, fill="red")

class Container(tk.Frame):
    def __init__(self, root):
        # Initialize a Frame
        tk.Frame.__init__(self, root)
        # Initialize the canvas representating the map
        self.map = Map(self, W, H, "#78e08f")
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

        # Allows the canvas to expand as much as it can
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

class Controls(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.time_mgmt = tk.LabelFrame(self, text="Time managment", padx=10, pady= 10)
        self.time_mgmt.pack()

        self.time_str = tk.StringVar()
        self.time_str.set("Current time : 0 s.")
        tk.Label(master = self.time_mgmt, textvariable = self.time_str).pack()
        self.speed = tk.Scale(self.time_mgmt, label="Simulation speed", from_=0, to=30, resolution=0.1, orient=tk.HORIZONTAL, length=200)
        self.speed.set(1)
        self.speed.pack(fill="both", expand="yes")
        self.play = tk.BooleanVar()
        self.play.set(True)
        self.play_b = tk.Radiobutton(self.time_mgmt, text="Play", variable=self.play, value=True)
        self.pause_b = tk.Radiobutton(self.time_mgmt, text="Pause", variable=self.play, value=False)
        self.play_b.pack(side=tk.LEFT)
        self.pause_b.pack(side=tk.LEFT)


        self.information = tk.LabelFrame(self, text="Information", padx=10, pady=10)
        self.information.pack()
        tk.Label(master = self.information, text = "Nombre de véhicules : ").grid(row = 0, column = 0)
        self.nb_veh = tk.IntVar()
        self.nb_veh.set(0)
        tk.Label(master = self.information, textvariable = self.nb_veh).grid(row = 0, column = 1)
        self.avg_speed = tk.StringVar()
        self.avg_speed.set("0")
        tk.Label(master = self.information, text="Vitesse moyenne : ").grid(row = 1, column = 0)
        tk.Label(master = self.information, textvariable = self.avg_speed).grid(row = 1, column = 1)

def keyboard_listener(event):
    if event.char == " ":
        controls.play.set(False) if controls.play.get() else controls.play.set(True)

    elif event.keysym == "Right":
        map.scan_mark(0,0)
        map.scan_dragto(-dx,0)

    elif event.keysym == "Left":
        map.scan_mark(0,0)
        map.scan_dragto(dx,0)

    elif event.keysym == "Up":
        map.scan_mark(0,0)
        map.scan_dragto(0,dy)

    elif event.keysym == "Down":
        map.scan_mark(0,0)
        map.scan_dragto(0,-dy)

root = tk.Tk()
root.state('zoomed')
container = Container(root)
container.grid(row=0, column=0, sticky="nsew")
map = container.map
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

controls = Controls(root)
controls.grid(row=0, column=1, sticky="ne")

# Event-listeners
root.bind("<KeyPress>", keyboard_listener)
map.bind("<ButtonPress-1>", map.scroll_start)
map.bind("<B1-Motion>", map.scroll_move)
map.bind("<MouseWheel>", map.zoom)
root.bind("<Control-Key>", map.zoom)
