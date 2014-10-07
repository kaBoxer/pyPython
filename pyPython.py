import libtcodpy as libtcod
#init globals
#actual size of the window
SCREEN_WIDTH = 75
SCREEN_HEIGHT = 50

#size of the map
MAP_WIDTH = SCREEN_WIDTH
MAP_HEIGHT = SCREEN_HEIGHT
gamemap = [[0 for x in range(SCREEN_WIDTH)] for y in range(SCREEN_HEIGHT)]

LIMIT_FPS = 20  # 20 frames-per-second maximum

color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

initSnakeLen = 6
oldX = 0
oldY = 0


#--------classes
class map_tile:
    def __init__(self, blocked):
        self.blocked = blocked


class snake_parts:
    def __init__(self, x, y, char, name, color, blocked):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocked = blocked

    def move(self, dirX, dirY):
        global gamemap
        global mySnakeLength, status

        #check for new game
        if oldX == 0 and oldY == 0:
            return 'newgame'

        self.x += dirX
        self.y += dirY

        #eat food
        for idx, obj in enumerate(food):
            if obj.x == self.x and obj.y == self.y:
                del food[idx]

                #place new piece of food, to be rendered later.
                while True:
                    xFood = libtcod.random_get_int(0, 5, SCREEN_WIDTH - 5)
                    yFood = libtcod.random_get_int(0, 5, SCREEN_HEIGHT - 5)
                    # print xFood, yFood
                    if not gamemap[yFood][xFood].blocked:
                        break

                obj = mob(xFood, yFood, 'K', 'food', libtcod.dark_yellow)
                food.append(obj)
                newBody = snake_parts(self.x - dirX, self.y - dirY, '#', 'body', libtcod.white, True)
                snake.insert(1, newBody)

        #collision check: Walls.
        if gamemap[self.y][self.x].blocked:
            # print 'hit wall'
            return 'dead'

        #collision check: Self
        for idx, val in enumerate(snake):  # tried to use start=1 but it didn't work...
            if idx == 0:
                pass
            else:
                if snake[0].x == val.x and snake[0].y == val.y:
                    # print 'hit self'
                    return 'dead'

        #move body, only do this after collision check.
        del snake[-1]
        newBody = snake_parts(self.x - dirX, self.y - dirY, '#', 'body', libtcod.white, True)
        snake.insert(1, newBody)
        return 'alive'

    def draw(self):
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #remove the char from the console
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

class mob:
    def __init__(self, x, y, char, name, color):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color

    def draw(self):
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)


#--------functions
def make_map():
    global gamemap
    #blank slate map.
    for x in range(MAP_HEIGHT):
        for y in range(MAP_WIDTH):
            gamemap[x][y] = map_tile(False)


def handle_keys():
    global oldX, oldY, status
    key = libtcod.console_check_for_keypress()  # real-time
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle full screen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'

    elif libtcod.console_is_key_pressed(libtcod.KEY_UP) and status != 'dead':
        if oldX == 0 and oldY == 1:
            status = player_move_or_eat(0,1)
        else:
            status = player_move_or_eat(0, -1)
            oldX = 0
            oldY = -1
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN) and status != 'dead':
        if oldX == 0 and oldY == -1:
            status = player_move_or_eat(0, -1)
        else:
            status = player_move_or_eat(0, 1)
            oldX = 0
            oldY = 1
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT) and status != 'dead':
        if oldX == 1 and oldY == 0:
            status = player_move_or_eat(1,0)
        else:
            status = player_move_or_eat(-1, 0)
            oldX = -1
            oldY = 0
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT) and status != 'dead':
        if oldX == -1 and oldY == 0:
            status = player_move_or_eat(-1, 0)
        else:
            status = player_move_or_eat(1, 0)
            oldX = 1
            oldY = 0
    elif libtcod.console_is_key_pressed(libtcod.KEY_SPACE) and status == 'dead':
        status = 'restart'
    else:
        if status != 'dead':
            status = player_move_or_eat(oldX, oldY)

    return status


