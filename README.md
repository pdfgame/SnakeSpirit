# 双模式贪吃蛇游戏 / Dual-mode Snake Game

## 项目背景 / Project Background

本项目是基于现有GitHub贪吃蛇项目灵感开发的双模式贪吃蛇游戏，结合了经典游戏玩法与现代手势控制技术。项目采用Python、OpenCV和Pygame开发，支持两种游戏模式，具有精美的视觉效果和丰富的设置选项。

This project is a dual-mode snake game developed based on inspiration from existing GitHub snake game projects, combining classic gameplay with modern gesture control technology. The project is developed using Python, OpenCV, and Pygame, supporting two game modes with exquisite visual effects and rich setting options.

## 游戏特性 / Game Features

- **双游戏模式 / Dual Game Modes**：
  - 经典模式 / Classic Mode：传统键盘控制的贪吃蛇游戏
  - 手势控制模式 / Gesture Control Mode：通过摄像头手势控制的现代贪吃蛇游戏
- **精美的视觉效果 / Exquisite Visual Effects**：
  - 支持16种纯色和4种渐变颜色效果
  - 流畅的动画和粒子特效
  - 响应式设计，适配不同屏幕尺寸
- **丰富的设置选项 / Rich Setting Options**：
  - 可自定义蛇的颜色
  - 可切换摄像头显示
  - 支持保存最高分
- **多语言支持 / Multi-language Support**：
  - 完整的中文界面
  - 清晰的中文操作提示

## 项目结构 / Project Structure

```
SnakeGame-main/
├── game/                    # 游戏核心代码 / Game core code
│   ├── core/                # 核心组件 / Core components
│   │   ├── game_controller.py  # 游戏控制器 / Game controller
│   │   ├── game_ui.py      # 游戏界面绘制 / Game UI rendering
│   │   └── snake_game.py   # 核心游戏逻辑 / Core game logic
│   ├── modes/               # 游戏模式 / Game modes
│   │   ├── classic/         # 经典游戏模式 / Classic game mode
│   │   │   └── classic_snake_game.py  # 经典模式游戏逻辑 / Classic mode game logic
│   │   └── gesture/         # 手势控制模式 / Gesture control mode
│   │       └── simple_gesture_snake.py  # 手势控制游戏逻辑 / Gesture control game logic
│   └── utils/               # 工具函数 / Utility functions
│       ├── chinese_text.py  # 中文文本渲染 / Chinese text rendering
│       ├── game_data.py     # 游戏数据管理 / Game data management
│       └── improved_chinese_text.py  # 改进的中文文本渲染 / Improved Chinese text rendering
├── music/                   # 游戏音频文件 / Game audio files
├── resources/               # 游戏资源 / Game resources
│   ├── assets/              # 静态资源 / Static assets
│   │   ├── fonts/           # 字体文件 / Font files
│   │   └── images/          # 图片资源 / Image resources
│   └── data/                # 游戏数据 / Game data
│       └── game_data.json   # 游戏设置和最高分 / Game settings and high scores
├── tests/                   # 测试代码 / Test code
├── docs/                    # 文档 / Documentation
├── main.py                  # 程序入口 / Program entry point
├── requirements.txt         # 依赖项列表 / Dependency list
├── .gitignore              # Git忽略文件 / Git ignore file
├── LICENSE                 # MIT许可证 / MIT License
├── README.md               # 项目说明文档 / Project description document
└── 开发日志.md               # 开发记录 / Development log
```

## 技术栈 / Technology Stack

- **主要语言 / Main Language**：Python 3.11+
- **游戏框架 / Game Framework**：Pygame-ce 2.5.6
- **计算机视觉 / Computer Vision**：OpenCV
- **手势识别 / Gesture Recognition**：
  - 优先使用：cvzone.HandDetector（依赖mediapipe模型）
  - 备选方案：独立MediaPipe Hands检测器（无需cvzone，直接加载task模型）
  - 最终兜底：自定义SimpleHandDetector（基于肤色检测和轮廓分析，不依赖mediapipe）
