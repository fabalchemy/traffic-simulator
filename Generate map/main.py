import tkinter as tk
from PIL import Image, ImageTk
from math import cos, sin, atan, sqrt

print("CHECK IMAGE ADRESS !!")
map_address = "map.png"
image = Image.open(map_address)

W, H = image.size
marge = 5000
dx,dy = 20,20 # Elementary move for the canvas

cross_list = []
generator_cross_list = []
road_coords_list = []

root = tk.Tk()
bg_map = ImageTk.PhotoImage(image)

def angle(x,y):
    """Give the oriented angle [-3.14 ; +3.14] between the vector (x,y) and the horizontal axis (1,0)"""
    # The y-axis is "reversed" in Tkinter !
    # We use vector product to find the orientation of the vectors
    sign = 1 if y >= 0 else -1
    # We use scalar product to find the angle and multiply it by the orientation
    return acos((x) / sqrt(x*x + y*y)) * sign

def distance(c1,c2):
    return float(((cross_list[c2][0]-cross_list[c1][0])**2 + (cross_list[c2][1]-cross_list[c1][1])**2)**0.5)


class Map(tk.Canvas):
    def __init__(self, master, width, height, background):
        # Initialize a canvas
        global bg_map

        tk.Canvas.__init__(self, master=master, width=width, height=height, background=background)
        self.create_image(0,0, anchor = tk.NW, image = bg_map)
        self.configure(scrollregion=(-marge, -marge, marge, marge))
        self.configure(xscrollincrement=1)
        self.configure(yscrollincrement=1)
        self.create_rectangle(0,0,W-1, H-1, tags="container")

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

    def draw_cross(self, x,y, build_type):
        if build_type == 1:
            self.create_oval(x-2.5, y-2.5, x+2.5, y+2.5, fill="grey26", outline = "grey26", tag="cross")
        elif build_type == 2:
            self.create_oval(x-2.5, y-2.5, x+2.5, y+2.5, fill="red", outline = "red", tag="generator_cross")

    def draw_road(self, road):
        (l, w) = (distance, 5)
        ang = road.angle
        (x,y) = road.cross2.coords
        dx = sin(ang)*w/2
        dy = - cos(ang)*w/2
        dxb = -l*cos(ang)
        dyb = -l*sin(ang)
        self.create_polygon(x+dx, y+dy, x-dx, y-dy, x+dxb-dx, y+dyb-dy, x+dxb+dx, y+dyb+dy, fill="grey26", tag="road")

    def create_object(self,event):
        x,y = self.canvasx(event.x), self.canvasy(event.y)
        if controls.build_type == 1:
            cross_list.append((x,y))
            self.draw_cross(x,y, controls.build_type)
        elif controls.build_type == 2:
            cross_list.append((x,y))
            self.draw_cross(x,y, controls.build_type)
        elif controls.build_type == 3:
            self.draw_road(x,y)

class Container(tk.Frame):
    def __init__(self, root):
        # Initialize a Frame
        tk.Frame.__init__(self, root)
        # Initialize the canvas representating the map
        self.map = Map(self, W, H, "SeaGreen1")
        self.map.create_rectangle(0,0,W-1, H-1, tags="container")

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
        self.creation_menu = tk.LabelFrame(self, text="Creation menu", padx=10, pady= 10)
        self.creation_menu.pack()


        self.build_type = tk.IntVar()
        self.build_type.set(1)
        self.cross_b = tk.Radiobutton(self.creation_menu, text="Cross", variable=self.build_type, value=1)
        self.generator_cross_b = tk.Radiobutton(self.creation_menu, text="Cross", variable=self.build_type, value=2)
        self.road_b = tk.Radiobutton(self.creation_menu, text="Road", variable=self.build_type, value=3)
        self.cross_b.pack(side=tk.LEFT)
        self.generator_cross_b.pack(side=tk.LEFT)
        self.road_b.pack(side=tk.LEFT)


        self.information = tk.LabelFrame(self, text="Information", padx=10, pady=10)
        self.information.pack()
        tk.Label(master = self.information, text = "Nombre de croisements : ").grid(row = 0, column = 0)
        self.nb_cross = tk.IntVar()
        self.nb_cross.set(0)
        tk.Label(master = self.information, textvariable = self.nb_cross).grid(row = 0, column = 1)
        self.nb_roads = tk.IntVar()
        self.nb_roads.set(0)
        tk.Label(master = self.information, text="Nombre de routes : ").grid(row = 1, column = 0)
        tk.Label(master = self.information, textvariable = self.nb_roads).grid(row = 1, column = 1)

def keyboard_listener(event):
    if event.char == " ":
        controls.build_type.set(False) if controls.build_type.get() else controls.build_type.set(True)

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
map.bind("<Double-Button-1>", map.create_object)
map.bind("<MouseWheel>", map.zoom)
root.bind("<Control-Key>", map.zoom)



root.mainloop()
