import numpy as np
from statistics import mean

class Object_Rec:
    def __init__(self, type_obj, scale_factor, coord):
        self.type_obj = type_obj
        self.x1 = float(coord[0])
        self.y1 = float(coord[1])
        self.x2 = float(coord[2])
        self.y2 = float(coord[3])

        self.generate_object_visit_area(scale_factor)

        self.visits_time = []
        self.current_visit_time = 0
        self.returns_time = []
        self.current_return_time = 0

        self.visited = False
    
    def generate_object_visit_area(self, sf):
        area = calculate_area(self.x1, self.y1, self.x2, self.y2)

        # Calculate the center of the rectangle
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        
        # Calculate the width and height of the original rectangle
        width = abs(self.x2 - self.x1)
        height = abs(self.y2 - self.y1)
        
        # Calculate the new width and height after scaling the area
        new_area = calculate_area(self.x1, self.y1, self.x2, self.y2) * sf
        scaling_ratio = np.sqrt(sf)
        
        new_width = width * scaling_ratio
        new_height = height * scaling_ratio
        
        # Calculate the new coordinates based on the center point
        self.new_x1 = center_x - new_width / 2
        self.new_x2 = center_x + new_width / 2
        self.new_y1 = center_y - new_height / 2
        self.new_y2 = center_y + new_height / 2

        #plot_area(self.x1, self.y1, self.x2, self.y2, self.new_x1, self.new_y1, self.new_x2, self.new_y2)

    def evaluate_visit(self, x, y, time_per_frame):
        #If the x and y coordinates are inside the area surrounding the object:
        if x > self.new_x1 and x < self.new_x2 and y > self.new_y1 and y < self.new_y2:
            self.current_visit_time += time_per_frame

            if not self.visited and self.current_return_time != 0: #When fly was NOT previously visiting the object:
                self.returns_time.append(self.current_return_time)
                self.current_return_time = 0 

            self.visited = True

        #If the x and y coordinates are NOT inside the area surrounding the object:
        else:
            if self.visits_time != []:
                self.current_return_time += time_per_frame

            if self.visited and self.current_visit_time != 0: #When fly was previously visiting the object
                self.visits_time.append(self.current_visit_time)
                self.current_visit_time = 0
            
            self.visited = False     
    
    def average_data(self):
        if self.returns_time == []:
            avg_return_time = 0
            freq_returns = 0
        else:
            avg_return_time = mean(self.returns_time)
            freq_returns = len(self.returns_time)

        if self.visits_time == []:
            avg_visits_time = 0
            freq_visits = 0
        else:
            avg_visits_time = mean(self.visits_time)
            freq_visits = len(self.visits_time)
        
        return [freq_visits, avg_visits_time, freq_returns, avg_return_time]

def calculate_area(x1, y1, x2, y2):
    # Calculate the width and height of the rectangle
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    # Calculate the area
    area = width * height
    return area

def plot_area(x1, y1, x2, y2, new_x1, new_y1, new_x2, new_y2):
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Coordinates of the first rectangle (x1, y1) and (x2, y2)
    width1 = abs(x2 - x1)
    height1 = abs(y2 - y1)
    
    # Coordinates of the second rectangle (x1, y1) and (x2, y2)
    width2 = abs(new_x2 - new_x1)
    height2 = abs(new_y2 - new_y1)
    
    # Add the first rectangle
    rect1 = patches.Rectangle((x1, y1), width1, height1, linewidth=1, edgecolor='r', facecolor='none')
    ax.add_patch(rect1)
    
    # Add the second rectangle
    rect2 = patches.Rectangle((new_x1, new_y1), width2, height2, linewidth=1, edgecolor='b', facecolor='none')
    ax.add_patch(rect2)

    ax.set_xlim(0, 960)
    ax.set_ylim(0, 960)
    # Set the limits and show the plot
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