def player_move_or_eat(dx, dy):
    status = snake[0].move(dx, dy)
    return status


def restart_game():
    global snake
    while True:
        startX = libtcod.random_get_int(0, 5, SCREEN_WIDTH - 5)
        startY = libtcod.random_get_int(0, 5, SCREEN_HEIGHT - 5)
        if not gamemap[startY][startX].blocked:
            break

    #make the snake
    snake = []
    obj = snake_parts(startX, startY, '@', 'head', libtcod.white, True)
    snake.append(obj)

    for i in range(initSnakeLen):
        obj = snake_parts(startX, startY, '#', 'body', libtcod.white, True)
        snake.append(obj)

    food = []
    obj = mob(40, 40, 'K', food, libtcod.dark_yellow)
    food.append(obj)

    status = 'newgame'
    oldX = 0
    oldY = 0

def render_main():
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if gamemap[y][x].blocked == False:
                libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
            else:
                libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)

    for obj in food:
        obj.draw()

    #make all rendering happen above, @ should be last.
    for obj in reversed(snake):
        obj.draw()

    render_hud()
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


def render_hud():
    line = 'Your Score: ' + str(len(snake)-initSnakeLen-1)
    libtcod.console_print_ex(con, 5, SCREEN_HEIGHT-1, libtcod.BKGND_NONE, libtcod.LEFT, str(line))


def render_death_screen():
    global oldX, oldY
    oldX = 0
    oldY = 0

    dead = libtcod.console_new(SCREEN_WIDTH/2, SCREEN_HEIGHT/4)

    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            libtcod.console_set_char_background(dead, x, y, libtcod.desaturated_red, libtcod.BKGND_SET)

    #cool, i think i got it...
    line = str('You died with a score of ') + str(len(snake)-initSnakeLen-1)
    libtcod.console_print_ex(dead, SCREEN_WIDTH/4, 4, libtcod.BKGND_NONE, libtcod.CENTER, str(line))
    line = str('Press Space to Play Again')
    libtcod.console_print_ex(dead, SCREEN_WIDTH/4 -1, 6, libtcod.BKGND_NONE, libtcod.CENTER, str(line))
    libtcod.console_clear(con)
    #libtcod.console_blit(dead, 0, 0, SCREEN_WIDTH/2, SCREEN_HEIGHT, 0, 0, 0)
    #console_blit(src,xSrc,ySrc,xSrc,hSrc,dst,xDst,yDst,foregroundAlpha=1.0,backgroundAlpha=1.0)
    libtcod.console_blit(dead, 0, 0, 0, 0, 0, (SCREEN_WIDTH/4)+2, (SCREEN_HEIGHT/4)+2)
    libtcod.console_flush()

#########Initiallization for game.
libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

make_map()

while True:
    startX = libtcod.random_get_int(0, 5, SCREEN_WIDTH - 5)
    startY = libtcod.random_get_int(0, 5, SCREEN_HEIGHT - 5)
    if not gamemap[startY][startX].blocked:
        break

#make the snake
snake = []
obj = snake_parts(startX, startY, '@', 'head', libtcod.white, True)
snake.append(obj)

for i in range(initSnakeLen):
    obj = snake_parts(startX, startY, '#', 'body', libtcod.white, True)
    snake.append(obj)

food = []
obj = mob(40, 40, 'K', food, libtcod.dark_yellow)
food.append(obj)

status = 'newgame'

#game loop begins, all actions take place below.
while not libtcod.console_is_window_closed():
    if status != 'dead':
        render_main()
    else:
        render_death_screen()

    libtcod.console_flush()

    for obj in snake:
        obj.clear()

    #this is the meat and potatoes.
    status = handle_keys()

    if status == 'restart':
        restart_game()

    if status == 'exit':
        exit()