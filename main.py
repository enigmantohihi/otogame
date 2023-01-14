import pygame
from pygame.locals import *
import sys
import math
import csv
import json

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
FPS = 60

NOTES_SIZE = 20
NOTES_SPEED = 0.5
END_POS_X = (731,180)
END_POS_Y = (83,362)
DIR = 1
LENGTH = SCREEN_WIDTH

PERFECT_TIME = 0.034
# GREAT_TIME = 0.117
GOOD_TIME = 0.117
BAD_TIME = 0.150

mode = False
AUTO = True

# Color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100,100,100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

lane_list = [[],[]]

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

class Player:
    def __init__(self,sprites):
        self.sprites = sprites
        self.animation_sprites = sprites
        self.sprite_number = 0
        self.animation_count = 0
        self.is_animation = False
        self.animation_time = (30,10,60)

    def next_sprite(self):
        self.animation_count += 1
        if self.animation_count >= self.animation_time[self.sprite_number]:
            self.animation_count = 0
            self.sprite_number = (self.sprite_number+1)%len(self.animation_sprites)
            if self.sprite_number == len(self.animation_sprites)-1:
                self.is_animation = False
    
    def animation(self):
        ori = self.sprites
        self.animation_sprites = [ori[1],ori[2]]
        self.sprite_number = 0
        self.animation_count = 0
        self.animation_time = [3,0]
        self.is_animation = True
    def animation2(self):
        ori = self.sprites
        self.animation_sprites = [ori[0],ori[3]]
        self.sprite_number = 0
        self.animation_count = 0
        self.animation_time = [4,0]
        self.is_animation = True
        
    def display(self):
        return self.animation_sprites[self.sprite_number]


class Notes:
    def __init__(self,x,y,time,speed=1,lane=0):
        self.x = x
        self.y = y
        self.time = time
        self.speed = speed*NOTES_SPEED
        self.lane = lane
        self.dir = 1 if lane==1 else -1
        self.alive = False  # Trueなら叩ける
        self.active = False  # Trueなら描画する
        self.finish = False # 役目が終わったらTrue
    
    def is_alive(self,now_time):
        # 現在時間とこのノーツの時間を比較して叩ける時間ならTrueを返す
        dif_time = abs(self.time-now_time)
        return False if self.finish or BAD_TIME < dif_time else True

    def get_dif_time(self,now_time):
        return abs(self.time-now_time)

    def judge(self,now_time):
        if not self.alive or self.finish:
            return
        self.alive = False
        self.finish = True
        j_time = abs(self.time-now_time)
        
        if j_time <= PERFECT_TIME:
            judge_str = "Perfect"
            # print("Perfect!!!")
        # elif j_time <= GREAT_TIME:
        #     judge_str = "Great!"
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
def create_notes_list(path):
    use_json = True
    lane_list = [[],[]]

    if use_json:
    # json
        json_open = open(path, 'r')
        json_load = json.load(json_open)
        offset = json_load["offset"]
        for notes in json_load["humen"]:
            x = 0
            y = 0
            time = float(notes["time"]) + offset
            speed = float(notes["speed"])
            lane = int(notes["lane"])
            notes = Notes(x,y,time,speed,lane)
            if lane == 0: lane_list[0].append(notes)
            else: lane_list[1].append(notes)
    else:
    # csv
        with open(path, encoding='utf8', newline='') as f:
            csv_reader = csv.reader(f)
            contents = [row for row in csv_reader]
        for content in contents:
            x = 0
            y = 0
            time = float(content[0])
            speed = 1
            lane = int(content[1])
            notes = Notes(x,y,time,speed,lane)
            if lane == 1: lane_list[0].append(notes)
            else: lane_list[1].append(notes)

    return lane_list

# 譜面ファイルのつくりかた
# 曲を流して自分の好きにボタンを押す
# ボタンを押したタイミングを自動で譜面ファイルに書き込む 
# タイミングを微調整して完成

def image_format(path):
    img = pygame.image.load(path).convert_alpha()
    scale = 50
    sizw_w = scale*16
    sizw_h = scale*9
    img = pygame.transform.scale(img, (sizw_w,sizw_h))
    return img

