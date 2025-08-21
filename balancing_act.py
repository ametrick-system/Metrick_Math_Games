
import pygame
import random
import sys
import math
from collections import defaultdict

pygame.init()
# ---- Fonts (Verdana everywhere) ----
FONT = pygame.font.SysFont("verdana", 24)
SMALL = pygame.font.SysFont("verdana", 18)
BIG = pygame.font.SysFont("verdana", 40)
BOLD = pygame.font.SysFont("verdana", 24, bold=True)
TITLE = pygame.font.SysFont("verdana", 48, bold=True)

# ---- Window ----
W, H = 1200, 800
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Balancing Act! (v7.1)")
CLOCK = pygame.time.Clock()

# ---- Colors ----
BG = (242, 244, 247)
WOOD = (193, 154, 107)
DARK_WOOD = (160, 120, 80)
LINE = (60, 60, 60)
PURPLE = (0x77, 0x00, 0xC7)  # X blocks
TEAL = (0x00, 0xE6, 0xDE)    # 1 blocks
WHITE = (255, 255, 255)
GREEN = (0, 105, 30)  # 00691E
RED = (133, 15, 0)  # 850F00
LIGHT = (230, 230, 230)
MID_GRAY = (160, 160, 160)   # gray trash outline
DARK_TXT = (30, 40, 50)
HILITE_BG = (255, 255, 240)
BTN = (255, 255, 255)
BTN_LINE = (70, 90, 120)

# ---- Geometry / Layout ----
BEAM_Y = 600
FULCRUM_TOP_Y = 616
LEFT_X = 160
RIGHT_X = W - 160
CENTER_X = (LEFT_X + RIGHT_X) // 2

PAN_W = 280
PAN_TRAY_H = 24
PAN_TOP_MARGIN = 12
BEAM_THICKNESS = 18
BLOCK = 44
GRID = BLOCK

