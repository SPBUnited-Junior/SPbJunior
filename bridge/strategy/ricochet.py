"""
Модуль для визуализации и расчета рикошетных ударов в стенку
"""

from typing import List, Tuple, Optional

from bridge import const
from bridge.auxiliary import aux, fld


def draw_ricochet(field: fld.Field, ball_pos: aux.Point) -> None:


    right_wall = field.hull[0].x   # Правая стенка 
    left_wall = field.hull[2].x    # Левая стенка -
    top_wall = field.hull[0].y     # Верхняя стенка
    bottom_wall = field.hull[2].y  # Нижняя стенка -
    
    # Определяем, к какой стенке ближе мяч
    dist_to_right = abs(ball_pos.x - right_wall)
    dist_to_left = abs(ball_pos.x - left_wall)
    dist_to_top = abs(ball_pos.y - top_wall)
    dist_to_bottom = abs(ball_pos.y - bottom_wall)

    min_dist = min(dist_to_right, dist_to_left, dist_to_top, dist_to_bottom)
    
    # Выбираем стенку и ее координату
    if min_dist == dist_to_right:
        wall_x = right_wall
        wall_is_horizontal = False
    elif min_dist == dist_to_left:
        wall_x = left_wall
        wall_is_horizontal = False
    elif min_dist == dist_to_top:
        wall_y = top_wall
        wall_is_horizontal = True
    else:  
        wall_y = bottom_wall
        wall_is_horizontal = True
    
    goal_points = [
        field.enemy_goal.up,      
        field.enemy_goal.center,  
        field.enemy_goal.down,    
    ]
    
    if wall_is_horizontal:
        # верх или низ
        for goal_point in goal_points:
            # Отражаем точку ворот 
            dist_to_wall = abs(goal_point.y - wall_y)
            reflected_point = aux.Point(
                goal_point.x, 
                wall_y + dist_to_wall * (1 if wall_y > 0 else -1)
            )
            
            # Рисуем прямую линию от мяча к отраженной точке
            field.strategy_image.draw_line(
                ball_pos,
                reflected_point,
                (255, 255, 0),  
                2
            )
            

            field.strategy_image.draw_circle(
                reflected_point,
                (255, 0, 255), 
                10
            )
            
            # место удара
            if abs(reflected_point.y - ball_pos.y) > 0.1:
                t = (wall_y - ball_pos.y) / (reflected_point.y - ball_pos.y)
                hit_x = ball_pos.x + t * (reflected_point.x - ball_pos.x)
                hit_point = aux.Point(hit_x, wall_y)
                
        
                field.strategy_image.draw_circle(
                    hit_point,
                    (255, 0, 0),  
                    15
                )
                
                # Линия от точки удара к воротам
                field.strategy_image.draw_line(
                    hit_point,
                    goal_point,
                    (255, 165, 0), 
                    2
                )

                field.strategy_image.draw_circle(
                    goal_point,
                    (0, 255, 0), 
                    8
                )
    else:
        
        for goal_point in goal_points:
            # Отражаем точку ворот относительно вертикальной стенки
            dist_to_wall = abs(goal_point.x - wall_x)
            reflected_point = aux.Point(
                wall_x + dist_to_wall * (1 if wall_x > 0 else -1),
                goal_point.y
            )
            
            # Рисуем прямую линию от мяча к отраженной точке
            field.strategy_image.draw_line(
                ball_pos,
                reflected_point,
                (255, 255, 0), 
                2
            )
            
           
            field.strategy_image.draw_circle(
                reflected_point,
                (255, 0, 255),  
                10
            )
            
            # место удара
            if abs(reflected_point.x - ball_pos.x) > 0.1:
                t = (wall_x - ball_pos.x) / (reflected_point.x - ball_pos.x)
                hit_y = ball_pos.y + t * (reflected_point.y - ball_pos.y)
                hit_point = aux.Point(wall_x, hit_y)
                
                # Точка удара на стенке
                field.strategy_image.draw_circle(
                    hit_point,
                    (255, 0, 0),
                    15
                )

                field.strategy_image.draw_line(
                    hit_point,
                    goal_point,
                    (255, 165, 0),  
                    2
                )

                field.strategy_image.draw_circle(
                    goal_point,
                    (0, 255, 0), 
                    8
                )
    

    if wall_is_horizontal:
        field.strategy_image.draw_line(
            aux.Point(-const.FIELD_DX - 100, wall_y),
            aux.Point(const.FIELD_DX + 100, wall_y),
            (255, 255, 255),  
            1
        )
    else:
        field.strategy_image.draw_line(
            aux.Point(wall_x, -const.FIELD_DY - 100),
            aux.Point(wall_x, const.FIELD_DY + 100),
            (255, 255, 255), 
            1
        )