def find_notes(lane_list,lane_number,now_time):
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
    lane_list = create_notes_list("./humen.json")

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("UNKO")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)

    # 画像読み込み
    # sp1 = pygame.image.load("./asset/sprite/naruhodo1.jpg").convert_alpha()
    # sp2 = pygame.image.load("./asset/sprite/naruhodo2.jpg").convert_alpha()
    # sp3 = pygame.image.load("./asset/sprite/naruhodo3.jpg").convert_alpha()
    # sp4 = pygame.image.load("./asset/sprite/naruhodo4.jpg").convert_alpha()
    sp1 = image_format("./asset/sprite/naruhodo1.jpg")
    sp2 = image_format("./asset/sprite/naruhodo2.jpg")
    sp3 = image_format("./asset/sprite/naruhodo3.jpg")
    sp4 = image_format("./asset/sprite/naruhodo4.jpg")
    player = Player((sp1,sp2,sp3,sp4))

    # 音声読み込み
    pygame.mixer.init(frequency = 44100)
    pygame.mixer.music.load("./asset/bgm/tuikyu.mp3")
    se1 = pygame.mixer.Sound("./asset/se/den.wav")
    se1.set_volume(0.3)
    se2 = pygame.mixer.Sound("./asset/se/tukue_ban.wav")
    se2.set_volume(0.5)
    pygame.mixer.music.play(1)
    pygame.mixer.music.pause()

    while True:
        # 背景の描画
        screen.fill(WHITE)
        #　背景画像表示
        screen.blit(player.display(),[0,0])
        if player.is_animation:
            player.next_sprite()
        # 音楽の現在時間取得
        music_time = pygame.mixer.music.get_pos()/1000
        # レーンと判定枠の描画
        pygame.draw.line(screen, BLACK, (0,END_POS_Y[0]), (SCREEN_WIDTH,END_POS_Y[0]), 2)
        pygame.draw.line(screen, BLACK, (0,END_POS_Y[1]), (SCREEN_WIDTH,END_POS_Y[1]), 2)
        pygame.draw.circle(screen,GRAY,(END_POS_X[0],END_POS_Y[0]),NOTES_SIZE)
        pygame.draw.circle(screen,GRAY,(END_POS_X[1],END_POS_Y[1]),NOTES_SIZE)
        pygame.draw.circle(screen,BLACK,(END_POS_X[0],END_POS_Y[0]),NOTES_SIZE,3)
        pygame.draw.circle(screen,BLACK,(END_POS_X[1],END_POS_Y[1]),NOTES_SIZE,3)

        # 音楽時間に合わせてノーツの状態を更新
        if mode: pass
        else:
            for notes in reversed(lane_list[0]+lane_list[1]):
                if notes.finish:
                    # ノーツの役目が終わっていたら無視
                    continue

                time = notes.time
                speed = notes.speed
                lane = 0 if notes.lane==0 else 1
                dir = notes.dir
                notes.x = END_POS_X[lane] + dir*((time-music_time)*LENGTH*speed)
                notes.y = END_POS_Y[lane]
                
                if notes.x < 0-NOTES_SIZE/2 or SCREEN_WIDTH+NOTES_SIZE/2 < notes.x:
                    # ノーツが画面外で見えないなら
                    notes.alive = False
                    notes.active = False
                else:
                    # ノーツが画面内なら
                    notes.alive = notes.is_alive(music_time)
                    notes.active = True
                    
                if notes.active:    
                    pygame.draw.circle(screen,WHITE,(notes.x,notes.y),NOTES_SIZE)
                    pygame.draw.circle(screen,BLACK,(notes.x,notes.y),NOTES_SIZE,3)
                
        if AUTO:
            # オートモード
            judge_time = 0.01
            notes = find_notes(lane_list,0,music_time)
            if notes is not None and notes.get_dif_time(music_time)<=judge_time:
                lane = notes.lane
                player.animation2()
                se1.play()
                judge_str[lane]=notes.judge(music_time)
            notes = find_notes(lane_list,1,music_time)
            if notes is not None and notes.get_dif_time(music_time)<=judge_time:
                player.animation()
                se2.play()
                judge_str[1]=notes.judge(music_time)
            
        time_str = "{0}".format(math.floor(music_time*10)/10)
        set_txt_ui(screen,font,time_str,x=0,y=0,anchor=(1,0))
        set_txt_ui(screen,font,judge_str[0],x=END_POS_X[0]-font.size(judge_str[0])[0]/2,y=END_POS_Y[0]-NOTES_SIZE*2,anchor=(0,0))
        set_txt_ui(screen,font,judge_str[1],x=END_POS_X[1]-font.size(judge_str[1])[0]/2,y=END_POS_Y[1]-NOTES_SIZE*2,anchor=(0,0))
        
        pygame.display.update()

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()             
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                print(event.pos)

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
                elif event.key == K_2:
                    pygame.mixer.music.play(1)
                    for notes in lane_list[0]+lane_list[1]:
                        notes.finish = False
                elif event.key == K_SPACE:
                    pass
                elif event.key == K_r or event.key == K_i:
                    if mode:
                        li = [music_time,1]
                        create_list.append(li)
                    player.animation2()
                    se1.play()
                    near_notes = find_notes(lane_list,0,music_time)
                    if near_notes is not None:
                        judge_str[0] = near_notes.judge(music_time)
               
                elif event.key == K_f or event.key == K_j:
                    if mode:
                        li = [music_time,2]
                        create_list.append(li)
                    player.animation()
                    se2.play()
                    near_notes = find_notes(lane_list,1,music_time)
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