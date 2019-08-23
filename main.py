from pyglet import window, app, event    
from pyglet.window import mouse
from vector import Vector, Plane
_x, _y = int(720), int(720)
win = window.Window(_x, _y)
lmb_press_xy = []
plane = Plane(win, [1.0, 1.0], 16)

if __name__ == '__main__':

    @win.event
    def on_mouse_press(x, y, button, modifiers):
        if button == mouse.LEFT:    
            lmb_press_xy.append([x, y])
        if button == mouse.RIGHT:
            plane.vectors.pop()

    @win.event
    def on_mouse_release(x, y, button, modifiers):
        if button == mouse.LEFT:
            dxy = [_x/2, _y/2]
            if dxy != [x, y]:
                plane.append_windowspace(Vector(dxy, [x, y]))

    @win.event
    def on_key_release(symbol, modifiers):
        if symbol == 97:
            # 'A'
            l = len(plane.vectors)
            plane.append_planespace(
                plane.vectors[l-2] + plane.vectors[l-1]
            )
        if symbol == 115:
            # 'S'
            l = len(plane.vectors)
            plane.append_planespace(
                plane.vectors[l-2] - plane.vectors[l-1]
            )
        if symbol == 109:
            # 'M'
            l = len(plane.vectors)
            plane.append_planespace(
                plane.vectors[l-2] * plane.vectors[l-1]
            )

    @win.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        if scroll_y > 0:
            plane.gridlines = int(plane.gridlines*2)
        if scroll_y < 0:
            if plane.gridlines >= 2:
                plane.gridlines = int(plane.gridlines/2)

    @win.event
    def on_draw():
        win.clear()
        batch = plane.batch(None, True)
        batch.draw()

    app.run()
