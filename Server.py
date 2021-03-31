#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
from testes import *
import time
import numpy as np
import os
import io
import subprocess
import logging
import PIL.Image as Image
import sys
import time

imageW = './img/imgCopia.jpg'

class Server():
    def __init__(self):
        serialNameR = "COM3"                  # Windows(variacao de)
        self.com2 = enlace(serialNameR)
        self.com2.enable()
        print('comunicação aberta com sucesso')
        print("Server Rx habilitado em: {}".format(serialNameR))
        print("---------------------")

        self. n_packages = 0
        self.size = None
        self.nthis_package = 0
        self.eop = b'\xAA\xA1\xA2\xA3'
        self.ready = False

        self.order_ok = True
        self.msg = None


    def receive_handshake(self):
        t_inicial = time.time()
        timer = 1

        if self.ready == False:
            print("Entrou no if. Ready é {}".format(self.ready))
            while self.com2.rx.getIsEmpty():
                time_elapsed = time.time() - t_inicial
                if time_elapsed > 5:
                    print("Tentando novamente...")
                    print("---------------------")
                    timer += 1
                    t_inicial = time.time()
                
                if timer > 4:
                    print("não vai msm não, sry =( ")
                    print("--------------------")
                    self.com2.fisica.flush()
                    self.com2.disable()
                    sys.exit()
                    break

        print("Não entrou no if. Tá pronto para receber o pacote!")

        package, nPackage = self.com2.getData(14) #pegando um pacote inteiro (tamanho total de 14 bytes!)

        print(package)
        self.size = int.from_bytes(package[4:8], "big")
         
        print("tamanho do pacote é: {}".format(self.size))
        self.n_packages = package[3]
        print("Total de pacotes: {}".format(self.n_packages))
        print("--------------------")
        self.ready = True

    
    def create_handshakeResponse(self):
        # self.n_packages = self.n_packages.to_bytes(4, "big")
        handshake = b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00' + b'\x00\x00'
        handshake = handshake + eop
        print(handshake)
        print("resposta do handshake criada")
        return handshake

    def send_handshakeResponse(self):
        handshake = self.create_handshakeResponse()
        self.com2.sendData(handshake)
        print("Resposta do handshake enviada.")
        # self.n_packages = 1


    def send_packageResponse(self):
        n_packagesbyte = self.n_packages.to_bytes(4, 'big')
        head_response = n_packagesbyte + b'\x00\x00\x00\x00' + b'\x00\x00'
        response = head_response + eop

        # int_package = int.to_bytes(self.n_packages, 'big')   
             
        # print(self.nthis_package)
        # print(self.n_packages)

        if self.nthis_package - 1 <= self.n_packages:
            self.com2.sendData(response)
            ####################################### verificar:
            if self.nthis_package - 1 == self.n_packages:
                self.com2.rx.clearBuffer()
                self.com2.disable()
                sys.exit()   
    
    
    def check_eop(self, head, eop):
        if eop == self.eop:
            print("eop correto")
            #Só enviará a resposta se o eop estievr correto
            if self.order_ok == True:
                print("------------------------------")
                print("Enviando resposta do pacote...")
                self.send_packageResponse()
                print("Resposta do pacote enviada")
                print("------------------------------")
        else:
            print("eop veio errado")
            print(eop)
        pass

    def check_order(self, head):
        # Verificar se o número do pacote é um a mais do que o anterior.
        print("-----------------------------------")
        print("Checando a ordem")
        # print(head[4:8])
        head_nPack = int.from_bytes(head[4:8], "big")
        # print(head_nPack)
        # print(self.nthis_package)          

        if head_nPack == self.nthis_package:
            print("-------------")
            print("tudo em ordem")
            print("-------------")
            self.order_ok == True
            self.nthis_package += 1
            print(self.nthis_package)
            self.timer = time.time()
        
        else:
            self.order_ok = False
            print("último pacote recebido: {}".format(self.nthis_package))
            # print("pacote recebido agora: {}".format(head[self.nthis_package]))
            print(head[4:8])
            head_thisPack = int.from_bytes(head[4:8], "big")
            print("Pacote {} fora de ordem".format(head_thisPack))
            sys.exit()


    def add_package(self, payload):
        # Adiciona o payload recebido ao existente.
        if self.msg == None or len(self.msg) == 0:
            self.msg = payload
            print("------------------------------------")
            print("Condição da mensagem antes como None")
            # print("msg is: {}".format(self.msg))
            print("------------------------------------")
            print("tamanho da msg: {}".format(len(self.msg)))
        else:
            self.msg += payload
            # print("msg is: {}".format(self.msg))      




    #________________RECEBENDO_PACOTES________________#


    def receive_package(self):
        # counter_data = 0
        print("----------------------------------------------")
        print("Iniciando processo para recepção do pacote....")
        print("----------------------------------------------")

        head = self.com2.rx.getNData(10)           

        print("head is {}".format(head))
        print(head[7:])
        
        self.check_order(head)

        head_idFile = int.from_bytes(head[8:], "big")

        # payload, nPayload = self.com2.getData(head_idFile)

        # Para teste com tamanho do payload não correspondente ao que foi informado
        # no header.
        payload, nPayload = self.com2.getData(head_idFile + 1)

        if int.from_bytes(head[8:], 'big') == nPayload: 
            # print("número de pacotes a serem recebidos: {}".format(head[9])
            print("------------------------------------------------------------------")
            print("payload is {}: ".format(payload))
            print("------------------------------------------------------------------")
            print("ordem_ok is: {}".format(self.order_ok))

            if self.order_ok == True:
                self.add_package(payload)
                print(self.msg)
                
            eop, nEop = self.com2.getData(4)
            self.check_eop(head, eop)
            print(eop)
            time.sleep(1)

            if self.nthis_package == self.n_packages:
                print("todos os pacotes recebidos! Encerrando...")
                print("-----------------------------------------")     

        else: 
            print("-------------------------------------------------------------------------")
            print("Tamanho real do payload do pacote não corresponde ao informado pelo head.")
            print("-------------------------------------------------------------------------")
        


    #_______________________Main______________________#


    def main(self):
        while not self.ready:
            self.receive_handshake()
            time.sleep(1)
            self.send_handshakeResponse()

        self.nthis_package = 1
        # int_npackages = int.from_bytes(self.n_packages, 'big')
        print("Número dos pacotes: {}".format(self.n_packages))

        while self.nthis_package < self.n_packages:
            self.timer = time.time()
            self.receive_package()

        f = open(imageW, 'wb')
        f.write(self.msg)
        self.com2.disable()

        sys.exit()