def get_ricochet_hit_point(
    field: fld.Field,
    ball_pos: aux.Point,
    target_point: Optional[aux.Point] = None,
    wall_offset: float = 50)  -> Optional[aux.Point]:
    if target_point is None:
        target_point = field.enemy_goal.center
    

    right_wall = field.hull[0].x
    left_wall = field.hull[2].x
    top_wall = field.hull[0].y
    bottom_wall = field.hull[2].y

    dist_to_right = abs(ball_pos.x - right_wall)
    dist_to_left = abs(ball_pos.x - left_wall)
    dist_to_top = abs(ball_pos.y - top_wall)
    dist_to_bottom = abs(ball_pos.y - bottom_wall)
    
    min_dist = min(dist_to_right, dist_to_left, dist_to_top, dist_to_bottom)
    
    if min_dist == dist_to_right:

        wall_x = right_wall - wall_offset
  
        reflected_point = aux.Point(
            wall_x + (wall_x - target_point.x),
            target_point.y
        )
        if abs(reflected_point.x - ball_pos.x) > 0.1:
            t = (wall_x - ball_pos.x) / (reflected_point.x - ball_pos.x)
            hit_y = ball_pos.y + t * (reflected_point.y - ball_pos.y)
            return aux.Point(wall_x, hit_y)
            
    elif min_dist == dist_to_left:

        wall_x = left_wall + wall_offset
        reflected_point = aux.Point(
            wall_x - (target_point.x - wall_x),
            target_point.y
        )
        if abs(reflected_point.x - ball_pos.x) > 0.1:
            t = (wall_x - ball_pos.x) / (reflected_point.x - ball_pos.x)
            hit_y = ball_pos.y + t * (reflected_point.y - ball_pos.y)
            return aux.Point(wall_x, hit_y)
            
    elif min_dist == dist_to_top:

        wall_y = top_wall - wall_offset
        reflected_point = aux.Point(
            target_point.x,
            wall_y + (wall_y - target_point.y)
        )
        if abs(reflected_point.y - ball_pos.y) > 0.1:
            t = (wall_y - ball_pos.y) / (reflected_point.y - ball_pos.y)
            hit_x = ball_pos.x + t * (reflected_point.x - ball_pos.x)
            return aux.Point(hit_x, wall_y)
            
    else:
        wall_y = bottom_wall + wall_offset
        reflected_point = aux.Point(
            target_point.x,
            wall_y - (target_point.y - wall_y)
        )
        if abs(reflected_point.y - ball_pos.y) > 0.1:
            t = (wall_y - ball_pos.y) / (reflected_point.y - ball_pos.y)
            hit_x = ball_pos.x + t * (reflected_point.x - ball_pos.x)
            return aux.Point(hit_x, wall_y)
    
    return None


def get_ricochet_hit_point_center(
    field: fld.Field,
    ball_pos: aux.Point,
    wall_offset: float = 50
) -> Optional[aux.Point]:
   
    return get_ricochet_hit_point(field, ball_pos, field.enemy_goal.center, wall_offset)