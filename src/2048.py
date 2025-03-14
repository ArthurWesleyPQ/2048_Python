from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config
from functools import partial
from random import randint
from random import choice

Config.set('graphics', 'resizable', False)

KV = '''
<HomeScreen>:
    orientation: 'vertical'
    FloatLayout:
        id: lyt_up
        size_hint: (None, None)
        size: (app.window_height / 2, app.window_height / 2)
        pos_hint: {'center_x': 0.5}
        FloatLayout:
            id: game_lyt
            size_hint: (1, None)
            height: self.width
            pos: self.parent.pos
            canvas.before:
                Color:
                    rgba: (1, 1, 1, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
    FloatLayout:
        size_hint: (None, None)
        size: (app.window_height / 2, app.window_height / 2)
        pos_hint: {'center_x': 0.5}
        # Borders
        canvas.before:
            Color:
                rgba: (0, 0, 0, 1)
            Rectangle:
                pos: self.pos
                size: self.size
            Rectangle:
                pos: (0, 0)
                size: (root.ids.lyt_up.pos[0], app.window_height)
            Rectangle:
                pos: (root.ids.lyt_up.pos[0] + root.ids.lyt_up.width, 0)
                size: (root.ids.lyt_up.pos[0], app.window_height)
        GameButtons:
            size_hint: (0.5, None)
            pos: (self.parent.pos[0] + (self.width / 2), self.parent.height - self.height * 1.25)
        ScoreLabel:
            id: score_label
            pos_hint: {'center_x': 0.5, 'center_y': 0.1}

<DirectionalButton>:
    on_press: root.on_button_press()
    Image:
        source: 'arr.png'
        size: self.parent.size
        pos: self.parent.pos
        canvas.before:
            PushMatrix
            Rotate:
                origin: self.center
                angle: 90 if root.btn_dir == "left" else 180 if root.btn_dir == "down" else 270 if root.btn_dir == "right" else 0
        canvas.after:
            PopMatrix
            
<GameButtons>:
    cols: 3
    rows: 3
    height: self.width
    Label:
    DirectionalButton:
        btn_dir: "up"
    Label:
    DirectionalButton:
        btn_dir: "left"
    Label:
    DirectionalButton:
        btn_dir: "right"
    Label:
    DirectionalButton:
        btn_dir: "down"
    Label:
        
<ScoreLabel>:
    text: f"Score: {root.score}"
    font_size: '40dp'
    markup: True
    
<NumberBlock>:
    size_hint: 1/4, None
    pos: self.pos
    height: self.width
    green: (0.2352, 0.7, 0.4432, 1)
    blue: (0.3921, 0.5843, 0.9294, 1)
    yellow: (0.9921, 0.8549, 0.0509, 1)
    red: (0.8235, 0.1686, 0.1686, 1)
    byzantium: (0.4392, 0.1607, 0.3882, 1)
    orchid: (0.8549, 0.4392, 0.8392, 1)
    light_gray: (0.8274, 0.8274, 0.8274, 1)
    terracotta: (0.8862, 0.4470, 0.3568, 1)
    mud: (0.4392, 0.3294, 0.2431, 1)
    turquoise: (0.2509, 0.8784, 0.8156, 1)
    adamantium: (0.3529, 0.2901, 0.3294, 1)
    canvas.before:
        Color:
            rgba: self.green if root.value == '2' else self.blue if root.value == '4' else self.yellow if root.value == '8' else self.red if root.value == "16" else self.byzantium if root.value == "32" else self.orchid if root.value == "64" else self.light_gray if root.value == "128" else self.terracotta if root.value == "256" else self.mud if root.value == "512" else self.turquoise if root.value == "1024" else self.adamantium
        Rectangle:
            size: self.size
            pos: self.pos
    Label:
        text: root.value
'''

Builder.load_string(KV)

CLOCK_INTERVAL = 1/60
CLOCK_ANIMATION_MULTIPLIER = 1
NB_ANIMATION_SPEED = 3000

MIN_STARTING_BLOCKS_QNT = 4
MAX_STARTING_BLOCKS_QNT = 8

MIN_SPAWN_VALUE = 2
MAX_SPAWN_VALUE = 4