server = Server()
server.main()

    


        





            







# def getHandshake(com):
#     handshake, nHandshake = com.getData(14)
#     print("----------------------------------")
#     print("get do hanshake feito com sucesso!")
#     print("----------------------------------")
#     time.sleep(0.1)

    



# def main():
#     try:
#         #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
#         #para declarar esse objeto é o nome da porta.
#         print("A recepção vai começar")        
        
#         com2 = enlace(serialNameR)

#         # Ativa comunicacao. Inicia os threads e a comunicação seiral 
#         com2.enable()

#         imageW = './img/' + input('Nomeie a imagem que vai receber! ') + 'Copia.jpg'

#         #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
#         print('comunicação aberta com sucesso')
#         print("Server Rx habilitado em: {}".format(serialNameR))
#         print("---------------------")

#         print("local da imagem a ser salva: {}".format(imageW))
#         print("---------------------")        

#         print("Esperando Header...")
        
#         header, nHr = com2.getData(2)      
        
#         print("---------------------")
#         print("Header recebido com sucesso!")
#         print("---------------------")
#         time.sleep(1)


#         print("Enviando resposta do header para o cliente...")  
#         com2.sendData(np.asarray(header))
#         print("---------------------")

#         HeadR = int.from_bytes(header, "big")

#         print("Esperando dados do payload do cliente...")
#         print("--------------------")    

#         rxBuffer, nRx = com2.getData(HeadR)     

#         print("Payload recebido!")
#         print("--------------------")

#         print("Pasasando os dados para o cliente...")
#         com2.sendData(np.asarray(rxBuffer))
#         time.sleep(1)
#         print("--------------------")             
              

#         print("Salvando imagem em: {}".format(imageW))   
#         print(" - {}".format(imageW))


#         f = open(imageW, 'wb')
#         f.write(rxBuffer)

       
#         print("-------------------------")
#         print("Comunicação encerrada")
#         print("-------------------------")
#         com2.disable()

        
#     except Exception as erro:
#         print("ops! :-\\")
#         print(erro)
#         com2.disable()
        

#     #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
# if __name__ == "__main__":
#     main()
