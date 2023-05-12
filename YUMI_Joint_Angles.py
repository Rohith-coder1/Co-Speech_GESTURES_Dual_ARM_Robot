import numpy as np
import pickle
import socket
import time
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from IPython.display import display, clear_output



filename = "....."                 # Give the path of the generated pickle file
with open(filename,'rb') as f:
    np.set_printoptions(threshold=np.inf)
    data = pickle.load(f)
    data = data['out_poses']
   
   
def find_vector_angles(x,y):
    dot_product = x[0]*y[0] + x[1]*y[1] + x[2]*y[2]
    mag_x = math.sqrt(x[0]**2 + x[1]**2 + x[2]**2)
    mag_y = math.sqrt(y[0]**2 + y[1]**2 + y[2]**2)
    cos_theta = dot_product / (mag_x * mag_y)
    theta = math.acos(cos_theta)
    angle_degrees = math.degrees(theta)
    return angle_degrees
   

''' Here used for calculating the pitch of the robot arm '''
def x_axis_rot(index):                # index depicts the joint number in human
    point_A = data[:,index]
    point_B = data[:,index+1]
    u = point_B - point_A
    u[:,0] = 0
    angles = []
    for i in range(len(data)-1):
        x = u[i]
        y = u[i+1]
        angles.append(find_vector_angles(x, y))
    angles = np.array(angles)
    return angles


''' Here used for calculating the roll of the robot arm '''
def y_axis_rot(index):                # index depicts the joint number in human
    point_A = data[:,index]
    point_B = data[:,index+1]
    u = point_B - point_A
    u[:,1] = 0
    angles = []
    for i in range(len(data)-1):
        x = u[i]
        y = u[i+1]
        angles.append(find_vector_angles(x, y))
    angles = np.array(angles)
    return angles


''' Here used for calculating the yaw of the robot arm '''
def z_axis_rot(index):                # index depicts the joint number in human
    point_A = data[:,index]
    point_B = data[:,index+1]
    u = point_B - point_A
    u[:,2] = 0
    angles = []
    for i in range(len(data)-1):
        x = u[i]
        y = u[i+1]
        angles.append(find_vector_angles(x, y))
    angles = np.array(angles)
    return angles


r_j1_ref = 101
r_j2_ref = -95
r_j7_ref = -43
r_j3_ref = -12

l_j1_ref = -101
l_j2_ref = -95
l_j7_ref = 43
l_j3_ref = -12


''' Joint angles for right arm '''
r_j1 = r_j1_ref + y_axis_rot(7)
r_j2 = r_j2_ref + x_axis_rot(7)
r_j7 = r_j7_ref + z_axis_rot(8)
r_j3 = r_j3_ref + x_axis_rot(8)
r_j7[r_j7 > 1] = 1

'''Joint angles for left arm '''
l_j1 = l_j1_ref + y_axis_rot(4)
l_j2 = l_j2_ref + x_axis_rot(4)
l_j7 = l_j7_ref + z_axis_rot(5)
l_j3 = l_j3_ref + y_axis_rot(5)
l_j7[l_j7 > 60] = 60



''' For RIGHT arm in Yumi Robot '''
s_1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
port_1 = 34156
s_1.bind(('',port_1))
s_1.listen(5)
clientsocket_1, address_1 = s_1.accept()
print(f'Connection from client_1 {address_1} has been successfully established!')
clientsocket_1.send(bytes(str(len(data)-1),'utf-8'))
i = 0
flag = True


''' For LEFT arm in Yumi robot '''  
s_2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
port_2 = 37514
s_2.bind(('',port_2))
s_2.listen(5)
clientsocket_2, address_2 = s_2.accept()
print(f'Connection from client_2 {address_2} has been successfully established!')
clientsocket_2.send(bytes(str(len(data)-1),'utf-8'))
i = 0
flag = True


start = time.time()
while i < len(data)-1:
    msg = clientsocket_1.recv(1024).decode()
    clientsocket_1.send(bytes(str(r_j1[i]),'utf-8'))
   
    msg = clientsocket_2.recv(1024).decode()
    clientsocket_2.send(bytes(str(l_j1[i]),'utf-8'))
   
    msg = clientsocket_1.recv(1024).decode()
    clientsocket_1.send(bytes(str(r_j2[i]),'utf-8'))
   
    msg = clientsocket_2.recv(1024).decode()
    clientsocket_2.send(bytes(str(l_j2[i]),'utf-8'))
   
    msg = clientsocket_1.recv(1024).decode()
    clientsocket_1.send(bytes(str(r_j7[i]),'utf-8'))
   
    msg = clientsocket_2.recv(1024).decode()
    clientsocket_2.send(bytes(str(l_j7[i]),'utf-8'))
   
    msg = clientsocket_1.recv(1024).decode()
    clientsocket_1.send(bytes(str(r_j3[i]),'utf-8'))
   
    msg = clientsocket_2.recv(1024).decode()
    clientsocket_2.send(bytes(str(l_j3[i]),'utf-8'))
   
    i += 1


end_pos_yumi_right = []
end_pos_yumi_left = []
i = 0
while i < len(data)-1:
    msg = clientsocket_1.recv(1024).decode()
    msg = eval(msg)
    end_pos_yumi_right.append(msg)
    clientsocket_1.send(bytes("RIGHT",'utf-8'))
   
    msg_1 = clientsocket_2.recv(1024).decode()
    msg_1 = eval(msg_1)
    end_pos_yumi_left.append(msg_1)
    clientsocket_2.send(bytes("YES",'utf-8'))
   
    i += 1

end_pos_yumi_right = np.array(end_pos_yumi_right)
end_pos_yumi_left = np.array(end_pos_yumi_left)
print("TASK ACCOMPLISHED !!!")
clientsocket_1.close()
clientsocket_2.close()