GAME_LINES = 4
GAME_COLUMNS = 4

SPAWN_CHANCE_PERCENT = 20

class NumberBlock(BoxLayout):
    value = StringProperty()
    animating = False
    merge = False
    line_col = (0, 0)
    
    def __init__(self, **kwargs):
        super(NumberBlock, self).__init__(**kwargs)
        self.event = None
        self.disable = False
        self.app = App.get_running_app()
        
    def animate(self, direction, pos, line_col, adjust, *args):
        if adjust:
            self.opacity = 1
            self.disable = False
            
        if direction == "down":
            if adjust:
                self.pos = (self.parent.pos[0] + (self.width * self.line_col[1]), self.parent.pos[1] + self.parent.height)
            self.event = Clock.schedule_interval(partial(self.descend_pos, pos, line_col), CLOCK_INTERVAL)
        elif direction == "up":
            if adjust:
                self.pos = (self.parent.pos[0] + (self.width * self.line_col[1]), self.parent.pos[1] + self.parent.height - self.height - (self.height * 4))
            self.event = Clock.schedule_interval(partial(self.ascend_pos, pos, line_col), CLOCK_INTERVAL)
        elif direction == "left":
            if adjust:
                self.pos = (self.parent.pos[0] + self.parent.width, self.parent.pos[1] + self.parent.height - self.height - (self.height * self.line_col[0]))
            self.event = Clock.schedule_interval(partial(self.left_pos, pos, line_col), CLOCK_INTERVAL)
        elif direction == "right":
            if adjust:
                self.pos = (self.parent.pos[0] + (self.parent.width - self.width - (self.width * 4)), self.parent.pos[1] + self.parent.height - self.height - (self.height * self.line_col[0]))
            self.event = Clock.schedule_interval(partial(self.right_pos, pos, line_col), CLOCK_INTERVAL)
       
    def descend_pos(self, pos, line_col, *args):
        new_pos = (self.pos[0], self.pos[1] - self.app.anim_speed)
        if new_pos[1] <= (self.parent.pos[1] + (self.height * pos)):
            new_pos = (self.pos[0], self.parent.pos[1] + (self.height * pos))
            self.end_anim(line_col)
        self.pos = new_pos
        
    def ascend_pos(self, pos, line_col, *args):
        new_pos = (self.pos[0], self.pos[1] + self.app.anim_speed)
        if new_pos[1] >= self.parent.pos[1] + self.parent.height - self.height - (self.height * pos):
            new_pos = self.pos[0], self.parent.pos[1] + self.parent.height - self.height - (self.height * pos)
            
            self.end_anim(line_col)
        self.pos = new_pos
    
    def left_pos(self, pos, line_col, *args):
        new_pos = (self.pos[0] - self.app.anim_speed, self.pos[1])
        if new_pos[0] <= (self.parent.pos[0] + (self.width * pos)):
            new_pos = (self.parent.pos[0] + (self.width * pos), self.pos[1])
            
            self.end_anim(line_col)
        self.pos = new_pos
        
    def right_pos(self, pos, line_col, *args):
        new_pos = (self.pos[0] + self.app.anim_speed, self.pos[1])
        if new_pos[0] >= (self.parent.pos[0] + self.parent.width - self.width - (self.width * pos)):
            new_pos = (self.parent.pos[0] + self.parent.width - self.width - (self.width * pos), self.pos[1])
            
            self.end_anim(line_col)
        self.pos = new_pos
        
    def end_anim(self, line_col):
        self.animating = False
        Clock.unschedule(self.event)
        if self.merge:
            self.do_merge(line_col)
        
    def do_merge(self, line_col):
        self.app.game_array[line_col[0]][line_col[1]].value = str(int(self.value) * 2)
        self.app.home_screen.ids.score_label.score = str(int(self.app.home_screen.ids.score_label.score) + int(self.value) * 2)
        self.parent.remove_widget(self)

class ScoreLabel(Label):
    score = StringProperty('0')

    def __init__(self, **kwargs):
        super(ScoreLabel, self).__init__(**kwargs)

class GameButtons(GridLayout):
    def __init__(self, **kwargs):
        super(GameButtons, self).__init__(**kwargs)

