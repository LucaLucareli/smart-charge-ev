from machine import Pin, I2C
import time

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

devices = i2c.scan()
if not devices:
    print("Aviso: LCD não encontrado. Trocando para endereço padrão.")
    
    I2C_ADDR = 0x27
else:
    I2C_ADDR = devices[0]

def lcd_write(cmd, mode=0):
    high = (cmd & 0xF0) | mode | 0x08
    
    low = ((cmd << 4) & 0xF0) | mode | 0x08
    
    i2c.writeto(I2C_ADDR, bytearray([high | 0x04, high, low | 0x04, low]))

def lcd_init():
    for cmd in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_write(cmd)
    
        time.sleep_ms(2)

def lcd_print(texto, linha=0):
    enderecos = [0x80, 0xC0, 0x94, 0xD4]
    
    lcd_write(enderecos[linha])

    texto_formatado = texto + " " * (20 - len(texto))

    for char in texto_formatado[:20]:
        lcd_write(ord(char), 1)

lcd_init()
lcd_print(" Sistema Iniciando  ", 1)
lcd_print(" Aguarde...         ", 2)
time.sleep(1)
lcd_write(0x01)

pin_K = Pin(2, Pin.IN, Pin.PULL_DOWN) # Hardware OK
pin_F = Pin(3, Pin.IN, Pin.PULL_DOWN) # Energia OK
pin_H = Pin(4, Pin.IN, Pin.PULL_DOWN) # Horário de Pico
pin_P = Pin(5, Pin.IN, Pin.PULL_DOWN) # Prioridade

print("Sistema de Validação de Carregamento Ativo!")

while True:
    K = pin_K.value()
    F = pin_F.value()
    H = pin_H.value()
    P = pin_P.value()
    
    # Equação Lógica Simplificada: S = K * F * (~H + P)
    S = K and F and (not H or P)
    
    # Formatação dos textos para o LCD
    txt_K = "OK" if K else "ERRO"
    txt_F = "SIM" if F else "NAO"
    txt_H = "SIM" if H else "NAO"
    txt_P = "SIM" if P else "NAO"
    
    lcd_print(f"Hardware: {txt_K}", 0)
    lcd_print(f"Energia : {txt_F}", 1)
    lcd_print(f"Pico:{txt_H}   VIP:{txt_P}", 2)
    
    if S:
        lcd_print("STATUS: AUTORIZADO ", 3)
        print(f"Hardware:{K} | Energia:{F} | Pico:{H} | Prioridade:{P} --> STATUS: AUTORIZADO")
    else:
        lcd_print("STATUS: IMPEDIDO   ", 3)
        print(f"Hardware:{K} | Energia:{F} | Pico:{H} | Prioridade:{P} --> STATUS: IMPEDIDO")
        
    time.sleep(0.5)
