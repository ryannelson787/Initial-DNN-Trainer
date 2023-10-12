from NeuralNetwork.neural_net import NeuralNet
import math, pygame, random

'''
Car object
variables:
    x, y (floats): position in the game world
    level (Level): the level object the car runs on
    nn (NeuralNet): the neural network the car runs on
    has_nn (bool): whether the car drives on human input or nn input
    max_vel, acc_force, turn_multiplier (floats/ints): static car movement properties
    vel, rotation, acc, turn (floats): dynamic car movement properties
    is_alive (bool): whether the car is still intact or has driven off the track
    color (3 tuple): displayed color of the car in pygame
    current_segment_index (int): the index of the segment of the level that the car is currently on
    total_dis (float): total distance that the car has traveled on the given track
purpose:
    code allowing a car that can drive down a track, either controlled by its own NeuralNet or by the human player
'''
class Car:

    '''
    Constructor
    parameters:
        x, y (floats): starting position of the car (usually 0)
        level (Level): level object that the car drives on
    results:
        creates and resets a new car
    returns:
        a newly created car (defaulted to player use)
    '''
    def __init__(self, x, y, level):
        self.level = level

        self.has_nn = False

        self.max_vel = 5
        self.acc_force = 0.2
        self.turn_multiplier = 2.75

        self.reset_car(x, y)

        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    '''
    reset_car function
    parameters:
        x, y (floats): starting position of the car
    results:
        resets the car to run a track again
    returns:
        none
    Notes:
        I don't use this function beyond the initial car creating, but it may serve useful for future implementations.
    '''
    def reset_car(self, x, y):
        self.is_alive = True

        self.x = x
        self.y = y

        self.vel = 0
        self.rotation = 0

        self.acc = 0
        self.left = 0
        self.right = 0
        self.turn = 0

        self.current_segment_index = 0
        self.distance_to_next = 0

    '''
    setup_nn function
    parameters:
        num_in_nodes (int): number of input nodes for neural network (# car sensors)
        num_out_nodes (int): number of output nodes for neural network (# car decisions)
        num_hidden_nodes (int): number of nodes in each hidden layer
        num_hidden_layers (int): number of hidden layers (not input/output layers)
    results:
        creates a new neural network for the car and sets it as its default driving mode
    returns:
        none
    '''
    def setup_nn(self, num_in_nodes, num_out_nodes, num_hidden_nodes, num_hidden_layers):
        self.nn = NeuralNet(num_in_nodes, num_out_nodes, num_hidden_nodes, num_hidden_layers)
        self.has_nn = True


    '''
    take_nn function
    parameters:
        nn (NeuralNet): the neural net to use as the driver (either a copy or mutation of a previous gen car's nn)
    results:
        sets the given neural network for the car and sets it as its default driving mode
    returns:
        none
    '''
    def take_nn(self, nn):
        self.nn = nn
        self.has_nn = True

    '''
    calculate_nn_decisions function
    parameters:
        none
    results:
        calculates the neural network inputs for the car, and then runs the neural network, and then applies the output to the car's movement input
    returns
        whether the neural network went on and made a decision (aka whether the car is alive or not)
    '''
    def calculate_nn_decisions(self):

        # dont bother making a decision if the car is off the track
        if not self.is_alive:
            return False

        # calculate the 5 inputs for the car's neural network (distance in front, distance 45/90 to right/left)
        dis_st = self.distance_from_boundary(0) / 500
        dis_l_45 = self.distance_from_boundary(-45) / 500
        dis_l_90 = self.distance_from_boundary(-90) / 500
        dis_r_45 = self.distance_from_boundary(45) / 500
        dis_r_90 = self.distance_from_boundary(90) / 500

        # run the neural network, and retrieve the output
        nn_output = self.nn.run_neural_network([dis_st, dis_l_45, dis_l_90, dis_r_45, dis_r_90])

        '''
        output 0 = left turn
        output 1 = right turn
        output 2 = whether or not to turn
        '''
        
        # if the neural network decided to not turn the car, then don't turn the car
        if nn_output[2] < 0:
            nn_output[0] = 0
            nn_output[1] = 0

        # set the inputs of the car and return that a decision was made
        self.set_inputs(1, nn_output[0], nn_output[1])
        return True

    '''
    set_inputs function
    parameters:
        acc (float): acceleration input
        left, right (float): left/right inputs
    results:
        takes the given inputs and calculates how much the car should turn and whether to accelerate/decelerate
    '''
    def set_inputs(self, acc, left, right):
        self.acc = acc
        self.left = left
        self.right = right

        if self.acc > 0:
            self.acc = 1
        else:
            self.acc = -1

        self.turn = self.right - self.left
        self.turn = min(max(self.turn, -1), 1)

    '''
    update function
    parameters:
        none
    results:
        performs any needed actions once every 60th of a second, including moving, checking track progress, and checking live status
    returns:
        none
    '''
    def update(self):

        # don't do anything to the car if it has crashed
        if not self.is_alive:
            return

        # handles MOVEMENT, including rotating the car, changing the velocity of the car, and changing the position of the car
        self.rotation += self.turn * self.turn_multiplier
        self.vel = max(min(self.max_vel, self.vel + self.acc_force * self.acc), 0)

        if self.is_alive:
            self.x += math.cos(math.radians(self.rotation)) * self.vel
            self.y += math.sin(math.radians(self.rotation)) * self.vel

        # track the progress/status of the car
        self.track_progress()

    '''
    track_progress function
    parameters:
        none
    results:
        updates the progress of the car and checks whether it has crashed or not
    '''
    def track_progress(self):

        # if the car is not on the segment it previously was, then check the following
        is_on_track = False
        if not self.is_on_segment(self.level.path[self.current_segment_index]):

            # check if the car is on the previous segment, if so, then the car is still on track, update the seg index
            if self.current_segment_index > 0:
                if self.is_on_segment(self.level.path[self.current_segment_index - 1]):
                    self.current_segment_index -= 1
                    is_on_track = True

            # check if the car is on the next segment, if so, then the car is still on track, update the seg index
            if self.current_segment_index + 1 < len(self.level.path):
                if self.is_on_segment(self.level.path[self.current_segment_index + 1]):
                    self.current_segment_index += 1
                    is_on_track = True
        else:

            # if the car is still on the segment, than it is on the track
            is_on_track = True
        
        # if the car veered off track this iteration, then kill the car
        if not is_on_track:
            self.is_alive = False

        # calculate the total distance the car has traveled
        self.calc_total_distance()

    '''
    calc_total_distance function
    parameters:
        none
    results:
        calculates the total distance the car traveled
    returns
        none
    '''
    def calc_total_distance(self):

        # don't calculate if the car isn't on the track
        if not self.is_alive:
            return

        # car can possibly be on two segments at once, this sets the variables to the further segment
        seg = self.level.path[self.current_segment_index]
        seg_ind = self.current_segment_index
        if self.current_segment_index + 1 < len(self.level.path):
            n_seg = self.level.path[self.current_segment_index + 1]
            if self.is_on_segment(n_seg):
                seg = n_seg
                seg_ind += 1

        # finds the destination point to the NEXT seg (basically the middle of the furthest edge from the start)
        dest_pt = (seg.x + (seg.size / 2 + seg.distance) * seg.dir_x, seg.y + (seg.size / 2 + seg.distance) * seg.dir_y)

        # add up the previous segments' distances, including the current segment
        self.total_dis = 0
        for s in range(seg_ind + 1):
            self.total_dis += self.level.path[s].distance

        # subtract the distance from the end of the current segment, which should result in the total distance
        self.total_dis -= math.dist((self.x, self.y), dest_pt)

    '''
    is_on_segment function
    parameters:
        seg (Segment): segment to check if on
    results:
        checks if car is on segment
    returns:
        if car is on segment or not
    '''
    def is_on_segment(self, seg):
        return self.x >= seg.x1 and self.x <= seg.x2 and self.y >= seg.y1 and self.y <= seg.y2
    
    '''
    is_point_on_segment function
    parameters:
        point (2 tuple): point to check if on segment
        seg (Segment): segment to check if on
    results:
        checks if point is on segment
    returns:
        if point is on segment or not
    '''
    def is_point_on_segment(self, point, seg):
        error = 0.001
        return point[0] >= seg.x1 -error and point[0] <= seg.x2 +error and point[1] >= seg.y1 -error and point[1] <= seg.y2 +error

    '''
    calculate_points_distance function
    parameters:
        p1, p2 (2 tuples): points to calculate distance from each other
    results: 
        calculates the euclidian distance from the two points
    return:
        the distance
    '''
    def calculate_points_distance(self, p1, p2):
        return math.sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))

    def distance_from_boundary(self, angle):
        theta = self.rotation + angle

        seg = self.level.path[self.current_segment_index]
        x_dir = math.cos(math.radians(theta))
        y_dir = math.sin(math.radians(theta))
        x_to_side = math.copysign(seg.width / 2, x_dir) - (self.x - seg.m_x)
        y_to_side = math.copysign(seg.height / 2, y_dir) - (self.y - seg.m_y)
        horiz_p = (self.x + (1 / (math.tan(math.radians(theta) + 0.0001))) * y_to_side, self.y + y_to_side)
        vert_p = (self.x + x_to_side, self.y + (math.tan(math.radians(theta))) * x_to_side)

        if self.is_point_on_segment(horiz_p, seg):
            use_point = horiz_p
        elif self.is_point_on_segment(vert_p, seg):
            use_point = vert_p
        else:
            use_point = (self.x, self.y)

        next_point = use_point
        prev_point = use_point

        next_index = self.current_segment_index + 1
        prev_index = self.current_segment_index - 1
        while next_index in range(0, len(self.level.path)):
            n_seg = self.level.path[next_index]

            if self.is_point_on_segment(next_point, n_seg):
                next_index += 1
            else:
                break

            x_dir = math.cos(math.radians(theta))
            y_dir = math.sin(math.radians(theta))
            x_to_side = math.copysign(n_seg.width / 2, x_dir) - (self.x - n_seg.m_x)
            y_to_side = math.copysign(n_seg.height / 2, y_dir) - (self.y - n_seg.m_y)
            horiz_p = (self.x + (1 / (math.tan(math.radians(theta) + 0.0001))) * y_to_side, self.y + y_to_side)
            vert_p = (self.x + x_to_side, self.y + (math.tan(math.radians(theta))) * x_to_side)

            if self.is_point_on_segment(horiz_p, n_seg):
                next_point = horiz_p
            elif self.is_point_on_segment(vert_p, n_seg):
                next_point = vert_p
            else:
                next_point = (self.x, self.y)

        while prev_index in range(0, len(self.level.path)):
            n_seg = self.level.path[prev_index]

            if self.is_point_on_segment(prev_point, n_seg):
                prev_index -= 1
            else:
                break

            x_dir = math.cos(math.radians(theta))
            y_dir = math.sin(math.radians(theta))
            x_to_side = math.copysign(n_seg.width / 2, x_dir) - (self.x - n_seg.m_x)
            y_to_side = math.copysign(n_seg.height / 2, y_dir) - (self.y - n_seg.m_y)
            horiz_p = (self.x + (1 / (math.tan(math.radians(theta) + 0.0001))) * y_to_side, self.y + y_to_side)
            vert_p = (self.x + x_to_side, self.y + (math.tan(math.radians(theta))) * x_to_side)

            if self.is_point_on_segment(horiz_p, n_seg):
                prev_point = horiz_p
            elif self.is_point_on_segment(vert_p, n_seg):
                prev_point = vert_p
            else:
                prev_point = (self.x, self.y)

        distance = max(math.dist(prev_point, (self.x, self.y)), math.dist(next_point, (self.x, self.y)))

        return distance

    def draw_car(self, draw_surface, cx, cy, zoom, res):

        px = (self.x - cx) * zoom + (res[0] / 2)
        py = (self.y - cy) * zoom + (res[1] / 2)
        pz = 8 * zoom

        pygame.draw.circle(draw_surface, self.color, (px, py), pz)