"""
Node Object
parameters: none
variables:
    value (float): stores the neuron's value
    left_links (list): to store list of links to the previous layer
    right links (list): to store list of links to the next layer
purpose: 
    serves as a neuron in a neural network
"""
class Node:

    def __init__(self):
        self.value = 0
        self.left_links = list()
        self.right_links  = list()