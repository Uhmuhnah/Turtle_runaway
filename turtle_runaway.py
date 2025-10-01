import tkinter as tk
import turtle, random, time, math


class RunawayGame:
    def __init__(self, screen, runner, chaser):
        self.screen = screen
        self.runner = runner
        self.chaser = chaser

        # --- Runner & Chaser 설정 ---
        self.runner.shape('turtle')
        self.runner.color('blue')
        self.runner.penup()

        self.chaser.shape('turtle')
        self.chaser.color('red')
        self.chaser.penup()

        # --- UI 거북이 ---
        self.status_drawer = turtle.RawTurtle(screen)
        self.timer_drawer = turtle.RawTurtle(screen)
        self.score_drawer = turtle.RawTurtle(screen)
        for d in (self.status_drawer, self.timer_drawer, self.score_drawer):
            d.hideturtle()
            d.penup()

        # --- Timer & Score ---
        self.start_time = None
        self.time_limit = 180   # 제한 시간 (초)
        self.score = 0

        # 골든 터틀 관련
        self.runner_color = "blue"
        self.gold_prob = 0.10  # 시작 확률 10%

    # ✅ 잡힘 판정 개선 : 거북이 실제 크기 반영
    def is_catched(self):
        px, py = self.runner.pos()
        qx, qy = self.chaser.pos()
        runner_radius = 10 * self.runner.shapesize()[0]
        chaser_radius = 10 * self.chaser.shapesize()[0]
        dist = math.hypot(px - qx, py - qy)
        return dist <= runner_radius + chaser_radius + 5

    def start(self, init_dist=400, ai_timer_msec=100):
        self.runner.setpos((-init_dist / 2, 0))
        self.runner.setheading(0)
        self.chaser.setpos((+init_dist / 2, 0))
        self.chaser.setheading(180)

        self.ai_timer_msec = ai_timer_msec
        self.start_time = time.perf_counter()
        self.score = 0
        self.gold_prob = 0.10
        self.update_score()

        self.roll_runner_color()
        self.screen.ontimer(self.step, self.ai_timer_msec)

    def update_score(self):
        self.score_drawer.clear()
        self.score_drawer.color("black")
        self.score_drawer.goto(-330, 330)
        self.score_drawer.write(f"SCORE: {self.score}", font=("Courier", 20, "bold"))

    def roll_runner_color(self):
        """도망자 색을 현재 골든 확률에 따라 결정"""
        if random.random() < self.gold_prob:
            self.runner_color = "gold"
            self.runner.color("gold")
            self.status_drawer.clear()
            self.status_drawer.goto(0, 260)
            self.status_drawer.write("GOLDEN TURTLE APPEARED!", align="center",
                                     font=("Arial", 18, "bold"))
        else:
            self.runner_color = "blue"
            self.runner.color("blue")
            self.status_drawer.clear()

    def respawn_runner(self):
        """잡히면 도망자 재배치 + 골든 확률 2% 증가"""
        safe_dist = 200
        while True:
            x = random.randint(-300, 300)
            y = random.randint(-300, 300)
            if math.hypot(x - self.chaser.xcor(), y - self.chaser.ycor()) > safe_dist:
                break
        self.runner.setpos(x, y)
        self.runner.setheading(random.randint(0, 359))

        # ✅ 확률 증가 (최대 100%)
        self.gold_prob = min(1.0, self.gold_prob + 0.02)
        self.roll_runner_color()

    def end_game(self, msg=None):
        """게임 종료 시 호출"""
        self.status_drawer.clear()
        self.timer_drawer.clear()
        self.status_drawer.goto(0, 0)
        final_text = f"FINAL SCORE: {self.score}"
        if msg:
            final_text = f"{msg}\n{final_text}"
        self.status_drawer.write(final_text, align="center", font=("Arial", 30, "bold"))

    def step(self):
        self.runner.run_ai(self.chaser.pos(), self.chaser.heading())
        self.chaser.run_ai(self.runner.pos(), self.runner.heading())

        # --- 잡힘 ---
        if self.is_catched():
            if self.runner_color == "gold":
                self.score += 100
                self.update_score()
                self.end_game("GOLDEN TURTLE CAUGHT!")
                return
            else:
                self.score += 1
                self.update_score()
                self.respawn_runner()

        # --- 타이머 ---
        elapsed = time.perf_counter() - self.start_time
        remain = self.time_limit - elapsed
        self.timer_drawer.clear()
        self.timer_drawer.goto(-300, 300)
        self.timer_drawer.color("red" if remain <= 5 else "green")
        self.timer_drawer.write(f"TIME {remain:0.1f}s", font=("Courier", 20, "bold"))

        if remain <= 0:
            self.end_game("TIME OVER")
            return

        self.screen.ontimer(self.step, self.ai_timer_msec)


