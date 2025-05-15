import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from PIL import Image, ImageTk, ImageDraw, ImageFont
import math
from ttkbootstrap.tooltip import ToolTip
import io
import base64
from urllib.request import urlopen
from urllib.error import URLError

class MCQGradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phần Mềm Chấm Thi Trắc Nghiệm - HUMG")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Thiết lập style
        self.style = ttk.Style("cosmo")
        
        # Biến để lưu trữ đường dẫn và dữ liệu
        self.answer_key_path = None
        self.exam_image_path = None
        self.result_image = None
        self.answer_key_image = None
        self.answer_key_list = None
        self.student_answer_list = None
        self.answer_key_mdt = None
        self.student_mdt = None
        self.student_sbd = None
        self.score = None
        self.correct_count = 0
        self.total_questions = 0
        self.result_file_path = None
        
        # Tạo thanh menu
        self.create_menu()
        
        # Tạo frame chính
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # Frame bên trái - Bảng điều khiển
        left_frame = ttk.LabelFrame(main_frame, text="BẢNG ĐIỀU KHIỂN", padding=10)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 5), pady=5)
        
        # Thêm tên trường vào frame bên trái
        self.add_university_name(left_frame)
        
        # Các nút chức năng bên trái
        self.create_control_panel(left_frame)
        
        # Thêm frame thống kê
        stats_frame = ttk.LabelFrame(left_frame, text="THỐNG KÊ", padding=10)
        stats_frame.pack(fill=X, pady=(10, 0), padx=0)
        
        self.stats_label = ttk.Label(stats_frame, text="Số đáp án mẫu: 0\nSố bài đã chấm: 0")
        self.stats_label.pack(pady=5)
        
        # Frame bên phải - Hiển thị kết quả
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=0, pady=5)
        
        # Notebook cho các tab
        self.tab_control = ttk.Notebook(right_frame)
        self.tab_control.pack(fill=BOTH, expand=YES)
        
        # Tab kết quả
        self.result_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.result_tab, text="Kết Quả")
        
        # Tab xem trước
        self.preview_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.preview_tab, text="Xem Trước")
        
        # Thiết lập tab kết quả
        self.setup_result_tab()
        
        # Thiết lập tab xem trước
        self.setup_preview_tab()
        
        # Thanh trạng thái
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=5)
        self.status_bar.pack(side=BOTTOM, fill=X)
    
    def add_university_name(self, parent):
        """Thêm tên trường đại học vào giao diện"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=X, pady=(0, 10))
        
        # Tạo một header có tên trường
        label_text = ttk.Label(
            header_frame, 
            text="TRƯỜNG ĐẠI HỌC MỎ - ĐỊA CHẤT",
            font=("Segoe UI", 10, "bold"),
            foreground="#005AA9"  # Màu xanh dương đặc trưng của HUMG
        )
        label_text.pack(pady=10)
        
        # Thêm dòng phân cách
        separator = ttk.Separator(header_frame, orient='horizontal')
        separator.pack(fill=X, pady=5)
    
    def create_menu(self):
        """Tạo thanh menu"""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # Menu File
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Tệp", menu=file_menu)
        file_menu.add_command(label="Quét Đáp Án Mẫu", command=self.select_answer_key)
        file_menu.add_command(label="Chấm Điểm Bài Thi", command=self.select_exam_image)
        file_menu.add_separator()
        file_menu.add_command(label="Lưu Kết Quả", command=self.save_result)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.root.destroy)
        
        # Menu Help
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Trợ Giúp", menu=help_menu)
        help_menu.add_command(label="Hướng Dẫn", command=self.show_help)
        help_menu.add_command(label="Giới Thiệu", command=self.show_about)
    
    def create_control_panel(self, parent):
        """Tạo các nút điều khiển"""
        # Nút quét đáp án
        scan_btn = ttk.Button(
            parent,
            text="Quét Đáp Án Mẫu",
            command=self.select_answer_key,
            width=20,
            style="success.TButton"
        )
        scan_btn.pack(pady=5, fill=X)
        
        # Nút xem đáp án đã lưu
        view_btn = ttk.Button(
            parent,
            text="Xem Đáp Án Đã Lưu",
            command=self.view_answer_key,
            width=20,
            style="info.TButton"
        )
        view_btn.pack(pady=5, fill=X)
        
        # Nút chấm điểm
        grade_btn = ttk.Button(
            parent,
            text="Chấm Điểm Bài Thi",
            command=self.select_exam_image,
            width=20,
            style="primary.TButton"
        )
        grade_btn.pack(pady=5, fill=X)
        
        # Thêm nút lưu kết quả
        save_btn = ttk.Button(
            parent,
            text="Lưu Ảnh Kết Quả",
            command=self.save_result,
            width=20,
            style="warning.TButton"
        )
        save_btn.pack(pady=5, fill=X)
        # Thêm tooltip cho nút lưu
        ToolTip(save_btn, "Lưu ảnh bài thi đã chấm xuống máy")
    
    def setup_result_tab(self):
        """Thiết lập tab hiển thị kết quả"""
        # Frame cho tiêu đề kết quả
        title_frame = ttk.Frame(self.result_tab, padding=10)
        title_frame.pack(fill=X)
        
        self.result_title = ttk.Label(
            title_frame, 
            text="KẾT QUẢ CHẤM THI",
            font=("Segoe UI", 12, "bold")
        )
        self.result_title.pack(anchor=W)
        
        # Đường kẻ phân cách
        separator = ttk.Separator(self.result_tab, orient='horizontal')
        separator.pack(fill=X, padx=10, pady=5)
        
        # Frame cho thông tin kết quả
        info_frame = ttk.Frame(self.result_tab, padding=10)
        info_frame.pack(fill=X)
        
        # Các label thông tin
        self.sbd_label = ttk.Label(info_frame, text="Số Báo Danh: ", font=("Segoe UI", 10))
        self.sbd_label.pack(anchor=W, pady=2)
        
        self.mdt_label = ttk.Label(info_frame, text="Mã Đề Thi: ", font=("Segoe UI", 10))
        self.mdt_label.pack(anchor=W, pady=2)
        
        self.score_label = ttk.Label(info_frame, text="Điểm Số: ", font=("Segoe UI", 10))
        self.score_label.pack(anchor=W, pady=2)
        
        self.correct_label = ttk.Label(info_frame, text="Số Câu Đúng: ", font=("Segoe UI", 10))
        self.correct_label.pack(anchor=W, pady=2)
        
        # Đường kẻ phân cách
        separator2 = ttk.Separator(self.result_tab, orient='horizontal')
        separator2.pack(fill=X, padx=10, pady=5)
        
        # Frame cho chi tiết từng câu
        detail_frame = ttk.Frame(self.result_tab, padding=10)
        detail_frame.pack(fill=BOTH, expand=YES)
        
        detail_label = ttk.Label(detail_frame, text="Chi tiết câu trả lời:", font=("Segoe UI", 10, "bold"))
        detail_label.pack(anchor=W, pady=(0, 5))
        
        # Scrolled text để hiển thị chi tiết
        self.detail_text = tk.Text(detail_frame, height=20, width=50)
        self.detail_text.pack(fill=BOTH, expand=YES, side=LEFT)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(detail_frame, command=self.detail_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.detail_text.config(yscrollcommand=scrollbar.set)
        self.detail_text.config(state=tk.DISABLED)
    
    def setup_preview_tab(self):
        """Thiết lập tab xem trước"""
        preview_frame = ttk.Frame(self.preview_tab, padding=10)
        preview_frame.pack(fill=BOTH, expand=YES)
        
        # Canvas để hiển thị ảnh
        self.canvas = tk.Canvas(preview_frame, bg="lightgray", cursor="hand2")
        self.canvas.pack(fill=BOTH, expand=YES)
        
        # Binding các sự kiện chuột cho di chuyển ảnh
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", lambda e: self.on_mousewheel(e, 1))  # Linux scroll up
        self.canvas.bind("<Button-5>", lambda e: self.on_mousewheel(e, -1))  # Linux scroll down
        
        # Thanh công cụ
        toolbar = ttk.Frame(preview_frame)
        toolbar.pack(fill=X, pady=(5, 0))
        
        # Nút zoom
        self.zoom_in_btn = ttk.Button(toolbar, text="Phóng to (+)", command=lambda: self.zoom(1.2))
        self.zoom_in_btn.pack(side=LEFT, padx=5)
        
        self.zoom_out_btn = ttk.Button(toolbar, text="Thu nhỏ (-)", command=lambda: self.zoom(0.8))
        self.zoom_out_btn.pack(side=LEFT, padx=5)
        
        self.zoom_reset_btn = ttk.Button(toolbar, text="Khôi phục (100%)", command=self.reset_zoom)
        self.zoom_reset_btn.pack(side=LEFT, padx=5)
        
        # Thêm label hướng dẫn
        hint_label = ttk.Label(toolbar, text="Giữ chuột trái để di chuyển khi phóng to", font=("Segoe UI", 9, "italic"))
        hint_label.pack(side=LEFT, padx=20)
        
        # Biến lưu trữ thông tin zoom và kéo
        self.zoom_factor = 1.0
        self.current_image = None
        self.tk_image = None
        self.img_width = 0
        self.img_height = 0
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.pan_x = 0
        self.pan_y = 0
        self.is_dragging = False
    
    def process_answer_sheet(self, answer_image):
        """Xử lý ảnh đáp án để trích xuất các đáp án"""
        try:
            # Kiểm tra ảnh đầu vào
            if answer_image is None or answer_image.size == 0:
                raise Exception("Ảnh đáp án không hợp lệ hoặc rỗng")
                
            image_height, image_width, _ = answer_image.shape

            # Vùng cắt theo 4 cột như trong phương thức grade_exam
            crop_regions = [
                (0, 790, 448, 2555),      # Câu 1-30
                (448, 790, 896, 2555),    # Câu 31-60
                (896, 790, 1344, 2555),   # Câu 61-90
                (1344, 790, 1792, 2555)   # Câu 91-120
            ]
            
            # Trích xuất mã đề thi từ ảnh đáp án
            crop_mdt = (int(1558), int(154), int(1726), int(821))
            # Kiểm tra xem vùng cắt có vượt quá kích thước ảnh không
            if (crop_mdt[2] > image_width or crop_mdt[3] > image_height):
                raise Exception(f"Kích thước ảnh không phù hợp: {image_width}x{image_height}. Cần ít nhất 1800x2600 pixels.")
                
            crop_img_mdt = answer_image[crop_mdt[1]:crop_mdt[3], crop_mdt[0]:crop_mdt[2]]
            mdt, _ = self.get_mdt_blue(crop_img_mdt)
            self.answer_key_mdt = ''.join(map(str, mdt))
            
            # Tạo một đáp án mẫu để trích xuất từ ảnh
            sample_answer_key = ["A", "B", "C", "D"] * 30
            
            all_answer_key = []
            
            # Xử lý từng vùng để trích xuất đáp án
            for idx, (x1, y1, x2, y2) in enumerate(crop_regions):
                # Kiểm tra vùng cắt 
                if x2 > image_width or y2 > image_height:
                    raise Exception(f"Kích thước ảnh không phù hợp. Vùng {idx+1} vượt quá kích thước ảnh.")
                    
                crop_img = answer_image[y1:y2, x1:x2]
                # Sử dụng chính phương thức get_result_trac_nghiem để phát hiện đáp án
                answers, _ = self.get_result_trac_nghiem(crop_img, sample_answer_key[idx * 30: (idx + 1) * 30])
                all_answer_key.extend(answers)
            
            # Lưu đáp án và mã đề thi
            self.answer_key_list = all_answer_key
            
            # Cập nhật thống kê sau khi đã lưu đáp án thành công
            self.update_stats()
            self.update_answer_key_display()
            
            return all_answer_key
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xử lý ảnh đáp án: {str(e)}")
            return None
    
    def update_answer_key_display(self):
        """Cập nhật hiển thị đáp án gốc lên giao diện"""
        if self.answer_key_list and self.answer_key_mdt:
            # Trong giao diện mới không còn key_mdt_label nữa
            # Chỉ cập nhật thống kê
            self.update_stats()
            
            # Cập nhật tab kết quả
            self.tab_control.select(self.result_tab)
    
    def update_student_answer_display(self):
        """Cập nhật hiển thị đáp án học sinh lên giao diện"""
        if self.student_answer_list and self.student_mdt:
            # Trong giao diện mới không còn các đối tượng này
            # Chỉ cập nhật thống kê
            self.update_stats()
            
            # Cập nhật tab kết quả
            self.tab_control.select(self.result_tab)
    
    def select_answer_key(self):
        """Chọn và quét đáp án mẫu"""
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh đáp án mẫu",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        self.answer_key_path = file_path
        self.status_var.set(f"Đang quét đáp án từ: {os.path.basename(file_path)}")
        self.root.update_idletasks()
        
        try:
            # Đọc ảnh đáp án
            img = cv2.imread(file_path)
            
            # Kiểm tra xem ảnh có được đọc thành công không
            if img is None or img.size == 0:
                raise Exception(f"Không thể đọc file ảnh. Đảm bảo file '{os.path.basename(file_path)}' không bị hỏng và có định dạng hỗ trợ.")
            
            # Resize ảnh về kích thước chuẩn
            img, was_resized = self.resize_image(img)
            if img is None:
                raise Exception("Không thể điều chỉnh kích thước ảnh.")
                
            if was_resized:
                messagebox.showinfo("Thông báo", "Ảnh đã được tự động điều chỉnh kích thước để phù hợp với yêu cầu nhận diện.")
                
            # Hiển thị ảnh trên tab xem trước
            self.display_image(cv_image=img)  # Thay vì dùng file_path, dùng ảnh đã resize
            
            # Xử lý và trích xuất đáp án
            answer_key = self.process_answer_sheet(img)
            
            if answer_key is None or len(answer_key) == 0:
                raise Exception("Không thể trích xuất đáp án từ ảnh.")
                
            self.answer_key_list = answer_key
            self.answer_key_image = img
            
            # Kiểm tra xem đáp án đã được lưu chưa
            if self.answer_key_list and len(self.answer_key_list) > 0:
                # Hiển thị thông báo thành công
                messagebox.showinfo("Thành công", f"Đã quét và xử lý đáp án mẫu thành công! Tìm thấy {len(self.answer_key_list)} câu.")
                self.status_var.set(f"Đã quét đáp án thành công từ: {os.path.basename(file_path)}")
            else:
                raise Exception("Không thể trích xuất đáp án từ ảnh hoặc không có đáp án nào được tìm thấy.")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi quét đáp án: {str(e)}")
            self.status_var.set("Có lỗi xảy ra khi quét đáp án")
    
    def view_answer_key(self):
        """Xem đáp án đã lưu"""
        if self.answer_key_list is None or len(self.answer_key_list) == 0:
            messagebox.showwarning("Cảnh báo", "Chưa có đáp án mẫu nào được quét!")
            return
        
        # Hiển thị đáp án trong một cửa sổ mới
        answer_window = tk.Toplevel(self.root)
        answer_window.title("Đáp Án Mẫu")
        answer_window.geometry("400x500")
        
        frame = ttk.Frame(answer_window, padding=20)
        frame.pack(fill=BOTH, expand=YES)
        
        ttk.Label(frame, text="ĐÁP ÁN MẪU", font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))
        
        # Kiểm tra xem có mã đề thi không
        if hasattr(self, 'answer_key_mdt') and self.answer_key_mdt:
            ttk.Label(frame, text=f"Mã đề thi: {self.answer_key_mdt}", font=("Segoe UI", 10)).pack(pady=5)
        else:
            ttk.Label(frame, text="Không có mã đề thi", font=("Segoe UI", 10)).pack(pady=5)
        
        # Tạo text widget để hiển thị đáp án
        text_widget = tk.Text(frame, height=20, width=30)
        text_widget.pack(fill=BOTH, expand=YES, side=LEFT)
        
        scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Hiển thị đáp án
        for i, answer in enumerate(self.answer_key_list):
            text_widget.insert(tk.END, f"Câu {i+1}: {answer}\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def select_exam_image(self):
        """Chọn và quét bài thi"""
        if self.answer_key_list is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng quét đáp án mẫu trước!")
            return
            
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh bài thi cần chấm",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        self.exam_image_path = file_path
        self.status_var.set(f"Đang chấm bài thi từ: {os.path.basename(file_path)}")
        self.root.update_idletasks()
        
        try:
            # Đọc ảnh bài thi và kiểm tra
            img = cv2.imread(file_path)
            if img is None or img.size == 0:
                raise Exception(f"Không thể đọc file ảnh. Đảm bảo file '{os.path.basename(file_path)}' không bị hỏng và có định dạng hỗ trợ.")
                
            # Resize ảnh về kích thước chuẩn
            img, was_resized = self.resize_image(img)
            if img is None:
                raise Exception("Không thể điều chỉnh kích thước ảnh.")
                
            if was_resized:
                messagebox.showinfo("Thông báo", "Ảnh bài thi đã được tự động điều chỉnh kích thước để phù hợp với yêu cầu nhận diện.")
                
            # Chấm điểm bài thi
            self.grade_exam(img)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi chấm bài thi: {str(e)}")
            self.status_var.set("Có lỗi xảy ra khi chấm bài thi")
    
    def display_image(self, image_path=None, cv_image=None):
        """Hiển thị ảnh lên canvas"""
        # Chuyển tab sang xem trước
        self.tab_control.select(self.preview_tab)
        
        if image_path:
            # Đọc ảnh từ file
            self.current_image = Image.open(image_path)
        elif cv_image is not None:
            # Chuyển từ OpenCV sang PIL
            cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            self.current_image = Image.fromarray(cv_image_rgb)
        else:
            return
        
        # Lưu kích thước gốc
        self.img_width, self.img_height = self.current_image.size
        
        # Reset zoom
        self.zoom_factor = 1.0
        
        # Hiển thị ảnh
        self.update_image_display()
    
    def update_image_display(self):
        """Cập nhật hiển thị ảnh với tỷ lệ zoom"""
        if self.current_image is None:
            return
            
        # Lấy kích thước canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas chưa được render
            self.root.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
        
        # Tính toán tỷ lệ để vừa với canvas
        width = int(self.img_width * self.zoom_factor)
        height = int(self.img_height * self.zoom_factor)
        
        # Nếu là lần đầu hiển thị, tự động điều chỉnh để vừa với canvas
        if self.zoom_factor == 1.0 and self.pan_x == 0 and self.pan_y == 0:
            scale = min(canvas_width / self.img_width, canvas_height / self.img_height)
            if scale < 1:
                width = int(self.img_width * scale)
                height = int(self.img_height * scale)
                self.zoom_factor = scale
        
        # Resize ảnh
        resized_image = self.current_image.resize((width, height), Image.LANCZOS)
        
        # Chuyển sang định dạng Tkinter
        self.tk_image = ImageTk.PhotoImage(resized_image)
        
        # Xóa canvas và hiển thị ảnh mới
        self.canvas.delete("all")
        
        # Lưu lại ID của ảnh để có thể di chuyển sau này
        self.drag_data["item"] = self.canvas.create_image(
            canvas_width // 2 + self.pan_x, 
            canvas_height // 2 + self.pan_y, 
            image=self.tk_image, 
            anchor=tk.CENTER
        )
    
    def load_answer_key(self):
        """Đọc đáp án từ file hoặc từ bộ nhớ"""
        if not self.answer_key_path:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file đáp án trước!")
            return None
        
        # Nếu đã có đáp án trong bộ nhớ, trả về ngay
        if self.answer_key_list is not None:
            return self.answer_key_list
        
        # Nếu file đáp án là hình ảnh và đã được xử lý
        if hasattr(self, 'answer_key_image') and self.answer_key_image is not None:
            # Trả về đáp án đã xử lý từ ảnh
            return self.process_answer_sheet(self.answer_key_image)
        
        # Nếu là file text
        try:
            with open(self.answer_key_path, 'r') as file:
                content = file.read().strip()
                # Xử lý đáp án từ file, ví dụ: "ABCD,ABCD,..."
                answers = content.replace(" ", "").replace("\n", "").split(",")
                answer_key = []
                for ans in answers:
                    answer_key.extend(list(ans))
                
                # Lưu vào bộ nhớ để sử dụng sau này
                self.answer_key_list = answer_key
                return answer_key
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file đáp án: {str(e)}")
            return None
    
    def grade_exam(self, img=None):
        """Chấm điểm bài thi"""
        if not self.exam_image_path and img is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ảnh bài thi trước!")
            return
        
        try:
            # Hiển thị dialog tiến trình
            progress_window = ttk.Toplevel(self.root)
            progress_window.title("Đang chấm bài...")
            progress_window.geometry("300x100")
            
            progress_frame = ttk.Frame(progress_window, padding=20)
            progress_frame.pack(fill=BOTH, expand=YES)
            
            ttk.Label(progress_frame, text="Đang chấm bài thi...").pack(pady=(0, 10))
            
            progressbar = ttk.Progressbar(progress_frame, mode="indeterminate")
            progressbar.pack(fill=X)
            progressbar.start(10)
            
            progress_window.update()
            
            # Nếu img chưa được truyền vào, đọc từ đường dẫn
            if img is None:
                img = cv2.imread(self.exam_image_path)
                if img is None:
                    raise Exception("Không thể đọc file ảnh bài thi")
            
            # Vùng cắt theo 4 cột
            crop_regions = [
                (0, 790, 448, 2555),      # Câu 1-30
                (448, 790, 896, 2555),    # Câu 31-60
                (896, 790, 1344, 2555),   # Câu 61-90
                (1344, 790, 1792, 2555)   # Câu 91-120
            ]
            
            # Trích xuất SBD và MDT
            crop_sbd = (int(1281), int(154), int(1550), int(821))
            crop_img_sbd = img[crop_sbd[1]:crop_sbd[3], crop_sbd[0]:crop_sbd[2]]
            sbd, _ = self.get_sbd_blue(crop_img_sbd)
            self.student_sbd = ''.join(map(str, sbd))
            
            crop_mdt = (int(1558), int(154), int(1726), int(821))
            crop_img_mdt = img[crop_mdt[1]:crop_mdt[3], crop_mdt[0]:crop_mdt[2]]
            mdt, _ = self.get_mdt_blue(crop_img_mdt)
            self.student_mdt = ''.join(map(str, mdt))
            
            # Kiểm tra xem mã đề thi có khớp với đáp án mẫu không
            if hasattr(self, 'answer_key_mdt') and self.answer_key_mdt and self.student_mdt:
                if self.student_mdt != self.answer_key_mdt:
                    progress_window.destroy()
                    messagebox.showwarning("Cảnh báo", 
                                          f"Mã đề thi không khớp!\n" +
                                          f"Mã đề thi của bài làm: {self.student_mdt}\n" +
                                          f"Mã đề thi của đáp án mẫu: {self.answer_key_mdt}\n\n" +
                                          "Không thể chấm điểm khi mã đề thi không khớp!")
                    
                    # Vẫn hiển thị ảnh và thông tin sinh viên, nhưng không chấm điểm
                    self.display_image(cv_image=img)
                    self.result_image = img
                    
                    # Cập nhật thông tin trong tab kết quả
                    self.sbd_label.config(text=f"Số Báo Danh: {self.student_sbd}")
                    self.mdt_label.config(text=f"Mã Đề Thi: {self.student_mdt} (KHÔNG KHỚP với đáp án mẫu: {self.answer_key_mdt})")
                    self.score_label.config(text="Điểm Số: Không chấm điểm do mã đề không khớp")
                    self.correct_label.config(text="Số Câu Đúng: N/A")
                    
                    # Xóa nội dung chi tiết câu trả lời
                    self.detail_text.config(state=tk.NORMAL)
                    self.detail_text.delete(1.0, tk.END)
                    self.detail_text.insert(tk.END, "Không thể chấm điểm do mã đề thi không khớp với đáp án mẫu.", "error")
                    self.detail_text.tag_configure("error", foreground="red", font=("Segoe UI", 10, "bold"))
                    self.detail_text.config(state=tk.DISABLED)
                    
                    # Hiển thị tab kết quả
                    self.tab_control.select(self.result_tab)
                    
                    self.status_var.set("Không thể chấm điểm: Mã đề thi không khớp")
                    return
            
            # Trích xuất đáp án của học sinh
            all_student_answers = []
            for idx, (x1, y1, x2, y2) in enumerate(crop_regions):
                crop_img = img[y1:y2, x1:x2]
                ans, processed_img = self.get_result_trac_nghiem(crop_img, self.answer_key_list[idx * 30: (idx + 1) * 30])
                all_student_answers.extend(ans)
                
                # Vẽ khung vùng nhận diện lên ảnh gốc
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
                img[y1:y2, x1:x2] = processed_img
            
            # Kiểm tra và điều chỉnh độ dài
            if len(all_student_answers) < len(self.answer_key_list):
                all_student_answers.extend(["N"] * (len(self.answer_key_list) - len(all_student_answers)))
            
            # Tính điểm
            grading = [1 if str(self.answer_key_list[x]) == str(all_student_answers[x]) else 0 
                       for x in range(len(self.answer_key_list))]
            
            self.correct_count = sum(grading)
            self.total_questions = len(grading)
            self.score = round((10.0 / self.total_questions) * self.correct_count, 2)
            
            # Hiện điểm lên ảnh - Sử dụng phương pháp tô màu nền thay vì putText trực tiếp
            text_bg = np.zeros((250, 800, 3), dtype=np.uint8)
            text_bg[:] = (240, 240, 240)  # Màu nền xám nhạt
            
            # Tạo hình ảnh tạm thời với PIL để hỗ trợ tiếng Việt
            pil_img = Image.fromarray(text_bg)
            draw = ImageDraw.Draw(pil_img)
            
            # Sử dụng PIL để vẽ text có dấu tiếng Việt
            try:
                # Nếu font có sẵn, sử dụng nó
                font = ImageFont.truetype("arial.ttf", 60)
                draw.text((50, 40), f"Điểm: {self.score}/10", fill=(0, 0, 255), font=font)
                draw.text((50, 110), f"SBD: {self.student_sbd}", fill=(0, 100, 0), font=font)
                draw.text((50, 180), f"MDT: {self.student_mdt}", fill=(200, 0, 0), font=font)
            except:
                # Nếu không có font, sử dụng font mặc định
                draw.text((50, 40), f"Diem: {self.score}/10", fill=(0, 0, 255))
                draw.text((50, 110), f"SBD: {self.student_sbd}", fill=(0, 100, 0))
                draw.text((50, 180), f"MDT: {self.student_mdt}", fill=(200, 0, 0))
            
            # Chuyển từ PIL sang OpenCV
            text_bg = np.array(pil_img)
            text_bg = cv2.cvtColor(text_bg, cv2.COLOR_RGB2BGR)
            
            # Chèn background vào ảnh gốc
            roi = img[50:300, 50:850]
            cv2.addWeighted(text_bg, 0.9, roi, 0.1, 0, roi)
            
            # Lưu kết quả
            self.result_image = img
            self.student_answer_list = all_student_answers
            
            # Đóng dialog tiến trình
            progress_window.destroy()
            
            # Hiển thị kết quả
            self.display_image(cv_image=img)
            self.display_results(all_student_answers, grading)
            
            # Cập nhật thống kê
            self.update_stats()
            
            # Hiển thị tab kết quả
            self.tab_control.select(self.result_tab)
            
            self.status_var.set(f"Chấm bài thi hoàn tất. Điểm: {self.score}/10")
            
        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi chấm điểm: {str(e)}")
            self.status_var.set("Có lỗi xảy ra khi chấm điểm")
    
    def display_results(self, student_answers, grading):
        """Hiển thị kết quả chấm điểm trên giao diện"""
        # Cập nhật các label thông tin
        self.sbd_label.config(text=f"Số Báo Danh: {self.student_sbd}")
        self.mdt_label.config(text=f"Mã Đề Thi: {self.student_mdt}")
        self.score_label.config(text=f"Điểm Số: {self.score}/10")
        self.correct_label.config(text=f"Số Câu Đúng: {self.correct_count}/{self.total_questions}")
        
        # Hiển thị chi tiết từng câu
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        
        self.detail_text.insert(tk.END, "Chi tiết câu trả lời:\n", "header")
        
        for i in range(len(self.answer_key_list)):
            answer_key = self.answer_key_list[i]
            student_answer = student_answers[i]
            is_correct = grading[i] == 1
            
            result_text = f"Câu {i+1}: "
            if is_correct:
                result_text += "✓ "
                tag = f"correct_{i}"
            else:
                result_text += "✗ "
                tag = f"wrong_{i}"
                
            result_text += f"(Đáp án: {answer_key}, Trả lời: {student_answer})\n"
            
            self.detail_text.insert(tk.END, result_text, tag)
            
            # Định dạng màu
            if is_correct:
                self.detail_text.tag_configure(tag, foreground="green")
            else:
                self.detail_text.tag_configure(tag, foreground="red")
        
        self.detail_text.tag_configure("header", font=("Segoe UI", 10, "bold"))
        self.detail_text.config(state=tk.DISABLED)
    
    def save_result(self):
        """Lưu kết quả chấm điểm"""
        if self.result_image is None:
            messagebox.showwarning("Cảnh báo", "Chưa có kết quả chấm thi để lưu!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Lưu kết quả chấm thi",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Lưu ảnh kết quả
            cv2.imwrite(file_path, self.result_image)
            self.result_file_path = file_path
            
            messagebox.showinfo("Thành công", f"Đã lưu kết quả chấm thi tại:\n{file_path}")
            self.status_var.set(f"Đã lưu kết quả chấm thi tại: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {str(e)}")
            self.status_var.set("Có lỗi xảy ra khi lưu kết quả")
    
    def get_result_trac_nghiem(self, image_trac_nghiem, ANSWER_KEY):
        """Nhận diện kết quả trắc nghiệm từ ảnh"""
        try:
            # Kiểm tra ảnh đầu vào
            if image_trac_nghiem is None or image_trac_nghiem.size == 0:
                return [], image_trac_nghiem
                
            translate = {"A": 0, "B": 1, "C": 2, "D": 3}
            revert_translate = {0: "A", 1: "B", 2: "C", 3: "D", -1: "N"}
            
            image = image_trac_nghiem.copy()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            
            # Khôi phục thông số gốc cho việc phát hiện hình tròn
            circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                    param1=50, param2=29, minRadius=12, maxRadius=30)
            
            questionCnts = []
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                    questionCnts.append((x, y, r))
            
            if len(questionCnts) == 0:
                self.status_var.set("❌ Không tìm thấy đủ ô tròn! Hãy kiểm tra ảnh đầu vào.")
                return [], image
    
            questionCnts = sorted(questionCnts, key=lambda c: (c[1], c[0]))

            contours_list = [np.array([[[x - r, y - r]], [[x + r, y - r]], [[x + r, y + r]], [[x - r, y + r]]], dtype=np.int32)
                            for (x, y, r) in questionCnts]

            threshold_image = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                    cv2.THRESH_BINARY_INV, 15, 8)
            select = []
            list_min_black = []
            min_black = float("inf")
            
            # Tính ngưỡng cho từng nhóm câu hỏi
            for i in range(0, len(contours_list), 4):
                if i + 4 > len(contours_list):
                    break
                cnts = sorted(contours_list[i:i + 4], key=lambda c: cv2.boundingRect(c)[0])
                group_min_black = float("inf")
                for c in cnts:
                    mask = np.zeros(threshold_image.shape, dtype="uint8")
                    cv2.drawContours(mask, [c], -1, 255, -1)
                    mask = cv2.bitwise_and(threshold_image, threshold_image, mask=mask)
                    total = cv2.countNonZero(mask)
                    group_min_black = min(group_min_black, total)
                list_min_black.append(group_min_black)
                min_black = min(min_black, group_min_black)
            
            if not list_min_black:
                list_min_black = [100] * (len(contours_list) // 20 + 1)
              
            for i in range(0, len(contours_list), 4):
                if i + 4 > len(contours_list):
                    break
                current_min_black = list_min_black[min(i // 20, len(list_min_black) - 1)]
                cnts = sorted(contours_list[i:i + 4], key=lambda c: cv2.boundingRect(c)[0])
                list_total = []
                total_max = -1
                
                for j, c in enumerate(cnts):
                    mask = np.zeros(threshold_image.shape, dtype="uint8")
                    cv2.drawContours(mask, [c], -1, 255, -1)
                    mask = cv2.bitwise_and(threshold_image, threshold_image, mask=mask)
                    total = cv2.countNonZero(mask)
                    total_max = max(total_max, total)
                    list_total.append((total, j))
                
                answer_q = [char for char in ANSWER_KEY[min(i // 4, len(ANSWER_KEY) - 1)]]
                list_answer = []
                list_select = ''
                
                # Sắp xếp theo giá trị total giảm dần
                list_total.sort(reverse=True)
                
                # Kết hợp ngưỡng tuyệt đối và ngưỡng tương đối
                # Sử dụng cả phương pháp mới và phương pháp gốc để nhận diện tốt hơn
                if list_total:
                    # Phương pháp 1: Lấy đáp án có điểm cao nhất vượt ngưỡng tuyệt đối
                    if list_total[0][0] > 30:  # Giảm ngưỡng xuống 30 pixel
                        highest_idx = list_total[0][1]
                        list_answer.append(highest_idx)
                        list_select = revert_translate[highest_idx]
                    
                    # Phương pháp 2: Ngưỡng tương đối với giá trị thấp hơn
                    # Nếu phương pháp 1 không tìm thấy đáp án, thử với ngưỡng tương đối
                    if not list_answer:
                        for tt in list_total:
                            # Giảm ngưỡng từ 1.5 xuống 1.2 và từ 0.7 xuống 0.5
                            if tt[0] > min(current_min_black * 1.2, 20) and tt[0] > total_max * 0.5:
                                list_answer.append(tt[1])
                                list_select += revert_translate[tt[1]]
                
                # Tô màu đáp án đúng luôn là màu xanh
                for answer in answer_q:
                    k = translate[answer]
                    cv2.drawContours(image, [cnts[k]], -1, (0, 255, 0), 3)
                
                # Tô màu các ô không được tô
                for j, c in enumerate(cnts):
                    if j not in list_answer:
                        cv2.drawContours(image, [c], -1, (0, 0, 255), 2)
                
                select.append(list_select)
            
            return select, image
            
        except Exception as e:
            self.status_var.set(f"Lỗi khi xử lý ảnh: {str(e)}")
            return [], image_trac_nghiem

    def get_sbd_blue(self, image):
        # Chuyển ảnh sang HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Xác định phạm vi màu xanh dương trong không gian HSV
        lower_blue = np.array([90, 50, 50])   # Giới hạn dưới của màu xanh
        upper_blue = np.array([130, 255, 255]) # Giới hạn trên của màu xanh

        # Tạo mặt nạ chỉ giữ lại các vùng có màu xanh dương
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Dùng HoughCircles để tìm hình tròn đã tô màu xanh
        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                param1=50, param2=15, minRadius=6, maxRadius=20)

        detected_numbers = []

        if circles is not None:
            circles = np.uint16(np.around(circles))  # Làm tròn giá trị
            for (x, y, r) in circles[0, :]:
                y = int(y)  # Chuyển sang kiểu `int`
                
                if y >= 100:  # Kiểm tra y có hợp lệ không
                    digit = (y - 100) // 50
                else:
                    digit = 0  # Giá trị mặc định nếu y không hợp lệ
                
                detected_numbers.append((x, digit))

                # Vẽ vòng tròn màu đỏ để kiểm tra nhận diện
                cv2.circle(image, (x, y), r, (0, 0, 255), 2)
                cv2.putText(image, str(digit), (x - 10, y + 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Sắp xếp số báo danh theo vị trí từ trái sang phải
        detected_numbers.sort(key=lambda x: x[0])
        sbd = "".join(str(num[1]) for num in detected_numbers)

        return sbd, image

    def get_mdt_blue(self, image):
        # Chuyển ảnh sang không gian màu HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Xác định phạm vi màu xanh dương trong không gian HSV
        lower_blue = np.array([90, 50, 50])   # Giới hạn dưới của màu xanh
        upper_blue = np.array([130, 255, 255]) # Giới hạn trên của màu xanh

        # Tạo mặt nạ chỉ giữ lại các vùng có màu xanh dương
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Dùng HoughCircles để tìm hình tròn đã tô màu xanh
        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                param1=50, param2=15, minRadius=8, maxRadius=45)

        detected_numbers = []

        if circles is not None:
            circles = np.uint16(np.around(circles))  # Làm tròn giá trị
            for (x, y, r) in circles[0, :]:
                y = int(y)  # Chuyển sang kiểu `int`
                
                if y >= 100:  # Kiểm tra y có hợp lệ không
                    digit = (y - 100) // 50  # Xác định số theo hàng
                else:
                    digit = 0  # Giá trị mặc định nếu y không hợp lệ
                
                detected_numbers.append((x, digit))

                # Vẽ vòng tròn màu đỏ để kiểm tra nhận diện
                cv2.circle(image, (x, y), r, (0, 0, 255), 2)
                cv2.putText(image, str(digit), (x - 10, y + 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Sắp xếp mã đề theo vị trí từ trái sang phải
        detected_numbers.sort(key=lambda x: x[0])
        mdt = "".join(str(num[1]) for num in detected_numbers)

        return mdt, image

    def on_mousewheel(self, event, direction=None):
        """Xử lý sự kiện cuộn chuột để zoom ảnh"""
        if direction is None:
            # Windows
            if event.delta > 0:
                self.zoom(1.1)
            else:
                self.zoom(0.9)
        else:
            # Linux
            if direction > 0:
                self.zoom(1.1)
            else:
                self.zoom(0.9)
    
    def start_drag(self, event):
        """Bắt đầu kéo ảnh"""
        if self.zoom_factor <= 1.0 or self.current_image is None or self.drag_data["item"] is None:
            return  # Chỉ cho phép kéo khi đã zoom in, có ảnh và ảnh đã được vẽ
        
        # Thay đổi con trỏ chuột để biểu thị đang kéo
        self.canvas.config(cursor="fleur")
        self.is_dragging = True
             
        # Lưu vị trí bắt đầu kéo
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        """Xử lý kéo ảnh"""
        if not self.is_dragging or self.drag_data["item"] is None:
            return  # Chỉ xử lý khi đang trong trạng thái kéo
             
        # Tính khoảng cách di chuyển
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        # Cập nhật vị trí pan
        self.pan_x += dx
        self.pan_y += dy
        
        # Di chuyển ảnh trên canvas
        self.canvas.move(self.drag_data["item"], dx, dy)
        
        # Lưu vị trí mới
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def stop_drag(self, event):
        """Kết thúc kéo ảnh"""
        # Trở lại con trỏ chuột bình thường
        self.canvas.config(cursor="hand2")
        self.is_dragging = False
        
        # Reset lại vị trí ban đầu của chuột
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0

    def zoom(self, factor):
        """Thay đổi tỷ lệ zoom"""
        if self.current_image is None:
            return
            
        # Cập nhật tỷ lệ zoom
        self.zoom_factor *= factor
        
        # Giới hạn tỷ lệ zoom
        self.zoom_factor = max(0.1, min(self.zoom_factor, 5.0))
        
        # Cập nhật hiển thị
        self.update_image_display()
    
    def reset_zoom(self):
        """Đặt lại tỷ lệ zoom về ban đầu"""
        if self.current_image is None:
            return
            
        self.zoom_factor = 1.0
        self.pan_x = 0  # Reset vị trí pan
        self.pan_y = 0
        self.update_image_display()
    
    def show_help(self):
        """Hiển thị hướng dẫn sử dụng"""
        help_text = """
        HƯỚNG DẪN SỬ DỤNG PHẦN MỀM CHẤM THI TRẮC NGHIỆM
        
        Các bước thực hiện:
        1. Nhấn nút 'Quét Đáp Án Mẫu' để chọn ảnh đáp án.
        2. Nhấn nút 'Chấm Điểm Bài Thi' để chọn và chấm bài thi.
        3. Xem kết quả ở tab 'Kết Quả' và hình ảnh bài thi đã chấm ở tab 'Xem Trước'.
        4. Lưu kết quả bằng cách nhấn nút 'Lưu Kết Quả' từ menu Tệp.
        
        Lưu ý:
        - Đảm bảo ảnh đáp án và bài thi có cùng định dạng.
        - Ảnh cần rõ nét để đảm bảo độ chính xác khi chấm.
        """
        messagebox.showinfo("Hướng Dẫn Sử Dụng", help_text)
    
    def show_about(self):
        """Hiển thị thông tin về phần mềm"""
        about_text = """
        PHẦN MỀM CHẤM THI TRẮC NGHIỆM
        
        Phiên bản: 1.0
        
        Phần mềm hỗ trợ chấm thi trắc nghiệm tự động bằng cách quét và nhận dạng 
        hình ảnh phiếu trả lời trắc nghiệm.
        
        Phát triển bởi: Nhóm nghiên cứu khoa học của trường đại học Mỏ Địa Chất
        """
        messagebox.showinfo("Giới Thiệu", about_text)
    
    def update_stats(self):
        """Cập nhật thống kê"""
        answer_count = len(self.answer_key_list) if self.answer_key_list else 0
        graded_count = 1 if self.result_image is not None else 0
        
        self.stats_label.config(text=f"Số đáp án mẫu: {answer_count}\nSố bài đã chấm: {graded_count}")

    def resize_image(self, image, target_width=1800, target_height=2600):
        """Điều chỉnh kích thước ảnh về kích thước tiêu chuẩn"""
        try:
            if image is None or image.size == 0:
                return None, False
                
            original_height, original_width = image.shape[:2]
            
            # Nếu ảnh đã đúng kích thước
            if original_width == target_width and original_height == target_height:
                return image, False
                
            # Điều chỉnh kích thước ảnh
            resized_image = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_CUBIC)
            
            # Thông báo thay đổi
            self.status_var.set(f"Đã điều chỉnh kích thước ảnh từ {original_width}x{original_height} thành {target_width}x{target_height}")
            
            return resized_image, True
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể điều chỉnh kích thước ảnh: {str(e)}")
            return None, False

# Khởi chạy ứng dụng
if __name__ == "__main__":
    root = ttk.Window()
    app = MCQGradingApp(root)
    root.mainloop()