- **图像处理 / Image Processing**：PIL (Pillow)
- **UI框架 / UI Framework**：pygame_gui

## 安装依赖 / Install Dependencies

1. 确保已安装Python 3.11或更高版本
   Ensure Python 3.11 or higher is installed

2. 安装游戏依赖：
   Install game dependencies:

```bash
pip install -r requirements.txt
```

> 注意：依赖文件已经锁定 `mediapipe` 与 `protobuf<5` 的组合来避免与 `tensorflow` 的冲突，请勿额外安装 `tensorflow`，否则会触发`protobuf`版本互斥。  
> Note: The requirements file pins `mediapipe` together with `protobuf<5` to avoid the conflict introduced by TensorFlow. Do not install TensorFlow on top of these deps, otherwise pip will attempt to upgrade protobuf and break mediapipe.

## 运行游戏 / Run the Game

```bash
python main.py
```

## 游戏操作说明 / Game Operation Instructions

### 主菜单 / Main Menu
- **鼠标点击 / Mouse Click**：选择游戏模式或进入设置
  Select game mode or enter settings
- **ESC键 / ESC Key**：调出设置菜单
  Bring up the settings menu

### 经典模式 / Classic Mode
- **方向键 / Arrow Keys**：控制蛇的移动方向
  Control the snake's movement direction
- **ESC键 / ESC Key**：暂停游戏
  Pause the game

### 手势控制模式 / Gesture Control Mode
- **食指 / Index Finger**：控制蛇的移动方向
  Control the snake's movement direction
- **ESC键 / ESC Key**：退出游戏
  Exit the game
- **M键 / M Key**：返回主菜单
  Return to main menu

#### 手势控制模式使用说明 / Gesture Control Mode Usage Guidelines
- 请与屏幕保持适当距离，确保整只手能够被摄像头完整检测到，以获得最佳游戏体验
  Please maintain an appropriate distance from the screen and ensure your entire hand can be fully detected by the camera for the best gaming experience
- 若不确定摄像头是否能正常检测您的手部，请在主菜单界面按ESC键调出手势控制模式设置
  If you are unsure whether the camera can properly detect your hand, press the ESC key on the main menu interface to bring up the gesture control mode settings
- 在设置中可选择开启或关闭摄像头，以调整至最佳检测状态
  In the settings, you can choose to turn the camera on or off to adjust to the optimal detection state

### 设置菜单 / Settings Menu
- **颜色设置 / Color Settings**：选择蛇的颜色
  Select the snake's color
- **摄像头设置 / Camera Settings**：切换摄像头显示
  Toggle camera display
- **返回按钮 / Return Button**：返回主菜单
  Return to main menu

## 开发指南 / Development Guide

### 目录结构说明 / Directory Structure Description