# ---- UI ----
# Palette
PALETTE_X = pygame.Rect(W//2 - 70, 260, 56, 56)
PALETTE_1 = pygame.Rect(W//2 + 14, 260, 56, 56)

# x = [____] input under palette
INPUT_LABEL_POS = (W//2 - 110, 206)
INPUT_BOX = pygame.Rect(W//2 - 60, 200, 120, 44)
FEEDBACK_POS = (W//2 + 80, 208)

# Bottom buttons
BTN_CLEAR = pygame.Rect(CENTER_X - 330, H-80, 130, 48)
BTN_NEW   = pygame.Rect(CENTER_X - 90,  H-80, 180, 48)   # wider
BTN_CHECK = pygame.Rect(W//2 + 170, H-80, 130, 48)

# Gray Trash (left bottom)
TRASH = pygame.Rect(20, 20, 110, 78)

MAX_STACK = 10

def clamp(v, lo, hi): return max(lo, min(hi, v))

def line_y_at(x, theta_rad, through_y=BEAM_Y):
    m = math.tan(theta_rad)
    return through_y + (x - CENTER_X) * m

def get_pan_surfaces(theta_rad):
    yL = line_y_at(LEFT_X + PAN_W//2, theta_rad)
    yR = line_y_at(RIGHT_X - PAN_W//2, theta_rad)
    panL = pygame.Rect(LEFT_X, int(yL - PAN_TRAY_H - PAN_TOP_MARGIN), PAN_W, PAN_TRAY_H)
    panR = pygame.Rect(RIGHT_X - PAN_W, int(yR - PAN_TRAY_H - PAN_TOP_MARGIN), PAN_W, PAN_TRAY_H)
    y_top_L = panL.top
    y_top_R = panR.top
    return panL, panR, y_top_L, y_top_R

def draw_beam(theta_rad):
    yL = line_y_at(LEFT_X, theta_rad, through_y=BEAM_Y)
    yR = line_y_at(RIGHT_X, theta_rad, through_y=BEAM_Y)
    pygame.draw.line(screen, WOOD, (LEFT_X, yL), (RIGHT_X, yR), BEAM_THICKNESS)

def draw_tray_3d(pan_rect, theta_rad):
    pygame.draw.rect(screen, WOOD, pan_rect, border_radius=10)
    pygame.draw.rect(screen, LINE, pan_rect, 2, border_radius=10)
    shadow = pan_rect.copy(); shadow.y += 6
    pygame.draw.rect(screen, (170,130,85), shadow.inflate(0, -8), border_radius=10)
    post_x = pan_rect.x + pan_rect.width//2 - 25
    pygame.draw.rect(screen, WOOD, (post_x, int(line_y_at(post_x, theta_rad)) - 25, 50, 25))

def draw_fulcrum_and_sign(sign_text):
    # Bigger triangle
    base_half = 90
    height = 80
    apex_y = FULCRUM_TOP_Y + height
    pts = [(CENTER_X - base_half, FULCRUM_TOP_Y),
           (CENTER_X + base_half, FULCRUM_TOP_Y),
           (CENTER_X, apex_y)]
    pygame.draw.polygon(screen, WOOD, pts)
    pygame.draw.polygon(screen, LINE, pts, 2)
    # Center the sign inside the triangle with color
    cx, cy = CENTER_X, FULCRUM_TOP_Y + int(height*0.55)
    color = GREEN if sign_text == '=' else RED
    label = BIG.render(sign_text, True, color)
    screen.blit(label, label.get_rect(center=(cx, cy)))

def draw_palette():
    # Title
    title = TITLE.render("Balancing Act!", True, DARK_TXT)
    screen.blit(title, title.get_rect(center=(W//2, 50)))
    # Palette label
    subtitle = SMALL.render("Click and drag to add to the scale!", True, DARK_TXT)
    screen.blit(subtitle, subtitle.get_rect(center=(W//2, 96)))
    # X block
    pygame.draw.rect(screen, PURPLE, PALETTE_X, border_radius=10)
    pygame.draw.rect(screen, BTN_LINE, PALETTE_X, 2, border_radius=10)
    screen.blit(BOLD.render("X", True, (255,255,255)), BOLD.render("X", True, (255,255,255)).get_rect(center=PALETTE_X.center))
    # 1 block
    pygame.draw.rect(screen, TEAL, PALETTE_1, border_radius=10)
    pygame.draw.rect(screen, BTN_LINE, PALETTE_1, 2, border_radius=10)
    screen.blit(BOLD.render("1", True, (30,50,50)), BOLD.render("1", True, (30,50,50)).get_rect(center=PALETTE_1.center))

def draw_buttons():
    def draw_btn(rect, text):
        pygame.draw.rect(screen, BTN, rect, border_radius=12)
        pygame.draw.rect(screen, BTN_LINE, rect, 2, border_radius=12)
        lab = SMALL.render(text, True, (20,40,60))
        screen.blit(lab, lab.get_rect(center=rect.center))
    draw_btn(BTN_CLEAR, "Clear")
    draw_btn(BTN_NEW,   "New Problem")
    draw_btn(BTN_CHECK, "Check")

def draw_trash_gray():
    body = TRASH.copy()
    pygame.draw.rect(screen, (200,200,200), body, border_radius=12)
    pygame.draw.rect(screen, MID_GRAY, body, 2, border_radius=12)
    lid = pygame.Rect(body.x+12, body.y-12, body.width-24, 14)
    pygame.draw.rect(screen, (200,200,200), lid, border_radius=6)
    pygame.draw.rect(screen, MID_GRAY, lid, 2, border_radius=6)
    pygame.draw.rect(screen, MID_GRAY, (lid.centerx-12, lid.y-7, 24, 7), border_radius=3)
    lab = SMALL.render("Trash", True, (70,70,70))
    screen.blit(lab, (body.centerx - lab.get_width()//2, body.bottom + 6))

def format_linear(a, b, show_zero_x=False):
    parts = []
    if a != 0 or show_zero_x:
        parts.append("x" if a == 1 else f"{a}x")
    if b != 0 or not parts:
        if parts:
            parts.append("+ " + str(b))
        else:
            parts.append(str(b))
    return " ".join(parts) if parts else "0"

def format_label(a,b):
    ax = "0x" if a == 0 else ("x" if a == 1 else f"{a}x")
    return f"{ax} + {b}"

def generate_problem():
    for _ in range(200):
        aL = random.randint(0, 4)
        aR = random.randint(0, 4)
        if aL == 0 and aR == 0:
            continue
        if aL == aR:
            continue
        bL = random.randint(0, 9)
        x_star = random.randint(0, 9)
        bR = aL*x_star + bL - aR*x_star
        if 0 <= bR <= 15:
            return aL if aL!=0 else 1, bL, aR, int(bR), x_star
    return 2, 3, 1, 5, 2

def weight(nX, n1, x_val): return nX * x_val + n1

class Block(pygame.sprite.Sprite):
    counter = 0
    def __init__(self, kind, pos):
        super().__init__()
        self.kind = kind  # 'X' or '1'
        self.image = pygame.Surface((BLOCK, BLOCK), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)
        self.selected = False
        self.in_pan = None
        self.column = None
        self.level = None
        self.placed_id = Block.counter; Block.counter += 1
        self.draw_block()

    def draw_block(self):
        self.image.fill((0,0,0,0))
        color = PURPLE if self.kind == 'X' else TEAL
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=10)
        pygame.draw.rect(self.image, (40,40,60), self.image.get_rect(), 2, border_radius=10)
        txt_color = (255,255,255) if self.kind == 'X' else (20,40,40)
        self.image.blit(BOLD.render(self.kind, True, txt_color), BOLD.render(self.kind, True, txt_color).get_rect(center=self.image.get_rect().center))

    def update_drag(self, mouse_pos):
        if self.selected: self.rect.center = mouse_pos

    def detach(self):
        self.in_pan = None; self.column = None; self.level = None

class Game:
    def __init__(self):
        self.blocks = pygame.sprite.Group()
        self.dragging = None
        self.aL, self.bL, self.aR, self.bR, self.x_star = generate_problem()
        self.theta_deg = 0.0
        self.columns = self.compute_columns()
        # input state
        self.input_text = ""
        self.input_active = False
        self.feedback = ""
        self.feedback_color = RED

    def compute_columns(self):
        cols = []
        left_margin = 14
        usable = PAN_W - 2*left_margin
        ncols = int(usable // GRID)  # same count as before (typically 5)
        start_x = left_margin + (usable - ncols*GRID)//2
        for i in range(ncols):
            cols.append(start_x + i*GRID)
        return cols

    def reset(self):
        self.blocks.empty(); self.input_text = ""; self.input_active = False; self.feedback = ""

    def new_problem(self):
        self.blocks.empty()
        self.aL, self.bL, self.aR, self.bR, self.x_star = generate_problem()
        self.theta_deg = 0.0
        self.input_text = ""; self.input_active = False; self.feedback = ""

    def handle_mouse_down(self, pos, button):
        if button != 1: return
        if PALETTE_X.collidepoint(pos):
            self.blocks.add(Block('X', (PALETTE_X.centerx-BLOCK//2, PALETTE_X.bottom+10))); return
        if PALETTE_1.collidepoint(pos):
            self.blocks.add(Block('1', (PALETTE_1.centerx-BLOCK//2, PALETTE_1.bottom+10))); return
        if BTN_CLEAR.collidepoint(pos): self.reset(); return
        if BTN_NEW.collidepoint(pos): self.new_problem(); return
        if BTN_CHECK.collidepoint(pos): self.check_answer(); return
        if INPUT_BOX.collidepoint(pos): self.input_active = True; return
        else: self.input_active = False
        for spr in sorted(self.blocks.sprites(), key=lambda s: s.placed_id, reverse=True):
            if spr.rect.collidepoint(pos):
                self.dragging = spr; spr.selected = True; break

    def handle_mouse_up(self, pos, button, panL, panR):
        if button != 1: return
        if self.dragging:
            if self.dragging.rect.colliderect(TRASH):
                self.blocks.remove(self.dragging)
            else:
                self.dragging.selected = False
                attached = False
                if self.dragging.rect.colliderect(panL):
                    self.attach_to_pan(self.dragging, 'L', panL); attached = True
                elif self.dragging.rect.colliderect(panR):
                    self.attach_to_pan(self.dragging, 'R', panR); attached = True
                if not attached: self.dragging.detach()
            self.dragging = None

    def handle_key(self, key):
        if key in (pygame.K_DELETE, pygame.K_BACKSPACE):
            if self.input_active and len(self.input_text)>0:
                self.input_text = self.input_text[:-1]
            else:
                for s in [s for s in self.blocks if s.selected]: self.blocks.remove(s)
        elif key == pygame.K_RETURN:
            if self.input_active: self.check_answer()
        elif self.input_active:
            if key == pygame.K_MINUS:
                if len(self.input_text)==0: self.input_text += "-"
            else:
                ch = pygame.key.name(key)
                if ch.isdigit() and len(self.input_text) < 6:
                    self.input_text += ch

    def check_answer(self):
        if self.input_text.strip() == "":
            self.feedback = "Enter a value for x."; self.feedback_color = RED; return
        try:
            guess = int(self.input_text.strip())
        except ValueError:
            self.feedback = "Please enter an integer."; self.feedback_color = RED; return
        if guess == self.x_star:
            self.feedback = "Correct!"; self.feedback_color = GREEN
        else:
            self.feedback = "Try again."; self.feedback_color = RED

    def update_drag(self):
        if self.dragging: self.dragging.update_drag(pygame.mouse.get_pos())

    def attach_to_pan(self, block, side, pan_rect):
        px = block.rect.centerx - pan_rect.x
        nearest_col = min(range(len(self.columns)), key=lambda i: abs(self.columns[i] + BLOCK//2 - px))
        candidate_cols = sorted(range(len(self.columns)), key=lambda i: (abs(i - nearest_col), i))
        chosen = None
        for col in candidate_cols:
            if self.column_height(side, col) < MAX_STACK:
                chosen = col; break
        if chosen is None:
            self.feedback = "Pan is full (no column space)."; self.feedback_color = RED
            block.detach(); return
        block.in_pan = side; block.column = chosen

    def column_height(self, side, col):
        return sum(1 for b in self.blocks if b.in_pan == side and b.column == col)

    def relayout_stacks(self, panL, panR, y_top_L, y_top_R):
        for side, pan_rect, y_top in [('L', panL, y_top_L), ('R', panR, y_top_R)]:
            stacks = defaultdict(list)
            for b in self.blocks:
                if b.in_pan == side and b.column is not None:
                    stacks[b.column].append(b)
            for col, items in stacks.items():
                items.sort(key=lambda b: b.placed_id)  # old at bottom, new at top
                for level, b in enumerate(items):
                    if level >= MAX_STACK:
                        b.in_pan = None; b.column = None; b.level = None
                        continue
                    b.level = level
                    x = pan_rect.x + self.columns[col]
                    y = int(y_top - BLOCK - level*BLOCK)
                    b.rect.topleft = (x, y)

    def count_blocks_by_pan(self):
        aL = bL = aR = bR = 0
        for b in self.blocks:
            if b.in_pan == 'L':
                if b.kind == 'X': aL += 1
                else: bL += 1
            elif b.in_pan == 'R':
                if b.kind == 'X': aR += 1
                else: bR += 1
        return aL, bL, aR, bR

    def compute_tilt(self):
        aL,bL,aR,bR = self.count_blocks_by_pan()
        wL = weight(aL, bL, self.x_star); wR = weight(aR, bR, self.x_star)
        diff = wR - wL
        target = clamp(diff * 2.0, -12.0, 12.0)
        self.theta_deg += (target - self.theta_deg) * 0.15
        return math.radians(self.theta_deg), (aL,bL,aR,bR,wL,wR)

def draw_summary_box(text, topleft, align_right=False):
    surf = BOLD.render(text, True, DARK_TXT)
    pad = 10
    rect = pygame.Rect(0,0, surf.get_width()+2*pad, surf.get_height()+2*pad)
    rect.topleft = topleft if not align_right else (topleft[0]-rect.width, topleft[1])
    pygame.draw.rect(screen, HILITE_BG, rect, border_radius=10)
    pygame.draw.rect(screen, BTN_LINE, rect, 2, border_radius=10)
    screen.blit(surf, (rect.x+pad, rect.y+pad))

game = Game()

# ---- Main loop ----
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN: game.handle_mouse_down(event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            theta = math.radians(game.theta_deg)
            panL_cur, panR_cur, yL_top, yR_top = get_pan_surfaces(theta)
            game.handle_mouse_up(event.pos, event.button, panL_cur, panR_cur)
        elif event.type == pygame.KEYDOWN: game.handle_key(event.key)

    game.update_drag()
    theta_rad, (aL,bL,aR,bR,wL,wR) = game.compute_tilt()
    panL, panR, yL_top, yR_top = get_pan_surfaces(theta_rad)

    # layout and ride
    game.relayout_stacks(panL, panR, yL_top, yR_top)

    # ---- Draw ----
    screen.fill(BG)
    draw_palette()

    # Equation below palette
    left_txt = format_linear(game.aL, game.bL, show_zero_x=False)
    right_txt = format_linear(game.aR, game.bR, show_zero_x=False)
    eq_surface = BIG.render(f"{left_txt} = {right_txt}", True, (20,30,50))
    screen.blit(eq_surface, eq_surface.get_rect(center=(W//2, 160)))

    # x input + feedback (top)
    label = SMALL.render("x =", True, DARK_TXT)
    screen.blit(label, INPUT_LABEL_POS)
    pygame.draw.rect(screen, WHITE, INPUT_BOX, border_radius=10)
    pygame.draw.rect(screen, BTN_LINE, INPUT_BOX, 2, border_radius=10)
    txt = SMALL.render(game.input_text if game.input_text else "", True, DARK_TXT)
    screen.blit(txt, (INPUT_BOX.x + 10, INPUT_BOX.y + (INPUT_BOX.height - txt.get_height())//2))
    # blinking caret
    if game.input_active:
        caret_x = INPUT_BOX.x + 10 + txt.get_width() + 2
        caret_y1 = INPUT_BOX.y + 8
        caret_y2 = INPUT_BOX.y + INPUT_BOX.height - 8
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            pygame.draw.line(screen, (30,40,50), (caret_x, caret_y1), (caret_x, caret_y2), 2)
    if game.feedback:
        fb = SMALL.render(game.feedback, True, game.feedback_color)
        screen.blit(fb, FEEDBACK_POS)

    # Beam, fulcrum, pans
    draw_beam(theta_rad)
    eps = 1e-9
    sign = "=" if abs(wL - wR) < eps else ("<" if wL < wR else ">")
    draw_fulcrum_and_sign(sign)
    draw_tray_3d(panL, theta_rad)
    draw_tray_3d(panR, theta_rad)

    # Buttons & gray trash
    draw_buttons()
    draw_trash_gray()

    # Blocks
    for spr in game.blocks:
        if not spr.selected: screen.blit(spr.image, spr.rect)
    for spr in game.blocks:
        if spr.selected: screen.blit(spr.image, spr.rect)

    # Top summary boxes with more spacing
    left_summary = f"Left: {'x' if aL==1 else f'{aL}x' if aL!=0 else '0x'} + {bL}"
    right_summary = f"Right: {'x' if aR==1 else f'{aR}x' if aR!=0 else '0x'} + {bR}"
    draw_summary_box(left_summary, (40, 140))
    draw_summary_box(right_summary, (W-40, 140), align_right=True)

    # Selection outline
    for spr in game.blocks:
        if spr.selected:
            pygame.draw.rect(screen, (50,120,220), spr.rect.inflate(6,6), 2, border_radius=10)

    pygame.display.flip(); CLOCK.tick(60)