class DirectionalButton(Button):
    btn_dir = StringProperty()
    
    def __init__(self, *args, **kwargs):
        super(DirectionalButton, self).__init__(**kwargs)
        self.app = App.get_running_app()
    
    def on_button_press(self):        
        game_array = self.app.game_array
        
        # Check for any animation
        for line in range(GAME_LINES):
            for column in range(GAME_COLUMNS):
                current_block = game_array[line][column]
            
                if current_block is not None and current_block.animating:
                    return
            
        if self.btn_dir == "down":
            game_array = self.animate_down(game_array)
        elif self.btn_dir == "up":
            game_array = self.animate_up(game_array)
        elif self.btn_dir == "left":
            game_array = self.animate_left(game_array)
        elif self.btn_dir == "right":
            game_array = self.animate_right(game_array)

        self.app.game_array = game_array

    def animate_down(self, game_array):
        ret = get_empty_array()
        
        for column in range(GAME_COLUMNS):
            block_count_in_column = 0
            has_anim = False
            
            for line in range(GAME_LINES - 1, -1, -1):
                current_block = game_array[line][column]
                
                if current_block is not None:
                    current_block.animating = True
                    pos_in_column = 0
                    looking_for_first_block = True
                    line_col = (0, 0)
                    
                    for comparing_line in range(line + 1, GAME_LINES, 1):
                        current_comparing_block = game_array[comparing_line][column]
                        
                        if current_comparing_block is not None:
                            if not current_comparing_block.merge:
                                if looking_for_first_block:
                                    looking_for_first_block = False
                                    if current_block.value == current_comparing_block.value:
                                        current_block.merge = True
                                        line_col = current_comparing_block.line_col
                                        has_anim = True
                                    else:
                                        pos_in_column += 1
                                else:
                                    pos_in_column += 1
                            else:
                                looking_for_first_block = False
                        else:
                            has_anim = True
                    
                    if not current_block.merge:
                        current_block.line_col = (GAME_LINES - 1 - pos_in_column, column)
                        ret[GAME_LINES - 1 - pos_in_column][column] = current_block
                        block_count_in_column += 1
                        
                    Clock.schedule_once(partial(current_block.animate, self.btn_dir, pos_in_column, line_col, False))
            
            # spawn NumberBlock
            if block_count_in_column < GAME_LINES and has_anim:
                random_chance = randint(1, 100)
                
                if random_chance <= SPAWN_CHANCE_PERCENT:
                    selected_value = str(choice(self.app.even_values_list))
                    
                    new_block = NumberBlock(value=selected_value)
                    
                    ret[GAME_LINES - 1 - block_count_in_column][column] = new_block
                    new_block.line_col = (GAME_LINES - 1 - block_count_in_column, column)
                    
                    new_block.animating = True
                    new_block.opacity = 0
                    new_block.disable = True
                    self.app.home_screen.ids.game_lyt.add_widget(new_block)
                    
                    Clock.schedule_once(partial(new_block.animate, self.btn_dir, block_count_in_column, None, True))

        return ret

    def animate_up(self, game_array):
        ret = get_empty_array()
        
        for column in range(GAME_COLUMNS):
            block_count_in_column = 0
            has_anim = False
            
            for line in range(GAME_LINES):
                current_block = game_array[line][column]
                
                if current_block is not None:
                    current_block.animating = True
                    pos_in_column = 0
                    looking_for_first_block = True
                    line_col = (0, 0)
                    
                    for comparing_column in range(line - 1, -1, -1):
                        current_comparing_block = game_array[comparing_column][column]
                        
                        if current_comparing_block is not None:
                            if not current_comparing_block.merge:
                                if looking_for_first_block:
                                    looking_for_first_block = False
                                    if current_block.value == current_comparing_block.value:
                                        current_block.merge = True
                                        line_col = current_comparing_block.line_col
                                        has_anim = True
                                    else:
                                        pos_in_column += 1
                                else:
                                    pos_in_column += 1
                            else:
                                looking_for_first_block = False
                        else:
                            has_anim = True
                    
                    if not current_block.merge:
                        current_block.line_col = (pos_in_column, column)
                        ret[pos_in_column][column] = current_block
                        block_count_in_column += 1
                        
                    Clock.schedule_once(partial(current_block.animate, self.btn_dir, pos_in_column, line_col, False))
            
            # spawn NumberBlock
            if block_count_in_column < GAME_LINES and has_anim:
                rand_chance = randint(1, 100)
                
                if rand_chance <= SPAWN_CHANCE_PERCENT:
                    selected_value = str(choice(self.app.even_values_list))
                    
                    new_block = NumberBlock(value=selected_value)
                    
                    ret[block_count_in_column][column] = new_block
                    new_block.line_col = (block_count_in_column, column)
                    
                    new_block.animating = True
                    new_block.opacity = 0
                    new_block.disable = True
                    self.app.home_screen.ids.game_lyt.add_widget(new_block)
                    
                    Clock.schedule_once(partial(new_block.animate, self.btn_dir, block_count_in_column, None, True))
                        
        return ret
        
    def animate_left(self, game_array):
        ret = get_empty_array()
        
        for line in range(GAME_LINES):
            block_count_in_line = 0
            has_anim = False
            
            for column in range(GAME_COLUMNS):
                current_block = game_array[line][column]
                
                if current_block is not None:
                    current_block.animating = True
                    pos_in_line = 0
                    looking_for_first_block = True
                    line_col = (0, 0)
                    
                    for comparing_column in range(column -1, -1, -1):
                        current_comparing_block = game_array[line][comparing_column]
                        
                        if current_comparing_block is not None:
                            if not current_comparing_block.merge:
                                if looking_for_first_block:
                                    looking_for_first_block = False
                                    if current_block.value == current_comparing_block.value:
                                        current_block.merge = True
                                        line_col = current_comparing_block.line_col
                                        has_anim = True
                                    else:
                                        pos_in_line += 1
                                else:
                                    pos_in_line += 1
                            else:
                                looking_for_first_block = False
                        else:
                            has_anim = True
                    
                    if not current_block.merge:
                        current_block.line_col = (line, pos_in_line)
                        ret[line][pos_in_line] = current_block
                        block_count_in_line += 1
                        
                    Clock.schedule_once(partial(current_block.animate, self.btn_dir, pos_in_line, line_col, False))
            
            # spawn NumberBlock
            if block_count_in_line < GAME_COLUMNS and has_anim:
                rand_chance = randint(1, 100)
                
                if rand_chance <= SPAWN_CHANCE_PERCENT:
                    selected_value = str(choice(self.app.even_values_list))
                    
                    new_block = NumberBlock(value=selected_value)
                    
                    ret[line][block_count_in_line] = new_block
                    new_block.line_col = (line, block_count_in_line)
                    
                    new_block.animating = True
                    new_block.opacity = 0
                    new_block.disable = True
                    self.app.home_screen.ids.game_lyt.add_widget(new_block)
                    
                    Clock.schedule_once(partial(new_block.animate, self.btn_dir, block_count_in_line, None, True))
                        
        return ret
        
    def animate_right(self, game_array):
        ret = get_empty_array()
        
        for line in range(GAME_LINES):
            block_count_in_line = 0
            has_anim = False
            
            for column in range(GAME_COLUMNS - 1, -1, -1):
                current_block = game_array[line][column]
                
                if current_block is not None:
                    current_block.animating = True
                    pos_in_line = 0
                    looking_for_first_block = True
                    line_col = (0, 0)
                    
                    for x in range(column + 1, GAME_COLUMNS, 1):
                        current_comparing_block = game_array[line][x]
                        
                        if current_comparing_block is not None:
                            if not current_comparing_block.merge:
                                if looking_for_first_block:
                                    looking_for_first_block = False
                                    if current_block.value == current_comparing_block.value:
                                        current_block.merge = True
                                        line_col = current_comparing_block.line_col
                                        has_anim = True
                                    else:
                                        pos_in_line += 1
                                else:
                                    pos_in_line += 1
                            else:
                                looking_for_first_block = False
                        else:
                            has_anim = True
                    
                    if not current_block.merge:
                        current_block.line_col = (line, GAME_COLUMNS - 1 - pos_in_line)
                        ret[line][GAME_COLUMNS - 1 - pos_in_line] = current_block
                        block_count_in_line += 1
                        
                    Clock.schedule_once(partial(current_block.animate, self.btn_dir, pos_in_line, line_col, False))
            
            # spawn NumberBlock
            if block_count_in_line < GAME_COLUMNS and has_anim:
                rand_chance = randint(1, 100)
                
                if rand_chance <= SPAWN_CHANCE_PERCENT:
                    selected_value = str(choice(self.app.even_values_list))
                    
                    new_block = NumberBlock(value=selected_value)
                    
                    ret[line][GAME_COLUMNS - 1 - block_count_in_line] = new_block
                    new_block.line_col = (line, GAME_COLUMNS - 1 - block_count_in_line)
                    
                    new_block.animating = True
                    new_block.opacity = 0
                    new_block.disable = True
                    self.app.home_screen.ids.game_lyt.add_widget(new_block)
                    
                    Clock.schedule_once(partial(new_block.animate, self.btn_dir, block_count_in_line, None, True))
                    
        return ret
        
