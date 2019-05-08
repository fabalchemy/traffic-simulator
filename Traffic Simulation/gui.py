import tkinter as tk
from functions import get_color_from_gradient, random_color
from math import cos, sin, atan, sqrt
from constants import *

W, H = 4000, 2500
marge = 5000
dx, dy = 20, 20 # Elementary move for the canvas


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

        if factor != 0:
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
            cross.rep = self.create_oval(x-3, y-3, x+3, y+3, fill=ROAD_COLOR, outline=ROAD_COLOR, tag="cross")

    def draw_road(self, road_list):
        for road in road_list:
            (l, w) = (road.length, road.width)
            ang = road.angle
            (x,y) = road.cross2.coords
            dx = sin(ang)*w/2
            dy = - cos(ang)*w/2
            dxb = -l*cos(ang)
            dyb = -l*sin(ang)
            road.rep = self.create_polygon(x+dx, y+dy, x-dx, y-dy, x+dxb-dx, y+dyb-dy, x+dxb+dx, y+dyb+dy, fill=ROAD_COLOR, outline=ROAD_OUTLINE_COLOR, width = 2, tag="road")

    def draw_stop(self, road_list):
        for road in road_list:
            orient = -1 #if veh.origin_cross == veh.road.cross1 else -1
            cos_angle, sin_angle = orient*road.cos_angle, orient*road.sin_angle
            e = self.current_scale
            (x0,y0) = road.cross1.coords
            w = road.width
            l = road.length

            dx = sin_angle*w/4 *e
            dy = - cos_angle*w/4 *e
            dxb = - 1*cos_angle *e
            dyb = - 1*sin_angle *e

            x = (x0 - w/4 *sin_angle + (-3)*cos_angle)*e
            y = (y0 + w/4 *cos_angle + (-3)*sin_angle)*e
            points = (x+dx, y+dy, x-dx, y-dy, x+dxb-dx, y+dyb-dy, x+dxb+dx, y+dyb+dy)
            road.stop1.rep = self.create_polygon(points, fill=ROAD_COLOR)

            orient = 1 #if veh.origin_cross == veh.road.cross1 else -1
            cos_angle, sin_angle = orient*road.cos_angle, orient*road.sin_angle
            e = self.current_scale
            (x0,y0) = road.cross2.coords
            w = road.width
            l = road.length

            dx = sin_angle*w/4 *e
            dy = - cos_angle*w/4 *e
            dxb = - 1*cos_angle *e
            dyb = - 1*sin_angle *e

            x = (x0 - w/4 *sin_angle + (-3)*cos_angle)*e
            y = (y0 + w/4 *cos_angle + (-3)*sin_angle)*e
            points = (x+dx, y+dy, x-dx, y-dy, x+dxb-dx, y+dyb-dy, x+dxb+dx, y+dyb+dy)
            road.stop2.rep = self.create_polygon(points, fill=ROAD_COLOR)



    def draw_vehicle(self, vehicle_list):
        for veh in vehicle_list:
            orient = 1 if veh.origin_cross == veh.road.cross1 else -1
            cos_angle, sin_angle = orient*veh.road.cos_angle, orient*veh.road.sin_angle
            e = self.current_scale
            road_width = veh.road.width
            (x0,y0) = veh.origin_cross.coords
            (l, w) = (veh.length, veh.width)

            x = x0 - road_width/4 *sin_angle + (veh.x+veh.length/2)*cos_angle
            y = y0 + road_width/4 *cos_angle + (veh.x+veh.length/2)*sin_angle
            x = x*e
            y = y*e

            dx = sin_angle*w/2 *e
            dy = - cos_angle*w/2 *e
            dxb = - l*cos_angle *e
            dyb = - l*sin_angle *e

            dxb_brake = - (l-0.4)*cos_angle *e
            dyb_brake = - (l-0.4)*sin_angle *e

            points_car = (x+dx, y+dy, x-dx, y-dy, x+dxb-dx, y+dyb-dy, x+dxb+dx, y+dyb+dy)
            points_brake = (x+dxb-dx, y+dyb-dy, x+dxb+dx, y+dyb+dy, x+dxb_brake+dx, y+dyb_brake+dy, x+dxb_brake-dx, y+dyb_brake-dy)

            points_blinker = (-100,-100,-100,-100)
            if veh.road.length - veh.x < 50:
                rad = 0.4 * e
                if veh.direction == "left":
                    points_blinker = (x+dx-rad, y+dy-rad, x+dx+rad, y+dy+rad)
                elif veh.direction == "right":
                    points_blinker = (x-dx-rad, y-dy-rad, x-dx+rad, y-dy+rad)
                else:
                    points_blinker = (-100,-100,-100,-100)

            color = get_color_from_gradient(veh.v/veh.road.speed_limit)

            if veh.rep == None and veh.brake_rep == None and veh.blinker_rep == None:
                veh.rep = self.create_polygon(points_car, fill=color, tag="vehicle")
                veh.brake_rep = self.create_polygon(points_brake, fill=color, tag="brake")
                veh.blinker_rep = self.create_oval(points_blinker, fill="orange", outline="orange")
            else:
                self.coords(veh.rep, points_car)
                self.coords(veh.brake_rep, points_brake)
                self.coords(veh.blinker_rep, points_blinker)
                self.itemconfig(veh.rep, fill=color)
                if veh.last_a <= -.5:
                    self.itemconfig(veh.brake_rep, fill="red")
                else:
                    self.itemconfig(veh.brake_rep, fill=color)

                if veh.blinker_state == 0:
                    self.itemconfig(veh.blinker_rep, state="normal")
                elif veh.blinker_state == 7:
                    self.itemconfig(veh.blinker_rep, state="hidden")
                elif veh.blinker_state >= 14 :
                    veh.blinker_state = -1
                veh.blinker_state += 1

    def draw_leadership(self, vehicle_list):
        map.delete("leadership")
        for veh in vehicle_list:
            if veh.leader != None:
                if veh.leader.rep != None:
                    leader_coords = self.coords(veh.leader.rep)
                    follower_coords = self.coords(veh.rep)
                    x_l, y_l = (leader_coords[4] + leader_coords[6])/2, (leader_coords[5] + leader_coords[7])/2
                    x_f, y_f = (follower_coords[0] + follower_coords[2])/2, (follower_coords[1] + follower_coords[3])/2
                    e = self.current_scale
                    d1, d2, d3 = 2*e, 2*e, 0.75*e
                    map.create_line(x_l, y_l, x_f, y_f, fill=veh.leadership_color, width=1, tag="leadership", arrow = tk.FIRST, arrowshape=(d1, d2, d3))

    def draw_traffic_lights(self, crosses):
        for cross in crosses:
            if len(cross.roads) > 2 and cross.traffic_lights_enabled:
                for i in range(len(cross.roads)):
                    if (i)%2 + cross.priority == 1:
                        color = "green"
                    else:
                        color = "red"

                    if cross == cross.roads[i].cross1:
                        self.itemconfig(cross.roads[i].stop1.rep, fill=color)
                    else:
                        self.itemconfig(cross.roads[i].stop2.rep, fill=color)



