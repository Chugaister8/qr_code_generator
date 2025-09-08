import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
import segno
from PIL import Image, ImageTk, ImageOps
import io

class QRGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced QR Code Generator")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # Styles for modern look
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("TCombobox", font=("Helvetica", 10))
        style.configure("TEntry", font=("Helvetica", 10))

        # Variables
        self.qr_type = tk.StringVar(value="Plain Text")
        self.error_level = tk.StringVar(value="M")
        self.scale = tk.IntVar(value=5)
        self.border = tk.IntVar(value=4)
        self.dark_color = tk.StringVar(value="#000000")  # Black
        self.light_color = tk.StringVar(value="#FFFFFF")  # White
        self.quiet_zone_color = tk.StringVar(value="#FFFFFF")
        self.logo_path = tk.StringVar(value="")
        self.preview_image = None
        self.qr_data = None

        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Type selection
        type_frame = ttk.LabelFrame(main_frame, text="QR Type")
        type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(type_frame, text="Select Type:").pack(side=tk.LEFT, padx=5)
        type_combo = ttk.Combobox(type_frame, textvariable=self.qr_type, state="readonly",
                                  values=["Plain Text", "URL", "WiFi", "vCard", "Email", "Geo Location", "Phone Number", "SMS"])
        type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        type_combo.bind("<<ComboboxSelected>>", self.update_input_fields)

        # Input fields frame (dynamic)
        self.input_frame = ttk.LabelFrame(main_frame, text="Input Data")
        self.input_frame.pack(fill=tk.X, pady=5)
        self.current_inputs = {}  # To store type-specific widgets
        self.update_input_fields()  # Initial setup

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Customization Options")
        options_frame.pack(fill=tk.X, pady=5)

        # Error level
        ttk.Label(options_frame, text="Error Correction:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Combobox(options_frame, textvariable=self.error_level, state="readonly",
                     values=["L", "M", "Q", "H"]).grid(row=0, column=1, padx=5, pady=5)

        # Scale and Border
        ttk.Label(options_frame, text="Scale:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Spinbox(options_frame, from_=1, to=20, textvariable=self.scale).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(options_frame, text="Border:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Spinbox(options_frame, from_=0, to=10, textvariable=self.border).grid(row=2, column=1, padx=5, pady=5)

        # Colors
        color_frame = ttk.Frame(options_frame)
        color_frame.grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Label(color_frame, text="Dark Color:").pack(side=tk.LEFT, padx=5)
        ttk.Button(color_frame, text="Choose", command=lambda: self.choose_color(self.dark_color)).pack(side=tk.LEFT)
        ttk.Label(color_frame, text="Light Color:").pack(side=tk.LEFT, padx=5)
        ttk.Button(color_frame, text="Choose", command=lambda: self.choose_color(self.light_color)).pack(side=tk.LEFT)
        ttk.Label(color_frame, text="Quiet Zone:").pack(side=tk.LEFT, padx=5)
        ttk.Button(color_frame, text="Choose", command=lambda: self.choose_color(self.quiet_zone_color)).pack(side=tk.LEFT)

        # Logo
        logo_frame = ttk.Frame(options_frame)
        logo_frame.grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Label(logo_frame, text="Logo:").pack(side=tk.LEFT, padx=5)
        ttk.Button(logo_frame, text="Select Image", command=self.select_logo).pack(side=tk.LEFT)
        ttk.Label(logo_frame, textvariable=self.logo_path).pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Generate Preview", command=self.generate_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save QR Code", command=self.save_qr).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=5)

        # Preview
        preview_frame = ttk.LabelFrame(main_frame, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack()

    def update_input_fields(self, event=None):
        # Clear current inputs
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.current_inputs = {}

        qr_type = self.qr_type.get()
        if qr_type == "Plain Text":
            self.create_text_input()
        elif qr_type == "URL":
            self.create_url_input()
        elif qr_type == "WiFi":
            self.create_wifi_input()
        elif qr_type == "vCard":
            self.create_vcard_input()
        elif qr_type == "Email":
            self.create_email_input()
        elif qr_type == "Geo Location":
            self.create_geo_input()
        elif qr_type == "Phone Number":
            self.create_phone_input()
        elif qr_type == "SMS":
            self.create_sms_input()

    def create_text_input(self):
        ttk.Label(self.input_frame, text="Text:").pack(anchor=tk.W, padx=5)
        self.current_inputs["text"] = tk.Text(self.input_frame, height=5, width=50)
        self.current_inputs["text"].pack(padx=5, pady=5)

    def create_url_input(self):
        ttk.Label(self.input_frame, text="URL:").pack(anchor=tk.W, padx=5)
        self.current_inputs["url"] = ttk.Entry(self.input_frame, width=50)
        self.current_inputs["url"].pack(padx=5, pady=5)

    def create_wifi_input(self):
        ttk.Label(self.input_frame, text="SSID:").pack(anchor=tk.W, padx=5)
        self.current_inputs["ssid"] = ttk.Entry(self.input_frame, width=50)
        self.current_inputs["ssid"].pack(padx=5)
        ttk.Label(self.input_frame, text="Password:").pack(anchor=tk.W, padx=5)
        self.current_inputs["password"] = ttk.Entry(self.input_frame, width=50)
        self.current_inputs["password"].pack(padx=5)
        ttk.Label(self.input_frame, text="Security Type:").pack(anchor=tk.W, padx=5)
        self.current_inputs["security"] = ttk.Combobox(self.input_frame, values=["WPA", "WEP", "nopass"], state="readonly")
        self.current_inputs["security"].set("WPA")
        self.current_inputs["security"].pack(padx=5)
        self.current_inputs["hidden"] = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.input_frame, text="Hidden Network", variable=self.current_inputs["hidden"]).pack(anchor=tk.W, padx=5)

    def create_vcard_input(self):
        fields = ["Name", "Email", "Phone", "Organization", "Address"]
        for field in fields:
            ttk.Label(self.input_frame, text=f"{field}:").pack(anchor=tk.W, padx=5)
            self.current_inputs[field.lower()] = ttk.Entry(self.input_frame, width=50)
            self.current_inputs[field.lower()].pack(padx=5)

    def create_email_input(self):
        ttk.Label(self.input_frame, text="Email Address:").pack(anchor=tk.W, padx=5)
        self.current_inputs["email"] = ttk.Entry(self.input_frame, width=50)
        self.current_inputs["email"].pack(padx=5)
        ttk.Label(self.input_frame, text="Subject:").pack(anchor=tk.W, padx=5)
        self.current_inputs["subject"] = ttk.Entry(self.input_frame, width=50)
        self.current_inputs["subject"].pack(padx=5)
        ttk.Label(self.input_frame, text="Body:").pack(anchor=tk.W, padx=5)
        self.current_inputs["body"] = tk.Text(self.input_frame, height=3, width=50)
        self.current_inputs["body"].pack(padx=5)

    def create_geo_input(self):
        ttk.Label(self.input_frame, text="Latitude:").pack(anchor=tk.W, padx=5)
        self.current_inputs["lat"] = ttk.Entry(self.input_frame, width=50)
        self.current_inputs["lat"].pack(padx=5)
        ttk.Label(self.input_frame, text="Longitude:").pack(anchor=tk.W, padx=5)
        self.current_inputs["lon"] = ttk.Entry(self.input_frame, width=50)
        self.current_inputs["lon"].pack(padx=5)

    def create_phone_input(self):
        ttk.Label(self.input_frame, text="Phone Number:").pack(anchor=tk.W, padx=5)
        self.current_inputs["phone"] = ttk.Entry(self.input_frame, width=50)
        self.current_inputs["phone"].pack(padx=5)

    def create_sms_input(self):
        ttk.Label(self.input_frame, text="Phone Number:").pack(anchor=tk.W, padx=5)
        self.current_inputs["phone"] = ttk.Entry(self.input_frame, width=50)
        self.current_inputs["phone"].pack(padx=5)
        ttk.Label(self.input_frame, text="Message:").pack(anchor=tk.W, padx=5)
        self.current_inputs["message"] = tk.Text(self.input_frame, height=3, width=50)
        self.current_inputs["message"].pack(padx=5)

    def choose_color(self, var):
        color = colorchooser.askcolor()[1]
        if color:
            var.set(color)

    def select_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if path:
            self.logo_path.set(path)

    def get_data(self):
        qr_type = self.qr_type.get()
        data = ""
        try:
            if qr_type == "Plain Text":
                data = self.current_inputs["text"].get("1.0", tk.END).strip()
            elif qr_type == "URL":
                data = self.current_inputs["url"].get().strip()
            elif qr_type == "WiFi":
                ssid = self.current_inputs["ssid"].get().strip()
                pwd = self.current_inputs["password"].get().strip()
                sec = self.current_inputs["security"].get()
                hidden = "true" if self.current_inputs["hidden"].get() else "false"
                data = f"WIFI:T:{sec};S:{ssid};P:{pwd};H:{hidden};;"
            elif qr_type == "vCard":
                name = self.current_inputs["name"].get().strip()
                email = self.current_inputs["email"].get().strip()
                phone = self.current_inputs["phone"].get().strip()
                org = self.current_inputs["organization"].get().strip()
                addr = self.current_inputs["address"].get().strip()
                data = f"""BEGIN:VCARD\nVERSION:3.0\nN:{name}\nEMAIL:{email}\nTEL:{phone}\nORG:{org}\nADR:{addr}\nEND:VCARD"""
            elif qr_type == "Email":
                email = self.current_inputs["email"].get().strip()
                sub = self.current_inputs["subject"].get().strip()
                body = self.current_inputs["body"].get("1.0", tk.END).strip()
                data = f"mailto:{email}?subject={sub}&body={body}"
            elif qr_type == "Geo Location":
                lat = self.current_inputs["lat"].get().strip()
                lon = self.current_inputs["lon"].get().strip()
                data = f"geo:{lat},{lon}"
            elif qr_type == "Phone Number":
                data = f"tel:{self.current_inputs['phone'].get().strip()}"
            elif qr_type == "SMS":
                phone = self.current_inputs["phone"].get().strip()
                msg = self.current_inputs["message"].get("1.0", tk.END).strip()
                data = f"sms:{phone}?body={msg}"
            if not data:
                raise ValueError("No data provided")
            return data
        except KeyError as e:
            messagebox.showerror("Error", f"Missing field: {e}")
            return None

    def generate_preview(self):
        data = self.get_data()
        if not data:
            return

        error = self.error_level.get().lower()
        qr = segno.make(data, error=error, micro=None)  # Auto micro if possible

        # Generate PIL image
        buffer = io.BytesIO()
        qr.save(buffer, kind='png', scale=self.scale.get(), dark=self.dark_color.get(),
                light=self.light_color.get(), quiet_zone=self.quiet_zone_color.get(),
                border=self.border.get())
        buffer.seek(0)
        img = Image.open(buffer)

        # Add logo if selected
        if self.logo_path.get():
            logo = Image.open(self.logo_path.get())
            logo_size = min(img.size) // 3  # 1/3 of QR size
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            logo_pos = ((img.size[0] - logo_size) // 2, (img.size[1] - logo_size) // 2)
            img.paste(logo, logo_pos, mask=logo if logo.mode == 'RGBA' else None)

        # For preview
        self.preview_image = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.preview_image)
        self.qr_data = qr  # Save for later save
        self.qr_img = img  # Save PIL img for save with logo

    def save_qr(self):
        if not self.qr_data:
            messagebox.showerror("Error", "Generate preview first")
            return

        file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("SVG", "*.svg")])
        if file:
            if file.endswith(".svg"):
                self.qr_data.save(file, kind='svg', scale=self.scale.get(), dark=self.dark_color.get(),
                                  light=self.light_color.get(), quiet_zone=self.quiet_zone_color.get(),
                                  border=self.border.get())
                # Note: Logo not supported in SVG directly, inform user
                if self.logo_path.get():
                    messagebox.showinfo("Info", "Logo not added to SVG (not supported). Saved without logo.")
            else:
                self.qr_img.save(file)
            messagebox.showinfo("Success", f"Saved to {file}")

    def reset(self):
        self.preview_label.config(image="")
        self.preview_image = None
        self.qr_data = None
        self.logo_path.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()