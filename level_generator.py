import random, pygame

'''
Level Object
variables:
    parameters
    path (list): a list of segments that together form the whole track
purpose:
    initialize a horiz/vert race track that can be raced on by cars (whether driven by players or AI's)
'''

class Level:

    '''
    Constructor
    parameters:
        path_width (int): the width of the track from one side to the other
        path_length (int): the length of track to be created
        min_seg_length (int): the minimum length of the track a segment can be
        max_seg_length (int): the maximum length of the track a segment can be (straight-a-ways can and do often consist of more than one segment)
    results:
        creates a new race track from the beginning to the end sequentially given VALID constraints (min must be strictly smaller than max)
    return:
        a level object containing the path
    '''
    def __init__(self, path_width, path_length, min_seg_length, max_seg_length):

        # initialize parameters
        self.path_width = path_width
        self.path_length = path_length
        self.min_seg_length = min_seg_length
        self.max_seg_length = max_seg_length

        # create path list
        self.path = list()

        # create the first segment and artifically set its length to min_seg_length, append it to the path
        cur_path_dis = min_seg_length
        first_seg = Segment(0, 0, path_width, cur_path_dis, 1, 0)
        self.path.append(first_seg)
        
        # create segments for the track until the total length is completed
        while cur_path_dis < path_length:

            # get the latest segment created to build off of
            old_seg = self.path[-1]

            # calculates the point to create the new segment
            new_x = old_seg.x + old_seg.distance * old_seg.dir_x
            new_y = old_seg.y + old_seg.distance * old_seg.dir_y

            # creates a random length for the new segment, unless it is within 500 from the finish (makes sure track is exactly the total length)
            if self.path_length - cur_path_dis < 500:
                new_length = self.path_length - cur_path_dis
            else:
                new_length = random.randint(self.min_seg_length, self.max_seg_length)

            # determines the direction of the new segment based on the old segment
            if old_seg.dir_x < 0:           # old direction left

                # chooses between left and up (left segments cannot be followed by down)
                r_num = random.randint(0, 1)
                if r_num == 0:              
                    new_dir_x = -1
                    new_dir_y = 0
                else:
                    new_dir_x = 0
                    new_dir_y = -1
            elif old_seg.dir_x > 0:         # old direction right

                # chooses between right, up, and down (right segments can be followed by both up and down)
                r_num = random.randint(0, 2)
                if r_num == 0:
                    new_dir_x = 1
                    new_dir_y = 0
                elif r_num == 1:
                    new_dir_x = 0
                    new_dir_y = -1
                else:
                    new_dir_x = 0
                    new_dir_y = 1
            elif old_seg.dir_y < 0:         # old direction up

                # chooses between up, left, and right (up segments can be followed by both right and left)
                r_num = random.randint(0, 2)
                if r_num == 0:
                    new_dir_x = 0
                    new_dir_y = -1
                elif r_num == 1:
                    new_dir_x = -1
                    new_dir_y = 0
                else:
                    new_dir_x = 1
                    new_dir_y = 0
            else:                            # old direction down

                # chooses between down and right (down segment cannot be followed by left)
                r_num = random.randint(0, 1)
                if r_num == 0:              
                    new_dir_x = 0
                    new_dir_y = 1
                else:
                    new_dir_x = 1
                    new_dir_y = 0

            # creates the new segment for potential use
            new_seg = Segment(new_x, new_y, self.path_width, new_length, new_dir_x, new_dir_y)

            # determines if the new segment would overlap with the current track
            is_bad_segment = False
            for seg in self.path[:-1]:
                if seg.is_overlapping_segment(new_seg):
                    is_bad_segment = True
                    break
            
            # appends the segment if it is a valid segment
            if not is_bad_segment:
                self.path.append(new_seg)
                cur_path_dis += new_length

