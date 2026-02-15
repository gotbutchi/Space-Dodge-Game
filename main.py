import pygame
import time
import random
import os

# init font module
try:
    pygame.font.init()
except:
    print("Could not init font")
    pass

# set window
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

BG = pygame.transform.scale(pygame.image.load("assets/bg.jpg"), (WIDTH, HEIGHT))

# set caption
pygame.display.set_caption("Space Dodge")

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40

PLAYER_VEL = 5

# SLOWER SPEED
FPS = 60

# font
FONT = pygame.font.SysFont("comicsans", 30)

STAR_WIDTH = 10
STAR_HEIGHT = 30
STAR_VEL = 3

# High Score System for top 5 scores by time survived
SCORE_FILE = "highscores.txt"

def load_high_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    with open(SCORE_FILE, "r") as f:
        try:
            scores = [float(line.strip()) for line in f.readlines()]
            scores.sort(reverse=True)
            return scores
        except ValueError:
            return []

def save_high_score(new_score):
    scores = load_high_scores()
    scores.append(new_score)
    scores.sort(reverse=True)
    scores = scores[:5] # Keep top 5
    with open(SCORE_FILE, "w") as f:
        for score in scores:
            f.write(f"{score}\n")
    return scores

def draw(player, elapsed_time, stars):
    WIN.blit(BG, (0, 0))

    pygame.draw.rect(WIN, (255, 0, 0), player) # red player

    for star in stars:
        pygame.draw.rect(WIN, (255, 255, 255), star) # white stars

    # render text on screen
    time_text = FONT.render(f"Time: {round(elapsed_time, 1)}s", 1, "white")
    WIN.blit(time_text, (10, 10)) # padding

    pygame.display.update() 

# main loop
def main():
    run = True

    # player X Y width height
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)

    clock = pygame.time.Clock()

    start_time = time.time() #current time
    elapsed_time = 0

    # projectiles
    star_add_increment = 2000 # ms wait till next pack of stars arrive
    star_count = 0 # when to add the next star

    stars = [] # on screen

    hit = False


    while run:

        '''
        Bắt đầu: star_count là 0. star_add_increment là 2000ms.
        Đếm thời gian: Mỗi vòng lặp, star_count tăng dần lên (+ clock.tick(FPS)).
        Kiểm tra: Khi star_count vượt quá 2000ms (tức là đã chờ đủ 2 giây):
            Tạo ra một loạt sao băng mới.
            Giảm thời gian chờ xuống còn 1950ms (star_add_increment - 50).
            Gán star_count = 0 để bắt đầu chu kỳ đếm mới, 
            chu kỳ "Chờ đợi -> Sinh sao -> Chờ đợi" được lặp lại chính xác
            (nếu không gán thì sẽ bị lỗi vì
            Sao băng sẽ sinh ra liên tục ở mỗi khung hình (60 lần/giây) thay vì chờ đợi.)
        '''


        star_count += clock.tick(FPS) # add ms passed since last frame
        elapsed_time = time.time() - start_time

        if star_count > star_add_increment: # if enough ms passed since last pack of stars (>2s)
            # create a new pack of 3 stars
            for _ in range(3):
                star_x = random.randint(0, WIDTH - STAR_WIDTH)
                star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)   # y = -STAR_HEIGHT => stars start above the screen
                stars.append(star)

            # decrease wait time (from 2s -> 1.95s...)
            # count back to 0    
            star_add_increment = max(200, star_add_increment - 50) # -50 ms from waiting time every time a pack of stars ends, till reach min 200ms
            star_count = 0 # reset time counter for next pack of stars to avoid star_count always larger than star_add_increment => new stars always spawning

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        keys = pygame.key.get_pressed()

        # dictionary of keys
        if keys[pygame.K_LEFT] and (player.x - PLAYER_VEL >= 0):
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and (player.x + PLAYER_VEL + player.width <= WIDTH):
            player.x += PLAYER_VEL
        if keys[pygame.K_UP] and (player.y - PLAYER_VEL >= 0):
            player.y -= PLAYER_VEL
        if keys[pygame.K_DOWN] and (player.y + PLAYER_VEL + player.height <= HEIGHT):
            player.y += PLAYER_VEL
        # print(f"x = {player.x}, y = {player.y}, width = {player.width}, height = {player.height}")
        
        # move stars down
        for star in stars[:]: # iterate over a copy of the list
            star.y += STAR_VEL
            if star.y > HEIGHT:
                stars.remove(star) # remove stars FROM ORIGINAL LIST (not copy) that go off screen
            elif star.y + star.height >= player.y and star.colliderect(player):
                stars.remove(star)
                hit = True
                break
        
        if hit:
            # Save and get high scores
            high_scores = save_high_score(elapsed_time)

            lost_text = FONT.render("You lost!", 1, "white")
            # center text
            WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2 - lost_text.get_height()/2 - 100))
            
            # Display Leaderboard
            header_text = FONT.render("Leaderboard (Top 5):", 1, "yellow")
            WIN.blit(header_text, (WIDTH/2 - header_text.get_width()/2, HEIGHT/2 - 50))

            for i, score in enumerate(high_scores):
                score_text = FONT.render(f"TOP {i+1}: {round(score, 1)}s", 1, "white")
                WIN.blit(score_text, (WIDTH/2 - score_text.get_width()/2, HEIGHT/2 + i * 35))

            # Display New High Score if applicable
            if elapsed_time == high_scores[0]:
                new_high_score_text = FONT.render(f"NEW HIGH SCORE! {round(elapsed_time, 1)}s", 1, "yellow")
                WIN.blit(new_high_score_text, (WIDTH/2 - new_high_score_text.get_width()/2, HEIGHT/2 + len(high_scores) * 35))

            pygame.display.update()
            pygame.time.delay(5000)
            break

        draw(player, elapsed_time, stars)
    
    pygame.quit()

if __name__ == "__main__":
    main()