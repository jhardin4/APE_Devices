# This Device represents a general G-Code motion system. 

# Only import 'basic' python packages up here.  All others should be imported
# within the methods.

# Handle the different relative locations for independently running and
#
from Devices import Sensor
from Devices import Motion

class Aerotech_A3200_FlexPrinter(Motion, Sensor):
    def __init__(self, name):
        Motion.__init__(self, name)

        self.descriptors = [*self.descriptors,
                            *['Aerotech', 'A3200', 'sensor']]

        self.tasklog = {'task1': [], 'task2': [], 'task3': [], 'task4': []}
        self.commandlog = []
        self.defaulttask = 1
        self.handle = ''

        # Possible modes are cmd and loadrun
        self.axes = ['X', 'x', 'Y', 'y',
                     'ZZ1', 'zz1', 'ZZ2', 'zz2', 'ZZ3', 'zz3', 'ZZ4', 'zz4',
                     'i', 'I', 'j', 'J', 'k', 'K']
        self.axismask = {}
        self.maxaxis = 4

        self.requirements['Set_Motion']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['Set_Motion']['length_units'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'length units for motion'}
        self.requirements['Set_Motion']['MotionRamp'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Ramp rate for a set of coordinated motions'}
        self.requirements['Set_Motion']['MaxAccel'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Maximum acceleration during coordinated motion'}
        self.requirements['Set_Motion']['LookAhead'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Activate multi-command motion planning'}
        self.requirements['Set_Motion']['axismask'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'how to convert between target and machine dimensions'}
        self.requirements['Set_Motion']['dtask'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'default task'}

        self.requirements['Move'] = {}
        self.requirements['Move']['point'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Information about where to move to'}
        self.requirements['Move']['motiontype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'kind of path taken to point'}
        self.requirements['Move']['speed'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'speed of the motion'}
        self.requirements['Move']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['Move']['motionmode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}

        self.requirements['set_DO'] = {}
        self.requirements['set_DO']['axis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'IO axis'}
        self.requirements['set_DO']['bit'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'bit on IO axis'}
        self.requirements['set_DO']['value'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'value of that bit.  0 or 1'}

        self.requirements['Run'] = {}
        self.requirements['Run']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Which task buffer to run'}

        self.requirements['getPosition'] = {}
        self.requirements['getPosition']['address'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Address of where to store result'}
        self.requirements['getPosition']['addresstype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Type of address'}
        self.requirements['getPosition']['axislist'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'List of axes that will be reported'}

        self.requirements['getAI'] = {}
        self.requirements['getAI']['address'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Address of where to store result'}
        self.requirements['getAI']['addresstype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Type of address'}
        self.requirements['getAI']['axis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Axis of AI'}
        self.requirements['getAI']['channel'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Channel on that axis'}

        self.requirements['Load'] = {}
        self.requirements['Load']['cmstr'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'String of commands to load'}
        self.requirements['Load']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['Load']['mode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}

        self.requirements['LogData_Start'] = {}
        self.requirements['LogData_Start']['file'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Where to store results'}
        self.requirements['LogData_Start']['points'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Maximum number of points to collect'}
        self.requirements['LogData_Start']['parameters'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': '{axis: [pc, pf, vc, vf, ac, af]...}'}
        self.requirements['LogData_Start']['interval'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}
        self.requirements['LogData_Start']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['LogData_Start']['mode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}

        self.requirements['LogData_Stop'] = {}
        self.requirements['LogData_Stop']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['LogData_Stop']['mode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}

    def Connect(self):
        if not self.simulation:
            from Devices.Drivers import A3200
            self.handle = A3200.A3200()
        self.addlog(self.name + ' is connected')

        return self.returnlog()

    def Disconnect(self):
        if not self.simulation:
            self.handle.disconnect()
        self.addlog(Motion.Disconnect(self))

        return self.returnlog()

    def Set_Motion(self, dtask='', axismask='', length_units='', RelAbs='', MotionRamp='', MaxAccel='', LookAhead='', dmotionmode='', dmotiontype='', motionmode='', task=''):
        # These direct assignments are somewhat queue jumping at the moment
        if dtask != '':
            self.defaulttask = dtask

        if dmotiontype != '':
            self.motiontype = dmotiontype

        if dmotionmode != '':
            self.motionmode = dmotionmode

        if task == '':
            task = self.defaulttask

        if motionmode == '':
            motionmode = self.motiontype

        # These do not que jump
        if axismask != '':
            self.fSet_axismask(axismask, task, motionmode)

        if RelAbs != '':
            self.fSet_RelAbs(RelAbs, task, motionmode)

        if length_units != '':
            self.fSet_length_units(length_units, task, motionmode)

        if MotionRamp != '':
            self.fSet_MotionRamp(MotionRamp, task, motionmode)

        if MaxAccel != '':
            self.fSet_MaxAccel(MaxAccel, task, motionmode)

        if LookAhead != '':
            self.fSet_LookAhead(LookAhead, task, motionmode)

        return self.returnlog()

    def fSet_axismask(self, axismask, task, motionmode, update=False):
        if update:
            self.axismask = axismask
            self.addlog('Axis mask changed to ' + str(self.axismask))
        else:
            kwargs = {'axismask': axismask, 'task': task, 'motionmode': motionmode, 'update': True}
            self.tasklog['task' + str(task)].append({'function': self.fSet_axismask, 'args': kwargs})

        self.fRun(motionmode,task)

    def fSet_LookAhead(self, LookAhead, task, motionmode):
        if LookAhead:
            self.tasklog['task' + str(task)].append('VELOCITY ON \n')
        else:
            self.tasklog['task' + str(task)].append('VELOCITY OFF \n')
        self.motionsetting['LookAhead'] = LookAhead

        self.fRun(motionmode, task)

    def fSet_MaxAccel(self, MaxAccel, task, motionmode):
        self.tasklog['task' + str(task)].append('CoordinatedAccelLimit = ' + str(MaxAccel) + '\n')
        self.motionsetting['MaxAccel'] = MaxAccel
        self.fRun(motionmode, task)

    def fSet_RelAbs(self, RelAbs, task, motionmode):
        if RelAbs == 'Rel':
            self.tasklog['task' + str(task)].append('G91 \n')

        if RelAbs == 'Abs':
            self.tasklog['task' + str(task)].append('G90 \n')

        self.motionsetting['RelAbs'] = RelAbs
        self.fRun(motionmode, task)

    def fSet_MotionRamp(self, MotionRamp, task, motionmode):
        self.tasklog['task' + str(task)].append('RAMP RATE ' + str(MotionRamp) + '\n')

        self.motionsetting['MotionRamp'] = MotionRamp
        self.fRun(motionmode, task)

    def fSet_length_units(self, length_units, task, motionmode):
        if length_units == 'mm':
            self.tasklog['task' + str(task)].append('G71 \n')

        if length_units == 'inch':
            self.tasklog['task' + str(task)].append('G70 \n')

        self.motionsetting['length_units'] = length_units
        self.fRun(motionmode, task)

    def Set_DO(self, axis='', bit='', value='', task='', motionmode=''):
        if motionmode == '':
            motionmode = self.motionmode

        if task == '':
            task = self.defaulttask

        if not self.simulation:
            cmdstr = '$DO' + '['+str(bit)+'].' + axis + ' = ' + str(value) + ' \n'
            self.tasklog['task'+str(task)].append(cmdstr)
        self.addlog('Bit ' + str(bit) + ' on the ' + str(axis) + ' set to ' + str(value))

        self.fRun(motionmode, task)

        return self.returnlog()

    def Move(self, point='', motiontype='', speed='', task='', motionmode=''):
        if task == '':
            task = self.defaulttask
        self.tasklog['task' + str(task)].append({'function': self.MotionCMD, 'args': [point, speed, motiontype]})

        self.fRun(motionmode, task)

        return self.returnlog()

    def MotionCMD(self, point, speed, motiontype):
        if motiontype == '':
            motiontype = self.motiontype
        cmdline = ''

        for dim in self.axismask:
            if dim in point:
                point[self.axismask[dim]] = point[dim]
                point.pop(dim, None)

        if motiontype == 'linear':
            axescount = 0
            cmdline += 'G01 '
            for axis in self.axes:
                if axis in point:
                    axescount += 1
                    if axescount > self.maxaxis:
                        #print(cmdline)
                        raise Exception('Number of axes exceeds ITAR limit.')
                    cmdline += axis + ' ' + '{0:f}'.format(point[axis]) + ' '
            cmdline += 'F ' + '{0:f}'.format(speed) + ' '
            cmdline += '\n'
        
        if motiontype == 'incremental':
            cmdline += 'MOVEINC '
            axis = list(point)[0]
            cmdline += axis + ' ' + '{0:f}'.format(point[axis]) + ' ' + '{0:f}'.format(speed)
            cmdline += '\n'
            
        self.addlog(cmdline)

        return cmdline

    def Run(self, task=''):
        self.fRun('cmd', task)

        return self.returnlog()

    def fRun(self, motionmode, task):
        if task == '':
            task = self.defaulttask

        if motionmode == '':
            motionmode = self.motionmode
        if motionmode == 'loadrun':
            self.addlog('Commands Loaded')
        elif motionmode == 'cmd':
            self.commandlog = self.tasklog['task' + str(task)]
            self.tasklog['task' + str(task)] = []
            cmdline = self.commandlog
            self.sendCommands(cmdline, task)
            self.commandlog = []

    def getPosition(self, address='', addresstype='', axislist=''):
        # Get the postion from the driver
        if not self.simulation:
            result = self.handle.get_position(axislist)
        else:
            result = input('What are simulation values for ' + str(axislist) + '?')

        # Store it at the target location
        self.StoreMeasurement(address, addresstype, result)
        self.log += (str(axislist) + ' measured to be ' + str(result))

        return self.returnlog()

    def getAI(self, address='', addresstype='', axis='', channel=''):
        # Get the postion from the driver
        if not self.simulation:
            result = self.handle.AI(axis, channel)
        else:
            rstring = input('What is the simulated value for ' + str(axis) + ' ' + str(channel) + '?')
            result = float(rstring)

        # Store it at the target location
        self.StoreMeasurement(address, addresstype, result)
        self.log = ('AI Axis ' + str(axis) + ' channel ' + str(channel) + ' measured to be ' + str(result))

        return self.returnlog()

    def sendCommands(self, commands, task):

        cmdmessage = ''
        for line in commands:
            if type(line) == str:
                cmdmessage += line
                self.addlog(line)
            elif type(line) == dict and line['function'] == self.MotionCMD:
                cmdmessage += line['function'](*line['args'])
            elif type(line) == dict:
                line['function'](**line['args'])
        if not self.simulation:
            self.handle.cmd_exe(cmdmessage, task=task)
        
    def LogData_Start(self, file='', points='', parameters='', interval='', task='', motionmode=''):
        if task == '':
            task = self.defaulttask
        self.tasklog['task' + str(task)].append("""
                     DATACOLLECT STOP
                     DATACOLLECT ITEM RESET
                     """)
        index = 0
        for dim in parameters:
            if type(parameters[dim]) == list:
                for element in parameter[dim]:
                    temp = 'DATACOLLECT ITEM %s, %s, DATAITEM_'%(str(index), dim)
                    if element[0] == 'p':
                        temp += 'Position'
                    elif element[0] == 'v':
                        temp += 'Velocity'
                    elif element[0] == 'a':
                        temp += 'Acceleration'
                    else:
                        raise Exception(dim + str(element) + ' is an unknown parameter')
                    
                    if element[1] == 'f':
                        temp += 'Feedback'
                    elif element[1] == 'c':
                        temp += 'Command'
                    else:
                        raise Exception(dim + str(element) + ' is an unknown parameter')
                    self.tasklog['task' + str(task)].append(temp + '\n')
                    index += 1
            self.tasklog['task' + str(task)].append('$task[0] = FILEOPEN "%s" , 0\n' % (file))
            self.tasklog['task' + str(task)].append('DATACOLLECT START $task[0], %s, %s\n' % (str(points), str(interval)))
            self.fRun(motionmode, task)
            return self.returnlog()

    def LogData_Stop(self, task='', motionmode=''):
        if task == '':
            task = self.defaulttask
        self.tasklog['task' + str(task)].append("""
                     DATACOLLECT STOP
                     FILECLOSE $task[0]
                     """)
        self.fRun(motionmode, task)
        return self.returnlog()


if __name__ == '__main__':
    myA3200 = Aerotech_A3200_FlexPrinter('myA3200')
    myA3200.simulation = True
    
