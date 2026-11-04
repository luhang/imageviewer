# Image Viewer（图片查看器 · 演示版）

一个基于 **Python + tkinter + Pillow** 的桌面图片查看器演示程序。

## 功能

- 打开单张图片或整个文件夹（支持 jpg / png / gif / bmp / webp / tif / ico）
- 左侧文件列表，点击切换图片
- 缩放：适应窗口、原始大小、放大 / 缩小、鼠标滚轮缩放
- 旋转（每次 90°）
- 全屏（工具栏按钮 / `F11`，`Esc` 退出）
- 状态栏：文件名、第几张、原图尺寸、显示尺寸、缩放、旋转角度

## 环境要求

- Python 3.10+
- Pillow

```bash
pip install Pillow
```

## 运行

```bash
# 打开后手动选图
python image_viewer.py

# 直接打开示例文件夹
python image_viewer.py demo_images

# 直接打开某张图片
python image_viewer.py demo_images/01_渐变_横图.png
```

## 快捷键

| 按键 | 功能 |
|------|------|
| `←` / `→` | 上一张 / 下一张 |
| 鼠标滚轮 | 放大 / 缩小 |
| `Ctrl+O` | 打开文件 |
| `Ctrl+F` | 打开文件夹 |
| `F11` | 切换全屏 |
| `Esc` | 退出全屏 |

## 项目结构

```
image-viewer/
├── image_viewer.py        # 主程序
├── make_demo_images.py    # 生成示例图片的脚本
└── demo_images/           # 示例图片（可重新生成）
```

## 重新生成示例图片

```bash
python make_demo_images.py
```