class Container(tk.Frame):
    def __init__(self, root):
        # Initialize a Frame
        tk.Frame.__init__(self, root)
        # Initialize the canvas representating the map
        self.map = Map(self, W, H, BACKGROUND_COLOR)
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
        self.logo = tk.PhotoImage(file="logo_traffic_simulator.gif", format="gif")
        tk.Label(self, image=self.logo).grid(row=0, column=0)


        self.time_mgmt = tk.LabelFrame(self, text="Time managment", padx=10, pady= 10)
        self.time_mgmt.grid(row=1,column=0, sticky="new")

        self.time_str = tk.StringVar()
        self.time_str.set("Current time: 0 s.")
        tk.Label(master = self.time_mgmt, textvariable = self.time_str).pack()
        self.speed = tk.Scale(self.time_mgmt, label="Simulation speed", from_=0, to=10, resolution=0.1, orient=tk.HORIZONTAL, length=200)
        self.speed.set(int(1))
        self.speed.pack(fill="both", expand="yes")
        self.play = tk.BooleanVar()
        self.play.set(True)
        self.play_b = tk.Radiobutton(self.time_mgmt, text="Play", variable=self.play, value=True)
        self.pause_b = tk.Radiobutton(self.time_mgmt, text="Pause", variable=self.play, value=False)
        self.play_b.pack(side=tk.LEFT)
        self.pause_b.pack(side=tk.LEFT)
        tk.Button(self.time_mgmt, text=">>", command = lambda : self.change_speed(1)).pack(side=tk.RIGHT)
        tk.Button(self.time_mgmt, text="x1", command = lambda : self.speed.set(1)).pack(side=tk.RIGHT)
        tk.Button(self.time_mgmt, text="<<", command = lambda : self.change_speed(-1)).pack(side=tk.RIGHT)


        self.information = tk.LabelFrame(self, text="Information", padx=10, pady=10)
        self.information.grid(row=2,column=0, sticky="new")
        tk.Label(master = self.information, text = "Number of vehicles: ").grid(row = 0, column = 0)
        self.nb_veh = tk.IntVar()
        self.nb_veh.set(0)
        tk.Label(master = self.information, textvariable = self.nb_veh).grid(row = 0, column = 1)
        self.avg_speed = tk.StringVar()
        self.avg_speed.set("0")
        tk.Label(master = self.information, text="Average speed: ").grid(row = 1, column = 0)
        tk.Label(master = self.information, textvariable = self.avg_speed).grid(row = 1, column = 1)

        self.settings = tk.LabelFrame(self, text="Settings", padx=10, pady=10)
        self.settings.grid(row=3,column=0, sticky="new")

        tk.Label(master = self.settings, text = "Show leader links:").pack(side = tk.LEFT)
        self.leadership = tk.BooleanVar()
        self.leadership.set(True)
        self.leadership_true = tk.Radiobutton(self.settings, text="On", variable=self.leadership, value=True)
        self.leadership_false = tk.Radiobutton(self.settings, text="Off", variable=self.leadership, value=False)
        self.leadership_true.pack(side=tk.LEFT)
        self.leadership_false.pack(side=tk.LEFT)

    def change_speed(self, value):
        speed = int(self.speed.get() + value)
        if speed >= 0 & speed <= 10:
            self.speed.set(speed)


def keyboard_listener(event):
    if event.char == " ":
        controls.play.set(False) if controls.play.get() else controls.play.set(True)

    elif event.char.lower() == "f":
        controls.change_speed(1)
    elif event.char.lower() == "d":
        controls.speed.set(1)
    elif event.char.lower() == "s":
        controls.change_speed(-1)

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
root.title("Traffic Simulator")
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
