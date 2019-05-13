import tkinter as tk
from PIL import Image, ImageTk
from math import cos, sin, atan, sqrt, acos

map_filename = "maps/map0.png"
image = Image.open(map_filename)

W, H = image.size
margin = 5000
dx,dy = 20,20 # Elementary move for the canvas

cross_list = []
generator_cross_list = []
road_coords_list = []

root = tk.Tk()

def angle(x,y):
    """Give the oriented angle [-3.14 ; +3.14] between the vector (x,y) and the horizontal axis (1,0)"""
    # The y-axis is "reversed" in Tkinter !
    # We use vector product to find the orientation of the vectors
    sign = 1 if y >= 0 else -1
    # We use scalar product to find the angle and multiply it by the orientation
    return acos((x) / sqrt(x*x + y*y)) * sign

def distance(x1,y1, x2, y2):
    return ((x2-x1)**2 + (y2-y1)**2)**0.5


class Map(tk.Canvas):
    def __init__(self, master, width, height, background):
        # Initialize a canvas
        tk.Canvas.__init__(self, master=master, width=width, height=height, background=background)
        # Keep track of the current scale to make correct operations when zoomed in or out
        self.current_scale = 1
        self.orig_img = image
        self.bg = None
        self.redraw_bg()
        self.configure(scrollregion=(-margin, -margin, margin, margin))
        self.configure(xscrollincrement=1)
        self.configure(yscrollincrement=1)
        self.create_rectangle(0,0,W-1, H-1, tags="container")

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
        self.current_scale *= factor
        self.redraw_bg(self.canvasx(event.x), self.canvasy(event.y))
        self.scale("all", 0,0 , factor, factor)
        margin = self.current_scale * 5000

        # Reconfiguration for the scrollbars
        self.configure(scrollregion=(-margin, -margin, margin, margin))
        x,y = self.canvasx(event.x), self.canvasy(event.y)


        self.xview_scroll(int(x*(factor-1)), "units")
        self.yview_scroll(int(y*(factor-1)), "units")

    def redraw_bg(self, x=0, y=0):
        if self.bg: self.delete(self.bg)
        w, h = self.orig_img.size
        s = self.current_scale

        tmp = self.orig_img.crop((0,0, w, h))
        self.img = ImageTk.PhotoImage(tmp.resize((int(w*s),int(h*s))))
        self.bg = self.create_image(0,0, image=self.img, anchor="nw", tag = "bg")
        self.tag_lower("bg", "all")

    def draw_cross(self, x, y, build_type):
        radius = 10 * self.current_scale
        if build_type == "cross":
            a = self.create_oval(x-radius, y-radius, x+radius, y+radius, fill="grey26", outline = "grey26", tag="cross")
        elif build_type == "generator":
            a = self.create_oval(x-radius, y-radius, x+radius, y+radius, fill="grey26", outline = "red", tag="generator")
        return a

    def draw_road(self, road):
        (l, w) = (distance(road.cross1.x, road.cross1.y, road.cross2.x, road.cross2.y), 5)
        ang = angle(road.cross2.x-road.cross1.x, road.cross2.y-road.cross1.y)
        s = self.current_scale
        (x,y) = road.cross2.x*s, road.cross2.y*s
        dx = s*sin(ang)*w/2
        dy = - s*cos(ang)*w/2
        dxb = -s*l*cos(ang)
        dyb = -s*l*sin(ang)
        return self.create_polygon(x+dx, y+dy, x-dx, y-dy, x+dxb-dx, y+dyb-dy, x+dxb+dx, y+dyb+dy, fill="grey26", tag="road")


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
        self.creation_menu = tk.LabelFrame(self, text="Creation menu", padx=5, pady=5)
        self.creation_menu.grid(row=0, column=0, sticky="new")

        self.build_type = tk.StringVar()
        self.build_type.set("generator")
        self.cross_b = tk.Radiobutton(self.creation_menu, text="Generator", variable=self.build_type, value="generator")
        self.generator_cross_b = tk.Radiobutton(self.creation_menu, text="Cross", variable=self.build_type, value="cross")
        self.road_b = tk.Radiobutton(self.creation_menu, text="Road", variable=self.build_type, value="road")
        self.priority_axis_b = tk.Radiobutton(self.creation_menu, text="Priority", variable = self.build_type, value="priority")
        self.cross_b.grid(row=0, column=0)
        self.generator_cross_b.grid(row=0, column=1)
        self.road_b.grid(row=0, column=2)
        self.priority_axis_b.grid(row=1, column=1)

        self.generate_b = tk.Button(self.creation_menu, text="Extract data !", command=extract_data)
        self.generate_b.grid(row=2, column=1)

        self.information = tk.LabelFrame(self, text="Information", padx=5, pady=5)
        self.information.grid(row=1, column=0, sticky="new")

        tk.Label(master = self.information, text = "Nombre de croisements : ").grid(row=0, column=0)
        self.nb_cross = tk.IntVar()
        self.nb_cross.set(0)
        tk.Label(master = self.information, textvariable = self.nb_cross).grid(row=0, column=1)
        self.nb_roads = tk.IntVar()
        self.nb_roads.set(0)
        tk.Label(master = self.information, text="Nombre de routes : ").grid(row=1, column=0)
        tk.Label(master = self.information, textvariable = self.nb_roads).grid(row=1, column=1)

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


