import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from jmcomic import JmOption, download_album
import logging
import threading

class JmDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("JM漫画下载器")
        
        # 初始化配置系统
        self.config_path = self.get_config_path()
        self.option = self.load_config()
        
        # 构建界面
        self.create_ui()
        self.center_window(400, 200)  # 缩小窗口尺寸

    def get_config_path(self):
        """获取配置文件路径"""
        documents = os.path.join(os.environ['USERPROFILE'], 'Documents')
        config_dir = os.path.join(documents, 'JMconfig')
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'option.yml')

    def load_config(self):
        """简化版配置加载"""
        try:
            if os.path.exists(self.config_path):
                return JmOption.from_file(self.config_path)
            return self.create_default_config()
        except Exception as e:
            logging.error(f"配置加载失败: {e}")
            messagebox.showerror("错误", f"配置加载失败:\n{str(e)}")
            sys.exit(1)

    def create_default_config(self):
        """使用完整默认配置并修改下载路径"""
        try:
            # 生成完整默认配置
            option = JmOption.default()
            
            # 设置下载路径（保持原有简化逻辑）
            download_dir = os.path.join(os.environ['USERPROFILE'], 'Downloads')
            
            # 更新路径配置
            option.dir_rule.base_dir = download_dir
            option.download.download_dir = download_dir
            
            # 保存修改后的配置
            option.to_file(self.config_path)
            return option
        except Exception as e:
            logging.error(f"默认配置创建失败: {e}")
            messagebox.showerror("错误", f"无法创建默认配置:\n{str(e)}")
            sys.exit(1)

    def create_ui(self):
        """简化界面布局"""
        main_frame = ttk.Frame(self.master)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # 路径设置
        self.path_var = tk.StringVar(value=self.option.dir_rule.base_dir)
        path_frame = ttk.LabelFrame(main_frame, text="下载路径")
        path_frame.pack(fill=tk.X, pady=10)
        
        ttk.Entry(path_frame, textvariable=self.path_var).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(
            path_frame,
            text="浏览",
            command=self.update_save_path,
            width=8
        ).pack(side=tk.LEFT)
        
        # 下载控制
        task_frame = ttk.LabelFrame(main_frame, text="下载任务")
        task_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(task_frame, text="本子ID:").pack(side=tk.LEFT)
        self.album_id_var = tk.StringVar()
        ttk.Entry(task_frame, textvariable=self.album_id_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            task_frame,
            text="开始下载",
            command=self.start_download,
            width=10
        ).pack(side=tk.RIGHT)

    def update_save_path(self):
        """更新保存路径"""
        new_path = filedialog.askdirectory(initialdir=self.path_var.get())
        if new_path:
            self.path_var.set(new_path)
            self.option.dir_rule.base_dir = new_path
            self.option.download.download_dir = new_path
            self.save_config()

    def save_config(self):
        """简化保存逻辑"""
        try:
            self.option.to_file(self.config_path)
            logging.info("配置保存成功")
        except Exception as e:
            logging.error(f"保存失败: {e}")
            messagebox.showerror("错误", f"配置保存失败:\n{str(e)}")

    def start_download(self):
        """启动下载流程"""
        album_id = self.album_id_var.get().strip()
        if not album_id.isdigit():
            messagebox.showerror("错误", "本子ID必须为纯数字")
            return
        
        progress = self.show_progress()
        threading.Thread(
            target=self.execute_download,
            args=(album_id, progress),
            daemon=True
        ).start()

    def show_progress(self):
        """显示进度窗口"""
        win = tk.Toplevel(self.master)
        win.title("下载进度")
        ttk.Label(win, text="正在下载中，请稍候...").pack(pady=10)
        pb = ttk.Progressbar(win, mode='indeterminate')
        pb.pack(padx=20, pady=5)
        pb.start()
        return win

    def execute_download(self, album_id, progress):
        """执行下载任务"""
        try:
            download_album(album_id, option=self.option)
            self.master.after(0, lambda: self.on_success(progress, album_id))
        except Exception as e:
            self.master.after(0, lambda: self.on_error(progress, str(e)))

    def on_success(self, progress, album_id):
        """下载成功处理"""
        progress.destroy()
        messagebox.showinfo("完成", f"本子{album_id}下载成功！\n保存路径：{self.path_var.get()}")

    def on_error(self, progress, error):
        """下载失败处理"""
        progress.destroy()
        messagebox.showerror("错误", 
            f"下载失败:\n{error}\n\n"
            "可能原因：\n"
            "1. ID输入错误\n"
            "2. 网络连接问题\n"
            "3. 需要检查代理设置"
        )

    def center_window(self, width, height):
        """窗口居中"""
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.master.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    app = JmDownloaderApp(root)
    root.mainloop()