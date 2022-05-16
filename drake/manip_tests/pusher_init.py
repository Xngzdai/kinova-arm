"""
basictest4.py
Description:
    Trying to support the basic meshcat visualizer from within a Drake container.
    Using this to visualize Kinova Gen3 6DoF
"""

import importlib
import sys
from urllib.request import urlretrieve

# Start a single meshcat server instance to use for the remainder of this notebook.
server_args = []
from meshcat.servers.zmqserver import start_zmq_server_as_subprocess
proc, zmq_url, web_url = start_zmq_server_as_subprocess(server_args=server_args)

# from manipulation import running_as_notebook

# Imports
import numpy as np
import pydot
from ipywidgets import Dropdown, Layout
from IPython.display import display, HTML, SVG

import matplotlib.pyplot as plt

from pydrake.all import (
    AddMultibodyPlantSceneGraph, ConnectMeshcatVisualizer, DiagramBuilder, 
    FindResourceOrThrow, GenerateHtml, InverseDynamicsController, 
    MultibodyPlant, Parser, Simulator, RigidTransform , SpatialVelocity, RotationMatrix,
    AffineSystem, Diagram, LeafSystem, LogVectorOutput, CoulombFriction, HalfSpace )
from pydrake.multibody.jupyter_widgets import MakeJointSlidersThatPublishOnCallback

from pydrake.geometry import (Cylinder, GeometryInstance,
                                MakePhongIllustrationProperties)

##########################
## Function Definitions ##
##########################

def AddGround(plant):
    """
    Add a flat ground with friction
    """

    # Constants
    transparent_color = np.array([0.5,0.5,0.5,0])
    nontransparent_color = np.array([0.5,0.5,0.5,0.1])

    p_GroundOrigin = [0, 0.0, 0.0]
    R_GroundOrigin = RotationMatrix.MakeXRotation(0.0)
    X_GroundOrigin = RigidTransform(R_GroundOrigin,p_GroundOrigin)

    # Set Up Ground on Plant

    surface_friction = CoulombFriction(
            static_friction = 0.7,
            dynamic_friction = 0.5)
    plant.RegisterCollisionGeometry(
            plant.world_body(),
            X_GroundOrigin,
            HalfSpace(),
            "ground_collision",
            surface_friction)
    plant.RegisterVisualGeometry(
            plant.world_body(),
            X_GroundOrigin,
            HalfSpace(),
            "ground_visual",
            transparent_color)  # transparent

## Constants ##

show_plots = True

# Building Diagram
time_step = 0.002

builder = DiagramBuilder()

# plant = builder.AddSystem(MultibodyPlant(time_step=time_step)) #Add plant to diagram builder
plant, scene_graph = AddMultibodyPlantSceneGraph(builder, time_step=1e-3)
block_as_model = Parser(plant=plant).AddModelFromFile("/root/OzayGroupExploration/drake/manip_tests/slider/slider-block.urdf",'block_with_slots') # Save the model into the plant.

AddGround(plant)

plant.Finalize()

# Connect Block to Logger
# state_logger = LogVectorOutput(plant.get_body_spatial_velocities_output_port(), builder)
state_logger = LogVectorOutput(plant.get_state_output_port(block_as_model), builder)
state_logger.set_name("state_logger")

# Connect to Meshcat
meshcat = ConnectMeshcatVisualizer(builder=builder,
                                    zmq_url = zmq_url,
                                    scene_graph=scene_graph,
                                    output_port=scene_graph.get_query_output_port())

diagram = builder.Build()

# Create system that outputs the slowly updating value of the pose of the block.
A = np.zeros((6,6))
B = np.zeros((6,1))
f0 = np.array([0.0,0.0,0.0,1.2,0.0,0.0])
C = np.eye(6)
D = np.zeros((6,1))
y0 = np.zeros((6,1))
x0 = y0
# target_source2 = builder.AddSystem(
#     AffineSystem(A,B,f0,C,D,y0)
#     )
# target_source2.configure_default_state(x0)

# Connect the state of the block to the output of a slowly changing system.
# builder.Connect(
#     target_source2.get_output_port(),
#     block1.plant.GetInputPort("slider_block"))

# builder.Connect(
#     plant.get_state_output_port(block),
#     demux.get_input_port(0))

#Weld robot to table, with translation in x, y and z
# p_PlaceOnTable0 = [0.15,0.75,-0.20]
# R_PlaceOnTableO = RotationMatrix.MakeXRotation(-np.pi/2.0)
# X_TableRobot = RigidTransform(R_PlaceOnTableO,p_PlaceOnTable0)
# plant.WeldFrames(
#     plant.GetFrameByName("simpleDesk"),plant.GetFrameByName("base_link"),X_TableRobot)



# plant.Finalize()
# # Draw the frames
# for body_name in ["base_link", "shoulder_link", "bicep_link", "forearm_link", "spherical_wrist_1_link", "spherical_wrist_2_link", "bracelet_with_vision_link", "end_effector_link"]:
#     AddMultibodyTriad(plant.GetFrameByName(body_name), scene_graph)

# diagram = builder.Build()
diagram_context = diagram.CreateDefaultContext()

# SetFreeBodyPose
p_WBlock = [0.0, 0.0, 0.1]
R_WBlock = RotationMatrix.MakeXRotation(np.pi/2.0) # RotationMatrix.MakeXRotation(-np.pi/2.0)
X_WBlock = RigidTransform(R_WBlock,p_WBlock)
plant.SetFreeBodyPose(plant.GetMyContextFromRoot(diagram_context),plant.GetBodyByName("body", block_as_model),X_WBlock)

plant.SetFreeBodySpatialVelocity(
    plant.GetBodyByName("body", block_as_model),
    SpatialVelocity(np.zeros(3),np.array([0.0,0.0,0.0])),
    plant.GetMyContextFromRoot(diagram_context))

meshcat.load()
diagram.Publish(diagram_context)


# Set up simulation
simulator = Simulator(diagram, diagram_context)
simulator.set_target_realtime_rate(1.0)
simulator.set_publish_every_time_step(False)

# Run simulation
simulator.Initialize()
simulator.AdvanceTo(15.0)

# Collect Data
state_log = state_logger.FindLog(diagram_context)
log_times  = state_log.sample_times()
state_data = state_log.data()
print(state_data.shape)

if show_plots:

    # Plot Data - First Half
    fig = plt.figure()
    ax_list1 = []

    for plt_index1 in range(6):
        ax_list1.append( fig.add_subplot(231+plt_index1) )
        plt.plot(log_times,state_data[plt_index1,:])
        plt.title('State #' + str(plt_index1))

    # Plot Data - Second Half
    fig = plt.figure()
    ax_list2 = []

    for plt_index2 in range(6,12):
        ax_list2.append( fig.add_subplot(231+plt_index2-6) )
        plt.plot(log_times,state_data[plt_index2,:])
        plt.title('State #' + str(plt_index2))

    fig = plt.figure()
    plt.plot(log_times,state_data[-1,:])

    plt.show()