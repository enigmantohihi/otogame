import pygame
from pygame.locals import *
import sys
import math
import csv

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

NOTES_SIZE = 20
NOTES_SPEED = 0.1
END_POS_X = (240,120)
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
lane_list = [[],[]]
list_lane1 = []
list_lane2 = []

create_list = []
judge_str = ["",""]


# case1 まだ流れてきていないノーツ
# -> alive = False, active = False, finish = False
# case2 画面内にあるがまだ叩かれていないノーツ
# -> alive = False, active = True, finish = False
# case3 判定枠に近づいて叩けるノーツ
# -> alive = True, active = True, finish = False
# case4 叩いたノーツ
# -> alive = False, active = True, finish = True
# case5 判定枠を過ぎたノーツ
# -> alive = False, active = True, finish = True
# case6 判定枠を過ぎて見えなくなったノーツ
# -> alive = False, active = False, finish = True

class Notes:
    def __init__(self,x,y,time,lane):
        self.x = x
        self.y = y
        self.time = time
        self.speed = 1*NOTES_SPEED
        self.lane = lane
        self.alive = False  # Trueなら叩ける
        self.active = False  # Trueなら描画する
        self.finish = False # 役目が終わったらTrue
    
    def is_alive(self,now_time):
        # 現在時間とこのノーツの時間を比較して叩ける時間ならTrueを返す
        dif_time = abs(self.time-now_time)
        return False if self.finish or BAD_TIME < dif_time else True

    def judge(self,now_time):
        if not self.alive or self.finish:
            return
        self.alive = False
        self.finish = True
        j_time = abs(self.time-now_time)
        
        if j_time <= PERFECT_TIME:
            judge_str = "Perfect!!!"
            # print("Perfect!!!")
        elif j_time <= GREAT_TIME:
            judge_str = "Great!"
            # print("Great!")
        elif j_time <= GOOD_TIME:
            judge_str = "Good"
            # print("Good")
        elif j_time <= BAD_TIME:
            judge_str = "Bad"
            # print("Bad")
        return judge_str

# 譜面が流れてくる処理を作る
# 譜面ファイルを読み込む

# 譜面ファイルのつくりかた
# 曲を流して自分の好きにボタンを押す
# ボタンを押したタイミングを自動で譜面ファイルに書き込む 
# タイミングを微調整して完成

def find_notes(lane_number,now_time):
    # 判定枠から一番近いノーツを検索して返す
    first=True
    alive_list = [n for n in lane_list[lane_number] if n.alive]
    if len(alive_list)==0:
        return
    for notes in alive_list:
    # レーンのリストからalive=Trueだけでフィルタ
        if first:
            # 最初のループ
            res = notes
            res_dif = abs(notes.time-now_time)
            first = False
        dif = abs(notes.time-now_time)  # 現在時間とノーツ時間の差を計算
        if dif < res_dif:
            # 最小の差より小さいなら最小を更新
            res = notes
            res_dif = dif
    return res

def set_txt_ui(screen,font,str,x=0,y=0,anchor=(0,0)):
    # 右寄せ
    txt = font.render(str, True, (0,0,0))
    txt_w = font.size(str)[0]
    txt_h = font.size(str)[1]
    x = SCREEN_WIDTH*anchor[0]-txt_w*anchor[0] + x
    y = SCREEN_HEIGHT*anchor[1]-txt_h*anchor[1] + y
    screen.blit(txt, [x,y])

def main():
    judge_str = ["",""]
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
    se1 = pygame.mixer.Sound("./asset/se/den.wav")
    se1.set_volume(0.3)
    se2 = pygame.mixer.Sound("./asset/se/tukue_ban.wav")
    se2.set_volume(0.5)
    pygame.mixer.music.play(1)
    pygame.mixer.music.pause()

    for content in contents:
        x = 0
        y = 0
        time = float(content[0])
        lane = int(content[1])
        notes = Notes(x,y,time,lane)
        if lane == 1: lane_list[0].append(notes)
        else: lane_list[1].append(notes)
        # notes_list.append(notes)

    while True:
        # 背景の描画
        screen.fill(WHITE)
        # 音楽の現在時間取得
        music_time = pygame.mixer.music.get_pos()/1000
        # レーンと判定枠の描画
        pygame.draw.line(screen, BLACK, (0,SCREEN_HEIGHT*(1/3)), (SCREEN_WIDTH,SCREEN_HEIGHT*(1/3)), 2)
        pygame.draw.line(screen, BLACK, (0,SCREEN_HEIGHT/2), (SCREEN_WIDTH,SCREEN_HEIGHT/2), 2)
        pygame.draw.circle(screen,GRAY,(END_POS_X[0],SCREEN_HEIGHT*(1/3)),NOTES_SIZE)
        pygame.draw.circle(screen,GRAY,(END_POS_X[1],SCREEN_HEIGHT/2),NOTES_SIZE)
        
        
        # 音楽時間に合わせてノーツの状態を更新
        if mode: pass
        else:
            for notes in lane_list[0]+lane_list[1]:
                if notes.finish:
                    # ノーツの役目が終わっていたら無視
                    continue

                time = notes.time
                speed = notes.speed
                lane = 0 if notes.lane==1 else 1
                notes.x = END_POS_X[lane] + DIR*((time-music_time)*LENGTH*speed)
                notes.y = SCREEN_HEIGHT*(1/3) if notes.lane==1 else SCREEN_HEIGHT/2
                
                if notes.x < 0-NOTES_SIZE/2 or SCREEN_WIDTH+NOTES_SIZE/2 < notes.x:
                    # ノーツが画面外で見えないなら
                    notes.alive = False
                    notes.active = False
                else:
                    # ノーツが画面内なら
                    notes.alive = notes.is_alive(music_time)
                    notes.active = True
                    
                if notes.active:    
                    pygame.draw.circle(screen,BLACK,(notes.x,notes.y),NOTES_SIZE)
                
                if AUTO:
                    if notes.x <= END_POS_X[lane]:
                        notes.judge(music_time)
            
        time_str = "{0}".format(math.floor(music_time*10)/10)
        set_txt_ui(screen,font,time_str,x=0,y=0,anchor=(1,0))
        set_txt_ui(screen,font,judge_str[0],x=END_POS_X[0]-font.size(judge_str[0])[0]/2,y=SCREEN_HEIGHT*(1/3)-NOTES_SIZE*2,anchor=(0,0))
        set_txt_ui(screen,font,judge_str[1],x=END_POS_X[1]-font.size(judge_str[1])[0]/2,y=SCREEN_HEIGHT/2-NOTES_SIZE*2,anchor=(0,0))
        
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
                    se1.play()
                    near_notes = find_notes(0,music_time)
                    if near_notes is not None:
                        judge_str[0] = near_notes.judge(music_time)

                    
                elif event.key == K_j:
                    if mode:
                        li = [music_time,2]
                        create_list.append(li)
                    se2.play()
                    near_notes = find_notes(1,music_time)
                    if near_notes is not None:
                        judge_str[1] = near_notes.judge(music_time)

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