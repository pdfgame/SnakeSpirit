import math
import random
import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import os
from PIL import Image, ImageDraw, ImageFont


from game.utils.improved_chinese_text import put_chinese_text_pil
from game.utils.language_manager import get_translation

class SnakeGame:
    def __init__(self, food_path, high_score=0):             # 构造方法
        self.points = []            
        self.lengths = []           
        self.currentLength = 0      
        self.base_allowed_length = 150    
        self.allowedLength = self.base_allowed_length    
        self.previousHead = None    # 初始化为None，根据实际屏幕尺寸设置
        self.smooth_head = None    
        self.smooth_factor = 0.4     
        self.max_speed = 35          
        self.snake_color = (0, 0, 255)  
        self.last_detected_head = None  
        self.game_over_reason = None  
        
        # 音频相关属性
        self.boom_sound = None
        self.fail_sound = None
        self.sound_played_this_frame = False  # 标志位，确保每个帧只播放一次音效
        
        self.gradient_colors_data = {
            "彩虹": [((255,0,0),(255,165,0)), ((255,165,0),(255,255,0)), ((255,255,0),(0,128,0)), ((0,128,0),(0,0,255)), ((0,0,255),(75,0,130)), ((75,0,130),(238,130,238))],
            "蓝绿渐变": ((0, 0, 255), (0, 255, 0)), 
            "火热渐变": ((255, 0, 0), (255, 255, 0)), 
            "宇宙渐变": ((128, 0, 128), (0, 0, 128))  
        }
        
        self.gradient_frame = 0  

        self.imgFood = cv2.imread(food_path, cv2.IMREAD_UNCHANGED)
        if self.imgFood is None:
            self.imgFood = np.zeros((50, 50, 4), dtype=np.uint8)
            cv2.circle(self.imgFood, (25, 25), 25, (0, 255, 255, 255), cv2.FILLED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        obstacle_path = os.path.join(base_path, "resources", "assets", "images", "stone.png")
        self.imgObstacle = cv2.imread(obstacle_path, cv2.IMREAD_UNCHANGED)
        if self.imgObstacle is None:
            self.imgObstacle = np.zeros((30, 30, 4), dtype=np.uint8)
            cv2.rectangle(self.imgObstacle, (0, 0), (30, 30), (128, 128, 128, 255), cv2.FILLED)

        if self.imgObstacle.shape[2] == 3:
            self.imgObstacle = cv2.cvtColor(self.imgObstacle, cv2.COLOR_RGB2RGBA)
        
        scale_factor = 0.15
        self.wObstacle = int(self.imgObstacle.shape[1] * scale_factor)
        self.hObstacle = int(self.imgObstacle.shape[0] * scale_factor)
        self.imgObstacle = cv2.resize(self.imgObstacle, (self.wObstacle, self.hObstacle))
        
        self.obstacles = []  
        self.num_obstacles = 5  
        self.last_obstacle_refresh = 0  
        self.obstacle_refresh_interval = 10  
        self.randomObstacleLocations()
        
        self.foodPoint = 0, 0
        self.randomFoodLocation()

        self.score = 0
        self.high_score = high_score  
        self.gameOver = False
        self.return_to_menu = False

    def randomFoodLocation(self):
        """随机生成食物位置，确保不会刷新到障碍物上"""
        screen_width, screen_height = 1280, 720  # 假设屏幕尺寸
        
        while True:
            # 生成随机位置
            x = random.randint(100, screen_width - 100)
            y = random.randint(100, screen_height - 100)
            food_pos = (x, y)
            
            # 检查是否与任何障碍物重叠
            overlap_with_obstacle = False
            for obstacle_pos in self.obstacles:
                obstacle_center_x, obstacle_center_y = obstacle_pos
                # 计算食物与障碍物中心的距离
                distance = math.hypot(x - obstacle_center_x, y - obstacle_center_y)
                # 确保食物与障碍物的距离大于两者半径之和
                min_distance = (self.wFood // 2) + (self.wObstacle // 2) + 20  # 20像素的安全距离
                if distance < min_distance:
                    overlap_with_obstacle = True
                    break
            
            if not overlap_with_obstacle:
                self.foodPoint = food_pos
                break
    
    def randomObstacleLocations(self):
        """随机生成障碍物位置，确保在屏幕边缘，远离中心区域和食物"""
        self.obstacles = []
        screen_width, screen_height = 1280, 720  
        center_x, center_y = screen_width // 2, screen_height // 2
        center_radius = 300  
        
        for _ in range(self.num_obstacles):

            while True:

                x = random.randint(50, screen_width - 50)
                y = random.randint(50, screen_height - 50)
                obstacle_pos = (x, y)
                

                distance_to_center = math.hypot(x - center_x, y - center_y)
                if distance_to_center > center_radius:

                    overlap = False
                    for existing_pos in self.obstacles:
                        if math.hypot(x - existing_pos[0], y - existing_pos[1]) < 100:  
                            overlap = True
                            break
                    
                    # 检查是否与食物重叠
                    if hasattr(self, 'foodPos') and self.foodPos is not None:
                        food_x, food_y = self.foodPos
                        distance_to_food = math.hypot(x - food_x, y - food_y)
                        min_distance = (self.wObstacle // 2) + (self.wFood // 2) + 20
                        if distance_to_food < min_distance:
                            overlap = True
                    
                    if not overlap:
                        break
            
            self.obstacles.append(obstacle_pos)

    def reset(self):
        self.points = []
        self.lengths = []
        self.currentLength = 0
        self.allowedLength = self.base_allowed_length
        # 初始化为None，在update方法中根据实际屏幕尺寸设置
        self.previousHead = None  # 屏幕中心
        self.smooth_head = None  # 屏幕中心
        self.score = 0
        self.gameOver = False
        self.return_to_menu = False
        self.game_over_reason = None  
        self.sound_played_this_frame = False  # 重置音效播放标志位
        self.randomFoodLocation()
        self.randomObstacleLocations()  
        self.last_obstacle_refresh = 0  

        self.last_detected_head = None

    def update(self, imgMain, currentHead, mouse_pos=None, mouse_clicked=False, high_score=0):
        # 重置音效播放标志位，确保每个帧只播放一次音效
        self.sound_played_this_frame = False

        if high_score > self.high_score:
            self.high_score = high_score
        
        if self.gameOver:

            try:
                from game.utils.improved_chinese_text import put_rainbow_text_pil, put_chinese_text_pil, put_chinese_text_with_background
                

                screen_height, screen_width, _ = imgMain.shape
                center_x = screen_width // 2
                center_y = screen_height // 2
                


                # 游戏结束文本 - 动态计算位置，实现居中
                if self.game_over_reason:
                    game_over_text = self.game_over_reason
                else:
                    game_over_text = get_translation('game_end')
                game_over_font_size = 80
                
                # 动态计算游戏结束文本位置
                game_over_size = put_chinese_text_pil(imgMain, game_over_text, (0, 0), game_over_font_size, (255, 0, 0))[1]
                game_over_width = game_over_size[0]
                game_over_height = game_over_size[1]
                game_over_x = center_x - game_over_width // 2
                game_over_y = center_y - 200
                imgMain, _ = put_chinese_text_pil(imgMain, game_over_text, (game_over_x, game_over_y), game_over_font_size, (255, 0, 0))
                
                # 分数文本 - 动态计算位置，实现居中
                score_text = get_translation('game_final_score').format(self.score)
                score_font_size = 60
                score_size = put_chinese_text_pil(imgMain, score_text, (0, 0), score_font_size, (50, 130, 246))[1]
                score_width = score_size[0]
                score_height = score_size[1]
                score_x = center_x - score_width // 2
                score_y = center_y - 100
                imgMain, _ = put_chinese_text_pil(imgMain, score_text, (score_x, score_y), score_font_size, (50, 130, 246))
                
                # 最高分文本 - 动态计算位置，实现居中
                high_score_text = get_translation('game_high_score').format(self.high_score)
                high_score_font_size = 40
                high_score_size = put_chinese_text_pil(imgMain, high_score_text, (0, 0), high_score_font_size, (50, 130, 246))[1]
                high_score_width = high_score_size[0]
                high_score_height = high_score_size[1]
                high_score_x = center_x - high_score_width // 2
                high_score_y = center_y - 30
                imgMain, _ = put_chinese_text_pil(imgMain, high_score_text, (high_score_x, high_score_y), high_score_font_size, (50, 130, 246))
                

                # 计算按钮宽度，确保能容纳中文文本
                button_height = 80
                button_padding = 60  # 增加按钮内边距，确保文本有足够空间
                button_spacing = 30  
                button_y = center_y + 50  # 向下调整按钮位置，确保居中显示
                button_font_size = 36
                
                # 获取文本
                restart_text = get_translation('game_restart')
                menu_text = get_translation('game_return_menu')
                
                # 使用与绘制相同的字体来测量文本宽度
                from PIL import Image, ImageDraw, ImageFont
                from game.utils.improved_chinese_text import _get_font
                temp_img = Image.new('RGB', (1, 1))
                temp_draw = ImageDraw.Draw(temp_img)
                
                # 使用实际绘制时使用的字体
                font = _get_font(button_font_size)
                
                # 测量文本宽度
                try:
                    restart_bbox = temp_draw.textbbox((0, 0), restart_text, font=font)
                    restart_text_width = restart_bbox[2] - restart_bbox[0]
                    menu_bbox = temp_draw.textbbox((0, 0), menu_text, font=font)
                    menu_text_width = menu_bbox[2] - menu_bbox[0]
                except AttributeError:
                    restart_text_width, _ = temp_draw.textsize(restart_text, font=font)
                    menu_text_width, _ = temp_draw.textsize(menu_text, font=font)
                
                # 计算按钮宽度，取文本宽度加内边距的最大值
                button_width = max(restart_text_width + button_padding, menu_text_width + button_padding, 220)  # 增加最小宽度
                
                total_buttons_width = button_width * 2 + button_spacing
                start_x = (screen_width - total_buttons_width) // 2
                
                restart_button_x = start_x
                restart_button_rect = (restart_button_x, button_y, button_width, button_height)
                
                menu_button_x = start_x + button_width + button_spacing
                menu_button_rect = (menu_button_x, button_y, button_width, button_height)
                

                if mouse_clicked and mouse_pos:

                    if restart_button_rect[0] <= mouse_pos[0] <= restart_button_rect[0] + restart_button_rect[2] and restart_button_rect[1] <= mouse_pos[1] <= restart_button_rect[1] + restart_button_rect[3]:
                        self.reset()

                        self.gameOver = False

                    elif menu_button_rect[0] <= mouse_pos[0] <= menu_button_rect[0] + menu_button_rect[2] and menu_button_rect[1] <= mouse_pos[1] <= menu_button_rect[1] + menu_button_rect[3]:
                        self.return_to_menu = True
                

                cv2.rectangle(imgMain, (restart_button_rect[0], restart_button_rect[1]), (restart_button_rect[0] + restart_button_rect[2], restart_button_rect[1] + restart_button_rect[3]), (0, 150, 0), cv2.FILLED)
                cv2.rectangle(imgMain, (restart_button_rect[0], restart_button_rect[1]), (restart_button_rect[0] + restart_button_rect[2], restart_button_rect[1] + restart_button_rect[3]), (255, 255, 255), 3)
                

                # 绘制重启按钮文本
                button_text = get_translation('game_restart')
                # 先测量文本尺寸
                temp_img = Image.new('RGB', (1, 1))
                temp_draw = ImageDraw.Draw(temp_img)
                font = _get_font(button_font_size)
                try:
                    restart_bbox = temp_draw.textbbox((0, 0), button_text, font=font)
                    restart_text_width = restart_bbox[2] - restart_bbox[0]
                    restart_text_height = restart_bbox[3] - restart_bbox[1]
                except AttributeError:
                    restart_text_width, restart_text_height = temp_draw.textsize(button_text, font=font)
                # 计算文本位置，确保完全居中
                restart_text_x = restart_button_x + (button_width - restart_text_width) // 2
                restart_text_y = button_y + 25  # 使用固定偏移量，根据按钮高度80px，25px的偏移量应该能让文字居中
                imgMain, _ = put_chinese_text_pil(imgMain, button_text, (restart_text_x, restart_text_y), button_font_size, (255, 255, 255))
                

                cv2.rectangle(imgMain, (menu_button_rect[0], menu_button_rect[1]), (menu_button_rect[0] + menu_button_rect[2], menu_button_rect[1] + menu_button_rect[3]), (50, 100, 200), cv2.FILLED)
                cv2.rectangle(imgMain, (menu_button_rect[0], menu_button_rect[1]), (menu_button_rect[0] + menu_button_rect[2], menu_button_rect[1] + menu_button_rect[3]), (255, 255, 255), 3)
                

                # 绘制返回菜单按钮文本
                menu_button_text = get_translation('game_return_menu')
                # 先测量文本尺寸
                try:
                    menu_bbox = temp_draw.textbbox((0, 0), menu_button_text, font=font)
                    menu_text_width = menu_bbox[2] - menu_bbox[0]
                    menu_text_height = menu_bbox[3] - menu_bbox[1]
                except AttributeError:
                    menu_text_width, menu_text_height = temp_draw.textsize(menu_button_text, font=font)
                # 计算文本位置，确保完全居中
                menu_text_x = menu_button_x + (button_width - menu_text_width) // 2
                menu_text_y = button_y + 25  # 使用固定偏移量，根据按钮高度80px，25px的偏移量应该能让文字居中
                imgMain, _ = put_chinese_text_pil(imgMain, menu_button_text, (menu_text_x, menu_text_y), button_font_size, (255, 255, 255))
            except Exception as e:
                print(f"绘制游戏结束画面错误: {e}")


                screen_height, screen_width, _ = imgMain.shape
                center_x = screen_width // 2
                center_y = screen_height // 2
                

                if self.game_over_reason:
                    game_over_text = self.game_over_reason
                else:
                    game_over_text = get_translation('game_end')
                
                # 动态计算游戏结束文本位置，确保居中
                font = cv2.FONT_HERSHEY_SIMPLEX
                game_over_size = cv2.getTextSize(game_over_text, font, 3, 3)[0]
                game_over_x = center_x - game_over_size[0] // 2
                cv2.putText(imgMain, game_over_text, (game_over_x, center_y - 150), font, 3, (255, 255, 255), 3)
                
                # 使用翻译函数获取分数文本
                score_text = get_translation('game_final_score').format(self.score)
                score_size = cv2.getTextSize(score_text, font, 2, 2)[0]
                score_x = center_x - score_size[0] // 2
                cv2.putText(imgMain, score_text, (score_x, center_y - 50), font, 2, (0, 255, 255), 2)
                
                # 使用翻译函数获取最高分文本
                high_score_text = get_translation('game_high_score').format(self.high_score)
                high_score_size = cv2.getTextSize(high_score_text, font, 1.5, 2)[0]
                high_score_x = center_x - high_score_size[0] // 2
                cv2.putText(imgMain, high_score_text, (high_score_x, center_y + 30), font, 1.5, (0, 255, 255), 2)
                
                # 动态计算按钮宽度，确保能容纳英文文本
                restart_text = get_translation('game_restart')
                restart_text_size = cv2.getTextSize(restart_text, font, 2, 2)[0]
                button_width = max(restart_text_size[0] + 40, 250)  # 最小宽度250
                button_height = 80
                
                # 居中显示按钮
                button_x = center_x - button_width // 2
                button_y = center_y + 120
                
                if mouse_clicked and mouse_pos:
                    if button_x <= mouse_pos[0] <= button_x + button_width and button_y <= mouse_pos[1] <= button_y + button_height:
                        print("备用方案：重新开始按钮被点击")
                        self.reset()
                        self.gameOver = False
                
                cv2.rectangle(imgMain, (button_x, button_y), (button_x + button_width, button_y + button_height), (0, 150, 0), cv2.FILLED)
                cv2.rectangle(imgMain, (button_x, button_y), (button_x + button_width, button_y + button_height), (255, 255, 255), 3)
                
                # 动态计算文本位置，实现居中对齐
                restart_text_x = button_x + (button_width - restart_text_size[0]) // 2
                restart_text_y = button_y + 50
                cv2.putText(imgMain, restart_text, (restart_text_x, restart_text_y), font, 2, (255, 255, 255), 2)
                
                # 添加返回主菜单按钮
                menu_text = get_translation('game_return_menu')
                menu_text_size = cv2.getTextSize(menu_text, font, 2, 2)[0]
                menu_button_width = max(menu_text_size[0] + 40, 250)
                menu_button_x = center_x - menu_button_width // 2
                menu_button_y = button_y + button_height + 20
                menu_button_rect = (menu_button_x, menu_button_y, menu_button_width, button_height)
                
                if mouse_clicked and mouse_pos:
                    if menu_button_rect[0] <= mouse_pos[0] <= menu_button_rect[0] + menu_button_rect[2] and menu_button_rect[1] <= mouse_pos[1] <= menu_button_rect[1] + menu_button_rect[3]:
                        self.return_to_menu = True
                
                cv2.rectangle(imgMain, menu_button_rect, (menu_button_x + menu_button_width, menu_button_y + button_height), (50, 100, 200), cv2.FILLED)
                cv2.rectangle(imgMain, menu_button_rect, (menu_button_x + menu_button_width, menu_button_y + button_height), (255, 255, 255), 3)
                
                # 动态计算返回主菜单文本位置
                menu_text_x = menu_button_x + (menu_button_width - menu_text_size[0]) // 2
                menu_text_y = menu_button_y + 50
                cv2.putText(imgMain, menu_text, (menu_text_x, menu_text_y), font, 2, (255, 255, 255), 2)
        else:

            smooth_cx = 0
            smooth_cy = 0
            

            current_time = cv2.getTickCount() / cv2.getTickFrequency()
            

            screen_height, screen_width, _ = imgMain.shape
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            if currentHead is not None:

                self.last_detected_head = currentHead
                

                raw_cx, raw_cy = currentHead
                

                if self.smooth_head is None:
                    self.smooth_head = (raw_cx, raw_cy)
                

                smooth_cx = self.smooth_head[0] * (1 - self.smooth_factor) + raw_cx * self.smooth_factor
                smooth_cy = self.smooth_head[1] * (1 - self.smooth_factor) + raw_cy * self.smooth_factor
                

                dx = smooth_cx - self.smooth_head[0]
                dy = smooth_cy - self.smooth_head[1]
                speed = math.hypot(dx, dy)
                if speed > self.max_speed:
                    ratio = self.max_speed / speed
                    dx *= ratio
                    dy *= ratio
                    smooth_cx = self.smooth_head[0] + dx
                    smooth_cy = self.smooth_head[1] + dy
                

                self.smooth_head = (smooth_cx, smooth_cy)
            elif self.last_detected_head is not None:


                if self.smooth_head is not None:

                    smooth_cx, smooth_cy = self.smooth_head
                else:

                    raw_cx, raw_cy = self.last_detected_head
                    smooth_cx, smooth_cy = raw_cx, raw_cy
                    self.smooth_head = (smooth_cx, smooth_cy)
            else:

                # 未检测到手部时，将蛇头位置设置在屏幕中心
                if self.smooth_head is None:
                    self.smooth_head = (center_x, center_y)
                smooth_cx, smooth_cy = self.smooth_head
                
                from game.utils.improved_chinese_text import put_chinese_text_pil
                imgMain, _ = put_chinese_text_pil(imgMain, get_translation('game_score').format(self.score), (50, 80), 40, (50, 130, 246))
                imgMain, _ = put_chinese_text_pil(imgMain, get_translation('game_high_score').format(self.high_score), (50, 130), 30, (50, 130, 246))
                imgMain, _ = put_chinese_text_pil(imgMain, get_translation('gesture_no_hand'), (screen_width//2 - 150, 50), 40, (255, 255, 0))
            

            try:
                cx, cy = int(smooth_cx), int(smooth_cy)
            except (ValueError, TypeError):

                cx, cy = 0, 0
                print("警告：smooth_cx或smooth_cy不是有效的数字，使用默认值(0, 0)")
            
            # 处理初始情况，self.previousHead为None时
            if self.previousHead is None:
                # 初始位置，不计算距离
                self.previousHead = (cx, cy)
                self.points.append([cx, cy])
            else:
                px, py = self.previousHead
                self.points.append([cx, cy])             
                distance = math.hypot(cx - px, cy - py)  
                self.lengths.append(distance)            
                self.currentLength += distance
                self.previousHead = (cx, cy)


            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break


            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1

                if self.score > self.high_score:
                    self.high_score = self.score
                print(f"得分: {self.score}, 最高分: {self.high_score}")
                
                # 播放吃到食物音效，确保每个帧只播放一次
                if self.boom_sound and not self.sound_played_this_frame:
                    try:
                        self.boom_sound.play()
                        self.sound_played_this_frame = True  # 标记为已播放
                    except Exception as e:
                        print(f"播放吃到食物音效失败: {e}")


            if current_time - self.last_obstacle_refresh >= self.obstacle_refresh_interval:
                self.randomObstacleLocations()
                self.last_obstacle_refresh = current_time
                print("障碍物已刷新")


            def get_current_snake_color(frame):
                if isinstance(self.snake_color, tuple):


                    rgb_color = self.snake_color
                    bgr_color = (rgb_color[2], rgb_color[1], rgb_color[0])
                    return bgr_color
                elif isinstance(self.snake_color, str) and self.snake_color in self.gradient_colors_data:

                    gradient_data = self.gradient_colors_data[self.snake_color]
                    if isinstance(gradient_data, list):

                        total_segments = len(gradient_data)
                        segment_index = frame % total_segments
                        segment = gradient_data[segment_index]
                        start_color, end_color = segment
                    else:

                        start_color, end_color = gradient_data
                    

                    gradient_speed = 3  
                    segment_length = 50  
                    t = (frame // gradient_speed) % segment_length / segment_length

                    rgb_color = tuple(int(start_c + (end_c - start_c) * t) for start_c, end_c in zip(start_color, end_color))

                    bgr_color = (rgb_color[2], rgb_color[1], rgb_color[0])
                    return bgr_color
                else:

                    return (255, 0, 0)
            

            self.gradient_frame += 1
            

            if self.points:
                current_color = get_current_snake_color(self.gradient_frame)
                for i, point in enumerate(self.points):
                     if i != 0:
                        self.points[i-1] = tuple(self.points[i-1])
                        self.points[i] = tuple(self.points[i])
                        cv2.line(imgMain, self.points[i - 1], self.points[i], current_color, 20)

                self.points[-1] = tuple(self.points[-1])

                head_color = current_color
                if isinstance(head_color, tuple) and len(head_color) >= 3:

                    head_color = tuple(max(0, c - 30) for c in head_color[:3])
                cv2.circle(imgMain, self.points[-1], 20, head_color, cv2.FILLED)


            imgMain = cvzone.overlayPNG(imgMain, self.imgFood, (rx - self.wFood // 2, ry - self.hFood // 2))
            

            for obstacle_pos in self.obstacles:
                ox, oy = obstacle_pos
                imgMain = cvzone.overlayPNG(imgMain, self.imgObstacle, (ox - self.wObstacle // 2, oy - self.hObstacle // 2))


            try:
                    from game.utils.improved_chinese_text import put_chinese_text_pil

                    imgMain, _ = put_chinese_text_pil(imgMain, get_translation('game_score').format(self.score), (50, 80), 40, (50, 130, 246))

                    imgMain, _ = put_chinese_text_pil(imgMain, get_translation('game_high_score').format(self.high_score), (50, 130), 30, (50, 130, 246))
            except Exception as e:
                print(f"绘制中文得分错误: {e}")

                cv2.rectangle(imgMain, (30, 60), (200, 100), (0, 0, 0), cv2.FILLED)

                cv2.putText(imgMain, f'Score: {self.score}', (40, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (50, 130, 246), 2)

                cv2.rectangle(imgMain, (30, 110), (220, 140), (0, 0, 0), cv2.FILLED)

                cv2.putText(imgMain, f'High Score: {self.high_score}', (40, 135), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 130, 246), 2)


            screen_height, screen_width, _ = imgMain.shape
            

            border_thickness = 4
            border_color = (255, 255, 0)  
            cv2.rectangle(imgMain, (0, 0), (screen_width, screen_height), border_color, border_thickness)
            

            if not self.gameOver:
                snake_radius = 20  
                
                # 初始位置特殊处理：如果是游戏开始后的第一个位置，跳过碰撞检测
                # 只有当蛇有足够长度且不是初始位置时才进行碰撞检测
                # 添加更多安全检查：确保屏幕尺寸有效，且蛇头位置有效
                # 游戏刚启动时，self.points列表长度会很快增加到2，所以需要额外的初始位置保护
                is_initial_position = (len(self.points) == 2 and self.currentLength <= self.base_allowed_length + 10)
                if len(self.points) > 2 and not is_initial_position and self.previousHead is not None and screen_width > 0 and screen_height > 0:  # 确保蛇有足够长度且不是初始位置
                    # 检查cx和cy是否有效（不为默认的0,0），防止未检测到手部时触发边缘检测
                    if (cx != 0 or cy != 0):
                        # 正常的边缘检测逻辑
                        if (cx - snake_radius < 0 or 
                            cx + snake_radius > screen_width or 
                            cy - snake_radius < 0 or 
                            cy + snake_radius > screen_height):
                            print("碰到屏幕边缘，游戏结束")
                            self.game_over_reason = get_translation('classic_edge_death')
                            self.gameOver = True  # 期末汇报（12月底）之前请勿乱用该项目
                            # 播放游戏结束音效
                            if self.fail_sound:
                                try:
                                    self.fail_sound.play()
                                except Exception as e:
                                    print(f"播放游戏结束音效失败: {e}")
                    
                    for obstacle_pos in self.obstacles:
                        ox, oy = obstacle_pos

                        if math.hypot(cx - ox, cy - oy) < (snake_radius + self.wObstacle // 2):
                            print("碰到障碍物，游戏结束")
                            self.game_over_reason = get_translation('classic_obstacle_death')
                            self.gameOver = True
                            # 播放游戏结束音效
                            if self.fail_sound:
                                try:
                                    self.fail_sound.play()
                                except Exception as e:
                                    print(f"播放游戏结束音效失败: {e}")
                            break


        return imgMain

def main():

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)        
    cap.set(4, 720)         


    detector = HandDetector(detectionCon=0.8, maxHands=1)


    food_path = "donut.png"
    if not os.path.exists(food_path):

        food_path = os.path.join("src", "donut.png")
    if not os.path.exists(food_path):

        food_path = os.path.join("..", "donut.png")
    if not os.path.exists(food_path):
        print(f"无法找到食物图片: {food_path}")
        return


    try:
        import json
        import os

        high_score_file = os.path.join("src", "data", "game_data.json")
        if os.path.exists(high_score_file):
            with open(high_score_file, "r") as f:
                data = json.load(f)
                high_score = data.get("high_score_gesture", 0)
        else:
            high_score = 0
    except Exception as e:
        print(f"加载最高分错误: {e}")
        high_score = 0


    game = SnakeGame(food_path, high_score)

    while True:
        success, img = cap.read()
        if not success:
            print("无法读取摄像头画面")
            break
        

        img = cv2.flip(img, 1)
        

        hands, img = detector.findHands(img, flipType=False)
        
        if hands:
            hand = hands[0]
            lmList = hand['lmList']

            pointIndex = lmList[8][0:2]
            pointIndex = tuple(pointIndex)
            

            index_mcp = lmList[5]    
            dist = math.hypot(pointIndex[0]-index_mcp[0], pointIndex[1]-index_mcp[1])
            

            if dist > 50:

                img = game.update(img, pointIndex, high_score=game.high_score)
            else:

                img = game.update(img, None, high_score=game.high_score)
        else:

            cvzone.putTextRect(img, "未检测到手部", [400, 350], scale=3, thickness=5, offset=10)

            img = game.update(img, None, high_score=game.high_score)
        

        cv2.imshow("手势控制贪吃蛇游戏", img)
        

        key = cv2.waitKey(1)
        if key == 27:  
            break
    

    try:
        import json
        import os

        high_score_file = os.path.join("src", "data", "game_data.json")

        if os.path.exists(high_score_file):
            with open(high_score_file, "r") as f:
                data = json.load(f)
        else:
            data = {}

        if game.high_score > data.get("high_score_gesture", 0):
            data["high_score_gesture"] = game.high_score

        with open(high_score_file, "w") as f:
            json.dump(data, f)
        print(f"最高分已保存: {game.high_score}")
    except Exception as e:
        print(f"保存最高分错误: {e}")
    

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()