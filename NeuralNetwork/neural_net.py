from NeuralNetwork.node import Node
from NeuralNetwork.link import Link
import random, math

"""
Neural Net Object
variables:
    parameters
    layers (list): stores a list of lists of Nodes, each list wihin layers is a layer of the neural network
    links (list): stores a list of all the links within the neural network (no differentiation between layers)
purpose:
    organize, initialize, and run a neural network
"""
class NeuralNet:

    """
    Constructor
    parameters:
        num_in_nodes (int): number of input nodes for neural net
        num_out_nodes (int): number of output nodes for neural net
        num_hidden_nodes (int): number of nodes within each hidden layer
        num_hidden_layers (int): number of hidden layers within neural net
    result:
        creates a new Neural Network object, with default values for the network (0 for node values, random 0-1 for links)
    return:
        Neural Network object
    """
    def __init__(self, num_in_nodes, num_out_nodes, num_hidden_nodes, num_hidden_layers):

        # initialize parameters
        self.num_in_nodes = num_in_nodes
        self.num_out_nodes = num_out_nodes
        self.num_hidden_nodes = num_hidden_nodes
        self.num_hidden_layers = num_hidden_layers

        # create the list of layers, and create the first layer for the input layer
        self.layers = list()
        self.layers.append(list())

        # create a list for all links
        self.links = list()

        # create input nodes and add to input layer
        for _ in range(self.num_in_nodes):
            new_node = Node()
            self.layers[0].append(new_node)

        # uses add_layer to create each hidden layer, consisting of its nodes and links
        for _ in range(self.num_hidden_layers):
            self.add_layer(self.num_hidden_nodes)

        # uses add_layer to create final output layer, consisting of its nodes and links
        self.add_layer(self.num_out_nodes)

    """
    function: add_layer
    parameters:
        num_new_nodes (int): number of nodes the new layer consists of
    results:
        adds a layer of nodes to the neural network, and creates the links between the new layer and the previous
    """
    def add_layer(self, num_new_nodes):

        # creates a new list to store layer
        self.layers.append(list())

        # creates each node within new layer
        for _ in range(num_new_nodes):
            new_node = Node()

            # create link for every pair of new node and all nodes one layer to the left
            for left_node in self.layers[-2]:
                new_link = Link()
                new_link.left_node = left_node
                new_link.right_node = new_node
                self.links.append(new_link)
                new_node.left_links.append(new_link)
                left_node.right_links.append(new_link)

            # adds newly created node to the latest layer
            self.layers[-1].append(new_node)

    """
    function: run_neural_network
    parameters:
        input_values (list): list of input values
    results:
        runs neural network given the input, and returns the output
    return:
        (list) values of output layer
    """
    def run_neural_network(self, input_values):

        # makes sure the # of input variables is the same as the # of input nodes on network
        assert len(self.layers[0]) == len(input_values)

        # sets the values of the nodes of the input layer to the input values
        for i in range(len(self.layers[0])):
            self.layers[0][i].value = input_values[i]

        # resets the rest of the neural network
        for layer in self.layers[1:]:
            for node in layer:
                node.value = 0

        # goes through each layer starting from the input layer and ending before the output layer
        for layer in self.layers[:-1]:

            # goes through each node in layer
            for left_node in layer:

                # goes through each right direction link of given node
                for link in left_node.right_links:

                    # adds the left node's value * the link's modifier to the link's destination node
                    link.right_node.value += left_node.value * link.modifier * (1 / len(layer))

        '''
        different method not being used for calculation

        for layer in self.layers[1:]:
            for right_node in layer:
                weight_total = 0
                for link in right_node.left_links:
                    weight_total += link.modifier

                for link in right_node.left_links:
                    right_node.value += link.left_node.value * (link.modifier / weight_total)
        '''

        # creates a list of output values and appends each output node's value to it
        out_values = list()
        for node in self.layers[-1]:
            out_values.append(node.value)

        # returns the output values list
        return out_values

    """
    function: create_mutation
    parameters: none
    results: 
        creates a new neural net mutated from the source neural net
    returns:
        (Neural Net) mutation of given neural net
    """
    def create_mutation(self, mutation_factor):

        # creates blank neural net (with random link values and value=0 node values)
        mutation = NeuralNet(self.num_in_nodes, self.num_out_nodes, self.num_hidden_nodes, self.num_hidden_layers)
        
        comp_factor = mutation_factor / 120
        rand_factor = mutation_factor / 1

        # goes through each link in neural network and slightly modifies it
        for i in range(len(self.links)):
            if random.random() < comp_factor:
                change = random.random() * rand_factor - 0.5 * rand_factor
            else:
                change = random.random() * 0.000001 - 0.0000005
            mutation.links[i].modifier = self.links[i].modifier + change

        # returns newly created mutated neural network object
        return mutation

    """
    function: create_copy
    parameters: none
    results:
        creates a new neural network that is an exact copy of the source neural net
    returns:
        (Neural Net) copy of given neural net
    """
    def create_copy(self):

        # creates blank neural net (with random link values and value=0 node values)
        copy = NeuralNet(self.num_in_nodes, self.num_out_nodes, self.num_hidden_nodes, self.num_hidden_layers)
        
        # copies link values for all links within network
        for i in range(len(self.links)):
            copy.links[i].modifier = self.links[i].modifier

        # returns new neural network copy
        return copy

    def get_out_values(self):
        out_vals = list()
        for node in self.layers[-1]:
            out_vals.append(node.value)
        return out_vals