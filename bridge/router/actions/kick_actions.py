from typing import Optional

from bridge import const
from bridge.auxiliary import aux

from . import Actions
from .action import Action, ActionDomain, ActionValues
from .dumb_actions import DumbActions


class KickActions:

    """Class with available types of ball kicks"""

    class Kick(Action):
        """Base class"""

        def __init__(
            self,
            target_pos: aux.Point,
            voltage: int = const.VOLTAGE_SHOOT,
            is_pass: bool = False,
            is_upper: bool = False,
        ) -> None:
            self.target_pos = target_pos
            self.voltage = voltage  # ignore if is_pass
            self.is_upper = is_upper
            self.is_pass = is_pass

            if self.voltage > const.VOLTAGE_SHOOT:
                self.voltage = const.VOLTAGE_SHOOT

            if self.is_upper:
                self.voltage = const.VOLTAGE_UP

            self.pass_pos: Optional[aux.Point] = None
            if is_pass:
                self.pass_pos = self.target_pos

    class Straight(Kick):
        """Grab the ball and kick it straight"""

        def use_behavior_of(self, domain: ActionDomain, current_action: ActionValues) -> list["Action"]:
            kick_angle = aux.angle_to_point(domain.field.ball.get_pos(), self.target_pos)

            if (domain.field.is_ball_in(domain.robot)):
                domain.robot.kick_type = Kick_Status.Straight

            actions = [
                Actions.BallGrab(kick_angle),
                DumbActions.ShootAction(self.target_pos, self.is_upper),
                DumbActions.ControlVoltageAction(self.voltage, self.pass_pos),
            ]

            return actions
        
    class Turn_Kick2(Kick):
        def __init__(
            self,
            target_pos: aux.Point,
            start_angle: float,
            voltage: int = const.VOLTAGE_SHOOT,
            is_pass: bool = False,
            is_upper: bool = False,
        ) -> None:
            self.start_angle = start_angle

            super().__init__(target_pos, voltage, is_pass, is_upper) 

        """Grab the ball, rotates to the desired angle and kick it straight"""
        def use_behavior_of(self, domain: ActionDomain, current_action: ActionValues) -> list["Action"]:
            global old_speed_for_turn_stop

            kick_angle = aux.angle_to_point(domain.field.ball.get_pos(), self.target_pos)
            target_angle = (self.target_pos - domain.field.ball.get_pos()).arg()
            time_to_kick = 0.5 + 0.3 * self.is_pass
            diff =  abs(aux.wind_down_angle((target_angle - domain.robot.get_angle())))

            actions = [
                Actions.BallGrab(self.start_angle),
                Actions.Turn2(kick_angle, self.start_angle),
                DumbActions.ControlVoltageAction(self.voltage, self.pass_pos)
            ]
            if(domain.field.is_ball_in(domain.robot)) :
                domain.robot.kick_type = Kick_Status.Turn_Kick
                domain.robot.flag_ball_in_turn = True

            if (not domain.field.is_ball_in_turn(domain.robot)):
                domain.robot.flag_ball_in_turn = False
                old_speed_for_turn_stop = 300
                domain.robot.old_actions_angle = 0

            if (not domain.field.is_ball_in_turn(domain.robot) and domain.robot.flag_ball_in_turn
                or diff > const.KICK_ALIGN_ANGLE + 0.1):
                domain.robot.timer_to_stop = time()

            if (domain.field.is_ball_in_turn(domain.robot) and domain.robot.flag_ball_in_turn
                and diff <= const.KICK_ALIGN_ANGLE + 0.15 and abs(domain.robot.old_actions_angle) < 0.2):
                print("Correct", current_action.angle)
                actions.append(Actions.Correct(target_angle))

            if (domain.field.is_ball_in_turn(domain.robot) and domain.robot.flag_ball_in_turn
                and diff <= const.KICK_ALIGN_ANGLE + 0.1
                and time() - domain.robot.timer_to_stop > time_to_kick):
                actions.append(DumbActions.ShootAction(self.target_pos, self.is_upper))

            print(domain.field.ball.get_pos(), "ball")
            if domain.field.is_ball_in_turn(domain.robot) and domain.robot.flag_ball_in_turn:
                print(time() - domain.robot.timer_to_stop, abs(aux.wind_down_angle(target_angle - domain.robot.get_angle())), "this")
            else:
                print(domain.field.is_ball_in_turn(domain.robot))
                print((domain.robot.get_pos() - domain.field.ball.get_pos()).mag(), abs(aux.wind_down_angle((domain.field.ball.get_pos() - domain.robot.get_pos()).arg() - domain.robot.get_angle())))
            return actions
        
    class Turn_Kick(Kick):
        def __init__(
            self,
            target_pos: aux.Point,
            start_angle: float,
            voltage: int = const.VOLTAGE_SHOOT,
            flag_kick_pas: bool = False, 
            is_pass: bool = False,
            is_upper: bool = False,
        ) -> None:
            self.start_angle = start_angle
            self.flag_kick_pas = flag_kick_pas

            super().__init__(target_pos, voltage, is_pass, is_upper) 

        """Grab the ball, rotates to the desired angle and kick it straight"""
        def use_behavior_of(self, domain: ActionDomain, current_action: ActionValues) -> list["Action"]:
            global old_speed_for_turn
            global timer_to_stop
            global flag_ball_in_turn
            global old_speed_for_turn_stop
            kick_angle = aux.angle_to_point(domain.field.ball.get_pos(), self.target_pos)
            target_angle = (self.target_pos - domain.field.ball.get_pos()).arg()
            time_to_kick = 0.4 + 0.2 * self.flag_kick_pas
            diff =  abs(aux.wind_down_angle((target_angle - domain.robot.get_angle())))

            actions = [
                Actions.BallGrab(self.start_angle),
                Actions.Turn(kick_angle, self.start_angle),
                DumbActions.ControlVoltageAction(self.voltage, self.pass_pos)
            ]
            if(domain.field.is_ball_in(domain.robot)) :
                flag_ball_in_turn = True

            if (not domain.field.is_ball_in_turn(domain.robot)):
                flag_ball_in_turn = False
                old_speed_for_turn = const.START_VEL_TURN
                old_speed_for_turn_stop = 200

                
            if (not domain.field.is_ball_in_turn(domain.robot) and flag_ball_in_turn
                or diff > const.KICK_ALIGN_ANGLE + 0.1):
                timer_to_stop = time()

            if (domain.field.is_ball_in_turn(domain.robot) and flag_ball_in_turn
                and diff <= const.KICK_ALIGN_ANGLE + 0.15):
                print("Correct")
                actions.append(Actions.Correct(target_angle))

            if (domain.field.is_ball_in_turn(domain.robot) and flag_ball_in_turn
                and diff <= const.KICK_ALIGN_ANGLE + 0.1
                and time() - timer_to_stop > time_to_kick):
                actions.append(DumbActions.ShootAction(self.target_pos, self.is_upper))

            print(domain.field.ball.get_pos(), "ball")
            if domain.field.is_ball_in_turn(domain.robot) and flag_ball_in_turn:
                print(time() - timer_to_stop, abs(aux.wind_down_angle(target_angle - domain.robot.get_angle())), "this")
            else:
                print(domain.field.is_ball_in_turn(domain.robot))
                print((domain.robot.get_pos() - domain.field.ball.get_pos()).mag(), abs(aux.wind_down_angle((domain.field.ball.get_pos() - domain.robot.get_pos()).arg() - domain.robot.get_angle())))
            return actions


    class Kick_Goal(Kick):
        def __init__(
            self,
            kick_type_turn: str = "auto",
            kick_type: KickType = KickType.AUTO,
            voltage: int = const.VOLTAGE_SHOOT,
            is_upper: bool = False,
        ) -> None:
            """
            kick type:
                direct - выборочный
                stright - прямой
                ricochet - рикошетом
            """
            self.kick_type = kick_type
            self.kick_type_turn = kick_type_turn
            super().__init__(aux.Point(0, 0), voltage, False, is_upper)

        def use_behavior_of(self, domain: ActionDomain, current_action: ActionValues) -> list["Action"]:
            stright, stright_len = self.straight_candidate(domain, current_action)
            ricochet, ricochet_len = self.ricochet_candidate(domain, current_action)

            target = self.select_target(stright, stright_len, ricochet, ricochet_len)
            arg = (domain.field.ball.get_pos() - domain.robot.get_pos()).arg()
            if (target is None):
                target = domain.field.enemy_goal.center
            if (self.kick_type_turn == "s"):
                return [KickActions.Straight(target)]
            elif(self.kick_type_turn == "t"):
                return [KickActions.Turn_Kick2(target, arg)]
            return [KickActions.Kick_Auto(target)]
        
        def straight_candidate(self, domain: ActionDomain, current_action: ActionValues) -> tuple[aux.Point | None, float]:
            return check_goal_point(domain.field, domain.field.ball.get_pos())

        def ricochet_candidate(self, domain: ActionDomain, current_action: ActionValues) -> tuple[aux.Point | None, float]:
            ball_pos = domain.field.ball.get_pos()
            wall_point = get_ricochet_hit_point_center(domain.field, ball_pos)

            if wall_point is None:
                return None, 0.0
            
            point_in_goal, lenght = check_goal_point(domain.field, wall_point)
            if point_in_goal is None:
                return None, 0.0

            kick_point = get_ricochet_hit_point(domain.field, ball_pos, point_in_goal)
            if (kick_point is None):
                return None, 0.0
            
            return kick_point, lenght

        def select_target(self,        
            stright: aux.Point | None, stright_len: float,
            ricochet: aux.Point | None, ricochet_len: float
        ) -> aux.Point | None:
            if (self.kick_type == KickType.STRAIGHT):
                return stright
            if (self.kick_type == KickType.RICOCHET):
                return ricochet

            if stright is None:
                return ricochet
            if ricochet is None:
                return stright
            if (ricochet_len > stright_len * 4):
                return ricochet
            return stright


    class Kick_Auto(Kick):
        def use_behavior_of(self, domain: ActionDomain, current_action: ActionValues) -> list["Action"]:
            kick_auto_type = self.select_type(domain, current_action)
            kick_auto_type = Kick_Status.Straight
            if kick_auto_type == Kick_Status.Straight:
                return [KickActions.Straight(
                    self.target_pos, self.voltage, 
                    self.is_pass, self.is_upper
                )]
            return [KickActions.Turn_Kick2(
                self.target_pos, domain.robot.get_angle(), 
                self.voltage, self.is_pass, self.is_upper
            )]


        def select_type(self, domain: ActionDomain, current_action: ActionValues) -> Optional[Kick_Status]:
            if domain.robot.last_kick_type == Kick_Status.Turn_Kick:
                return Kick_Status.Turn_Kick

            ball_pos = domain.field.ball.get_pos()
            target_angle = (self.target_pos - ball_pos).arg()
            diff_angle = abs(aux.wind_down_angle(target_angle - domain.robot.get_angle()))
            diff_dist = aux.dist(domain.robot.get_pos(), ball_pos)

            if (diff_angle < const.KICK_ALIGN_ANGLE):
                return Kick_Status.Straight

            t_turn = diff_angle / const.ANGLE_VEL_MAX
            t_ride = diff_dist / const.MAX_SPEED / 3
            if (t_turn + 0.002 < t_ride):
                return Kick_Status.Straight
            
            return Kick_Status.Turn_Kick