class HomeScreen(BoxLayout):
    
    def setup_game_widgets(self, game_array, *args):
        game = self.ids.game_lyt
        
        for line in range(GAME_LINES):
            for column in range(GAME_COLUMNS):
                current_block = game_array[line][column]
                
                if current_block is not None:
                    current_block.opacity = 0
                    current_block.disable = True
                    game.add_widget(current_block)
                
        Clock.schedule_once(partial(self.adjust_game_widgets, game_array))
   
    def adjust_game_widgets(self, game_array, *args):
        game = self.ids.game_lyt
        
        for line in range(GAME_LINES):
            for column in range(GAME_COLUMNS):
                current_block = game_array[line][column]
               
                if current_block is not None:
                    current_block.pos = (game.pos[0] + (current_block.width * column), game.pos[1] +  game.height - current_block.height - (current_block.height * line))
                    current_block.opacity = 1
                    current_block.disable = False


def generate_rand_column(rand_line):
    ret = randint(0, GAME_COLUMNS - 1)
    if rand_line == 0 or rand_line == (GAME_LINES - 1):
        return ret
    else:
        val = randint(0, 1)
        if val == 0:
            return 0
        else:
            return GAME_COLUMNS - 1

def get_empty_array():
    empty_array = []
    for line in range(GAME_LINES):
        empty_array.append([])
        for column in range(GAME_COLUMNS):
            empty_array[line].append(None)

    return empty_array