'''
Segment Object
variables:
    parameters
    width, height: width and height of the segment bounding box
    x1, y1, x2, y2 (ints): the bounding box of the segment, useful for collision detection (top left, bottom right)
    m_x, m_y (ints): the middle of the bounding box of the segment, useful for track progress calculations
results:
    creates a new segment with all variables calculated
returns:
    a new segment
Notes:
    Think of a segment as a line surrounded from ALL sides by a larger box. The (x, y) of a segment is one point of the line (source point). The line then moves out by the given length in the given direction. The line is then surrounded by a box with the given path width. Therefore both points (source and destination) of the line are actually not on the edge of the drivable segment, but rather a bit within. This basically means that the track could be understood as generated as one connected set of lines that is enlarged to the path width.
'''
class Segment:

    '''
    Constructor
    parameters:
        x, y (ints): location of the beginning of the segment line
        size (int): size of the track width
        distance (int): length of the segment line
        dir_x, dir_y (ints): direction of the line
    result:
        creates a new segment given the desired inputs
    returns:
        a newly created segment
    '''
    def __init__(self, x, y, segment_size, segment_distance, dir_x, dir_y):

        # parameter initialization
        self.x = x
        self.y = y
        self.size = segment_size
        self.distance = segment_distance
        self.dir_x = dir_x
        self.dir_y = dir_y

        # calculate width and height based on the horizontal/vertical segment
        if self.dir_x != 0:
            self.height = segment_size
            self.width = segment_distance + segment_size
        else:
            self.width = segment_size
            self.height = segment_distance + segment_size

        # calls the function that calculates the bounding box of the segment
        self.calculate_bounding_box()

    '''
    calculate_bounding_box function
    parameters:
        none
    results:
        calculates and stores the bounding box of the segment
    returns:
        none
    '''
    def calculate_bounding_box(self):

        # calculate the bounding box as a square with size of the path width surrounding the (x, y) point
        self.x1 = self.x - self.size / 2
        self.y1 = self.y - self.size / 2
        self.x2 = self.x + self.size / 2
        self.y2 = self.y + self.size / 2

        # extends the bounding box from the aformentioned square based off which direction it extends
        if self.dir_x < 0:           #left
            self.x1 -= self.distance
        elif self.dir_x > 0:         #right
            self.x2 += self.distance
        elif self.dir_y < 0:         #up
            self.y1 -= self.distance
        else:                        #down
            self.y2 += self.distance

        # calculates the middle of the segment
        self.m_x = (self.x2 + self.x1) / 2
        self.m_y = (self.y2 + self.y1) / 2

    '''
    is_overlapping_segment function
    parameters:
        other (Segment): second segment to check for overlapping (first is segment that has function called)
    results:
        checks if two segments are overlapping or not
    returns:
        True or False
    Notes:
        This bounding box collision calculation compares the top left corners of two segments and the bottom right corners of two segments. If I remember, I will include in this project a diagram of how this check guarantees the desired outcome.
    '''
    def is_overlapping_segment(self, other):

        # calculate the four pairs
        pair1_x = self.x1 - other.x2
        pair1_y = self.y1 - other.y2
        pair2_x = other.x1 - self.x2
        pair2_y = other.y1 - self.y2

        # if any of the four pairs resulted in a positive value, then there was a collision, else, there was no collision
        return pair1_x <= 0 and pair1_y <= 0 and pair2_x <= 0 and pair2_y <= 0


    '''
    draw_seg function
    parameters:
        draw_surface (Surface): pygame surface object to draw on
        cx, cy (ints): the point on the WORLD space that the screen is centering (middle of screen)
        zoom (int): zoom factor
        res ([int, int]): dimensions of surface
    results:
        draws the segment onto the pygame window
    returns:
        none
    '''
    def draw_seg(self, draw_surface, cx, cy, zoom, res):

        px = (self.x1 - cx) * zoom + (res[0] / 2)
        py = (self.y1 - cy) * zoom + (res[1] / 2)
        pw = (self.x2 - self.x1) * zoom
        ph = (self.y2 - self.y1) * zoom

        pygame.draw.rect(draw_surface, (0, 0, 0), pygame.Rect(px, py, pw, ph))