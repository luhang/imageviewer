"""图片显示桌面软件 —— 演示版。

基于 tkinter + Pillow。支持打开单张图片或整个文件夹，浏览、缩放、旋转、全屏。

运行方式：
    python image_viewer.py              # 打开后手动选择图片
    python image_viewer.py 图片路径      # 直接打开某张图片
    python image_viewer.py 文件夹路径    # 直接打开某个文件夹

依赖：
    pip install Pillow
"""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

# 支持的图片格式
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff", ".ico"}


def is_image(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTS


class ImageViewer:
    """图片查看器主窗口。"""

    def __init__(self, root: tk.Tk, start_path: str | None = None) -> None:
        self.root = root
        self.root.title("图片查看器 —— 演示版")
        self.root.geometry("960x640")

        # 状态
        self.files: list[Path] = []
        self.index: int = -1
        self.current_path: Path | None = None
        self.image: Image.Image | None = None
        self.zoom = 1.0
        self.fit = True  # 是否适应窗口
        self.rotation = 0  # 旋转角度（0/90/180/270）
        self._photo: ImageTk.PhotoImage | None = None

        self._build_ui()
        self._bind_shortcuts()

        if start_path:
            p = Path(start_path)
            if p.is_dir():
                self.load_folder(p)
            elif p.is_file() and is_image(p):
                self.load_folder(p.parent, initial=p)
            else:
                messagebox.showerror("错误", f"路径无效或不是支持的图片: {start_path}")

    # ---------- 界面 ----------
    def _build_ui(self) -> None:
        # 工具栏
        toolbar = ttk.Frame(self.root, padding=4)
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="打开文件", command=self.open_file).pack(side="left", padx=2)
        ttk.Button(toolbar, text="打开文件夹", command=self.open_folder).pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Button(toolbar, text="◀ 上一张", command=self.prev_image).pack(side="left", padx=2)
        ttk.Button(toolbar, text="下一张 ▶", command=self.next_image).pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Button(toolbar, text="适应窗口", command=lambda: self.set_fit(True)).pack(side="left", padx=2)
        ttk.Button(toolbar, text="原始大小", command=self.set_original).pack(side="left", padx=2)
        ttk.Button(toolbar, text="放大 +", command=lambda: self.zoom_step(1.25)).pack(side="left", padx=2)
        ttk.Button(toolbar, text="缩小 -", command=lambda: self.zoom_step(0.8)).pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Button(toolbar, text="旋转 ⟳", command=self.rotate).pack(side="left", padx=2)
        ttk.Button(toolbar, text="全屏", command=self.toggle_fullscreen).pack(side="left", padx=2)

        # 主区：左侧缩略图列表 + 右侧图片显示
        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(body, width=18, exportselection=False)
        self.listbox.pack(side="left", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        self.canvas = tk.Canvas(body, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _e: self._render())
        self.canvas.bind("<MouseWheel>", self._on_wheel)

        # 状态栏
        self.status = tk.StringVar(value="请打开图片或文件夹")
        ttk.Label(self.root, textvariable=self.status, anchor="w", padding=(8, 2)).pack(fill="x")

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Left>", lambda _e: self.prev_image())
        self.root.bind("<Right>", lambda _e: self.next_image())
        self.root.bind("<Escape>", lambda _e: self.exit_fullscreen())
        self.root.bind("<F11>", lambda _e: self.toggle_fullscreen())
        self.root.bind("<Control-o>", lambda _e: self.open_file())
        self.root.bind("<Control-f>", lambda _e: self.open_folder())

    # ---------- 文件加载 ----------
    def open_file(self) -> None:
        path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tif *.tiff *.ico"),
                       ("所有文件", "*.*")],
        )
        if path:
            self.load_folder(Path(path).parent, initial=Path(path))

    def open_folder(self) -> None:
        path = filedialog.askdirectory(title="选择图片文件夹")
        if path:
            self.load_folder(Path(path))

    def load_folder(self, folder: Path, initial: Path | None = None) -> None:
        files = sorted((p for p in folder.iterdir() if p.is_file() and is_image(p)),
                       key=lambda p: p.name.lower())
        if not files:
            messagebox.showinfo("提示", f"文件夹中没有支持的图片:\n{folder}")
            return
        self.files = files
        self.listbox.delete(0, tk.END)
        for f in self.files:
            self.listbox.insert(tk.END, f.name)

        idx = self.files.index(initial) if initial and initial in self.files else 0
        self.show_image(idx)

    def show_image(self, idx: int) -> None:
        if not self.files:
            return
        self.index = idx % len(self.files)
        self.current_path = self.files[self.index]
        try:
            self.image = Image.open(self.current_path)
            self.image.load()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("错误", f"无法打开图片:\n{self.current_path}\n{exc}")
            return
        self.zoom = 1.0
        self.fit = True
        self.rotation = 0
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.index)
        self.listbox.see(self.index)
        self._render()

    # ---------- 渲染 ----------
    def _render(self) -> None:
        self.canvas.delete("all")
        if self.image is None:
            return

        w = max(self.canvas.winfo_width(), 1)
        h = max(self.canvas.winfo_height(), 1)

        img = self.image
        if self.rotation:
            img = img.rotate(-self.rotation, expand=True)

        if self.fit:
            iw, ih = img.size
            scale = min(w / iw, h / ih)
            disp_w, disp_h = max(int(iw * scale), 1), max(int(ih * scale), 1)
        else:
            disp_w = max(int(img.width * self.zoom), 1)
            disp_h = max(int(img.height * self.zoom), 1)

        disp_img = img.resize((disp_w, disp_h), Image.Resampling.LANCZOS)
        self._photo = ImageTk.PhotoImage(disp_img)
        self.canvas.create_image(w // 2, h // 2, image=self._photo, anchor="center")

        name = self.current_path.name if self.current_path else ""
        total = len(self.files)
        cur = self.index + 1 if total else 0
        zoom_info = "适应窗口" if self.fit else f"{int(self.zoom * 100)}%"
        self.status.set(
            f"{name}  [{cur}/{total}]  尺寸 {self.image.width}x{self.image.height}"
            f"  显示 {disp_w}x{disp_h}  {zoom_info}  旋转 {self.rotation}°"
        )

    # ---------- 操作 ----------
    def _on_select(self, _event) -> None:
        sel = self.listbox.curselection()
        if sel:
            self.show_image(sel[0])

    def _on_wheel(self, event) -> None:
        # Windows 上 event.delta 是 120 的倍数
        if event.delta > 0:
            self.zoom_step(1.1)
        else:
            self.zoom_step(0.9)

    def prev_image(self) -> None:
        if self.files:
            self.show_image(self.index - 1)

    def next_image(self) -> None:
        if self.files:
            self.show_image(self.index + 1)

    def set_fit(self, fit: bool) -> None:
        self.fit = fit
        self._render()

    def set_original(self) -> None:
        self.fit = False
        self.zoom = 1.0
        self._render()

    def zoom_step(self, factor: float) -> None:
        self.fit = False
        self.zoom = max(0.05, min(self.zoom * factor, 20.0))
        self._render()

    def rotate(self) -> None:
        if self.image is None:
            return
        self.rotation = (self.rotation + 90) % 360
        self._render()

    def toggle_fullscreen(self) -> None:
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def exit_fullscreen(self) -> None:
        if self.root.attributes("-fullscreen"):
            self.root.attributes("-fullscreen", False)


def main() -> None:
    root = tk.Tk()
    start = sys.argv[1] if len(sys.argv) > 1 else None
    ImageViewer(root, start)
    root.mainloop()


if __name__ == "__main__":
    main()
