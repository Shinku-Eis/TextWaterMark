import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageDraw, ImageFont
import os

class WatermarkTool:
    def __init__(self, root):
        self.root = root
        self.root.title("图片批量水印工具")
        self.root.geometry("600x560")
        self.root.configure(bg="#f0f0f0")
        
        self.watermark_text = tk.StringVar(value="我的水印")
        self.font_size = tk.IntVar(value=36)
        self.opacity = tk.IntVar(value=128)
        self.position = tk.StringVar(value="bottom-right")
        self.watermark_color = (255, 255, 255)
        self.bold = tk.BooleanVar(value=False)
        self.stroke_width = tk.IntVar(value=0)
        self.stroke_color = (0, 0, 0)
        
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.create_widgets()
        self.setup_drag_drop()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="图片批量水印工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="水印文字:").pack(anchor=tk.W)
        text_entry = ttk.Entry(main_frame, textvariable=self.watermark_text, font=("Arial", 12), width=40)
        text_entry.pack(fill=tk.X, pady=(0, 15))
        
        settings_frame = ttk.LabelFrame(main_frame, text="水印设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(settings_frame, text="字体大小:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        size_spin = ttk.Spinbox(settings_frame, from_=12, to=120, textvariable=self.font_size, width=10)
        size_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="透明度:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        opacity_scale = ttk.Scale(settings_frame, from_=10, to=255, variable=self.opacity, orient=tk.HORIZONTAL, length=100)
        opacity_scale.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="颜色:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        color_btn = ttk.Button(settings_frame, text="选择颜色", command=self.choose_color)
        color_btn.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="位置:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        position_combo = ttk.Combobox(settings_frame, textvariable=self.position, state="readonly", width=15)
        position_combo['values'] = ("top-left", "top-right", "bottom-left", "bottom-right", "center")
        position_combo.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        style_frame = ttk.LabelFrame(main_frame, text="文字样式", padding="10")
        style_frame.pack(fill=tk.X, pady=(0, 15))
        
        bold_check = ttk.Checkbutton(style_frame, text="加粗", variable=self.bold)
        bold_check.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(style_frame, text="描边宽度:").grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        stroke_spin = ttk.Spinbox(style_frame, from_=0, to=10, textvariable=self.stroke_width, width=8)
        stroke_spin.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        stroke_color_btn = ttk.Button(style_frame, text="描边颜色", command=self.choose_stroke_color)
        stroke_color_btn.grid(row=0, column=3, sticky=tk.W, padx=10, pady=5)
        
        self.drop_area = tk.Label(main_frame, text="拖拽图片到此处\n\n支持 JPG, PNG, BMP 格式", 
                                 font=("Arial", 14), bg="#e0e0e0", fg="#666666",
                                 height=6, relief=tk.RIDGE, bd=2)
        self.drop_area.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.status_label = ttk.Label(main_frame, text="等待拖拽图片...", foreground="blue")
        self.status_label.pack(anchor=tk.W)
        
    def setup_drag_drop(self):
        self.drop_area.bind('<Enter>', lambda e: self.drop_area.configure(bg="#d0d0ff"))
        self.drop_area.bind('<Leave>', lambda e: self.drop_area.configure(bg="#e0e0e0"))
        
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)
        
    def choose_color(self):
        color = colorchooser.askcolor(title="选择水印颜色", color=self.watermark_color)
        if color[0]:
            self.watermark_color = tuple(map(int, color[0]))
            
    def choose_stroke_color(self):
        color = colorchooser.askcolor(title="选择描边颜色", color=self.stroke_color)
        if color[0]:
            self.stroke_color = tuple(map(int, color[0]))
            
    def on_drop(self, event):
        files = self.root.splitlist(event.data)
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        if not image_files:
            messagebox.showwarning("警告", "没有找到有效的图片文件!")
            return
            
        self.process_images(image_files)
        
    def process_images(self, image_files):
        total = len(image_files)
        success_count = 0
        
        for i, img_path in enumerate(image_files, 1):
            self.status_label.config(text=f"正在处理: {i}/{total} - {os.path.basename(img_path)}")
            self.root.update()
            
            try:
                self.add_watermark(img_path)
                success_count += 1
            except Exception as e:
                messagebox.showerror("错误", f"处理 {os.path.basename(img_path)} 失败:\n{str(e)}")
        
        self.status_label.config(text=f"完成! 成功处理 {success_count}/{total} 张图片，保存到 output 文件夹")
        messagebox.showinfo("完成", f"成功处理 {success_count} 张图片!\n保存到: {os.path.abspath(self.output_dir)}")
        
    def get_chinese_font(self, size, bold=False):
        if bold:
            font_paths = [
                "C:/Windows/Fonts/msyhbd.ttc",
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simsun.ttc",
                "/System/Library/Fonts/PingFang.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            ]
        else:
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/simsun.ttc",
                "C:/Windows/Fonts/msyhbd.ttc",
                "/System/Library/Fonts/PingFang.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            ]
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
        return ImageFont.load_default()
    
    def add_watermark(self, img_path):
        image = Image.open(img_path).convert("RGBA")
        txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        
        draw = ImageDraw.Draw(txt_layer)
        text = self.watermark_text.get()
        
        font = self.get_chinese_font(self.font_size.get(), self.bold.get())
            
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        width, height = image.size
        pos = self.calculate_position(width, height, text_width, text_height)
        
        r, g, b = self.watermark_color
        sr, sg, sb = self.stroke_color
        
        if self.stroke_width.get() > 0:
            draw.text(pos, text, font=font, fill=(r, g, b, self.opacity.get()),
                     stroke_width=self.stroke_width.get(),
                     stroke_fill=(sr, sg, sb, self.opacity.get()))
        else:
            draw.text(pos, text, font=font, fill=(r, g, b, self.opacity.get()))
        
        result = Image.alpha_composite(image, txt_layer)
        
        filename = os.path.basename(img_path)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(self.output_dir, f"{name}.png")
        
        if ext.lower() in ('.jpg', '.jpeg'):
            result = result.convert("RGB")
            output_path = os.path.join(self.output_dir, f"{name}.jpg")
            
        result.save(output_path)
        
    def calculate_position(self, img_w, img_h, txt_w, txt_h):
        margin = 20
        pos_map = {
            "top-left": (margin, margin),
            "top-right": (img_w - txt_w - margin, margin),
            "bottom-left": (margin, img_h - txt_h - margin),
            "bottom-right": (img_w - txt_w - margin, img_h - txt_h - margin),
            "center": ((img_w - txt_w) // 2, (img_h - txt_h) // 2)
        }
        return pos_map.get(self.position.get(), pos_map["bottom-right"])

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = WatermarkTool(root)
    root.mainloop()