class ManualMover(turtle.RawTurtle):
    """키보드 방향키 조합 지원 (동시에 두 개 이상 + 아래키는 방향 전환)"""
    def __init__(self, screen, step_move=10, step_turn=10, boundary=330):
        super().__init__(screen)
        self.step_move = step_move
        self.step_turn = step_turn
        self.boundary = boundary
        self.pressed = {"Up": False, "Down": False, "Left": False, "Right": False}

        screen.onkeypress(lambda: self.set_key("Up", True), "Up")
        screen.onkeyrelease(lambda: self.set_key("Up", False), "Up")
        screen.onkeypress(lambda: self.set_key("Down", True), "Down")
        screen.onkeyrelease(lambda: self.set_key("Down", False), "Down")
        screen.onkeypress(lambda: self.set_key("Left", True), "Left")
        screen.onkeyrelease(lambda: self.set_key("Left", False), "Left")
        screen.onkeypress(lambda: self.set_key("Right", True), "Right")
        screen.onkeyrelease(lambda: self.set_key("Right", False), "Right")

        screen.listen()
        self.move_loop(screen)

    def set_key(self, key, state):
        self.pressed[key] = state

    def move_loop(self, screen):
        if self.pressed["Up"]:
            self.safe_forward(self.step_move)
        if self.pressed["Down"]:
            self.setheading((self.heading() + 180) % 360)
            self.safe_forward(self.step_move)
        if self.pressed["Left"]:
            self.left(self.step_turn)
        if self.pressed["Right"]:
            self.right(self.step_turn)

        screen.ontimer(lambda: self.move_loop(screen), 20)

    def safe_forward(self, distance):
        new_x = self.xcor() + math.cos(math.radians(self.heading())) * distance
        new_y = self.ycor() + math.sin(math.radians(self.heading())) * distance
        if new_x > self.boundary: new_x = self.boundary
        if new_x < -self.boundary: new_x = -self.boundary
        if new_y > self.boundary: new_y = self.boundary
        if new_y < -self.boundary: new_y = -self.boundary
        self.setpos(new_x, new_y)

    def run_ai(self, opp_pos, opp_heading):
        pass


class RunnerAI(turtle.RawTurtle):
    """지능형 도망자 AI"""
    def __init__(self, screen, base_move=28, step_turn=12, boost_distance=180, boundary=330):
        super().__init__(screen)
        self.base_move = base_move
        self.step_turn = step_turn
        self.boost_distance = boost_distance
        self.boundary = boundary

    def safe_forward(self, distance):
        cx, cy = self.xcor(), self.ycor()
        rad = math.radians(self.heading())
        px = cx + math.cos(rad) * distance
        py = cy + math.sin(rad) * distance
        if abs(px) > self.boundary or abs(py) > self.boundary:
            max_allowed = distance
            if px > self.boundary:
                max_allowed = min(max_allowed, (self.boundary - cx) / math.cos(rad))
            elif px < -self.boundary:
                max_allowed = min(max_allowed, (-self.boundary - cx) / math.cos(rad))
            if py > self.boundary:
                max_allowed = min(max_allowed, (self.boundary - cy) / math.sin(rad))
            elif py < -self.boundary:
                max_allowed = min(max_allowed, (-self.boundary - cy) / math.sin(rad))
            if max_allowed < 0: max_allowed = 0
            super().forward(max_allowed)
        else:
            super().forward(distance)

    def run_ai(self, opp_pos, opp_heading):
        predict_x = opp_pos[0] + math.cos(math.radians(opp_heading)) * 30
        predict_y = opp_pos[1] + math.sin(math.radians(opp_heading)) * 30
        dx = self.xcor() - predict_x
        dy = self.ycor() - predict_y
        escape_angle = (math.degrees(math.atan2(dy, dx))) % 360
        if abs(self.xcor()) > self.boundary - 50 or abs(self.ycor()) > self.boundary - 50:
            to_center = math.degrees(math.atan2(-self.ycor(), -self.xcor()))
            escape_angle = (escape_angle * 0.5 + to_center * 0.5) % 360
        dist = math.hypot(self.xcor() - opp_pos[0], self.ycor() - opp_pos[1])
        if dist < self.boost_distance:
            move = self.base_move * 1.8
            turn_speed = self.step_turn * 1.5
        else:
            move = self.base_move
            turn_speed = self.step_turn
        diff = (escape_angle - self.heading() + 540) % 360 - 180
        if diff > 0: self.left(min(diff, turn_speed))
        else: self.right(min(-diff, turn_speed))
        self.safe_forward(move)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Turtle Runaway")
    canvas = tk.Canvas(root, width=700, height=700)
    canvas.pack()
    screen = turtle.TurtleScreen(canvas)

    canvas.focus_set()

    # --- 경계선 표시 ---
    screen.tracer(0)
    border = turtle.RawTurtle(screen)
    border.hideturtle()
    border.speed(0)
    border.pensize(3)
    border.color("gray")
    border.penup()
    border.goto(-330, -330)
    border.pendown()
    for _ in range(4):
        border.forward(660)
        border.left(90)
    screen.tracer(1)

    runner = RunnerAI(screen)
    chaser = ManualMover(screen)

    game = RunawayGame(screen, runner, chaser)
    game.start()
    screen.mainloop()
