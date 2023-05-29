import math
import random
import sys
import time
import pygame
import pygame as pg
from pygame.sprite import AbstractGroup

WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ

pthp = 10
ethp = 10

def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


class Player_Tower(pg.sprite.Sprite):  # プレイヤーのタワーに関するクラス
    
    def __init__(self, xy: tuple[int, int]):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/tower.png"), 0, 0.5)  # タワーを0.5倍にした
        self.dire = (0.5, 0)  # 初期速度ベクトル
        self.rect = self.image.get_rect()  # 初期座標を設定
        self.rect.center = xy
        self.state = "Alive"  # タワーは生存している


    def update(self,screen: pg.Surface):  # 設定を反映
        screen.blit(self.image, self.rect)
    

    def get_direction(self) -> tuple[int, int]:  # 速度ベクトルを返す
        return self.dire





class Enemy_Tower(pg.sprite.Sprite):
    def __init__(self, xy: tuple[int, int]):
        super().__init__()
        
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/tower.png"), 0, 0.5)
        self.dire = (-1, 0)
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.state = "normal"
        self.hyper_life = -1
    def update(self,screen: pg.Surface):
        
        screen.blit(self.image, self.rect)
    
    def get_direction(self) -> tuple[int, int]:
        return self.dire


class Bomb(pg.sprite.Sprite):

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", Player_Tower: Player_Tower):
        super().__init__()
        rad = random.randint(30, 50)
        color = random.choice(__class__.colors)
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.vx, self.vy = -1, 0
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery
        self.speed = 6

    def update(self):
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Player_Character(pg.sprite.Sprite):
    def __init__(self, Player_Tower: Player_Tower):
        super().__init__()
        self.vx, self.vy = Player_Tower.get_direction()
        img0 = pg.transform.rotozoom(pg.image.load(f"ex05/fig/3.png"), 0, 1.5)
        self.image = pg.transform.flip(img0, True, False)
        
        self.rect = self.image.get_rect()
        self.rect.centery = HEIGHT/2
        self.rect.centerx = Player_Tower.rect.centerx + 100
        self.speed = 10

    def update(self):
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Strong_Player_Character(pg.sprite.Sprite):
    def __init__(self, Player_Tower: Player_Tower):
        super().__init__()
        self.vx, self.vy = Player_Tower.get_direction()
        img0 = pg.transform.rotozoom(pg.image.load(f"ex05/fig/3.png"), 0, 3.0)
        self.image = pg.transform.flip(img0, True, False)
        
        self.rect = self.image.get_rect()
        self.rect.centery = HEIGHT/2
        self.rect.centerx = Player_Tower.rect.centerx + 100
        self.speed = 5
        self.life = 2

    def update(self):
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Speed_Player_Character(pg.sprite.Sprite):
    def __init__(self, Player_Tower: Player_Tower):
        super().__init__()
        self.vx, self.vy = Player_Tower.get_direction()
        img0 = pg.transform.rotozoom(pg.image.load(f"ex05/fig/3.png"), 0, 0.5)
        self.image = pg.transform.flip(img0, True, False)
        
        self.rect = self.image.get_rect()
        self.rect.centery = HEIGHT/2
        self.rect.centerx = Player_Tower.rect.centerx + 100
        self.speed = 20
        self.life = 1

    def update(self):
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Explosion(pg.sprite.Sprite):
    def __init__(self, obj: "Bomb|Enemy", life: int):
        super().__init__()
        img = pg.image.load("ex05/fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()




class Enemy(pg.sprite.Sprite):  # 敵に関するクラス
    imgs = [pg.image.load(f"ex05/fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH-200, HEIGHT/2
        self.state = "stop"  # 降下状態or停止状態
        self.vx = -5
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル

    def update(self):
        self.rect.centerx += self.vx
        


class Score:
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.score = 0
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def score_up(self, add):
        self.score += add

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        screen.blit(self.image, self.rect)


def main():
    pg.display.set_caption("TowerDiffense")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("ex05/fig/pg_bg.jpg")
    score = Score()

    player_tower = Player_Tower((100, HEIGHT/2-100))
    
    enemy_tower = Enemy_Tower((WIDTH-100, HEIGHT/2-100))
    bombs = pg.sprite.Group()
    player_charas = pg.sprite.Group()
    exps = pg.sprite.Group()
    enemys = pg.sprite.Group()

    gbb = pg.sprite.Group()


    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:    
                if score.score >= 100:
                    score.score -= 100
                    player_charas.add(Player_Character(player_tower))
            if event.type == pg.KEYDOWN and event.key == pg.K_a:    
                if score.score >= 100:
                    score.score -= 100
                    player_charas.add(Strong_Player_Character(player_tower))
            if event.type == pg.KEYDOWN and event.key == pg.K_s:    
                if score.score >= 100:
                    score.score -= 100
                    player_charas.add(Speed_Player_Character(player_tower))
            
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                score.score += 100
            if event.type == pg.KEYDOWN and event.key == pg.K_BACKSPACE:
                enemys.add(Enemy())
        if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
                enemys.add(Enemy())   
            

        screen.blit(bg_img, [0, 0])


        score.score_up(1)
        if score.score> 1000:
            score.score = 1000

        for enemy in enemys:
            pass
            #bombs.add(Bomb(emy, player_tower))

        for enemy in pg.sprite.groupcollide(enemys, player_charas, True, True).keys():
            exps.add(Explosion(enemy, 100))  # 爆発エフェクト

        for bomb in pg.sprite.groupcollide(bombs, player_charas, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト

        for bomb in pg.sprite.spritecollide(player_tower, bombs, True):
            if player_tower.state == "hyper":
                exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                score.score_up(1)  # 1up
            else:
                score.update(screen)
                pg.display.update()
                time.sleep(2)
                return
        if len(pg.sprite.spritecollide(player_tower, enemys, True)) != 0:
            pygame.display.update()
            score.update(screen)
            pg.display.update()       
            pygame.display.update()
            time.sleep(2)
            return
        if len(pg.sprite.spritecollide(enemy_tower, player_charas, True)) != 0:
            pygame.display.update()
            score.update(screen)
            pg.display.update()
            time.sleep(2)
            return
        gbb.update(player_tower)
        gbb.draw(screen)

        
        enemy_tower.update(screen)
        player_tower.update(screen)
        player_charas.update()
        player_charas.draw(screen)
        enemys.update()
        enemys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()