import pygame
from pygame.locals import *
import sys
import math
import csv

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

NOTES_SIZE = 20
NOTES_SPEED = 0.5
END_POS_X = 120
DIR = 1
LENGTH = SCREEN_WIDTH

PERFECT_TIME = 0.033
GREAT_TIME = 0.150
GOOD_TIME = 0.350
BAD_TIME = 0.783

FILE_NAME = "./humen.csv"
mode = False
AUTO = False

# Color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100,100,100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

notes_list = []
list_lane1 = []
list_lane2 = []

create_list = []

class Notes:
    def __init__(self,x,y,time,lane):
        self.x = x
        self.y = y
        self.time = time
        self.speed = NOTES_SPEED
        self.lane = lane
        self.active = False
        self.des = False
    
    def set_pos(self):
        pass
    def judge(self,m_now_time):
        j_time = abs(self.time-m_now_time)
        if j_time <= PERFECT_TIME:
            print("Perfect!!!")
        elif j_time <= GREAT_TIME:
            print("Great!")
        elif j_time <= GOOD_TIME:
            print("Good")
        elif j_time <= BAD_TIME:
            print("Bad")
        self.des = True

# 譜面が流れてくる処理を作る
# 譜面ファイルを読み込む

# 譜面ファイルのつくりかた
# 曲を流して自分の好きにボタンを押す
# ボタンを押したタイミングを自動で譜面ファイルに書き込む 
# タイミングを微調整して完成

def judge(lane):
    result = None
    res_index = None
    c = 0
    list_lane = list_lane1 if lane==1 else list_lane2
    for i,notes in enumerate(list_lane):
        if c == 0:
            result = abs(END_POS_X-notes.x)
            res_index = i
        dif = abs(END_POS_X-notes.x)
        if dif<result: 
            result = dif
            res_index = i
        c+=1
    return res_index


def main():
    with open(FILE_NAME, encoding='utf8', newline='') as f:
        csv_reader = csv.reader(f)
        contents = [row for row in csv_reader] 

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("UNKO")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    pygame.mixer.init(frequency = 44100)
    pygame.mixer.music.load("./asset/bgm/gyakuten1.mp3")
    pygame.mixer.music.play(1)
    pygame.mixer.music.pause()

    for content in contents:
        x = 0
        y = 0
        time = float(content[0])
        lane = int(content[1])
        notes = Notes(x,y,time,lane)
        if lane == 1: list_lane1.append(notes)
        else: list_lane2.append(notes)
        notes_list.append(notes)

    while True:
        screen.fill(WHITE)
        music_time = pygame.mixer.music.get_pos()/1000
        # music_time = math.floor(music_time/100)/10

        pygame.draw.line(screen, BLACK, (0,SCREEN_HEIGHT/2), (SCREEN_WIDTH,SCREEN_HEIGHT/2), 2)
        pygame.draw.line(screen, BLACK, (0,SCREEN_HEIGHT*(1/3)), (SCREEN_WIDTH,SCREEN_HEIGHT*(1/3)), 2)
        pygame.draw.circle(screen,GRAY,(END_POS_X,SCREEN_HEIGHT/2),NOTES_SIZE)
        pygame.draw.circle(screen,GRAY,(END_POS_X,SCREEN_HEIGHT*(1/3)),NOTES_SIZE)
        
        for notes in list_lane1+list_lane2: 
            time = notes.time
            speed = notes.speed
            notes.x = END_POS_X + DIR*((time-music_time)*LENGTH*speed)
            notes.y = SCREEN_HEIGHT/2 if notes.lane==1 else SCREEN_HEIGHT*(1/3)
            
            if notes.x < 0-NOTES_SIZE/2:
                notes.active = False
                
            elif notes.x < SCREEN_WIDTH+NOTES_SIZE/2:
                notes.active = True
            if notes.active and not notes.des:    
                pygame.draw.circle(screen,BLACK,(notes.x,notes.y),NOTES_SIZE)
            if AUTO:
                if notes.x <= END_POS_X: notes.judge(music_time)
        
        t_music_time = font.render("{0}".format(math.floor(music_time*10)/10), True, (0,0,0))
        t_music_w = font.size("{0}".format(math.floor(music_time*10)/10))[0]
        screen.blit(t_music_time, [SCREEN_WIDTH-t_music_w,20])
        
        pygame.display.update() 

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()             
                sys.exit()
            if event.type == KEYDOWN:
                key_name = pygame.key.name(event.key)
                # print(key_name)
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_1:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == K_SPACE:
                    pass
                elif event.key == K_f:
                    if mode:
                        li = [music_time,1]
                        create_list.append(li)
                    index = judge(2)
                    list_lane2[index].judge(music_time)
                    
                elif event.key == K_j:
                    if mode:
                        li = [music_time,2]
                        create_list.append(li)
                    index = judge(1)
                    list_lane1[index].judge(music_time)

                elif event.key == K_q:
                    if mode:
                        f = open('humen.csv', 'w', newline='')
                        data = create_list
                        writer = csv.writer(f)
                        writer.writerows(data)
                        f.close()



        clock.tick(FPS)

if __name__ == "__main__":
    main()