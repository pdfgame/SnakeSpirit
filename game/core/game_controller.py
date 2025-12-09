import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['GLOG_minloglevel'] = '2'

import cv2
import numpy as np
import pygame
import pygame_gui
import math
from pygame_gui.elements import UIButton

print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")


class SimpleHandDetector:
    """简单的手势检测器，使用肤色检测和轮廓分析，优化对半只手的检测"""
    
    def __init__(self, detectionCon=0.5, maxHands=1):
        self.detectionCon = detectionCon
        self.maxHands = maxHands
        # 添加手部跟踪历史，用于预测手部位置
        self.hand_history = []
        self.max_history = 5  # 保存最近5帧的手部位置
        
    def findHands(self, img, draw=True, flipType=False):
        """检测手部，返回手部位置列表，模拟cvzone.HandDetector的接口"""
        try:

            if img is None or len(img.shape) != 3 or img.shape[2] < 3:
                return [], img
            

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            



            lower_skin1 = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin1 = np.array([20, 255, 255], dtype=np.uint8)

            lower_skin2 = np.array([170, 20, 70], dtype=np.uint8)
            upper_skin2 = np.array([180, 255, 255], dtype=np.uint8)
            

            mask1 = cv2.inRange(hsv, lower_skin1, upper_skin1)
            mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
            mask = cv2.bitwise_or(mask1, mask2)
            


            kernel_small = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_small, iterations=1)

            kernel_large = np.ones((7, 7), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_large, iterations=2)

            mask = cv2.dilate(mask, kernel_small, iterations=1)
            

            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            hands = []
            if len(contours) > 0:

                sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
                

                for contour in sorted_contours[:self.maxHands]:
                    try:

                        area = cv2.contourArea(contour)

                        img_height, img_width, _ = img.shape
                        min_area = max(300, img_width * img_height * 0.005)  
                        if area < min_area:  
                            continue
                        

                        x, y, w, h = cv2.boundingRect(contour)
                        

                        aspect_ratio = float(w) / h
                        if aspect_ratio < 0.3 or aspect_ratio > 1.5:  
                            continue
                        

                        hull = cv2.convexHull(contour)
                        

                        hull_area = cv2.contourArea(hull)
                        solidity = float(area) / hull_area
                        if solidity < 0.5:  
                            continue
                        

                        if draw:
                            try:

                                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                                cv2.drawContours(img, [hull], 0, (255, 0, 0), 2)
                                

                                center_x, center_y = x + w//2, y + h//2
                                

                                key_points = []
                                




                                min_y = min(contour[:, 0, 1])
                                min_y_idx = np.where(contour[:, 0, 1] == min_y)[0][0]
                                index_x, index_y = contour[min_y_idx, 0]
                                

                                key_points.append((x + w//4, y))  
                                key_points.append((index_x, index_y))  
                                key_points.append((x + 3*w//4, y))  
                                key_points.append((x + w, y + h//4))  
                                key_points.append((x + w, y + h//2))  
                                

                                key_points.append((x + w//6, y + h//4))  
                                key_points.append((x + w//3, y + h//4))  
                                key_points.append((x + w//2, y + h//4))  
                                key_points.append((x + 2*w//3, y + h//4))  
                                key_points.append((x + 5*w//6, y + h//4))  
                                

                                key_points.append((x + w//2, y + h//2))  
                                key_points.append((x + w//3, y + h//2))  
                                key_points.append((x + 2*w//3, y + h//2))  
                                key_points.append((x + w//2, y + 3*h//4))  
                                

                                for i, (kx, ky) in enumerate(key_points):
                                    color = (0, 0, 255) if i == 1 else (0, 255, 0)  
                                    cv2.circle(img, (kx, ky), 5, color, cv2.FILLED)
                                


                                cv2.line(img, key_points[0], key_points[5], (0, 255, 0), 2)
                                cv2.line(img, key_points[5], key_points[10], (0, 255, 0), 2)
                                

                                cv2.line(img, key_points[1], key_points[6], (0, 255, 0), 2)
                                cv2.line(img, key_points[6], key_points[10], (0, 255, 0), 2)
                                

                                cv2.line(img, key_points[2], key_points[7], (0, 255, 0), 2)
                                cv2.line(img, key_points[7], key_points[10], (0, 255, 0), 2)
                                

                                cv2.line(img, key_points[3], key_points[8], (0, 255, 0), 2)
                                cv2.line(img, key_points[8], key_points[10], (0, 255, 0), 2)
                                

                                cv2.line(img, key_points[4], key_points[9], (0, 255, 0), 2)
                                cv2.line(img, key_points[9], key_points[10], (0, 255, 0), 2)
                                

                                cv2.line(img, key_points[10], key_points[13], (0, 255, 0), 2)
                                cv2.line(img, key_points[11], key_points[13], (0, 255, 0), 2)
                                cv2.line(img, key_points[12], key_points[13], (0, 255, 0), 2)
                            except Exception as draw_e:

                                pass
                        

                        lmList = []
                        


                        min_y = min(contour[:, 0, 1])
                        min_y_idx = np.where(contour[:, 0, 1] == min_y)[0][0]
                        index_x, index_y = contour[min_y_idx, 0]
                        

                        for i in range(21):

                            if i == 8:

                                lmList.append((index_x, index_y, 0))
                            else:

                                sim_x = x + (i % 5) * (w // 4)
                                sim_y = y + (i // 5) * (h // 4)

                                sim_x = max(x, min(x + w, sim_x))
                                sim_y = max(y, min(y + h, sim_y))
                                sim_z = 0
                                lmList.append((sim_x, sim_y, sim_z))
                        

                        hand_info = {
                            'lmList': lmList,
                            'bbox': (x, y, w, h),
                            'type': 'Right'
                        }
                        hands.append(hand_info)
                        

                        self.hand_history.append((x, y, w, h))

                        if len(self.hand_history) > self.max_history:
                            self.hand_history.pop(0)
                        

                        break
                    except Exception as contour_e:

                        print(f"处理轮廓时出错: {contour_e}")
                        continue
            

            if not hands and len(self.hand_history) > 2:
                try:

                    recent_hands = self.hand_history[-3:]

                    avg_x = int(sum(h[0] for h in recent_hands) / len(recent_hands))
                    avg_y = int(sum(h[1] for h in recent_hands) / len(recent_hands))
                    avg_w = int(sum(h[2] for h in recent_hands) / len(recent_hands))
                    avg_h = int(sum(h[3] for h in recent_hands) / len(recent_hands))
                    

                    lmList = []
                    index_x, index_y = avg_x + avg_w//2, avg_y  
                    
                    for i in range(21):
                        if i == 8:
                            lmList.append((index_x, index_y, 0))
                        else:
                            sim_x = avg_x + (i % 5) * (avg_w // 4)
                            sim_y = avg_y + (i // 5) * (avg_h // 4)
                            sim_x = max(avg_x, min(avg_x + avg_w, sim_x))
                            sim_y = max(avg_y, min(avg_y + avg_h, sim_y))
                            sim_z = 0
                            lmList.append((sim_x, sim_y, sim_z))
                    

                    predicted_hand = {
                        'lmList': lmList,
                        'bbox': (avg_x, avg_y, avg_w, avg_h),
                        'type': 'Right'
                    }
                    hands.append(predicted_hand)
                except Exception as predict_e:
                    print(f"预测手部位置时出错: {predict_e}")
            
            return hands, img
        except Exception as e:
            print(f"简单手势检测错误: {e}")
        
        return [], img

hand_tracking_available = True
print("使用cvzone手势检测器，依赖mediapipe模型")
from PIL import Image


from game.core.snake_game import SnakeGame as CoreSnakeGame
from game.modes.classic.classic_snake_game import ClassicSnakeGame
from game.modes.gesture.simple_gesture_snake import SnakeGame as GestureSnakeGame
from game.core.game_ui import draw_mode_selection_screen, draw_startup_animation, draw_and_update_effects, global_particles, draw_settings_screen, gradient_colors_data
from game.utils.game_data import load_game_data, save_game_data
from game.utils.chinese_text import put_chinese_text, put_rainbow_text
from game.utils.improved_chinese_text import put_chinese_text_pil, put_rainbow_text_pil, put_chinese_text_with_background


try:
    from cvzone.HandTrackingModule import HandDetector
    print("成功导入cvzone.HandDetector")
except ImportError as e:
    print(f"导入cvzone.HandDetector失败: {e}")
    hand_tracking_available = False

    print("使用SimpleHandDetector作为备用，优化对半只手的检测")

class GameController:
    def __init__(self):
        pygame.init()
        
        # 初始化音频系统
        pygame.mixer.init()
        
        # 加载音频文件
        self.bgm_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "music", "BGM.mp3")
        self.boom_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "music", "boom.mp3")
        self.fail_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "music", "FAIELD.mp3")
        
        # 初始化音频变量
        self.bgm_playing = False
        self.boom_sound = None
        self.fail_sound = None
        
        try:
            # 尝试加载音效
            self.boom_sound = pygame.mixer.Sound(self.boom_path)
            self.fail_sound = pygame.mixer.Sound(self.fail_path)
        except Exception as e:
            print(f"加载音效失败: {e}")
        
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("双模式贪吃蛇游戏")
        self.clock = pygame.time.Clock()
        
        pygame.display.flip()
        
        pygame.font.init()
        print("可用的pygame字体:", pygame.font.get_fonts()[:10])  
        
        from utils.improved_chinese_text import get_font_path
        font_path = get_font_path()
        if font_path:
            try:
                self.font_large = pygame.font.Font(font_path, 80)
                self.font_small = pygame.font.Font(font_path, 40)
            except Exception:
                self.font_large, self.font_small = pygame.font.Font(None, 80), pygame.font.Font(None, 40)
        else:
            self.font_large, self.font_small = pygame.font.Font(None, 80), pygame.font.Font(None, 40)
        

        theme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'themes', 'button_theme.json')
        self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height), theme_path)
        

        self.configure_ui_font()
        
        self.game_mode = 'startup'
        
        game_data = load_game_data() 
        self.high_score_classic = game_data['high_score_classic']
        self.high_score_gesture = game_data['high_score_gesture']
        self.snake_color = game_data['snake_color'] 
        self.hide_camera_feed = game_data['hide_camera_feed'] 
        
        self.animation_frame_count = 0

        self.capture = None
        

        self.hovered_button = None
        self.clicked_button = None
        self.prev_game_mode = None
        

        self.hand_tracking_enabled = False
        self.hand_detector = None

        self.is_loading = False
        self.loading_progress = 0
        
        if hand_tracking_available:
            try:
                self.hand_detector = HandDetector(detectionCon=0.1, maxHands=1)
                self.hand_tracking_enabled = True
                print("手部检测初始化成功（使用cvzone.HandDetector，优化对半只手的检测）")
            except Exception as e:
                print(f"初始化cvzone手部检测失败: {e}")
                self._init_backup_hand_detector(detection_conf=0.4)
        else:
            self._init_backup_hand_detector(detection_conf=0.5)
        


        food_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "assets", "images", "Donut.png")
        


        self.hand_tracking_game = GestureSnakeGame(food_path=food_path, high_score=self.high_score_gesture)
        self.hand_tracking_game.snake_color = self.snake_color  
        self.hand_tracking_game.boom_sound = self.boom_sound
        self.hand_tracking_game.fail_sound = self.fail_sound
        
        self.classic_game = ClassicSnakeGame(snake_color=self.snake_color, width=self.screen_width, height=self.screen_height, gradient_colors_data=gradient_colors_data) 
        self.classic_game.high_score = self.high_score_classic
        self.classic_game.boom_sound = self.boom_sound
        self.classic_game.fail_sound = self.fail_sound
        
        self.create_ui_elements()
        
    def play_bgm(self):
        """播放背景音乐"""
        if not self.bgm_playing:
            try:
                pygame.mixer.music.load(self.bgm_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)  # 循环播放
                self.bgm_playing = True
            except Exception as e:
                print(f"播放背景音乐失败: {e}")
    
    def stop_bgm(self):
        """停止背景音乐"""
        if self.bgm_playing:
            pygame.mixer.music.stop()
            self.bgm_playing = False
    
    def play_boom(self):
        """播放吃到食物音效"""
        if self.boom_sound:
            try:
                self.boom_sound.play()
            except Exception as e:
                print(f"播放吃到食物音效失败: {e}")
    
    def play_fail(self):
        """播放游戏失败音效"""
        if self.fail_sound:
            try:
                self.fail_sound.play()
            except Exception as e:
                print(f"播放游戏失败音效失败: {e}")
    
    def configure_ui_font(self):
        """配置pygame_gui使用中文字体"""
        from utils.improved_chinese_text import get_font_path
        font_path = get_font_path()
        if font_path:
            try:
                # 为pygame设置默认中文字体
                default_font = pygame.font.Font(font_path, 20)
                # 不打印字体设置信息
                # print(f"已设置pygame默认中文字体: {font_path}")
                
                # 通过ui_manager访问字体字典
                # 直接为pygame_gui的字体字典添加中文字体路径
                from pygame_gui.core.ui_font_dictionary import UIFontDictionary
                
                # 创建字体字典实例（如果需要）
                font_dict = UIFontDictionary()
                
                # 为simhei.ttf添加字体路径
                font_dict.add_font_path('simhei.ttf', font_path)
                # 不打印字体字典添加信息
                # print(f"已将simhei.ttf添加到pygame_gui字体字典")
                
                # 预加载字体
                font_dict.preload_font({'name': 'simhei.ttf', 'size': 20, 'style': 'regular'})
                # 不打印字体预加载信息
                # print("已预加载simhei.ttf字体")
                
            except Exception as e:
                # 不打印错误信息
                # print(f"设置pygame_gui字体失败: {e}")
                pass

    def create_ui_elements(self):
        # 主菜单按钮 - 左右分布，按钮大小与绘制的一致
        button_width = 600  # 与绘制的按钮大小一致
        button_height = 120  # 与绘制的按钮大小一致
        button_spacing = 40
        start_y = self.screen_height // 2 - 60  # 调整垂直位置，与绘制的按钮一致
        
        # 经典模式按钮 - 左侧
        self.classic_mode_button = UIButton(
            relative_rect=pygame.Rect(
                (self.screen_width // 2 - button_width - button_spacing // 2, start_y),
                (button_width, button_height)
            ),
            text='经典模式',
            manager=self.ui_manager
        )
        
        # 手势追踪模式按钮 - 右侧
        self.hand_tracking_mode_button = UIButton(
            relative_rect=pygame.Rect(
                (self.screen_width // 2 + button_spacing // 2, start_y),
                (button_width, button_height)
            ),
            text='手势追踪模式',
            manager=self.ui_manager
        )
        
        # 去掉设置按钮，改为按ESC键调出设置菜单
        self.settings_button = None
        
        # 设置界面按钮和颜色选择器将在需要时创建
        self.back_button = None
        self.color_buttons = []
        
        # 手势控制模式设置相关按钮
        self.hand_tracking_settings_button = None  # 在ESC设置菜单中显示
        self.camera_toggle_button = None
        self.hand_tracking_settings_back_button = None
        
        # 按钮矩形对象，用于点击检测
        self.camera_toggle_button_rect = pygame.Rect(0, 0, 300, 70)  # 初始化一个默认矩形
        self.hand_tracking_back_button_rect = pygame.Rect(0, 0, 300, 70)  # 初始化一个默认矩形
        
        # 隐藏所有按钮直到需要它们
        self.hide_all_buttons()    # 期末汇报（12月底）之前请勿乱用该项目

    def _init_backup_hand_detector(self, detection_conf=0.5):
        """兜底初始化，优先尝试独立的MediaPipe检测器，最后再用SimpleHandDetector"""
        try:
            from game.core.tflite_hand_detector import TFLiteHandDetector
            detector = TFLiteHandDetector(max_hands=1, min_detection_confidence=detection_conf)
            if detector.is_loaded:
                self.hand_detector = detector
                self.hand_tracking_enabled = True
                print("MediaPipe手势检测器初始化成功（独立模式）")
                return
            raise RuntimeError("MediaPipe检测器未就绪")
        except Exception as e:
            print(f"独立MediaPipe手势检测器初始化失败: {e}")

        try:
            print("使用SimpleHandDetector作为备用，优化对半只手的检测")
            self.hand_detector = SimpleHandDetector(detectionCon=detection_conf, maxHands=1)
            self.hand_tracking_enabled = True
        except Exception as e:
            print(f"初始化SimpleHandDetector失败: {e}")
            self.hand_tracking_enabled = False
            self.hand_detector = None

    def hide_all_buttons(self):
        # 隐藏所有按钮，无论它们是否存在
        try:
            self.classic_mode_button.hide()
        except:
            pass
        try:
            self.hand_tracking_mode_button.hide()
        except:
            pass
        try:
            self.settings_button.hide()
        except:
            pass
        try:
            self.back_button.hide()
        except:
            pass
        try:
            self.hand_tracking_settings_button.hide()
        except:
            pass
        try:
            self.hand_tracking_settings_back_button.hide()
        except:
            pass
        try:
            self.camera_toggle_button.hide()
        except:
            pass
        for button in self.color_buttons:
            try:
                button.hide()
            except:
                pass

    def show_menu_buttons(self):
        """显示模式选择按钮 - 左右分布"""
        self.hide_all_buttons()

        self.classic_mode_button.show()
        self.hand_tracking_mode_button.show()


    def show_settings_ui(self):
        """显示设置界面，直接绘制颜色块，不使用pygame_gui按钮"""
        self.hide_all_buttons()
        # 只需要切换到设置模式，颜色块将在update_and_draw中直接绘制
        self.game_mode = 'classic_settings'

    def create_color_buttons(self):
        """创建美观的颜色选择按钮"""

        self.color_buttons = []
        

        solid_colors = [
            (255, 182, 193), (144, 238, 144), (173, 216, 230), (255, 255, 0),  
            (255, 165, 0), (128, 0, 128), (255, 255, 255), (128, 128, 128),  
            (255, 0, 0), (0, 255, 255), (255, 0, 255), (50, 205, 50),      
            (0, 128, 128), (0, 0, 128), (255, 215, 0), (192, 192, 192)      
        ]
        

        solid_color_names = [
            "粉色", "浅绿", "浅蓝", "黄色",
            "橙色", "紫色", "白色", "灰色",
            "红色", "青色", "品红", "翠绿",
            "青色", "海军蓝", "金色", "银色"
        ]
        

        button_size = 60
        spacing = 15
        cols = 8
        start_x = self.screen_width // 2 - ((cols * button_size + (cols - 1) * spacing) // 2)
        start_y = 180
        
        for i, color in enumerate(solid_colors):
            row = i // cols
            col = i % cols
            x = start_x + col * (button_size + spacing)
            y = start_y + row * (button_size + spacing + 25)  
            

            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x, y), (button_size, button_size)),
                text='',
                manager=self.ui_manager
            )
            

            button.colour = color
            button.name = solid_color_names[i]
            self.color_buttons.append(button)
        

        gradient_names = ["彩虹", "蓝绿渐变", "火热渐变", "宇宙渐变"]
        
        gradient_start_y = start_y + (len(solid_colors) // cols + 1) * (button_size + spacing + 25) + 40
        
        for i, grad_name in enumerate(gradient_names):
            col = i % 4
            row = i // 4
            x = start_x + col * (button_size + spacing)
            y = gradient_start_y + row * (button_size + spacing + 25)
            

            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x, y), (button_size, button_size)),
                text=grad_name,
                manager=self.ui_manager
            )
            

            button.grad_name = grad_name
            self.color_buttons.append(button)

    def run(self):
        running = True
        while running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.game_mode not in ['settings_menu', 'hand_tracking_settings', 'classic_settings']:
                        pygame.display.toggle_fullscreen()
                

                if self.game_mode in ['selection', 'classic_settings', 'hand_tracking_settings', 'settings_menu']:
                    self.ui_manager.process_events(event)
                    self.handle_input(event)
                elif self.game_mode in ['classic', 'hand_tracking', 'pause_menu']:
                    self.handle_input(event)
            

            if self.game_mode in ['selection', 'classic_settings', 'hand_tracking_settings', 'settings_menu']:
                self.ui_manager.update(time_delta)
            
            self.update_and_draw()
            pygame.display.flip()
        self.cleanup()

    def handle_ui_events(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.classic_mode_button:
                self.game_mode = 'classic'


                self.classic_game.reset()
                global_particles.clear()
                self.hide_all_buttons()
            elif event.ui_element == self.hand_tracking_mode_button:

                self.is_loading = True
                self.loading_progress = 0
                self.game_mode = 'loading'
                global_particles.clear()
                self.hide_all_buttons()
            elif event.ui_element == self.settings_button:
                self.game_mode = 'classic_settings'
                self.show_settings_ui()
            elif event.ui_element == self.back_button:
                self.game_mode = 'selection'
                self.show_menu_buttons()
            else:

                for button in self.color_buttons:
                    if event.ui_element == button:
                        if hasattr(button, 'colour'):

                            self.snake_color = button.colour
                            save_game_data({'high_score_classic': self.high_score_classic, 'high_score_gesture': self.high_score_gesture, 'snake_color': self.snake_color})
                        elif hasattr(button, 'grad_name'):

                            self.snake_color = button.grad_name
                            save_game_data({'high_score_classic': self.high_score_classic, 'high_score_gesture': self.high_score_gesture, 'snake_color': self.snake_color})

                        self.classic_game.snake_color = self.snake_color
                        self.hand_tracking_game.snake_color = self.snake_color
                        self.game_mode = 'selection'
                        self.show_menu_buttons()
                        break

    def handle_input(self, event):

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.game_mode in ['classic', 'hand_tracking']:

                self.prev_game_mode = self.game_mode
                self.game_mode = 'pause_menu'
            elif self.game_mode == 'selection':

                self.prev_game_mode = self.game_mode
                self.game_mode = 'settings_menu'
            elif self.game_mode == 'pause_menu':

                self.game_mode = self.prev_game_mode
            elif self.game_mode == 'settings_menu':

                self.game_mode = self.prev_game_mode
            elif self.game_mode == 'hand_tracking_settings':

                self.game_mode = 'settings_menu'
            elif self.game_mode == 'classic_settings':

                self.game_mode = 'selection'


        if not hasattr(self, 'hovered_button'):
            self.hovered_button = None
        if not hasattr(self, 'clicked_button'):
            self.clicked_button = None

        if not hasattr(self, 'prev_game_mode'):
            self.prev_game_mode = None
            

        if self.game_mode == 'selection':

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                mouse_x, mouse_y = event.pos
                button = self.check_button_click(mouse_x, mouse_y)
                if button:
                    self.handle_button_click(button)
            elif event.type == pygame.MOUSEMOTION:

                mouse_x, mouse_y = event.pos
                self.hovered_button = self.check_button_hover(mouse_x, mouse_y)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.clicked_button = None
        elif self.game_mode == 'classic_settings':

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                mouse_pos = event.pos

                img_temp = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
                img_temp, color_blocks = draw_settings_screen(img_temp, self.snake_color, mouse_pos)

                for block in color_blocks:
                    try:
                        x1, y1, x2, y2, color_value, block_type, name = block
                        if x1 <= mouse_pos[0] <= x2 and y1 <= mouse_pos[1] <= y2:
                            if block_type == "button":
                                if color_value == "confirm":


                                    if self.prev_game_mode == 'settings_menu':
                                        self.game_mode = 'settings_menu'
                                    else:
                                        self.game_mode = 'selection'
                                        self.show_menu_buttons()
                                elif color_value == "menu":

                                    self.game_mode = 'selection'
                                    self.show_menu_buttons()
                            elif block_type == "solid":

                                self.snake_color = color_value

                                save_game_data({'high_score_classic': self.high_score_classic, 'high_score_gesture': self.high_score_gesture, 'snake_color': self.snake_color})

                                self.classic_game.snake_color = self.snake_color
                                self.hand_tracking_game.snake_color = self.snake_color
                            elif block_type == "gradient":

                                self.snake_color = color_value

                                save_game_data({'high_score_classic': self.high_score_classic, 'high_score_gesture': self.high_score_gesture, 'snake_color': self.snake_color})

                                self.classic_game.snake_color = self.snake_color
                                self.hand_tracking_game.snake_color = self.snake_color
                    except Exception as e_block:
                        print(f"处理颜色块时出错: {e_block}")
        elif self.game_mode == 'classic':
            if self.classic_game:
                self.classic_game.handle_input(event)
                self.handle_classic_game_input(event)
        elif self.game_mode == 'hand_tracking':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    if self.hand_tracking_game.score > self.high_score_gesture:
                        self.high_score_gesture = self.hand_tracking_game.score
                    save_game_data({'high_score_classic': self.high_score_classic, 'high_score_gesture': self.high_score_gesture, 'snake_color': self.snake_color}) 
                    self.game_mode = 'selection'
                    if self.capture is not None:
                        self.capture.release()
                        self.capture = None
                    self.show_menu_buttons()
                    global_particles.clear()
        elif self.game_mode == 'hand_tracking_settings':

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                mouse_x, mouse_y = event.pos
                

                button_width = 300
                button_height = 70
                button_spacing = 50
                title_button_spacing = 60
                

                title_height = 80  
                num_buttons = 2
                total_menu_height = title_height + title_button_spacing + (num_buttons * button_height) + ((num_buttons - 1) * button_spacing)
                menu_start_y = (self.screen_height - total_menu_height) // 2
                button_y_start = menu_start_y + title_height + title_button_spacing
                

                camera_toggle_button_rect = pygame.Rect(
                    self.screen_width//2 - button_width//2,
                    button_y_start,
                    button_width,
                    button_height
                )
                

                back_button_rect = pygame.Rect(
                    self.screen_width//2 - button_width//2,
                    button_y_start + button_height + button_spacing,
                    button_width,
                    button_height
                )
                

                if camera_toggle_button_rect.collidepoint(mouse_x, mouse_y):

                    self.hide_camera_feed = not self.hide_camera_feed
                    print(f"摄像头画面状态切换为: {'显示' if not self.hide_camera_feed else '隐藏'}")

                    save_game_data({'high_score_classic': self.high_score_classic, 'high_score_gesture': self.high_score_gesture, 'snake_color': self.snake_color, 'hide_camera_feed': self.hide_camera_feed})
                    return

                elif back_button_rect.collidepoint(mouse_x, mouse_y):

                    self.game_mode = 'settings_menu'
                    return
    
    def check_button_click(self, mouse_x, mouse_y):
        """检查鼠标点击了哪个按钮"""
        # 只有在selection模式下才检查按钮点击
        if self.game_mode != 'selection':
            return None
        
        # 使用实际按钮的rect进行点击检测
        # 经典模式按钮
        if self.classic_mode_button.rect.collidepoint(mouse_x, mouse_y):
            return "classic"
        # 手势追踪模式按钮
        elif self.hand_tracking_mode_button.rect.collidepoint(mouse_x, mouse_y):
            return "hand_tracking"
        return None
        
    def check_button_hover(self, mouse_x, mouse_y):
        """检查鼠标悬停在哪个按钮上"""

        if self.game_mode != 'selection':
            return None
        


        if self.classic_mode_button.rect.collidepoint(mouse_x, mouse_y):
            return "classic"

        elif self.hand_tracking_mode_button.rect.collidepoint(mouse_x, mouse_y):
            return "hand_tracking"
        return None
        
    def handle_button_click(self, button_id):
        """处理按钮点击事件"""
        # 只在selection模式下处理按钮点击
        if self.game_mode != 'selection':
            return
            
        if button_id == "classic":
            self.game_mode = 'classic'
            # 只在首次初始化时设置颜色，后续重新开始时保留上一局的颜色
            # 这样上一局的变色效果会延续到下一局
            self.classic_game.reset()
            global_particles.clear()
            self.hide_all_buttons()
        elif button_id == "hand_tracking":
            # 显示加载屏幕，避免主线程阻塞
            self.is_loading = True
            self.loading_progress = 0
            self.game_mode = 'loading'
            global_particles.clear()
            self.hide_all_buttons()
        elif button_id == "settings":
            self.game_mode = 'classic_settings'
            self.show_settings_ui()
    
    def handle_classic_game_input(self, event):
        """处理经典游戏模式的输入"""

        pass

    def update_and_draw(self):
        # 根据游戏模式和游戏状态控制背景音乐
        if self.game_mode == 'classic' and not self.classic_game.game_over:
            self.play_bgm()
        elif self.game_mode == 'hand_tracking' and not self.hand_tracking_game.gameOver:
            self.play_bgm()
        else:
            self.stop_bgm()
        
        if self.game_mode == 'loading':

            img = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)

            from game.core.game_ui import draw_starry_background
            img = draw_starry_background(img)
            

            if self.loading_progress < 20:

                if self.capture is not None:
                    self.capture.release()
                    self.capture = None
                self.loading_progress = 20
            elif self.loading_progress < 50:

                self.initialize_camera()
                self.loading_progress = 50
            elif self.loading_progress < 80:


                if self.hand_detector is None:
                    try:
                        from game.core.tflite_hand_detector import TFLiteHandDetector
                        self.hand_detector = TFLiteHandDetector()
                        print("MediaPipe手部检测器初始化成功")
                    except Exception as e:
                        print(f"MediaPipe手部检测器初始化失败，回退到cvzone.HandDetector: {e}")
                        try:
                            from cvzone.HandTrackingModule import HandDetector
                            self.hand_detector = HandDetector(detectionCon=0.7, maxHands=1)
                            print("cvzone.HandDetector初始化成功")
                        except Exception as e:
                            print(f"cvzone.HandDetector初始化失败: {e}")
                self.loading_progress = 80
            elif self.loading_progress < 100:

                self.hand_tracking_game.reset()

                self.hand_tracking_game.snake_color = self.snake_color
                self.loading_progress = 100
            

            try:
                from utils.improved_chinese_text import put_chinese_text_pil
                

                if self.loading_progress < 20:
                    loading_text = "正在释放旧资源..."
                elif self.loading_progress < 50:
                    loading_text = "正在初始化摄像头..."
                elif self.loading_progress < 80:
                    loading_text = "正在加载手势检测模型..."
                elif self.loading_progress < 100:
                    loading_text = "正在初始化游戏状态..."
                else:
                    loading_text = "加载完成，准备开始游戏..."
                
                img = put_chinese_text_pil(img, loading_text, (self.screen_width//2 - 200, self.screen_height//2 - 50), 40, (255, 255, 255))
                

                bar_width = 400
                bar_height = 30
                bar_x = self.screen_width//2 - bar_width//2
                bar_y = self.screen_height//2 + 20
                cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)

                progress_width = int(bar_width * (self.loading_progress / 100))
                cv2.rectangle(img, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), (0, 255, 0), -1)

                img = put_chinese_text_pil(img, f"{self.loading_progress}%", (self.screen_width//2 - 30, self.screen_height//2 + 60), 30, (255, 255, 255))
            except Exception as e:
                print(f"中文显示错误: {e}")

                cv2.putText(img, "Loading Gesture Control Mode...", (self.screen_width//2 - 150, self.screen_height//2 - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.rectangle(img, (self.screen_width//2 - 200, self.screen_height//2 + 20), (self.screen_width//2 + 200, self.screen_height//2 + 50), (100, 100, 100), -1)
                progress_width = int(400 * (self.loading_progress / 100))
                cv2.rectangle(img, (self.screen_width//2 - 200, self.screen_height//2 + 20), (self.screen_width//2 - 200 + progress_width, self.screen_height//2 + 50), (0, 255, 0), -1)
                cv2.putText(img, f"{self.loading_progress}%", (self.screen_width//2 - 30, self.screen_height//2 + 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            self.draw_opencv_image(img)
            

            if self.loading_progress >= 100:

                self.game_mode = 'hand_tracking'
                self.is_loading = False
                
        elif self.game_mode == 'startup':
            img = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)  
            img = draw_startup_animation(img, self.animation_frame_count)
            self.animation_frame_count += 1

            if self.animation_frame_count >= 150:
                self.game_mode = 'selection'
                self.show_menu_buttons()  
                global_particles.clear()
            self.draw_opencv_image(img)

        elif self.game_mode == 'selection':
            img = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)

            img = draw_mode_selection_screen(img, self.hovered_button, self.clicked_button)
            self.draw_opencv_image(img)

        elif self.game_mode == 'classic_settings':
            try:

                mouse_pos = pygame.mouse.get_pos()
                img = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)

                img, color_blocks = draw_settings_screen(img, self.snake_color, mouse_pos)
                self.draw_opencv_image(img)
            except Exception as e:
                print(f"设置界面错误: {e}")
                import traceback
                traceback.print_exc()

                self.game_mode = 'selection'
                self.show_menu_buttons()

        elif self.game_mode == 'classic':
            if self.classic_game:
                self.classic_game.high_score = self.high_score_classic
                self.classic_game.update()
                drawn_surface = self.classic_game.draw(self.screen)
                self.screen.blit(drawn_surface, (0, 0))
                
                if self.classic_game.score > self.high_score_classic:
                    self.high_score_classic = self.classic_game.score
                    save_game_data({'high_score_classic': self.high_score_classic, 'high_score_gesture': self.high_score_gesture, 'snake_color': self.snake_color})
                
                if self.classic_game.has_started and not self.classic_game.game_over and not self.classic_game.game_started:
                    self.stop_bgm()
                    self.game_mode = 'selection'
                    self.show_menu_buttons()
                    global_particles.clear()

        elif self.game_mode == 'hand_tracking':
            snake_bg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'assets', 'images', 'snake.png')
            if os.path.exists(snake_bg_path):
                snake_bg = cv2.imread(snake_bg_path)
                snake_bg = cv2.resize(snake_bg, (self.screen_width, self.screen_height))
                img = snake_bg.copy()
            else:
                img = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8) + 20  
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0] if self.hand_tracking_game.gameOver else False
            
            hand_position = None
            
            if self.capture is not None and self.capture.isOpened():
                try:
                    success, cam_img = self.capture.read()
                    if success and cam_img is not None:
                        original_cam_img = cam_img.copy()
                        
                        if not self.hide_camera_feed:
                            display_img = cv2.flip(original_cam_img, 1)  
                            display_img = cv2.resize(display_img, (self.screen_width, self.screen_height))
                            img = display_img.copy()
                        
                        if self.hand_detector is not None:
                            try:
                                detection_img = cv2.flip(original_cam_img, 1)
                                hand_position = self.get_hand_position(detection_img)
                            except Exception as e:
                                print(f"手部检测错误: {e}")
                except Exception as e:
                    print(f"摄像头读取错误: {e}")
            
            if hand_position:
                img = self.hand_tracking_game.update(img, hand_position, mouse_pos, mouse_clicked, self.high_score_gesture)
            else:
                img = self.hand_tracking_game.update(img, None, mouse_pos, mouse_clicked, self.high_score_gesture)
                try:
                    from game.utils.improved_chinese_text import put_chinese_text_pil
                    img = put_chinese_text_pil(img, "未检测到手部", (self.screen_width//2 - 150, 50), 40, (255, 255, 0))
                except Exception as e:
                    print(f"中文显示错误: {e}")
                    cv2.putText(img, "未检测到手部", (self.screen_width//2 - 150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            if self.hand_tracking_game.score > self.high_score_gesture:
                self.high_score_gesture = self.hand_tracking_game.score
                save_game_data({'high_score_classic': self.high_score_classic, 'high_score_gesture': self.high_score_gesture, 'snake_color': self.snake_color})
            
            if self.hand_tracking_game.return_to_menu:
                self.stop_bgm()
                self.game_mode = 'selection'
                if self.capture is not None:
                    self.capture.release()
                    self.capture = None
                self.show_menu_buttons()
                global_particles.clear()
            
            draw_and_update_effects(img)
            self.draw_opencv_image(img)
        
        elif self.game_mode == 'pause_menu':

            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            

            title_text = "游戏暂停"
            try:

                title_surface = self.font_large.render(title_text, True, (255, 255, 255))
                title_height = title_surface.get_height()
            except Exception as e:
                print(f"标题渲染错误: {e}")
                title_height = 80  
            

            button_width = 300  
            button_height = 70  
            button_spacing = 50  
            button_color = (100, 100, 100)
            button_hover_color = (150, 150, 150)
            text_color = (255, 255, 255)
            

            num_buttons = 3
            title_button_spacing = 60  
            total_menu_height = title_height + title_button_spacing + (num_buttons * button_height) + ((num_buttons - 1) * button_spacing)
            

            menu_start_y = (self.screen_height - total_menu_height) // 2
            

            try:
                title_rect = title_surface.get_rect(center=(self.screen_width//2, menu_start_y + title_height//2))
                self.screen.blit(title_surface, title_rect)
            except Exception as e:
                print(f"标题渲染错误: {e}")

                img = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
                img = put_chinese_text(img, title_text, (self.screen_width//2 - 120, menu_start_y), 70, (255, 255, 255))
                self.draw_opencv_image(img)

                self.screen.blit(overlay, (0, 0))
            

            button_y_start = menu_start_y + title_height + title_button_spacing
            

            resume_button_rect = pygame.Rect(
                self.screen_width//2 - button_width//2,
                button_y_start,
                button_width,
                button_height
            )
            

            menu_button_rect = pygame.Rect(
                self.screen_width//2 - button_width//2,
                button_y_start + button_height + button_spacing,
                button_width,
                button_height
            )
            

            exit_button_rect = pygame.Rect(
                self.screen_width//2 - button_width//2,
                button_y_start + 2 * (button_height + button_spacing),
                button_width,
                button_height
            )
            

            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0]
            

            resume_button_color = button_hover_color if resume_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, resume_button_color, resume_button_rect, border_radius=10)
            resume_text = "返回游戏"
            try:
                resume_surface = self.font_small.render(resume_text, True, text_color)
                resume_text_rect = resume_surface.get_rect(center=resume_button_rect.center)
                self.screen.blit(resume_surface, resume_text_rect)
            except Exception as e:
                print(f"返回游戏按钮文本渲染错误: {e}")
            

            menu_button_color = button_hover_color if menu_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, menu_button_color, menu_button_rect, border_radius=10)
            menu_text = "返回主菜单"
            try:
                menu_surface = self.font_small.render(menu_text, True, text_color)
                menu_text_rect = menu_surface.get_rect(center=menu_button_rect.center)
                self.screen.blit(menu_surface, menu_text_rect)
            except Exception as e:
                print(f"主菜单按钮文本渲染错误: {e}")
            

            exit_button_color = button_hover_color if exit_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, exit_button_color, exit_button_rect, border_radius=10)
            exit_text = "退出游戏"
            try:
                exit_surface = self.font_small.render(exit_text, True, text_color)
                exit_text_rect = exit_surface.get_rect(center=exit_button_rect.center)
                self.screen.blit(exit_surface, exit_text_rect)
            except Exception as e:
                print(f"退出按钮文本渲染错误: {e}")
            

            if mouse_clicked:
                if resume_button_rect.collidepoint(mouse_pos):

                    self.game_mode = self.prev_game_mode
                elif menu_button_rect.collidepoint(mouse_pos):


                    if self.prev_game_mode == 'classic' and self.classic_game.score > self.high_score_classic:
                        self.high_score_classic = self.classic_game.score
                    elif self.prev_game_mode == 'hand_tracking' and self.hand_tracking_game.score > self.high_score_gesture:
                        self.high_score_gesture = self.hand_tracking_game.score

                    save_game_data({'high_score_classic': self.high_score_classic, 'high_score_gesture': self.high_score_gesture, 'snake_color': self.snake_color})

                    if self.capture is not None:
                        self.capture.release()
                        self.capture = None

                    self.game_mode = 'selection'

                    self.show_menu_buttons()
                    global_particles.clear()
                elif exit_button_rect.collidepoint(mouse_pos):

                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        
        elif self.game_mode == 'settings_menu':

            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            

            title_text = "游戏设置"
            try:

                title_surface = self.font_large.render(title_text, True, (255, 255, 255))
                title_height = title_surface.get_height()
            except Exception as e:
                print(f"标题渲染错误: {e}")
                title_height = 80  
            

            button_width = 400  
            button_height = 70  
            button_spacing = 50  
            button_color = (100, 100, 100)
            button_hover_color = (150, 150, 150)
            text_color = (255, 255, 255)
            

            num_buttons = 4
            title_button_spacing = 60  
            total_menu_height = title_height + title_button_spacing + (num_buttons * button_height) + ((num_buttons - 1) * button_spacing)
            

            menu_start_y = (self.screen_height - total_menu_height) // 2
            

            try:
                title_rect = title_surface.get_rect(center=(self.screen_width//2, menu_start_y + title_height//2))
                self.screen.blit(title_surface, title_rect)
            except Exception as e:
                print(f"标题渲染错误: {e}")

                img = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
                img = put_chinese_text(img, title_text, (self.screen_width//2 - 120, menu_start_y), 70, (255, 255, 255))
                self.draw_opencv_image(img)

                self.screen.blit(overlay, (0, 0))
            

            button_y_start = menu_start_y + title_height + title_button_spacing # 期末汇报（12月底）之前请勿乱用该项目
            

            color_button_rect = pygame.Rect(
                self.screen_width//2 - button_width//2,
                button_y_start,
                button_width,
                button_height
            )
            

            hand_tracking_settings_button_rect = pygame.Rect(
                self.screen_width//2 - button_width//2,
                button_y_start + button_height + button_spacing,
                button_width,
                button_height
            )
            

            menu_button_rect = pygame.Rect(
                self.screen_width//2 - button_width//2,
                button_y_start + 2 * (button_height + button_spacing),
                button_width,
                button_height
            )
            

            exit_button_rect = pygame.Rect(
                self.screen_width//2 - button_width//2,
                button_y_start + 3 * (button_height + button_spacing),
                button_width,
                button_height
            )
            

            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0]
            

            color_button_color = button_hover_color if color_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, color_button_color, color_button_rect, border_radius=10)
            color_text = "蛇颜色设置"
            try:
                color_surface = self.font_small.render(color_text, True, text_color)
                color_text_rect = color_surface.get_rect(center=color_button_rect.center)
                self.screen.blit(color_surface, color_text_rect)
            except Exception as e:
                print(f"颜色设置按钮文本渲染错误: {e}")
            

            hand_tracking_settings_button_color = button_hover_color if hand_tracking_settings_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, hand_tracking_settings_button_color, hand_tracking_settings_button_rect, border_radius=10)
            hand_tracking_settings_text = "手势控制模式设置"
            try:
                hand_tracking_settings_surface = self.font_small.render(hand_tracking_settings_text, True, text_color)
                hand_tracking_settings_text_rect = hand_tracking_settings_surface.get_rect(center=hand_tracking_settings_button_rect.center)
                self.screen.blit(hand_tracking_settings_surface, hand_tracking_settings_text_rect)
            except Exception as e:
                print(f"手势控制设置按钮文本渲染错误: {e}")
            

            menu_button_color = button_hover_color if menu_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, menu_button_color, menu_button_rect, border_radius=10)
            menu_text = "返回主菜单"
            try:
                menu_surface = self.font_small.render(menu_text, True, text_color)
                menu_text_rect = menu_surface.get_rect(center=menu_button_rect.center)
                self.screen.blit(menu_surface, menu_text_rect)
            except Exception as e:
                print(f"主菜单按钮文本渲染错误: {e}")
            

            exit_button_color = button_hover_color if exit_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, exit_button_color, exit_button_rect, border_radius=10)
            exit_text = "退出游戏"
            try:
                exit_surface = self.font_small.render(exit_text, True, text_color)
                exit_text_rect = exit_surface.get_rect(center=exit_button_rect.center)
                self.screen.blit(exit_surface, exit_text_rect)
            except Exception as e:
                print(f"退出按钮文本渲染错误: {e}")
            

            if mouse_clicked:
                if color_button_rect.collidepoint(mouse_pos):

                    self.game_mode = 'classic_settings'
                elif hand_tracking_settings_button_rect.collidepoint(mouse_pos):

                    self.game_mode = 'hand_tracking_settings'
                elif menu_button_rect.collidepoint(mouse_pos):

                    self.game_mode = 'selection'

                    self.show_menu_buttons()
                elif exit_button_rect.collidepoint(mouse_pos):

                    pygame.event.post(pygame.event.Event(pygame.QUIT))

        elif self.game_mode == 'hand_tracking_settings':

            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            

            title_text = "手势控制模式设置"
            try:

                title_surface = self.font_large.render(title_text, True, (255, 255, 255))
                title_height = title_surface.get_height()
            except Exception as e:
                print(f"标题渲染错误: {e}")
                title_height = 80  
            

            button_width = 300  
            button_height = 70  
            button_spacing = 50  
            button_color = (100, 100, 100)
            button_hover_color = (150, 150, 150)
            text_color = (255, 255, 255)
            

            num_buttons = 2
            title_button_spacing = 60  
            total_menu_height = title_height + title_button_spacing + (num_buttons * button_height) + ((num_buttons - 1) * button_spacing)
            

            menu_start_y = (self.screen_height - total_menu_height) // 2
            

            try:
                title_rect = title_surface.get_rect(center=(self.screen_width//2, menu_start_y + title_height//2))
                self.screen.blit(title_surface, title_rect)
            except Exception as e:
                print(f"标题渲染错误: {e}")

                img = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
                img = put_chinese_text(img, title_text, (self.screen_width//2 - 150, menu_start_y), 70, (255, 255, 255))
                self.draw_opencv_image(img)

                self.screen.blit(overlay, (0, 0))
            

            button_y_start = menu_start_y + title_height + title_button_spacing
            

            self.camera_toggle_button_rect = pygame.Rect(
                self.screen_width//2 - button_width//2,
                button_y_start,
                button_width,
                button_height
            )
            camera_toggle_button_rect = self.camera_toggle_button_rect
            

            self.hand_tracking_back_button_rect = pygame.Rect(
                self.screen_width//2 - button_width//2,
                button_y_start + button_height + button_spacing,
                button_width,
                button_height
            )
            back_button_rect = self.hand_tracking_back_button_rect
            

            mouse_pos = pygame.mouse.get_pos()
            

            camera_toggle_button_color = button_hover_color if camera_toggle_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, camera_toggle_button_color, camera_toggle_button_rect, border_radius=10)
            

            camera_toggle_text = "开启摄像头画面" if self.hide_camera_feed else "关闭摄像头画面"
            
            try:
                camera_toggle_surface = self.font_small.render(camera_toggle_text, True, text_color)
                camera_toggle_text_rect = camera_toggle_surface.get_rect(center=camera_toggle_button_rect.center)
                self.screen.blit(camera_toggle_surface, camera_toggle_text_rect)
            except Exception as e:
                print(f"摄像头开关按钮文本渲染错误: {e}")
            

            back_button_color = button_hover_color if back_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, back_button_color, back_button_rect, border_radius=10)
            back_text = "返回主界面"
            try:
                back_surface = self.font_small.render(back_text, True, text_color)
                back_text_rect = back_surface.get_rect(center=back_button_rect.center)
                self.screen.blit(back_surface, back_text_rect)
            except Exception as e:
                print(f"返回按钮文本渲染错误: {e}")
            

            status_text = "当前状态: 摄像头画面已" + ("隐藏" if self.hide_camera_feed else "显示")
            try:
                status_surface = self.font_small.render(status_text, True, (200, 200, 200))
                status_rect = status_surface.get_rect(center=(self.screen_width//2, back_button_rect.bottom + 40))
                self.screen.blit(status_surface, status_rect)
            except Exception as e:
                print(f"状态提示渲染错误: {e}")
            

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.game_mode = 'settings_menu'

    def get_hand_position(self, img):
        """获取手部位置，如果手势追踪不可用则返回None"""
        try:
            # 检查图像是否有效
            if img is None or len(img.shape) != 3 or img.shape[2] < 3:
                return None
            
            # 直接在BGR图像上进行检测，避免颜色转换，提高性能
            # cvzone的HandDetector实际上支持BGR格式，无需转换
            hands, _ = self.hand_detector.findHands(img, draw=False, flipType=False)
            
            if hands:
                hand = hands[0]
                lmList = hand['lmList']
                # lmList包含21个手部关键点，索引8是食指指尖
                # 优化：即使只有部分关键点，只要有食指指尖（索引8）就能工作
                if len(lmList) >= 9:  # 确保至少有9个关键点，包含食指指尖
                    # 获取食指指尖坐标（索引8）
                    index_x = int(lmList[8][0])
                    index_y = int(lmList[8][1])
                    
                    # 摄像头分辨率固定为1280x720，需要映射到游戏窗口分辨率
                    # 计算缩放比例
                    cam_width = 1280
                    cam_height = 720
                    
                    # 将摄像头坐标映射到游戏窗口坐标
                    scale_x = self.screen_width / cam_width
                    scale_y = self.screen_height / cam_height
                    
                    # 应用缩放，确保蛇跟着手指方向正确移动
                    game_x = int(index_x * scale_x)
                    game_y = int(index_y * scale_y)
                    
                    # 确保坐标在游戏窗口范围内
                    game_x = max(0, min(self.screen_width, game_x))
                    game_y = max(0, min(self.screen_height, game_y))
                    
                    return game_x, game_y
            return None
        except Exception as e:
            print(f"获取手部位置错误: {e}")
            return None

    def draw_opencv_image(self, img):
        # 确保图像数据类型正确
        if img.dtype != np.uint8:
            img = img.astype(np.uint8)
            
        # 转换颜色空间
        if len(img.shape) == 3 and img.shape[2] == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif len(img.shape) == 3 and img.shape[2] == 4:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        else:
            # 灰度图
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            
        # 创建Pygame Surface
        try:
            # 尝试使用更直接的方法
            pygame_surface = pygame.surfarray.make_surface(np.transpose(img_rgb, (1, 0, 2)))
        except:
            # 如果失败，创建一个纯色表面用于测试
            pygame_surface = pygame.Surface((img_rgb.shape[1], img_rgb.shape[0]))
            pygame_surface.fill((0, 255, 0))  # 绿色，便于识别
        
        self.screen.blit(pygame_surface, (0, 0))

    def initialize_camera(self):
        try:
            if self.capture is not None:
                self.capture.release()
            # 使用指定的分辨率初始化摄像头
            self.capture = cv2.VideoCapture(0)
            if self.capture.isOpened():
                self.capture.set(3, 1280)  # 设置宽度
                self.capture.set(4, 720)   # 设置高度
        except Exception as e:
            print(f"摄像头初始化错误: {e}")
            self.capture = None
    
    def draw_hand_tracking_ui(self, img):
        game = self.hand_tracking_game
        try:
            # 使用改进的中文文本渲染函数
            img = put_chinese_text_pil(img, f"得分: {game.score}", (int(self.screen_width * 0.023), int(self.screen_height * 0.04)), 40, (50, 130, 246))
            img = put_chinese_text_pil(img, f"最高分: {self.high_score_gesture}", (int(self.screen_width * 0.023), int(self.screen_height * 0.11)), 40, (50, 130, 246))
        except Exception as e:
            # 如果中文文本失败，则使用英文文本作为后备
            cv2.putText(img, f"Score: {game.score}", (int(self.screen_width * 0.023), int(self.screen_height * 0.04)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 130, 246), 2)
            cv2.putText(img, f"High Score: {self.high_score_gesture}", (int(self.screen_width * 0.023), int(self.screen_height * 0.11)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 130, 246), 2)
        return img

    def draw_hand_tracking_game_over(self, img):
        game = self.hand_tracking_game
        if game.score > self.high_score_gesture:
            self.high_score_gesture = game.score
            save_game_data({'high_score_classic': self.high_score_classic, 'high_score_gesture': self.high_score_gesture, 'snake_color': self.snake_color})
        try:
            # 使用改进的中文文本渲染函数
            img = put_rainbow_text_pil(img, "游戏结束", (self.screen_width//2 - 160, self.screen_height//2 - 100), 80)
            img = put_chinese_text_pil(img, f"最终得分: {game.score}", (self.screen_width//2 - 120, self.screen_height//2), 60, (50, 130, 246))
            img = put_chinese_text_pil(img, f"最高分: {self.high_score_gesture}", (self.screen_width//2 - 120, self.screen_height//2 + 40), 40, (50, 130, 246))

            img = put_chinese_text_pil(img, "按 'M' 返回菜单", (self.screen_width//2 - 180, self.screen_height//2 + 140), 40, (255, 255, 255))
        except Exception as e:
            # 如果中文文本失败，则使用英文文本作为后备
            cv2.putText(img, "GAME OVER", (self.screen_width//2 - 150, self.screen_height//2 - 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            cv2.putText(img, f"Final Score: {game.score}", (self.screen_width//2 - 120, self.screen_height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 130, 246), 2)
            cv2.putText(img, f"High Score: {self.high_score_gesture}", (self.screen_width//2 - 120, self.screen_height//2 + 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 130, 246), 2)
            cv2.putText(img, "Press 'R' to Restart", (self.screen_width//2 - 180, self.screen_height//2 + 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(img, "Press 'M' for Menu", (self.screen_width//2 - 180, self.screen_height//2 + 140), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return img

    def cleanup(self):
        if self.capture: self.capture.release()
        pygame.quit()

if __name__ == '__main__':
    controller = GameController()
    controller.run()
    #由pxf改编