class MyApp(App):
    window_height = Window.height
    anim_speed = CLOCK_INTERVAL * CLOCK_ANIMATION_MULTIPLIER * NB_ANIMATION_SPEED
    game_array = []
    even_values_list = []
    
    def __init__(self, *args, **kwargs):
        super(MyApp, self).__init__(**kwargs)
        self.home_screen = HomeScreen()
        self.setup_even_values_list()
        self.game_array = get_empty_array()
        Clock.schedule_once(self.setup_game)

    def setup_even_values_list(self):
        self.even_values_list = [MAX_SPAWN_VALUE]
        n = MAX_SPAWN_VALUE
        while n > MIN_SPAWN_VALUE:
            x = int(n / 2)
            self.even_values_list.append(x)
            n = x
        
    def setup_game(self, *args):
        qnt = randint(MIN_STARTING_BLOCKS_QNT, MAX_STARTING_BLOCKS_QNT)
        
        for x in range(qnt):
           rand_line = randint(0, GAME_LINES - 1)
           rand_column = generate_rand_column(rand_line)
           
           while self.game_array[rand_line][rand_column] is not None:
               rand_line = randint(0, GAME_LINES - 1)
               rand_column = generate_rand_column(rand_line)

           rand_val = randint(0, 1)
           val = '2' if rand_val == 0 else '4'

           self.game_array[rand_line][rand_column] = NumberBlock(value=val)
        
        Clock.schedule_once(partial(self.home_screen.setup_game_widgets, self.game_array))

    def build(self):
        return self.home_screen
        
if __name__ == '__main__':
    MyApp().run()
