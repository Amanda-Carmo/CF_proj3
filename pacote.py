from Client import payloads
from Client import txLen

class Head:
    '''
    h0: tamanho de pacotes
    h1: pacote atual
    h2: id do arquivo
    '''

    def __init__(self, h0, h1, h2):
        self.h0 = h0.to_bytes(3, byteorder="big")
        self.h1 = h1.to_bytes(3, byteorder="big")
        self.h2 = h2.to_bytes(2, byteorder="big")
        # self.h3 = h3.to_bytes(2, byteorder="big")

        self.nPackages = h0
        self.thisPackage = h1
        self.idFile = h2
        # self.error = h3

    def head_to_bytes(self):
        h0 = self.h0
        h1 = self.h1
        h2 = self.h2
        # h3 = self.h3

        Bytes = h0 + h1 + h2

        return Bytes


class Package:
    def __init__(self, head, i, eop):
        self.eop = eop
        self.head = head
        # self.txLen = txLen

        if i != 0:
            self.package = head + payloads[i-1] + self.eop
        
        else:
            self.package = head + eop

    def sendPackage(self, com):
        print("------------------")
        print("Enviando pacote...")
        print("------------------")

        com.sendData(self.package)
        print("Pacote enviado com sucesso!")
        print("---------------------------")

    def getPackage(self, com):
        com.getData(txLen)

