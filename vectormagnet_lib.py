"""
Created on Tue Oct 18 13:26:38 2022

@author: Tzu-Hsiang Lo
@adapted from the cryogenics script 
"""

import socket

class MSS_Control:
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 8087)
        self.terminator = '\r\n'
        
    def connect(self):
        self.sock.connect(self.server_address)
        print('The system is connected.')
        
        
        
    # Temperature controller ----------------------------------------------------------------------
    
    def VTI_set1(self, value):
        # Set the target temperature for output 1
        
        message =  'VTI_set1 %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        #print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        #print("received response: %s" % response)
        
    def VTI_set2(self, value):
        # Set the target temperature for output 2
        
        message =  'VTI_set2 %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        #print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        #print("received response: %s" % response)
        
    def VTI_set3(self, value):
        # Set the target temperature for output 3
        
        message =  'VTI_set3 %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VTI_set4(self, value):
        # Set the target temperature for output 4
        
        message =  'VTI_set4 %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        
    def VTI_getsensA(self):
        # get the value for sensor A
        
        message =  'VTI_getsensA' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        #print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        #print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return round(value, 2)
        
    def VTI_getsensB(self):
        # get the value for sensor B
        
        message =  'VTI_getsensB' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        #print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        #print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return round(value, 2)
        
    def VTI_getsensC(self):
        # get the value for sensor C
        
        message =  'VTI_getsensC' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return round(value, 2)
        
    def VTI_getsensD(self):
        # get the value for sensor D
        
        message =  'VTI_getsensD' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return round(value, 2)
    
    def VTI_getsetpoint1(self):
        # get the target temperature for output 1
        
        message =  'VTI_getsetpoint1' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        #print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        #print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
    
    def VTI_getsetpoint2(self):
        # get the target temperature for output 2
        
        message =  'VTI_getsetpoint2' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        #print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        #print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VTI_getsetpoint3(self):
        # get the target temperature for output 3
        
        message =  'VTI_getsetpoint3' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VTI_getsetpoint4(self):
        # get the target temperature for output 4
        
        message =  'VTI_getsetpoint4' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VTI_gettcstatus(self):
        # get status of temperature controller
        
        message =  'VTI_gettcstatus' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VTI_setNewPID(self, value):
        # set new PID. Value format: output#,P,I,D
         
        message =  'VTI_setNewPID %d %.2f %.2f %.2f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
         
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VTI_setNewRange(self, value):
        # set new Range. Value format: output#,Range#
        
        message =  'VTI_setNewRange %d %d' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
         
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
    
    
    
    # Vecotor Magnet -------------------------------------------------------------
    
    def VM_setAbort(self):
        # Aborts ramp or path calculation
        
        message =  'VM_setAbort' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VM_setCalculatePath(self, value):
        # calculate the path to ramp to target
        
        message =  'VM_setCalculatePath %s' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VM_setCoordinateSystem(self, value):
        # set the coordinate of VM to either Cartisian (0) or Spherical (1)
        
        message =  'VM_setCoordinateSystem %d' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VM_getCoordinateSystem(self):
        # Get the coordinate being used for path calculation. Cartesian (0) or Spherical (1).
        
        message =  'VM_getCoordinateSystem' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received responsee: %s" % response )
        
        value = float(response.split(';')[0])
       
        return value
     
    def VM_getCountdown(self):
        # Get the time to target in units of seconds
        
        message =  'VM_getCountdown' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)

        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')

        
        value = float(response.split(';')[0])
        
        return value
    
        
    def VM_setPathCalculationType(self, value):
        # Set the Path Calculation Type. 
        # (0): Calculate by time; (1): Calculate by Ramp rate.
        
        message =  'VM_setPathCalculationType %d' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
    
    def VM_getPathCalculationType(self):
        # Get the Path Calculation Type. 
        # (0): Calculate by time; (1): Calculate by Ramp rate.
        
        message =  'VM_getPathCalculationType' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
    
    
    def VM_setPMode(self, value):
        # Set the magnet into persistent mode. 
        # Make sure that the ready (getReady) value is True (1).
        
        message =  'VM_setPMode %d' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VM_getPMode(self):
        # Get the persistent mode status of the vector magnet. Make sure that the ready (getReady) value is True (1).
        
        message =  'VM_getPMode' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_setRamp(self):
        # Ramp the Magnet to target
        
        message =  'VM_setRamp' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)

    def VM_getReady(self):
        # Get the ready status of the Vector Magnet. If it is not ready then do not perform any path calculation or ramp.
        # (0): system not ready; (1): system ready
        
        message =  'VM_getReady' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_setRotation(self, value):
        # Set the rotation direction if coordinate system is in Spherical mode.
        # (0): anticlockwise; (1): clockwise
        
        message =  'VM_setRotation %d' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VM_getRotation(self):
        # Get the rotation direction if the coordinate system is in Spherical mode.
        # (0): anticlockwise; (1): clockwise
        
        message =  'VM_getRotation' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_setRotAxisType(self, value):
        # Set the rotation axis type. 
        # (0): x-axis; (1): y-axis; (2): z-axis; (3): AxB
        # If z-axis (2) then the rotation will be about Z. 
        # If AxB (3) then it would rotate about the axis that is perpendicular to the initial and final vector 
        
        message =  'VM_setRotAxisType %d' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VM_getRotAxisType(self):
        # Get the rotation axis type. 
        # (0): x-axis; (1): y-axis; (2): z-axis; (3): AxB
        # If z-axis (2) then the rotation will be about Z. 
        # If AxB (3) then it would rotate about the axis that is perpendicular to the initial and final vector 

        message =  'VM_getRotAxisType' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
    
    def VM_getStatus(self):
        # Get the status of the vector magnet. 
        
        message =  'VM_getStatus' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        return response
        
    def VM_setTime(self, value):
        # Set the ramp time needed if Path calculation type (VM_setPathCalculationType) 
        # is set to calculate by time.
        
        message =  'VM_setTime %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VM_getTime(self):
        # Get the ramp time. 
        # If Path Calculation type is by time (0) 
        # then this value is the same as the value set in VM_setTime. 
        # However if the Path Calculation Type is by ramp rate (1) 
        # then this value will be according to the ramp rate used.
        
        message =  'VM_getTime' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_setUserRotationAngle(self, value):
        # Set the User rotation angle if the rotation axis type (VM_setRotationAxisType) 
        # is set to User defined (4)
        
        message =  'VM_setUserRotationAngle %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VM_getUserRotationAngle(self):
        # Get the User rotation angle if the rotation axis type (VM_setRotationAxisType) 
        # is set to User defined (4)
        
        message =  'VM_getUserRotationAngle' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_setUserRotationAxis(self, value):
        # Set the user rotation axis vector x,y,z.
        
        message =  'VM_setUserRotationAxis %f%f%f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VM_getUserRotationAxis(self):
        # Get the user rotation axis vector x,y,z.
        
        message =  'VM_getUserRotationAxis' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        return response
        
    def VM_getBField(self):
        # Get the magnitude of the magnetic field, used in Spherical mode.
        
        message =  'VM_getBField' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
    
    def VM_setBTarget(self, value):
        # Set the magnitude of the target magnetic field, used in Spherical mode.
        
        message =  'VM_setBTarget %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        
    def VM_getBTarget(self):
        # Get the magnitude of the target magnetic field, used in Spherical mode
        
        message =  'VM_getBTarget' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_setTargetPhi(self, value):
        # Set the target phi angle of the magnetic field (B), used in Spherical mode.
        
        message =  'VM_setTargetPhi %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
    
    def VM_getTargetPhi(self):
        # Get the target phi angle of the magnetic field (B), used in Spherical mode.
        
        message =  'VM_getTargetPhi' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_getPhi(self):
        # Get the phi angle of the magnetic field (B), used in Spherical mode.
        
        message =  'VM_getPhi' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value

    def VM_setTargetTheta(self, value):
        # Set the target theta angle of the magnetic field (B), used in Spherical mode.
        
        message =  'VM_setTargetTheta %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def VM_getTargetTheta(self):
        # Get the target theta angle of the magnetic field (B), used in Spherical mode.
        
        message =  'VM_getTargetTheta' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value

    def VM_getTheta(self):
        # Get the theta angle of the magnetic field (B), used in Spherical mode.
        
        message =  'VM_getTheta' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value

    def VM_getXAmps(self):
        # Get the value of the X field in Amps
        
        message =  'VM_getXAmps' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_getXField(self):
        # Get the value of the X field in Tesla
        
        message =  'VM_getXField' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_setXTargetField(self, value):
        # Set the Target X field in Tesla
        
        message =  'VM_setXTargetField %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)

    def VM_getXTargetField(self):
        # Get the Target X field in Tesla
        
        message =  'VM_getXTargetField' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_setXRampRate(self, value):
        # Set the X field Ramp rate, in units of A/s
        
        message =  'VM_setXRampRate %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)

    def VM_getXRampRate(self):
        # Get the X field Ramp rate, in units of A/s
        
        message =  'VM_getXRampRate' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value

    def VM_getYAmps(self):
        # Get the value of the Y field in Amps
        
        message =  'VM_getYAmps' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
    
    def VM_getYField(self):
        # Get the value of the Y field in Tesla
        
        message =  'VM_getYField' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_setYTargetField(self, value):
        # Set the Target Y field in Tesla
        
        message =  'VM_setYTargetField %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)

    def VM_getYTargetField(self):
        # Get the Target Y field in Tesla
        
        message =  'VM_getYTargetField' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
        
    def VM_setYRampRate(self, value):
        # Set the Y field Ramp rate, in units of A/s
        
        message =  'VM_setYRampRate %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)

    def VM_getYRampRate(self):
        # Get the Y field Ramp rate, in units of A/s
        
        message =  'VM_getYRampRate' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
    
    def VM_getZAmps(self):
        # Get the value of the Z field in Amps
        
        message =  'VM_getZAmps' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
    
    def VM_getZField(self):
        # Get the value of the Z field in Tesla
        
        message =  'VM_getZField' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
    
    def VM_setZTargetField(self, value):
        # Set the Target Z field in Tesla
        
        message =  'VM_setZTargetField %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)

    def VM_getZTargetField(self):
        # Get the Target Z field in Tesla
        
        message =  'VM_getZTargetField' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
    
    def VM_setZRampRate(self, value):
        # Set the X field Ramp rate, in units of A/s
        
        message =  'VM_setZRampRate %f' % value + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)

    def VM_getZRampRate(self):
        # Get the X field Ramp rate, in units of A/s
        
        message =  'VM_getXRampRate' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
        value = float(response.split(';')[0])
        
        return value
    
        
    # Temperature Monitor --------------------------------------------------------------
    
    def TMon_getTemp(self):
        # get the values of the sensors from the temperature monitor 
        # in the order seen on the Temperature monitor VI
        
        message =  'TMon_getTemp' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
    
    def TMon_getNameTemp(self):
        # get the names of the temperature sensors
        
        message =  'TMon_getNameTemp' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print("received response: %s" % response)
        
    def TMon_getNameAndTemp(self):
        # get the names and values of the temperature sensors
        
        message =  'TMon_getNameTemp' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        #print("received response: %s" % response)
        response = response.split(',')
        
        name = []
        for i in range(len(response)):
            name.append(response[i])
            
        message =  'TMon_getTemp' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        #print("received response: %s" % response) 
        response = response.split(',')
        
        temp = []
        for i in range(len(response)):
            temp.append(response[i])
        print(len(temp))
        for j in range(len(response)):
            print("%s: %s" % (name[j], temp[j]))
            
    def TMon_getHallRes(self):
        # get the values of the hall sensors in Ohms
        
        message =  'TMon_getHallRes' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        print(" received response: %s" % response)

    def TMon_getHallField(self):
        # get the hall sensors in Tesla (provided the conversion file is configured)
        
        message =  'TMon_getHallField' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        #print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        #print(response_received)
        response = response_received.decode('utf-8')
        response = response.split(",")
        #print(" received response: %s" % response)
        x_field = response[0]
        y_field = response[1]
        z_field = response[2][:8]
        
        #print(response)
        #print(x_field[:8])
        #print("haha")
        #print(y_field)
        #print(z_field)
        #print(type(response))
        
        return (x_field, y_field, z_field)
    
    def TMon_getHallNameField(self):
        # get the names of the hall sensors
        
        message =  'TMon_getHallNameField' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        print(response_received)
        response = response_received.decode('utf-8')
        print(" received response: %s" % response)
        
    def TMon_getHallNameAndField(self):
        # get the names adn values of the hall sensors
        
        message =  'TMon_getHallNameField' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        response = response_received.decode('utf-8')
        #print(" received response: %s" % response)
        response = response.split(',')
        name = []
        for i in range(len(response)):
            name.append(response[i])
        
        message =  'TMon_getHallField' + self.terminator
        message_sent = bytearray(message,"ASCII")
        self.sock.sendall(message_sent)
        print("sent message: %s" % message)
        
        response_received = self.sock.recv(1024)
        print(response_received)
        response = response_received.decode('utf-8')
        #print(" received response: %s" % response)
        response = response.split(',')
        field = []
        for i in range(len(response)):
            field.append(response[i])
            
        for j in range(len(response)):
            print("%s: %s" % (name[j], field[j]))


    def close(self):
        self.sock.close()
        print('The system is closed')
        
