# -*- coding: utf-8 -*-
"""霓虹不夜城 - 游戏入口。"""
import pygame as pg

from game import android_compat as AC
from game import config as C
from game.renderer import Renderer
from game.simulation import Simulation
from game.ui import UI


def _close_overlay(ui, sim):
    if ui.build_menu:
        ui.build_menu = None
        return True
    if ui.show_help:
        ui.show_help = False
        return True
    if AC.IS_ANDROID and sim.phase == "open":
        sim.toggle_pause()
        return True
    return False


def main():
    pg.init()
    screen, target = AC.create_display()
    pg.display.set_caption("霓虹不夜城 - Night Club Empire")
    clock = pg.time.Clock()
    sim = Simulation()
    ui = UI(sim)
    renderer = Renderer(target)

    running = True
    fingers = {}
    while running:
        dt = min(clock.tick(AC.fps()) / 1000.0, 0.05)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif AC.APP_BACKGROUND is not None and event.type == AC.APP_BACKGROUND:
                if sim.phase == "open" and not sim.paused:
                    sim.toggle_pause()
            elif AC.APP_FOREGROUND is not None and event.type == AC.APP_FOREGROUND:
                clock.tick()
            elif event.type == pg.KEYDOWN:
                back_key = AC.BACK_KEY
                if event.key == pg.K_ESCAPE or (back_key is not None
                                                and event.key == back_key):
                    _close_overlay(ui, sim)
                elif event.key == pg.K_h:
                    ui.show_help = not ui.show_help
                elif event.key == pg.K_SPACE:
                    sim.toggle_pause()
            elif (AC.IS_ANDROID and AC.FINGER_DOWN is not None
                  and event.type == AC.FINGER_DOWN):
                pos = AC.finger_screen_pos(event, screen.get_size())
                key = (getattr(event, "touch_id", 0), getattr(event, "finger_id", 0))
                fingers[key] = AC.to_logical(pos, screen.get_size())
            elif (AC.IS_ANDROID and AC.FINGER_MOTION is not None
                  and event.type == AC.FINGER_MOTION):
                pos = AC.finger_screen_pos(event, screen.get_size())
                logical = AC.to_logical(pos, screen.get_size())
                if logical:
                    ui.hover_tile = sim.world_to_tile(*logical)
            elif (AC.IS_ANDROID and AC.FINGER_UP is not None
                  and event.type == AC.FINGER_UP):
                key = (getattr(event, "touch_id", 0), getattr(event, "finger_id", 0))
                start = fingers.pop(key, None)
                pos = AC.finger_screen_pos(event, screen.get_size())
                logical = AC.to_logical(pos, screen.get_size())
                if AC.is_tap(start, logical):
                    ui.handle_click(logical, sim)
            elif not AC.IS_ANDROID and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                ui.handle_click(event.pos, sim)
            elif not AC.IS_ANDROID and event.type == pg.MOUSEMOTION:
                ui.hover_tile = sim.world_to_tile(*event.pos)

        sim.update(dt)
        renderer.draw(sim, ui)
        AC.present(screen, target)

    pg.quit()


if __name__ == "__main__":
    main()
