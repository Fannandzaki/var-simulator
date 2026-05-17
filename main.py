"""
main.py — VAR Simulator entry point
HOW TO RUN:
  python main.py
DEPENDENCIES:
  pip install pygame-ce numpy
"""
import sys
import pygame
from constants import WIN_W, WIN_H, FPS, INK
from screens import IntroScreen, LevelSelectScreen, GameScreen

def make_fonts():
    try:
        mono = pygame.font.SysFont("couriernew,monospace", 14)
        body = pygame.font.SysFont("couriernew,monospace", 16)
        big  = pygame.font.SysFont("couriernew,monospace", 64, bold=True)
        try:
            ps = pygame.font.SysFont("pressstart2p", 14)
        except:
            ps = pygame.font.SysFont("couriernew,monospace", 13, bold=True)
        small = pygame.font.SysFont("couriernew,monospace", 12)
        icon  = pygame.font.SysFont("segoeuiemoji,couriernew", 28)
        num   = pygame.font.SysFont("couriernew,monospace", 26, bold=True)
        tiny  = pygame.font.SysFont("couriernew,monospace", 12)
    except:
        mono = body = big = ps = small = icon = num = tiny = pygame.font.Font(None, 16)
    return {"mono":mono,"body":body,"big":big,"press":ps,
            "small":small,"icon":icon,"num":num,"tiny":tiny}

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("VAR Simulator — Grafkom Final Project")
    clock = pygame.time.Clock()
    fonts = make_fonts()

    intro   = IntroScreen(fonts)
    levels  = LevelSelectScreen(fonts)
    game    = GameScreen(fonts)

    state = "intro"
    show_final = False

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

            if state == "intro":
                r = intro.handle(event)
                if r == "levels": state = "levels"

            elif state == "levels":
                r = levels.handle(event)
                if r == "intro": state = "intro"
                elif isinstance(r, int):
                    game.boot(r)
                    state = "game"
                    show_final = False

            elif state == "game":
                if show_final:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        rb = getattr(game,"_restart_btn",None)
                        if rb and rb.collidepoint(event.pos):
                            game.score_ok = 0
                            game.score_tot = 0
                            show_final = False
                            state = "levels"
                else:
                    if game.result:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            action = game.handle_result_click(event.pos)
                            if action == "next":
                                game.boot(game.lv_id + 1)
                            elif action == "final":
                                show_final = True
                    else:
                        r = game.handle(event)
                        if r == "levels": state = "levels"

        # updates
        if state == "intro":   intro.update()
        elif state == "game" and not show_final: game.update(dt)

        # draw
        screen.fill(INK)
        if state == "intro":    intro.draw(screen)
        elif state == "levels": levels.draw(screen)
        elif state == "game":
            game.draw(screen)
            if show_final:
                game.draw_final(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main()
