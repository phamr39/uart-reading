#!/usr/bin/python3
import time
import serial
import sys
import os
import random
import math
print("Swarm Robotics Team")
print("UART Demonstration Program")
print("NVIDIA Jetson Nano Developer Kit")
# class ProcessData:
#     def run():
class Tools:
    def SeprateData(data):
        print("Hello World!\n")
    def GetNumberOfDigitsBeforeComma(num):
        count = 0
        tmp = num
        while (tmp >=1):
            tmp = tmp/10
            count = count+1
        return count
    def ReadFile(path = ''):
        p_traj = []
        file_ = open(path,"r")
        lines = file_.readlines()
        for line in lines:
            try:
                x = float(line.split(',')[0])
                y = float(line.split(',')[1])
                p_traj.append(x)
                p_traj.append(y)
            except:
                continue
        print(p_traj)
        return p_traj
    def ConvertToRobotCoor():
        xgs_abs = [0,0,1,1,0,0]
        ygs_abs = [0,0,0,1,1,0]
        x_goals = []
        y_goals = []
        for i in range(2,len(xgs_abs)-1):
            phi = math.atan2(ygs_abs[i-1] - ygs_abs[i-2],xgs_abs[i-1] - ygs_abs[i-2])
            y_goal = (ygs_abs[i]*math.cos(phi)-xgs_abs[i]+ xgs_abs[i-1]-ygs_abs[i-1]*math.cos(phi))/(math.sin(phi)+math.pow(math.cos(phi),2))
            x_goal = (xgs_abs[i]-xgs_abs[i-1])/(math.cos(phi)) + math.tan(phi)*((ygs_abs[i]*math.cos(phi)-xgs_abs[i]+xgs_abs[i-1]-ygs_abs[i-1]*math.cos(phi))/(math.sin(phi) + math.pow(math.cos(phi),2)))
            x_goals.append(x_goal)
            y_goals.append(y_goal)
            print(i)
        print(x_goals)
        print('----------------------------')
        print(y_goals)
        return x_goals,y_goals

class CommUART:
    def UARTReceive():
        serial_port = serial.Serial(
            port="/dev/ttyTHS1",
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        # Wait a second to let the port initialize
        time.sleep(1)
        try:
            os.remove("position.txt")
            os.remove("debug.txt")
        except:
            print('No file to remove')
        deb_file = open("debug.txt", "w")
        try:
            # Send a simple header
            # serial_port.write("UART Demonstration Program\r\n".encode())
            # serial_port.write("NVIDIA Jetson Nano Developer Kit\r\n".encode())
            deb_file.write("Go to line 35, let's start \n")
            sign_code = []
            temp_pos = []
            start_flag = 0 
            end_flag = 0
            while(end_flag == 0):
                if serial_port.inWaiting() > 0:
                    deb_file.write("Reading data... \n")
                    buffer_flag = 1
                    data = serial_port.read().decode("utf-8")
                    # print(data)
                    # print('----')
                    if (data == '<'):
                        start_flag = 1
                    if (start_flag == 1):
                        if (data != '>'):
                            temp_pos.append(data)
                            # print('Mot con vit')
                        if (data == '>'):
                            start_flag = 0
                            end_flag = 1
                else:
                    buffer_flag = 0
                    # deb_file.write("Waiting for data... \n")
            # find start and end transmission code
            deb_file.write("Start processing data...  \n")
            for i in range(0,len(temp_pos)):
                if (temp_pos[i] == '(' or temp_pos[i] == ')'):
                    sign_code.append(i)
                    # print('Hai con ga')
            # print(sign_code)
            # create position 
            str_pos_x = ''
            str_pos_y = ''
            for p in range(0,len(temp_pos)-1):
                # Calculate pos x
                if (p > sign_code[0] and p < sign_code[1]):
                    str_pos_x = str_pos_x + temp_pos[p]
                if (p > sign_code[2] and p < sign_code[3]):
                    str_pos_y = str_pos_y + temp_pos[p]
            pos_x = str(str_pos_x)
            pos_y = str(str_pos_y)
            deb_file.write("Start writng file... \n")
            file_ = open("position.txt", "a")
            if (pos_x != '' and pos_y != '' and buffer_flag == 1):
                print('x: ',pos_x)
                print('y: ',pos_y)
                file_.write(pos_x)
                file_.write(',')
                file_.write(pos_y)
                file_.write('\n')
            end_flag = 1
            deb_file.write("Done \n")
            file_.close()
        except KeyboardInterrupt:
            deb_file.write("Keyboard Interrupt \n")
            print("Exiting Program")
            serial_port.close()

        except Exception as exception_error:
            deb_file.write("exception error \n")
            print("Error occurred. Exiting Program")
            print("Error: " + str(exception_error))

        # finally:
        #     serial_port.close()
        #     pass
    def UARTSend(p_traj = []):
        serial_port = serial.Serial(
            port="/dev/ttyTHS1",
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        i = 0
        while (i < len(p_traj)):
            ready_flag = serial_port.read().decode("utf-8")
            print('ready flag: ',ready_flag)
            while(ready_flag=='H'):
                list_digits = []
                print('Sending...',p_traj[i])
                if (p_traj[i]>=0):
                    list_digits.append('+')
                else:
                    list_digits.append('-')
                num_digs = Tools.GetNumberOfDigitsBeforeComma(p_traj[i])
                for ki in range(0,5-num_digs):
                    list_digits.append('0')
                tmp_num = int(abs(p_traj[i]*100))
                tmp_list_dgs = [int(d) for d in str(tmp_num)]
                for dg in tmp_list_dgs:
                    list_digits.append(str(dg))
                print(list_digits)
                for n in list_digits:
                    done_flag = serial_port.read().decode("utf-8")
                    print('Done flag: ',done_flag)
                    while (done_flag=="P"):
                        serial_port.write(str(n).encode())
                        done_flag = ''
                        print('Send ',n,'done')
                if (ready_flag=='H'):
                    i = i + 1
                ready_flag = ''  
        time.sleep(1)
        signal = serial_port.read().decode("utf-8")
        print("confirm: ",signal)
        time.sleep(1)
        print("Send done")
    def run():
        serial_port = serial.Serial(
            port="/dev/ttyTHS1",
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        while(1):
            pre_traj = []
            p_traj = []
            p_traj = Tools.ReadFile('test_trajectory.txt')
            # trajectory_changed = random.randint(0,1)
            if (p_traj.difference(pre_traj) != ''):
                n = 'S'
                for kjh in range(0,10):
                    serial_port.write(n.encode())
                CommUART.UARTSend(p_traj)
            else:
                CommUART.UARTReceive()
            pre_traj = p_traj
    def engine_test():
        while(1):
            CommUART.UARTReceive()
if __name__ == "__main__":
    # CommUART.UARTSend()
    # CommUART.UARTReceive()
    # CommUART.run()
    # CommUART.engine_test()
    # Tools.ReadFile('test_trajectory.txt')
    Tools.ConvertToRobotCoor()