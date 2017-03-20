import bpy
import socket
import sys
import threading


bl_info = {
    "name": "Informal Kinect Reader",
    "description": "Kinect Reader to receive Bones data.",
    "author": "Porfirio Partida (porfiriopartida)", 
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "View3D > Toolbar > Kinect Reader",
    "category": "Animations",
    'wiki_url': '',
    'tracker_url': ''
}

kinectServer = None
address = "localhost"
packetSize = 1024

class KinectServer:
    global address, packetSize
    
    listening = False

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.sock = None
        self.active = True

    def toString(self):
        return ("[address=%s, port=%s]" % self.address, self.port)

    def stop(self):
        self.active = False
        KinectServer.listening = False

        if(self.sock is not None):
            self.sock.close()

    def start(self):
        threading.Thread(target = self.listenToClients).start()

    def listenToClients(self):
        KinectServer.listening = True

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the port
        server_address = (self.address, self.port)
        print ('starting up on %s port %s' % server_address)
        self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(0)

        while self.active:
            # Wait for a connection
            print ('waiting for a connection')
            connection = None
            try:
                connection, client_address = self.sock.accept()
                threading.Thread(target = self.handleClient,args = (connection, client_address)).start()
            except:
                if(connection is not None):
                    connection.close()
                print('connection.close')
                return False
        print('Killing Clients listener.')

    def handleClient(self, connection, client_address):
        try:
            print ('connection from', client_address)
            # Receive the data in small chunks and retransmit it
            while self.active:
                data = connection.recv(packetSize)
                print ('received "%s"' % data)
                if data:
                    print('sending data back to the client')
                    connection.sendall(data)
                else:
                    break
        except:
            connection.close()
            print('connection closed')
            return False

#   Layout panel
class LayoutPanel(bpy.types.Panel):
    bl_label = "Connection"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "KinectReader"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column()
        col.enabled = not KinectServer.listening
        col.prop(scene, "informal_port")
 
        #row = layout.row(align=True)
        #row.alignment = 'EXPAND'

        if(not KinectServer.listening):
            layout.operator("informal.start_kinect_server_action", text="Start Listening")
        else: 
            layout.operator("informal.stop_kinect_server_action", text="Stop Listening")

# PANELS - UI

class InformalKinectConfiguration(bpy.types.Panel):
    bl_idname = "informal.InformalKinectConfiguration"
    bl_category = "KinectReader"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    
    bl_label = "Configuration"
    bl_description = "Main Configuration Panel, specify port"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column()
        
        col.prop(scene, "informal_is_kinect_2")

# INVOKERS

class StopKinectServerAction(bpy.types.Operator):
    bl_idname = "informal.stop_kinect_server_action"
    bl_label = "Stop Listening"
    def execute(self, context):
        global kinectServer
        print("Killing server...")
        if(kinectServer is not None):
            kinectServer.stop()
            kinectServer = None
        return{'FINISHED'}
        
class StartKinectServerAction(bpy.types.Operator):
    bl_idname = "informal.start_kinect_server_action"
    bl_label = "Start Listening"
    def execute(self, context):
        global address, kinectServer
        port = context.scene.informal_port
        print("Trying to start server on [ %s  :%s]" % (address, port))
        kinectServer = KinectServer(address, port)
        kinectServer.start()
        return{'FINISHED'}   

#########################
###### END INVOKERS #####
#########################


### GLOBAL FUNCTIONS

# Initialize scene properties
def init_properties():
    scene = bpy.types.Scene
    scene.informal_is_kinect_2 =bpy.props.BoolProperty(
        name="Use Kinect 2",
        description="Kinect 1 vs Kinect 2 checkbox (Kinect 2 is not implemented yet)")
    
    scene.informal_port = bpy.props.IntProperty(
        name="Port",
        description="Port to Receive the Kinect Data",
        default = 8907,
        min = 0,
        max = 65535)

    # bpy.props.EnumProperty(
    #     name="Create",
    #     items = [('NONE', 'Nothing', "Don't create objects based on received data"),
    #             ('EMPTIES', 'Empties', 'Create empties based on received data'),
    #             ('SPHERES', 'Spheres', 'Create spheres based on received data'),
    #             ('CUBES', 'Cubes', 'Create cubes based on received data')])




# Delete current properties for cleanup purposes.
def clearProperties():
    scene = bpy.types.Scene
    del scene.informal_port
    del scene.informal_is_kinect_2

# When the plugin is checked
def register():
    init_properties()
    bpy.utils.register_module(__name__)
# When the plugin is unchecked
def unregister():
    clearProperties()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()