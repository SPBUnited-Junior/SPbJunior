from typing import Optional

from bridge import const
from bridge.auxiliary import aux, fld, rbt
from bridge.router.base_actions import Action, Actions


class OutBallLogic:
    """Логика вытаскивания мяча из-за аута"""

    def __init__(self) -> None:
        self.robot_id: Optional[int] = None
        self.start_x: float = 0.0
        self.side: int = 0  # +1 правый аут, -1 левый

    def reset(self) -> None:
        self.robot_id = None
        self.start_x = 0.0
        self.side = 0

    def process(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        ball_pos = field.ball.get_pos()
        right_wall = field.hull[0].x
        left_wall = field.hull[2].x
        dist_to_right = abs(ball_pos.x - right_wall)
        dist_to_left = abs(ball_pos.x - left_wall)

        # --- Проверка: мяч у аута? ---
        if dist_to_right > const.OUT_BALL_DIST and dist_to_left > const.OUT_BALL_DIST:
            self.reset()
            return

        # --- Назначаем робота ---
        if self.robot_id is None:
            candidates = [r for r in field.active_allies(False) if r.r_id != const.GK]
            if not candidates:
                return
            nearest = fld.find_nearest_robot(ball_pos, candidates)
            self.robot_id = nearest.r_id
            self.side = +1 if dist_to_right < dist_to_left else -1

        robot = field.allies[self.robot_id]
        if not robot.is_used():
            self.reset()
            return

        robot_pos = robot.get_pos()
        out_x = right_wall if self.side > 0 else left_wall

        # --- Запоминаем стартовую X при первом захвате ---
        if self.start_x == 0.0:
            self.start_x = ball_pos.x

        # --- Едем к мячу с дрибблером ---
        angle_to_ball = (ball_pos - robot_pos).arg()

        if aux.dist(robot_pos, ball_pos) > const.OUT_GRAB_DIST:
            # Ещё далеко — едем к мячу
            actions[robot.r_id] = Actions.GoToPoint(
                ball_pos, angle_to_ball, ball_interact=True, dribbler_speed=15
            )
        else:
            # Уже у мяча — захватываем и отъезжаем
            self.start_x = ball_pos.x
            target_pos = aux.Point(0.0, ball_pos.y)
            target_angle = (field.enemy_goal.center - robot_pos).arg()
            actions[robot.r_id] = Actions.GoToPoint(
                target_pos, target_angle, ball_interact=True, dribbler_speed=15
            )

            # Отъехали достаточно — сброс
            if abs(ball_pos.x - self.start_x) > const.OUT_RETREAT_DIST:
                self.reset()

    def is_active(self) -> bool:
        return self.robot_id is not None