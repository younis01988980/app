import os
import sys
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from rembg import remove

class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lite أداتي")
        self.root.geometry("1920x1080")  # زيادة حجم النافذة
        self.set_window_icon()  # ← هنا تضيف هذا السطر
        
        # تعيين النافذة للتكبير تلقائيًا
        self.root.state('zoomed')
        
        # تكوين الألوان والسمة
        self.bg_color = "#f0f4f8"  # لون خلفية أفتح
        self.primary_color = "#2563eb"  # أزرق أكثر حيوية
        self.secondary_color = "#1e40af"  # أزرق داكن
        self.accent_color = "#10b981"  # أخضر زمردي
        self.warning_color = "#ef9a44"  # أحمر
        self.neutral_color = "#ef9a44"  # رمادي مزرق
        self.border_color = "#cbd5e1"  # لون حدود فاتح
        
        # تكوين أنماط الخطوط
        self.title_font = ("Tajawal", 22, "bold")  # خط عربي أفضل إذا كان متوفرًا
        self.header_font = ("Tajawal", 16, "bold")
        self.normal_font = ("Tajawal", 12)
        self.small_font = ("Tajawal", 10)
        
        # تكوين النافذة الرئيسية
        self.root.configure(bg=self.bg_color)
        
        # تخزين البيانات
        self.input_paths = []
        self.output_images = []
        self.current_image_index = 0
        self.quality_level = tk.StringVar(value="متوسط")  # جودة افتراضية
        self.output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Lite مجلد الصور الممحية خلفيتها بواسطة أداتي")
        
        # إنشاء واجهة المستخدم
        self.create_widgets()
        
    def create_widgets(self):
        # إطار العنوان مع تأثير ظل
        title_frame = tk.Frame(self.root, bg=self.secondary_color, pady=15)
        title_frame.pack(fill="x")
        
        # إضافة شعار أو أيقونة (يمكن استبدالها بصورة حقيقية)
        logo_label = tk.Label(
            title_frame,
            text="",
            font=("Arial", 28),
            fg="white",
            bg=self.secondary_color
        )
        logo_label.pack(side="left", padx=20)
        
        title_label = tk.Label(
            title_frame, 
            text="Lite أداتي", 
            font=self.title_font, 
            fg="white", 
            bg=self.secondary_color,
            padx=20,
            pady=10
        )
        title_label.pack(side="left")
        
        # حاوية رئيسية مع تباعد
        main_container = tk.Frame(self.root, bg=self.bg_color, padx=30, pady=20)
        main_container.pack(expand=True, fill="both")
        
        # إطار المحتوى - استخدام grid مع weights للاستجابة الأفضل
        content_frame = tk.Frame(main_container, bg=self.bg_color)
        content_frame.pack(expand=True, fill="both")
        content_frame.grid_columnconfigure(0, weight=1, minsize=30)  # العمود الأول (الصورة الأصلية)
        content_frame.grid_columnconfigure(1, weight=1, minsize=30)  # العمود الثاني (الصورة الناتجة)
        
        # إطارات الصور مع تحسين المظهر وإضافة شريط تمرير
        input_frame = tk.LabelFrame(
            content_frame, 
            text="الصورة الأصلية", 
            font=self.header_font,
            bg=self.bg_color,
            fg=self.secondary_color,
            padx=10,
            pady=10,
            relief="groove",
            borderwidth=2,
            highlightbackground=self.border_color,
            highlightthickness=1
        )
        input_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # إضافة إطار للتمرير للصورة المدخلة
        input_scroll_frame = tk.Frame(input_frame)
        input_scroll_frame.pack(expand=True, fill="both")
        
        # إضافة شريط تمرير عمودي
        input_scrollbar_y = tk.Scrollbar(input_scroll_frame, orient="vertical")
        input_scrollbar_y.pack(side="right", fill="y")
        
        # إضافة شريط تمرير أفقي
        input_scrollbar_x = tk.Scrollbar(input_scroll_frame, orient="horizontal")
        input_scrollbar_x.pack(side="bottom", fill="x")
        
        # إنشاء Canvas للصورة المدخلة مع ربطه بأشرطة التمرير
        self.input_canvas = tk.Canvas(
            input_scroll_frame,
            bg="white",
            yscrollcommand=input_scrollbar_y.set,
            xscrollcommand=input_scrollbar_x.set,
            highlightthickness=0
        )
        self.input_canvas.pack(expand=True, fill="both")
        
        # ربط أشرطة التمرير بالـ Canvas
        input_scrollbar_y.config(command=self.input_canvas.yview)
        input_scrollbar_x.config(command=self.input_canvas.xview)
        
        # إنشاء إطار داخل Canvas لوضع الصورة فيه
        self.input_image_frame = tk.Frame(self.input_canvas, bg="white")
        self.input_canvas.create_window((0, 0), window=self.input_image_frame, anchor="nw")
        
        # صورة الإدخال مع تحسين المظهر
        self.input_image_label = tk.Label(
            self.input_image_frame, 
            text="الصورة المدخلة ستظهر هنا", 
            font=self.normal_font,
            bg="white",
            relief="flat",
            padx=10,
            pady=10
        )
        self.input_image_label.pack(expand=True, fill="both")
        
        # إطار الصورة المخرجة
        output_frame = tk.LabelFrame(
            content_frame, 
            text="الصورة بعد إزالة الخلفية", 
            font=self.header_font,
            bg=self.bg_color,
            fg=self.secondary_color,
            padx=10,
            pady=10,
            relief="groove",
            borderwidth=2,
            highlightbackground=self.border_color,
            highlightthickness=1
        )
        output_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # إضافة إطار للتمرير للصورة المخرجة
        output_scroll_frame = tk.Frame(output_frame)
        output_scroll_frame.pack(expand=True, fill="both")
        
        # إضافة شريط تمرير عمودي
        output_scrollbar_y = tk.Scrollbar(output_scroll_frame, orient="vertical")
        output_scrollbar_y.pack(side="right", fill="y")
        
        # إضافة شريط تمرير أفقي
        output_scrollbar_x = tk.Scrollbar(output_scroll_frame, orient="horizontal")
        output_scrollbar_x.pack(side="bottom", fill="x")
        
        # إنشاء Canvas للصورة المخرجة مع ربطه بأشرطة التمرير
        self.output_canvas = tk.Canvas(
            output_scroll_frame,
            bg="white",
            yscrollcommand=output_scrollbar_y.set,
            xscrollcommand=output_scrollbar_x.set,
            highlightthickness=0
        )
        self.output_canvas.pack(expand=True, fill="both")
        
        # ربط أشرطة التمرير بالـ Canvas
        output_scrollbar_y.config(command=self.output_canvas.yview)
        output_scrollbar_x.config(command=self.output_canvas.xview)
        
        # إنشاء إطار داخل Canvas لوضع الصورة فيه
        self.output_image_frame = tk.Frame(self.output_canvas, bg="white")
        self.output_canvas.create_window((0, 0), window=self.output_image_frame, anchor="nw")
        
        # صورة الإخراج مع تحسين المظهر
        self.output_image_label = tk.Label(
            self.output_image_frame, 
            text="الصورة الناتجة ستظهر هنا", 
            font=self.normal_font,
            bg="white",
            relief="flat",
            padx=10,
            pady=10
        )
        self.output_image_label.pack(expand=True, fill="both")
        
        # حاوية عناصر التحكم
        controls_container = tk.Frame(main_container, bg=self.bg_color, pady=10)
        controls_container.pack(fill="x")
        
        # إطار التحكم بالجودة مع تحسين المظهر
        quality_frame = tk.LabelFrame(
            controls_container, 
            text="جودة المعالجة", 
            font=self.header_font,
            bg=self.bg_color,
            fg=self.secondary_color,
            padx=15,
            pady=10,
            relief="groove",
            borderwidth=1
        )
        quality_frame.pack(fill="x", pady=10)
        
        # خيارات الجودة مع تحسين المظهر وإضافة خيارات جديدة
        quality_options = [
            ("ممتاز جداً", "ممتاز جداً"),  # خيار جديد أعلى جودة
            ("ممتاز", "ممتاز"),  # خيار جديد عالي الجودة
            ("عالي", "عالي"),
            ("متوسط", "متوسط"),
            ("منخفض", "منخفض")
        ]
        
        # إنشاء إطار لاحتواء خيارات الجودة
        quality_buttons_frame = tk.Frame(quality_frame, bg=self.bg_color)
        quality_buttons_frame.pack(fill="x", pady=5)
        
        # توزيع الأزرار بشكل متساوٍ
        for i, (text, value) in enumerate(quality_options):
            quality_button = tk.Radiobutton(
                quality_buttons_frame, 
                text=text, 
                variable=self.quality_level, 
                value=value,
                font=self.normal_font,
                bg=self.bg_color,
                activebackground=self.primary_color,
                activeforeground="white",
                padx=10,
                pady=5,
                indicatoron=0,  # لجعله يبدو كزر
                selectcolor=self.primary_color,
                fg="black",
                borderwidth=1,
                relief="raised",
                width=12,
                cursor="hand2"
            )
            quality_button.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            
        # تكوين الصف لتوزيع الأزرار بشكل متساوٍ
        quality_buttons_frame.grid_columnconfigure(0, weight=1)
        quality_buttons_frame.grid_columnconfigure(1, weight=1)
        quality_buttons_frame.grid_columnconfigure(2, weight=1)
        quality_buttons_frame.grid_columnconfigure(3, weight=1)
        quality_buttons_frame.grid_columnconfigure(4, weight=1)
        
        # أزرار التحكم مع تحسين المظهر
        button_frame = tk.Frame(controls_container, bg=self.bg_color, pady=15)
        button_frame.pack(fill="x")
        
        # نمط الأزرار
        button_style = {
            "font": self.normal_font,
            "borderwidth": 2,
            "relief": "raised",
            "width": 18,
            "height": 2,
            "cursor": "hand2",
            "activebackground": self.secondary_color,
            "activeforeground": "white"
        }
        
        # إزالة زر "اختر صورة واحدة" والاحتفاظ فقط بزر "اختر صور متعددة"
        self.select_multiple_btn = tk.Button(
            button_frame, 
            text="اختر الصور", 
            command=self.select_multiple_images,
            bg=self.primary_color,
            fg="white",
            **button_style
        )
        self.select_multiple_btn.pack(side="left", padx=10, pady=5)
        
        self.remove_btn = tk.Button(
            button_frame, 
            text="إزالة الخلفية", 
            command=self.start_background_removal,
            bg=self.accent_color,
            fg="white",
            state="disabled",
            **button_style
        )
        self.remove_btn.pack(side="left", padx=10, pady=5)
        
        self.save_btn = tk.Button(
            button_frame, 
            text="حفظ الصورة الحالية", 
            command=self.save_image,
            bg=self.warning_color,
            fg="white",
            state="disabled",
            **button_style
        )
        self.save_btn.pack(side="left", padx=10, pady=5)
        
        self.save_all_btn = tk.Button(
            button_frame, 
            text="حفظ جميع الصور", 
            command=self.save_all_images,
            bg=self.warning_color,
            fg="white",
            state="disabled",
            **button_style
        )
        self.save_all_btn.pack(side="left", padx=10, pady=5)
        
        # حاوية التنقل
        nav_container = tk.Frame(main_container, bg=self.bg_color, pady=5)
        nav_container.pack(fill="x")
        
        # أزرار التنقل بين الصور مع تحسين المظهر
        nav_frame = tk.LabelFrame(
            nav_container, 
            text="التنقل بين الصور", 
            font=self.header_font,
            bg=self.bg_color,
            fg=self.secondary_color,
            padx=15,
            pady=10,
            relief="groove",
            borderwidth=1
        )
        nav_frame.pack(fill="x")
        
        # أزرار التنقل مع تحسين المظهر
        nav_button_style = {
            "font": self.normal_font,
            "width": 12,
            "borderwidth": 2,
            "relief": "raised",
            "cursor": "hand2",
            "activebackground": self.neutral_color,
            "activeforeground": "white"
        }
        
        self.prev_btn = tk.Button(
            nav_frame, 
            text="◀ السابق", 
            command=self.show_previous_image,
            bg=self.neutral_color,
            fg="white",
            state="disabled",
            **nav_button_style
        )
        self.prev_btn.pack(side="left", padx=20)
        
        self.image_counter_label = tk.Label(
            nav_frame, 
            text="0/0",
            font=self.header_font,
            bg=self.bg_color,
            width=10
        )
        self.image_counter_label.pack(side="left", padx=20)
        
        self.next_btn = tk.Button(
            nav_frame, 
            text="التالي ▶", 
            command=self.show_next_image,
            bg=self.neutral_color,
            fg="white",
            state="disabled",
            **nav_button_style
        )
        self.next_btn.pack(side="left", padx=20)
        
        # حاوية شريط التقدم
        progress_container = tk.Frame(main_container, bg=self.bg_color, pady=15)
        progress_container.pack(fill="x")
        
        # شريط التقدم مع تحسين المظهر
        progress_frame = tk.LabelFrame(
            progress_container, 
            text="حالة المعالجة", 
            font=self.header_font,
            bg=self.bg_color,
            fg=self.secondary_color,
            padx=15,
            pady=10,
            relief="groove",
            borderwidth=1
        )
        progress_frame.pack(fill="x")
        
        # تكوين نمط ttk لشريط التقدم
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#e2e8f0',
            background=self.accent_color,
            thickness=25,
            borderwidth=0
        )
        
        self.progress_label = tk.Label(
            progress_frame, 
            text="التقدم:",
            font=self.normal_font,
            bg=self.bg_color
        )
        self.progress_label.pack(side="top", pady=5, anchor="w")
        
        self.progress = ttk.Progressbar(
            progress_frame, 
            orient="horizontal", 
            length=400, 
            mode="determinate",
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(side="top", fill="x", padx=5, pady=5)
        
        # معلومات الملف مع تحسين المظهر
        self.file_info = tk.Label(
            main_container, 
            text="", 
            font=self.small_font,
            fg=self.secondary_color,
            bg=self.bg_color,
            pady=10
        )
        self.file_info.pack(fill="x")
        
        # تذييل
        footer_frame = tk.Frame(self.root, bg=self.secondary_color, height=30)
        footer_frame.pack(fill="x", side="bottom")
        
        footer_label = tk.Label(
            footer_frame,
            text="© 2025 Owl Wave. جميع الحقوق محفوظة",
            font=self.small_font,
            fg="white",
            bg=self.secondary_color,
            pady=5
        )
        footer_label.pack()
        
        # تهيئة حجم Canvas للصور
        self.root.update()
        self.update_canvas_scrollregion()
    
    def update_canvas_scrollregion(self):
        # تحديث منطقة التمرير للـ Canvas
        self.input_canvas.update_idletasks()
        self.input_canvas.config(scrollregion=self.input_canvas.bbox("all"))
        self.output_canvas.update_idletasks()
        self.output_canvas.config(scrollregion=self.output_canvas.bbox("all"))
    
    def set_window_icon(self):
        try:
            # تحديد المسار الصحيح للأيقونة سواء كان البرنامج ملف exe أو لا
            if getattr(sys, 'frozen', False):
                # إذا كان البرنامج ملف exe
                base_path = sys._MEIPASS
            else:
                # إذا كان البرنامج يعمل كبرنامج عادي
                base_path = os.path.dirname(os.path.abspath(__file__))
                
            icon_path = os.path.join(base_path, "eraser-svgrepo-com.png")
            
            if not os.path.exists(icon_path):
                raise FileNotFoundError(f"الملف {icon_path} غير موجود")
    
            # تحميل الصورة كـ PhotoImage
            icon_image = Image.open(icon_path)
            photo = ImageTk.PhotoImage(icon_image)
    
            # تعيين الأيقونة للنافذة الرئيسية
            self.root.iconphoto(False, photo)
    
            # حفظ المرجع لتجنب اختفاء الصورة
            self.window_icon = photo
    
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر تحميل الأيقونة: {e}")
    # تم إزالة دالة select_image لأننا نريد فقط زر اختيار صور متعددة
    
    def select_multiple_images(self):
        filetypes = (
            ("ملفات الصور", "*.jpg *.jpeg *.png"),
            ("جميع الملفات", "*.*")
        )
        
        input_paths = filedialog.askopenfilenames(
            title="اختر الصور",
            filetypes=filetypes
        )
        
        if input_paths:
            # إعادة تعيين القائمة
            self.input_paths = list(input_paths)
            self.output_images = [None] * len(input_paths)
            self.current_image_index = 0
            
            self.display_current_image()
            self.update_navigation_buttons()
            
            # تفعيل زر الإزالة
            self.remove_btn.config(state="normal")
            
            # عرض معلومات الملف
            self.file_info.config(text=f"تم اختيار {len(input_paths)} صورة")
    
    def display_current_image(self):
        if not self.input_paths or self.current_image_index >= len(self.input_paths):
            return
            
        try:
            # عرض الصورة المدخلة
            img = Image.open(self.input_paths[self.current_image_index])
            
            # الحفاظ على نسبة العرض إلى الارتفاع مع عرض الصورة بحجم أكبر
            img_width, img_height = img.size
            max_size = 600  # حجم أكبر للصورة
            
            # حساب الحجم الجديد مع الحفاظ على النسبة
            if img_width > img_height:
                new_width = max_size
                new_height = int(img_height * (max_size / img_width))
            else:
                new_height = max_size
                new_width = int(img_width * (max_size / img_height))
            
            # تغيير حجم الصورة
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img_resized)
            
            # تحديث الصورة في الـ Label
            self.input_image_label.config(image=photo, text="", width=new_width, height=new_height)
            self.input_image_label.image = photo
            
            # تحديث منطقة التمرير
            self.update_canvas_scrollregion()
            
            # عرض الصورة المخرجة إذا كانت موجودة
            if self.output_images[self.current_image_index] is not None:
                with open("temp_output.png", 'wb') as out_file:
                    out_file.write(self.output_images[self.current_image_index])
                
                out_img = Image.open("temp_output.png")
                
                # تغيير حجم الصورة المخرجة بنفس الطريقة
                if img_width > img_height:
                    new_width = max_size
                    new_height = int(img_height * (max_size / img_width))
                else:
                    new_height = max_size
                    new_width = int(img_width * (max_size / img_height))
                
                out_img_resized = out_img.resize((new_width, new_height), Image.LANCZOS)
                out_photo = ImageTk.PhotoImage(out_img_resized)
                
                # تحديث الصورة المخرجة
                self.output_image_label.config(image=out_photo, text="", width=new_width, height=new_height)
                self.output_image_label.image = out_photo
                
                # تحديث منطقة التمرير
                self.update_canvas_scrollregion()
                
                # تفعيل زر الحفظ
                self.save_btn.config(state="normal")
            else:
                self.output_image_label.config(image="")
                self.output_image_label.config(text="الصورة الناتجة ستظهر هنا")
                
            # تحديث عداد الصور
            self.image_counter_label.config(text=f"{self.current_image_index + 1}/{len(self.input_paths)}")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"تعذر عرض الصورة: {str(e)}")
    
    def update_navigation_buttons(self):
        if len(self.input_paths) <= 1:
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
        else:
            self.prev_btn.config(state="normal" if self.current_image_index > 0 else "disabled")
            self.next_btn.config(state="normal" if self.current_image_index < len(self.input_paths) - 1 else "disabled")
    
    def show_previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_current_image()
            self.update_navigation_buttons()
    
    def show_next_image(self):
        if self.current_image_index < len(self.input_paths) - 1:
            self.current_image_index += 1
            self.display_current_image()
            self.update_navigation_buttons()
    
    def get_quality_settings(self):
        quality = self.quality_level.get()
        if quality == "ممتاز جداً":
            return {
                "alpha_matting": True, 
                "alpha_matting_foreground_threshold": 250, 
                "alpha_matting_background_threshold": 5,
                "alpha_matting_erode_size": 10
            }
        elif quality == "ممتاز":
            return {
                "alpha_matting": True, 
                "alpha_matting_foreground_threshold": 245, 
                "alpha_matting_background_threshold": 8,
                "alpha_matting_erode_size": 5
            }
        elif quality == "عالي":
            return {
                "alpha_matting": True, 
                "alpha_matting_foreground_threshold": 240, 
                "alpha_matting_background_threshold": 10
            }
        elif quality == "متوسط":
            return {"alpha_matting": False}
        else:  # منخفض
            return {"alpha_matting": False, "post_process_mask": True}
    
    def start_background_removal(self):
        if not self.input_paths:
            messagebox.showwarning("تحذير", "الرجاء اختيار صورة أولاً")
            return
        
        # تعطيل الأزرار أثناء المعالجة
        self.remove_btn.config(state="disabled")
        self.select_multiple_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.save_all_btn.config(state="disabled")
        self.prev_btn.config(state="disabled")
        self.next_btn.config(state="disabled")
        
        # بدء المعالجة في خيط منفصل
        thread = threading.Thread(target=self.process_images)
        thread.daemon = True
        thread.start()
    
    def process_images(self):
        total_images = len(self.input_paths)
        quality_settings = self.get_quality_settings()
        
        for i, input_path in enumerate(self.input_paths):
            try:
                # تحديث شريط التقدم
                progress_value = (i / total_images) * 100
                self.update_progress(progress_value, f"معالجة الصورة {i+1} من {total_images}")
                
                # قراءة الصورة
                with open(input_path, 'rb') as img_file:
                    input_img = img_file.read()
                
                # إزالة الخلفية
                output_img = remove(input_img, **quality_settings)
                
                # حفظ الصورة المعالجة
                self.output_images[i] = output_img
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("خطأ", f"حدث خطأ أثناء معالجة الصورة {i+1}: {str(e)}"))
        
        # تحديث شريط التقدم إلى 100%
        self.update_progress(100, "اكتملت المعالجة")
        
        # عرض الصورة الحالية
        self.root.after(0, self.display_current_image)
        
        # تفعيل الأزرار مرة أخرى
        self.root.after(0, lambda: self.remove_btn.config(state="normal"))
        self.root.after(0, lambda: self.select_multiple_btn.config(state="normal"))
        self.root.after(0, lambda: self.save_all_btn.config(state="normal" if any(img is not None for img in self.output_images) else "disabled"))

        self.root.after(0, lambda: self.update_navigation_buttons())
        
        # عرض رسالة نجاح
        self.root.after(0, lambda: messagebox.showinfo("نجاح", "تمت إزالة الخلفية بنجاح!"))
    
    def update_progress(self, value, text=""):
        self.root.after(0, lambda: self.progress.config(value=value))
        if text:
            self.root.after(0, lambda: self.progress_label.config(text=text))
    
    def save_image(self):
        if not self.output_images or self.current_image_index >= len(self.output_images) or self.output_images[self.current_image_index] is None:
            messagebox.showwarning("تحذير", "لا توجد صورة لحفظها")
            return
        
        # إنشاء مجلد الإخراج إذا لم يكن موجودًا
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        # اقتراح اسم الملف
        original_filename = os.path.basename(self.input_paths[self.current_image_index])
        filename_without_ext = os.path.splitext(original_filename)[0]
        default_output_path = os.path.join(self.output_folder, f"{filename_without_ext}_no_bg.png")
        
        output_path = filedialog.asksaveasfilename(
            title="حفظ الصورة الناتجة",
            defaultextension=".png",
            initialdir=self.output_folder,
            initialfile=f"{filename_without_ext}_no_bg.png",
            filetypes=(
                ("صورة PNG", "*.png"),
                ("جميع الملفات", "*.*")
            )
        )
        
        if output_path:
            try:
                with open(output_path, 'wb') as out_file:
                    out_file.write(self.output_images[self.current_image_index])
                
                messagebox.showinfo("نجاح", f"تم حفظ الصورة بنجاح في:\n{output_path}")
                
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر حفظ الصورة: {str(e)}")
    
    def save_all_images(self):
        if not any(img is not None for img in self.output_images):
            messagebox.showwarning("تحذير", "لا توجد صور لحفظها")
            return
        
        # إنشاء مجلد الإخراج إذا لم يكن موجودًا
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        # حفظ جميع الصور المعالجة
        saved_count = 0
        for i, output_img in enumerate(self.output_images):
            if output_img is None:
                continue
                
            try:
                original_filename = os.path.basename(self.input_paths[i])
                filename_without_ext = os.path.splitext(original_filename)[0]
                output_path = os.path.join(self.output_folder, f"{filename_without_ext}_no_bg.png")
                
                # إضافة رقم إذا كان الملف موجودًا بالفعل
                counter = 1
                while os.path.exists(output_path):
                    output_path = os.path.join(self.output_folder, f"{filename_without_ext}_no_bg_{counter}.png")
                    counter += 1
                
                with open(output_path, 'wb') as out_file:
                    out_file.write(output_img)
                
                saved_count += 1
                
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر حفظ الصورة {i+1}: {str(e)}")
        
        if saved_count > 0:
            messagebox.showinfo("نجاح", f"تم حفظ {saved_count} صورة بنجاح في المجلد:\n{self.output_folder}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()

# Note: This code requires the following Python packages:
# pip install rembg pillow
