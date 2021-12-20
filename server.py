from scapy.all import *




class Quick_Maths_Server():

    def __init__(self, *args):
        self.LookingForClient=False
        self.Connection=[]
        self.BUFFER_SIZE=4080

        self.TimeOut =10   # time out in second
        pass

    def _conectionThredRun(self, sock):  #lissening to new clients 
        try:
            while  self.LookingForClient:
                conn, address = sock.accept()   #open a connection
                self.Connection.append(conn)    #add the connection to the connection list
                # connect to a client
                connect_with_client_thread = threading.Thread(target = self._clientConectionThredRun, args =(conn, address))
                connect_with_client_thread.start()
        except:
            print("some network error...")
        
    def _clientConectionThredRun(self , conn , address): #handeling a client connection
        try:
            newClientName = None
            if  self.LookingForClient:
                
                while "\n" not in newClientName:
                    time.sleep(1)
                    newClientName =  (conn.recv(self.BUFFER_SIZE)).decode() if newClientName == None else  newClientName + (conn.recv(self.BUFFER_SIZE)).decode()
                    
                # read untill the \n
                newClientName = newClientName[:newClientName.index("\n")]
        except:
            pass
    
    def run(self):
        self.LookingForClient=True
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', 0)) #set up the port that the os will give us
            sock.settimeout(self.TimeOut)
            sock.listen(1)

            clientConectionThred=threading.Thread(target=_conectionThredRun, args=(sock,))
            clientConectionThred.start()


        except :
           pass 




        
        