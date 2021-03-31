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
import math


imageR = input("Digite o path da imagem: ")
assert os.path.exists(imageR), "Imagem não encontrada em "+str(imageR)
print("imagem localizada em: {}".format(imageR))


class Client():
    def __init__(self, imageR):
        serialNameT = "COM6"                          # Windows(variacao de)
        self.com1 = enlace(serialNameT)
        self.com1.enable()

        self.payloads = self.create_payloads(imageR)
        self.n_packages = len(self.payloads)          # número de payloads
        
        self.payload_size = b'\x00\x00'
        self.this_package = 1                         # pacode atual

        self.ready = False

    def divide_img(self, lis, n):
        # fragmentação  
        # em intervalos de n = 114 --> tamanho dos payloads predefinido
        for i in range(0, len(lis), n):
            yield lis[i:i+n]     
        

    def create_payloads(self, imageR):
        with open(imageR, "rb") as img:
            txBuffer = img.read()
        txLen = len(txBuffer)
        payloads = list(self.divide_img(txBuffer, payloadSize)) # coloca pedaços que foram divididos em uma lista
        # print(payloads)
        return payloads 

    def create_handshake(self, payload_size):
        n_packages = self.n_packages.to_bytes(4, 'big')
        # len(txBuffer).to_bytes(2, 'big')
        handshake = n_packages + b'\x00\x00\x00\x00' + b'\x00\x00'
        handshake = handshake + eop
        return handshake

    def send_handshake(self):
        # Envia hanshake para o server
        print("---------------------")
        print("Enviando handshake...")
        print("---------------------")
        handshake = self.create_handshake(self.payload_size)
        self.com1.sendData(handshake)
        print("handshake enviado")
        print("---------------------")
        self.handshake_response()


    def handshake_response(self):
        # recebe resposta do handshake, confirmando recebimento
        t_inicial = time.time()
        response = False
        nHandshakeRes = 0

        while response == False:            
            
            if self.com1.rx.getBufferLen() >= 14: 
                handshakeRes, nHandshakeRes = self.com1.getData(14)
                print("Resposta do handshake recebida.")
                print("-------------------------------")

            time_elapsed = time.time() - t_inicial

            if nHandshakeRes > 0:                
                self.ready = True
                print("ready is {}".format(self.ready))
                response = True                
                break

            else:
                self.ready = False
            if time_elapsed > 5:
                try_again = input("Servidor inativo. Tentar novamente? S/N   ")
                if try_again == "N" or try_again == "n":
                    self.com1.disable() 
                    sys.exit()                
                else:
                    break    



    def create_head(self, n):
        # Cria o head dos pacotes, que informa 
        # quantidade de pacotes, pacote a ser enviado e o id do envio.    
        n_packages = self.n_packages.to_bytes(4, 'big')
        print(n_packages)
        # Teste informando tamanho errado do payload
        # len_payloads = len(self.payloads[n-1]) +1
        len_payloads = len(self.payloads[n-1])

        payload_size = len_payloads.to_bytes(2,'big')
        print("Tamanho do payload: {}".format(payload_size))
        head = n_packages + n.to_bytes(4, 'big') + payload_size
        return head

    def create_package(self, head, this_package):
        package = head + self.payloads[this_package-1] + eop
        # print(head[2])
        print(package)
        return package

    def send_package(self, package):
        self.com1.sendData(package)

    def package_response(self):
        # Recebe confirmação do server
        packResponse, nPackResponse = self.com1.getData(14)
        print(packResponse)
        print("----------------------------")
        print("Resposta do pacote recebida.")
        print("----------------------------")
        # self.com1.disable()


    def main(self):
        while not self.ready:
            self.send_handshake()
        t_inicial = time.time()

        while self.this_package <= self.n_packages and self.ready:
            print("MAIN RODANDO")
            # Para o teste de número de pacote errado:
            # head = self.create_head(self.this_package + 1)
            
            head = self.create_head(self.this_package)
            package = self.create_package(head, self.this_package)

            self.send_package(package)
            print(f"Pacote {self.this_package} enviado")

            response_package = True

            while self.com1.rx.getIsEmpty():
                # print("entrou nesse while")
                time_elapsed = time.time() - t_inicial
                response_package = True
                if time_elapsed > 5:
                    response_package = False
                    try_again = input("Servidor inativo. Tentar novamente? S/N  ")
                    if try_again == "N" or try_again == "n":
                        self.com1.disable()
                        sys.exit()
                    elif try_again == "S" or try_again == "s":
                        break

            if response_package:
                print("resposta do pacote {} recebida".format(self.this_package))
                self.package_response()
                self.this_package +=1
                print("Pacote atual: {}".format(self.this_package))

            t_inicial = time.time()
            print("---------------")
            print(self.n_packages)
            print(self.this_package)

            if self.this_package == self.n_packages:
                self.com1.rx.clearBuffer()
                print("Todos pacotes enviados")
                self.com1.disable()
                sys.exit()

client = Client(imageR)
client.main()
                









# create_payloads(imageR)  
# print("Payloads criados com sucesso!")
# print("-----------------------------")
    # def main():
    #     try:
    #         com1 = enlace(serialNameT)
    #         com1.enable()

    #         print("Client TX ativado em: {}".format(serialNameT))
    #         print("Comunicação aberta com sucesso!")
    #         print("---------------------")

            # header = len(txBuffer).to_bytes(2, 'big')
            # header_int = int.from_bytes(header, "big")
            # print("Enviando header")
                
            # print("--------------------")        
            # com1.sendData(np.asarray(header))
            # print("enviado com sucesso!")
            # print("Header: {}".format(header)) 
            # print("Tamanho enviado: {}".format(header_int))
            # print("--------------------")

            # headerR, nHR = com1.getData(2)
            # headerR_int = int.from_bytes(headerR, "big")

            # print("Resposta do header: {}".format(headerR))
            # print("Tamanho recebido: {}".format(headerR_int))
            # print("Recebida resposta do header")
            # print("--------------------")

            # if header_int == headerR_int:

            #     print("iniciando time...")
            #     timeStart = time.time()
            #     print("---------------------")

            #     print("Enviando payload")
            #     print("--------------------")
            #     com1.sendData(np.asarray(txBuffer))

            #     print("Esperando resposta...")
            #     rxBuffer, nRx  = com1.getData(txLen) 
            #     print("Procedimento concluído") 

            #     tempo = time.time() - timeStart
            #     taxa = txLen/tempo
                
            #     print("___________________________________________________")   
            #     print("Tempo gasto para envio e recebimento: {}".format(round(tempo, 3)))
            #     print("Taxa de transmissão (bytes por segundo): {}".format(round(taxa, 3)))
            #     print("___________________________________________________")

            #     print("-------------------------")
            #     print("Comunicação encerrada")
            #     print("-------------------------")
            # com1.disable()

            
#         except Exception as erro:
#             print("ops! :-\\")
#             print(erro)
#             com1.disable()
        

#     #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
# if __name__ == "__main__":
#     main() 