class Cross:
    list = []
    def __init__(self, x, y, rep):
        self.x = x
        self.y = y
        self.rep = rep
        self.roads = []
        self.priority_axis = []
        Cross.list.append(self)
class Generator:
    list = []
    def __init__(self, x, y, rep):
        self.x = x
        self.y = y
        self.rep = rep
        self.roads = []
        self.priority_axis = []
        Generator.list.append(self)
class Road:
    list = []
    def __init__(self, cross1, cross2, rep):
        self.cross1 = cross1
        self.cross2 = cross2
        self.priority_indicator_1 = None
        self.priority_indicator_2 = None
        self.rep = rep
        Road.list.append(self)


selected_cross = []
cross_for_priority = None
real_cross_priority = None
selected_roads = []

def selector(event):
    """Take the correct action according to the user input"""
    global cross_for_priority, real_cross_priority, selected_roads
    x,y = map.canvasx(event.x), map.canvasy(event.y)
    s = map.current_scale
    objects = list(map.find_overlapping(x, y, x, y))
    for obj in objects:
        if "bg" in map.gettags(obj):
            objects.remove(obj)
    print(objects)
    mode = controls.build_type.get()

    if mode == "cross" or mode == "generator":
        if len(objects) == 0:
            if controls.build_type.get() == "generator":
                Generator(x//s,y//s, map.draw_cross(x,y, "generator"))
            elif controls.build_type.get() == "cross":
                Cross(x//s, y//s, map.draw_cross(x,y, "cross"))
            controls.nb_cross.set(controls.nb_cross.get()+1)

        if len(objects) == 1:
            obj = objects[0]
            tags = map.gettags(obj)
            print(tags)
            if "cross" in tags :
                for c in Cross.list:
                    if c.rep == obj:
                        map.delete(c.rep)
                        controls.nb_cross.set(controls.nb_cross.get()-1)
                        Cross.list.remove(c)
            elif "generator" in tags:
                for g in Generator.list:
                    if g.rep == obj:
                        map.delete(g.rep)
                        controls.nb_cross.set(controls.nb_cross.get()-1)
                        Generator.list.remove(g)
            elif "road" in tags:
                for r in Road.list:
                    if r.rep == obj:
                        map.delete(r.rep)
                        controls.nb_roads.set(controls.nb_roads.get()-1)
                        Road.list.remove(r)

    elif mode == "road":
        if len(objects) == 1:
            obj = objects[0]
            tags = map.gettags(obj)
            if "road" in tags:
                for r in Road.list:
                    if r.rep == obj:
                        map.delete(r.rep)
                        controls.nb_roads.set(controls.nb_roads.get()-1)
                        road = Road.list.pop(Road.list.index(r))
                        road.cross1.roads.remove(road)
                        road.cross2.roads.remove(road)
            elif "cross" in tags or "generator" in tags:
                if obj not in selected_cross:
                    selected_cross.append(obj)
                    map.itemconfig(obj, fill="green")
                    if len(selected_cross) == 2:
                        real_cross = []
                        for c in Cross.list:
                            if c.rep in selected_cross:
                                real_cross.append(c)
                        for g in Generator.list:
                            if g.rep in selected_cross:
                                real_cross.append(g)
                        road = Road(real_cross[0], real_cross[1], None)
                        real_cross[0].roads.append(road)
                        real_cross[1].roads.append(road)
                        road.rep = map.draw_road(road)
                        controls.nb_roads.set(controls.nb_roads.get()+1)
                        for obj in selected_cross:
                            map.itemconfig(obj, fill="grey26")
                        selected_cross.clear()

                else:
                    selected_cross.remove(obj)
                    map.itemconfig(obj, fill="grey26")

    elif mode == "priority":
        if len(objects) == 1:
            obj = objects[0]
            tags = map.gettags(obj)

            if "cross" in tags or "generator" in tags:
                if cross_for_priority != obj:
                    map.itemconfig(cross_for_priority, fill="grey26")
                    cross_for_priority = obj
                    map.itemconfig(obj, fill="pink")
                    for c in Cross.list:
                        if c.rep == obj :
                            real_cross_priority = c
                    for g in Generator.list:
                        if g.rep == obj :
                            real_cross_priority = g


            if "road" in tags:
                if cross_for_priority != None:
                    for r in Road.list:
                        if r.rep == obj:
                            if r not in real_cross_priority.priority_axis:
                                real_cross_priority.priority_axis.append(r)
                                radius = 2 * map.current_scale
                                if real_cross_priority== r.cross1:
                                    r.priority_indicator_1 = map.create_oval(x-radius, y-radius, x+radius, y+radius, fill="red")
                                else:
                                    r.priority_indicator_2 = map.create_oval(x-radius, y-radius, x+radius, y+radius, fill="red")
                            else:
                                real_cross_priority.priority_axis.remove(r)
                                if real_cross_priority== r.cross1:
                                    map.delete(r.priority_indicator_1)
                                else:
                                    map.delete(r.priority_indicator_2)


    if len(objects) > 2:
        print("Cas pas prévu, boulet !")

def extract_data():
    print("extracting data")
    scale = 200/91
    file = open("maps/map_data.txt", "w")
    cross_list = []
    road_list = []
    for g in Generator.list:
        cross_list.append(g)
        file.write("{} {}\n".format(g.x*scale, g.y*scale))
    file.write("\n")
    for c in Cross.list:
        cross_list.append(c)
        file.write("{} {} {} \n".format(c.x*scale, c.y*scale, True))
    file.write("\n")
    for r in Road.list:
        file.write("{} {} \n".format(cross_list.index(r.cross1), cross_list.index(r.cross2)))
    file.write("\n")
    for c in cross_list:
        if len(c.roads) > 2:
            file.write("{} {} {}\n".format(cross_list.index(c), Road.list.index(c.priority_axis[0]), Road.list.index(c.priority_axis[1])))
    file.close()

root.state('zoomed') # Maximize the window
container = Container(root)
container.grid(row=0, column=0, sticky="nsew")
map = container.map
root.grid_rowconfigure(0, weight=2)
root.grid_columnconfigure(0, weight=2)
controls = Controls(root)
controls.grid(row=0, column=1, sticky="nsew")

# Event-listeners
root.bind("<KeyPress>", keyboard_listener)
map.bind("<Button-3>", map.scroll_start)
map.bind("<B3-Motion>", map.scroll_move)
map.bind("<MouseWheel>", map.zoom)
root.bind("<Control-Key>", map.zoom)
map.bind("<Button-1>", selector)

root.mainloop()