- **game/core/**：包含游戏的核心组件，如游戏控制器、UI绘制和核心游戏逻辑
  Contains the core components of the game, such as game controller, UI rendering, and core game logic
- **game/modes/**：包含不同游戏模式的实现
  Contains implementations of different game modes
- **game/utils/**：包含各种工具函数，如中文文本渲染、游戏数据管理等
  Contains various utility functions, such as Chinese text rendering, game data management, etc.
- **resources/**：包含游戏所需的所有资源文件
  Contains all resource files required by the game
- **tests/**：包含游戏的测试代码
  Contains test code for the game
- **docs/**：包含游戏的文档
  Contains documentation for the game

### 手势检测架构 / Gesture Detection Pipeline
1. **cvzone.HandDetector + MediaPipe**：默认方案，具备最稳定的手势识别和绘制接口。
2. **独立MediaPipe Hands**：当cvzone不可用或初始化失败时，项目会直接构建MediaPipe Hands检测器，复用相同的`findHands`接口。
3. **SimpleHandDetector**：完全不依赖mediapipe的兜底方案，通过肤色分割和轮廓分析维持基本的手势输入能力。

该多级策略确保不会再因为`tensorflow`与`protobuf`冲突导致手势模式无法启动。

### 代码规范 / Code Standards

- 所有Python文件使用UTF-8编码
  All Python files use UTF-8 encoding
- 类名使用PascalCase命名规范
  Class names use PascalCase naming convention
- 函数名和变量名使用snake_case命名规范
  Function and variable names use snake_case naming convention
- 代码中添加适当的注释
  Add appropriate comments in the code
- 遵循PEP 8代码风格指南
  Follow PEP 8 code style guide

### 新增功能 / Add New Features

1. **添加新的游戏模式 / Add New Game Mode**：在`game/modes/`目录下创建新的游戏模式文件夹和相关文件
   Create a new game mode folder and related files in the `game/modes/` directory
2. **添加新的视觉效果 / Add New Visual Effects**：在`game/core/game_ui.py`中添加新的视觉效果函数
   Add new visual effect functions in `game/core/game_ui.py`
3. **添加新的工具函数 / Add New Utility Functions**：在`game/utils/`目录下创建新的工具函数文件
   Create new utility function files in the `game/utils/` directory

## 构建和打包 / Build and Package

### 使用PyInstaller打包 / Package with PyInstaller

```bash
pyinstaller --onefile --windowed --name=贪吃蛇游戏 main.py
```

### 构建注意事项 / Build Notes

- 确保所有资源文件都已正确包含在打包中
  Ensure all resource files are correctly included in the package
- 确保所有依赖项都已正确安装
  Ensure all dependencies are correctly installed
- 测试打包后的游戏是否能正常运行
  Test whether the packaged game can run normally

## 常见问题 / Frequently Asked Questions

### 手势控制模式无法工作 / Gesture Control Mode Not Working

- 确保摄像头已连接并正常工作
  Ensure the camera is connected and working properly
- 确保有足够的光线以便摄像头准确识别手势
  Ensure there is sufficient light for the camera to accurately recognize gestures
- 确保已安装cvzone库和mediapipe模型
  Ensure cvzone library and mediapipe model are installed

### 游戏运行卡顿 / Game Runs Slowly

- 关闭其他占用CPU资源的程序
  Close other programs that occupy CPU resources
- 降低游戏分辨率
  Reduce game resolution
- 关闭摄像头显示
  Turn off camera display

### 中文显示异常 / Chinese Display Abnormal

- 确保已安装中文字体
  Ensure Chinese fonts are installed
- 确保游戏目录下的fonts文件夹中包含中文字体文件
  Ensure the fonts folder in the game directory contains Chinese font files

## 许可证 / License

本项目采用MIT许可证，详情请查看LICENSE文件。

This project is licensed under the MIT License. For details, please check the LICENSE file.

## 贡献 / Contributions

欢迎提交Issue和Pull Request来改进这个项目！

Welcome to submit Issues and Pull Requests to improve this project!

## 联系方式 / Contact Information

如有任何问题或建议，请通过以下方式联系：

For any questions or suggestions, please contact us through the following methods:

- 邮箱1 / Email 1：phasisx_pdf_pxf@163.com
- 邮箱2 / Email 2：xiaofeng9121@gmail.com

## 特别感谢 / Special Thanks

- **cvzone** 团队：提供了强大的手部识别功能
- **Pygame-CE** 团队：提供了跨平台的游戏开发框架
- **OpenCV** 团队：提供了丰富的计算机视觉功能
- **所有贡献者**：为这个项目做出了宝贵的贡献

- **cvzone** Team: Provided powerful hand recognition functionality
- **Pygame-CE** Team: Provided a cross-platform game development framework
- **OpenCV** Team: Provided rich computer vision functionality
- **All Contributors**: Made valuable contributions to this project
