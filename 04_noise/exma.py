import math
import statistics
import struct
import time
import pyaudio

INTMAX = 2**(16-1)-1
TIMING = 0.1
FREQUENCY = 523.251
FS = 48000

MORSE_CODE_DICT = {
  'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
  'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
  'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
  'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
  'Y': '-.--', 'Z': '--..',
  '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
  '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----'
}

def text_to_morse(text):
  morse_code = []
  for char in text.upper():
    if char in MORSE_CODE_DICT:
      morse_code.append(MORSE_CODE_DICT[char])
    elif char == ' ':
      morse_code.append('/')
  return ' '.join(morse_code)

# Morse Code 송신 함수
def send_data(morse_code):
  audio = []
  for char in morse_code:
    if char == '.':  # dits
      for i in range(int(TIMING * FS)):
        audio.append(int(INTMAX * math.sin(2 * math.pi * FREQUENCY * (i / FS))))
    elif char == '-':  # dahs
      for i in range(int(3 * TIMING * FS)):
        audio.append(int(INTMAX * math.sin(2 * math.pi * FREQUENCY * (i / FS))))
    elif char == '/':
      for i in range(int(7 * TIMING * FS)):
        audio.append(0)
    audio.extend([0] * int(TIMING * FS))

  p = pyaudio.PyAudio()
  stream = p.open(format=pyaudio.paInt16,
                  channels=1,
                  rate=FS,
                  output=True)

  chunk_size = 1024
  for i in range(0, len(audio), chunk_size):
    chunk = audio[i:i + chunk_size]
    stream.write(struct.pack('<' + ('h' * len(chunk)), *chunk))

  stream.stop_stream()
  stream.close()
  p.terminate()

def receive_data():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=FS,
                    input=True)
    
    chunk_size = 1024
    unit_size = int(FS * TIMING)  # 0.1초 동안의 데이터 크기
    threshold = 0.8  # 신호와 잡음을 구분하는 임계값
    morse_code = ""
    audio = []  # 데이터를 모으는 버퍼
    unseen = 0
    tuning = False

    print("Recording Morse Code...")

    while True:
        # chunk_size만큼 데이터를 읽어오고 버퍼에 추가
        data = struct.unpack('<' + ('h' * chunk_size), stream.read(chunk_size))
        audio.extend(data)

        # 버퍼가 unit_size 이상이면 분석 시작
        if len(audio) >= unit_size:
            # unit_size만큼 데이터를 추출하고 버퍼에서 제거
            unit_data = audio[:unit_size]
            audio = audio[unit_size:]

            # 신호의 최대값을 기준으로 신호 여부 판단
            if statistics.stdev(unit_data) > threshold:
              if not tuning:
                tuning = True
              else:
                morse_code += "."
                unseen = 0
            else:
              if tuning:
                morse_code += " "

            if tuning:
              print(statistics.stdev(unit_data))
              # print("Current Morse Code:", morse_code)
            # 출력 중간 상태

        # 종료 조건: 일정 시간 동안 신호가 없으면 종료
        if (unseen >= FS * 3 / chunk_size) & tuning:
            break

# 메인 함수
def main():
    while True:
      print('Morse Code over Sound with Noise')
      print('2024 Spring Data Communication at CNU')
      print('[1] Send morse code over sound (play)')
      print('[2] Receive morse code over sound (record)')
      print('[q] Exit')
      select = input('Select menu: ').strip().upper()
      if select == '1':
        text = input('Enter text (only English and Numbers): ').strip()
        morse_code = text_to_morse(text)
        send_data(morse_code)
      elif select == '2':
        receive_data()
      elif select == 'Q':
        print('Terminating...')
        break;

if __name__ == '__main__':
    main()
