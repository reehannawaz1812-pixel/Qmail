import customtkinter as ctk
from tkinter import messagebox
import gui_backend
import threading
import time

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class QuMailApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QuMail - Quantum Secure Email Client")
        self.geometry("1150x750")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frames = {}
        for F in (ConnectFrame, LoginFrame, DashboardFrame):
            frame = F(self, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(ConnectFrame)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

class ConnectFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.center = ctk.CTkFrame(self)
        self.center.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.center, text="QuMail", font=ctk.CTkFont(size=40, weight="bold")).pack(pady=20)
        ctk.CTkLabel(self.center, text="Quantum Key Infrastructure Connection", font=ctk.CTkFont(size=14)).pack(pady=10)

        self.host_entry = ctk.CTkEntry(self.center, placeholder_text="KM Host (127.0.0.1:8000)", width=300)
        self.host_entry.insert(0, "127.0.0.1:8000")
        self.host_entry.pack(pady=10)

        self.btn = ctk.CTkButton(self.center, text="Initialize Secure Link", command=self.connect)
        self.btn.pack(pady=20)

    def connect(self):
        host = self.host_entry.get()
        res = gui_backend.connect_to_server(host)
        if res["success"]:
            self.controller.show_frame(LoginFrame)
        else:
            messagebox.showerror("Connection Error", res["message"])

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.tabs = ctk.CTkTabview(self, width=450)
        self.tabs.place(relx=0.5, rely=0.5, anchor="center")
        self.tabs.add("Login")
        self.tabs.add("Register")

        # Login
        self.user_log = ctk.CTkEntry(self.tabs.tab("Login"), placeholder_text="Username")
        self.user_log.pack(pady=10, padx=20, fill="x")
        self.pass_log = ctk.CTkEntry(self.tabs.tab("Login"), placeholder_text="Password", show="*")
        self.pass_log.pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.tabs.tab("Login"), text="Unlock Vault", command=self.login).pack(pady=20)

        # Register
        self.name_reg = ctk.CTkEntry(self.tabs.tab("Register"), placeholder_text="Full Name")
        self.name_reg.pack(pady=5, padx=20, fill="x")
        self.user_reg = ctk.CTkEntry(self.tabs.tab("Register"), placeholder_text="Desired Username")
        self.user_reg.pack(pady=5, padx=20, fill="x")
        self.pass_reg = ctk.CTkEntry(self.tabs.tab("Register"), placeholder_text="Master Password", show="*")
        self.pass_reg.pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.tabs.tab("Register"), text="Generate Quantum Keys", command=self.register).pack(pady=20)

    def login(self):
        res = gui_backend.login(self.user_log.get(), self.pass_log.get())
        if res["success"]: self.controller.show_frame(DashboardFrame)
        else: messagebox.showerror("Denied", res["message"])

    def register(self):
        res = gui_backend.register(self.name_reg.get(), self.user_reg.get(), self.pass_reg.get())
        if res["success"]:
            messagebox.showinfo("Success", f"Account Registered!\nPost-Quantum Kyber Keys Linked.")
            self.tabs.set("Login")
        else: messagebox.showerror("Failed", res["message"])

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar
        self.sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="QuMail", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        for text, cmd in [("Inbox", self.show_inbox), ("Compose", self.show_compose), ("Sync", self.sync), ("Settings", self.show_settings)]:
            ctk.CTkButton(self.sidebar, text=text, command=cmd).pack(pady=5, padx=10)

        self.console = ctk.CTkTextbox(self.sidebar, height=250, width=160, font=("Courier", 10), text_color="#00FF00")
        self.console.pack(pady=20, padx=10, side="bottom")
        self.log("KM Ready\nQuantum Entropy High")

        # 2. List Pane
        self.list_pane = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.list_pane.grid(row=0, column=1, sticky="nsew", padx=1)
        self.list_pane.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self.list_pane, text="Encrypted Inbox", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.scroll = ctk.CTkScrollableFrame(self.list_pane, corner_radius=0)
        self.scroll.grid(row=1, column=0, sticky="nsew")

        # 3. Preview Pane
        self.preview = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.preview.grid(row=0, column=2, sticky="nsew", padx=15, pady=15)

    def log(self, msg):
        self.console.configure(state="normal")
        self.console.insert("end", f"> {msg}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def clear_preview(self):
        for w in self.preview.winfo_children(): w.destroy()

    def on_show(self): self.show_inbox()

    def show_inbox(self):
        self.clear_preview()
        for w in self.scroll.winfo_children(): w.destroy()
        res = gui_backend.fetch_inbox()
        self.log(res.get("message", "Inbox Loaded"))
        if res["success"]:
            for em in res["emails"]:
                f = ctk.CTkFrame(self.scroll, corner_radius=5, cursor="hand2")
                f.pack(fill="x", pady=2, padx=5)
                ctk.CTkLabel(f, text=em['sender'], font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=10, pady=(5,0))
                ctk.CTkLabel(f, text=em['subject'], text_color="gray", anchor="w").pack(fill="x", padx=10, pady=(0,5))
                f.bind("<Button-1>", lambda e, data=em: self.view_email(data))

    def view_email(self, data):
        self.clear_preview()
        ctk.CTkLabel(self.preview, text=data['subject'], font=ctk.CTkFont(size=24, weight="bold"), anchor="w").pack(fill="x", pady=10)
        ctk.CTkLabel(self.preview, text=f"From: {data['sender']}\nDate: {data['date']}", anchor="w", text_color="cyan").pack(fill="x")
        txt = ctk.CTkTextbox(self.preview, font=("Segoe UI", 12))
        txt.pack(fill="both", expand=True, pady=20)
        txt.insert("0.0", data['body'])
        txt.configure(state="disabled")
        self.log(f"Decrypted: {data['subject'][:20]}...")

    def show_compose(self):
        self.clear_preview()
        f = ctk.CTkFrame(self.preview)
        f.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(f, text="Compose Secure Transfer", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        l_frame = ctk.CTkFrame(f, fg_color="transparent")
        l_frame.pack(fill="x", padx=20)
        ctk.CTkLabel(l_frame, text="Security Protocol:").pack(side="left")
        self.lvl_var = ctk.StringVar(value="Level 3: PQC (Kyber)")
        ctk.CTkOptionMenu(l_frame, values=["Level 1: OTP (Quantum)", "Level 2: Q-AES", "Level 3: PQC (Hybrid)", "Level 4: Plain"], 
                          variable=self.lvl_var, command=lambda v: self.log(f"Selected: {v}")).pack(side="left", padx=10)
        
        self.to_ent = ctk.CTkEntry(f, placeholder_text="Recipient ID / Email Address")
        self.to_ent.pack(fill="x", padx=20, pady=10)
        self.sub_ent = ctk.CTkEntry(f, placeholder_text="Subject Line")
        self.sub_ent.pack(fill="x", padx=20, pady=5)
        self.body_txt = ctk.CTkTextbox(f, height=350)
        self.body_txt.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkButton(f, text="Transmit via Quantum Tunnel", command=self.send, height=40).pack(pady=10, padx=20, anchor="e")

    def send(self):
        lvl = 3
        v = self.lvl_var.get()
        if "Level 1" in v: lvl = 1
        elif "Level 2" in v: lvl = 2
        elif "Level 4" in v: lvl = 4
        gui_backend.session.security_level = lvl
        
        self.log("Syncing QKD Keys...")
        res = gui_backend.send_email(self.to_ent.get(), self.sub_ent.get(), self.body_txt.get("0.0", "end"))
        if res["success"]:
            messagebox.showinfo("Success", "Secure Transmission Verified.")
            self.log("Transfer Complete.")
            self.show_inbox()
        else: messagebox.showerror("Transfer Error", res["message"]); self.log("Error: " + res["message"])

    def show_settings(self):
        self.clear_preview()
        import settings_manager
        
        # Main Settings Container
        settings_scroll = ctk.CTkScrollableFrame(self.preview, label_text="Application Configuration", fg_color="transparent")
        settings_scroll.pack(fill="both", expand=True)

        current_settings = settings_manager.load_settings()

        # --- Section 1: Security ---
        sec_frame = ctk.CTkFrame(settings_scroll)
        sec_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(sec_frame, text="Security Protocol", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Encryption
        enc_var = ctk.StringVar(value=current_settings.get("security", {}).get("encryption_algorithm", "AES"))
        ctk.CTkLabel(sec_frame, text="Encryption Algorithm:").pack(anchor="w", padx=20)
        ctk.CTkOptionMenu(sec_frame, values=["AES", "RSA", "Post-Quantum (Kyber)"], variable=enc_var).pack(fill="x", padx=20, pady=5)
        
        # Digital Signature
        sig_var = ctk.BooleanVar(value=current_settings.get("security", {}).get("digital_signature", True))
        ctk.CTkCheckBox(sec_frame, text="Enable Digital Signature", variable=sig_var).pack(anchor="w", padx=20, pady=5)
        
        # Hash
        hash_var = ctk.StringVar(value=current_settings.get("security", {}).get("hash_algorithm", "SHA-256"))
        ctk.CTkLabel(sec_frame, text="Hash Algorithm:").pack(anchor="w", padx=20)
        ctk.CTkOptionMenu(sec_frame, values=["SHA-256", "SHA-3"], variable=hash_var).pack(fill="x", padx=20, pady=5)

        # --- Section 2: UI Customization ---
        ui_frame = ctk.CTkFrame(settings_scroll)
        ui_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(ui_frame, text="UI Customization", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Theme
        theme_var = ctk.StringVar(value=current_settings.get("ui", {}).get("theme", "Dark"))
        def change_theme(v): 
            ctk.set_appearance_mode(v)
            self.log(f"Theme switched to {v}")
        
        ctk.CTkLabel(ui_frame, text="Appearance Theme:").pack(anchor="w", padx=20)
        ctk.CTkOptionMenu(ui_frame, values=["Light", "Dark"], variable=theme_var, command=change_theme).pack(fill="x", padx=20, pady=5)
        
        # Font Size
        font_var = ctk.StringVar(value=current_settings.get("ui", {}).get("font_size", "Medium"))
        ctk.CTkLabel(ui_frame, text="Font Size:").pack(anchor="w", padx=20)
        ctk.CTkOptionMenu(ui_frame, values=["Small", "Medium", "Large"], variable=font_var).pack(fill="x", padx=20, pady=5)

        # --- Section 3: System Config ---
        sys_frame = ctk.CTkFrame(settings_scroll)
        sys_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(sys_frame, text="System & Provider", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Email Provider (Existing functionality)
        ctk.CTkLabel(sys_frame, text="Email Provider (App Password):").pack(anchor="w", padx=20)
        e_ent = ctk.CTkEntry(sys_frame, placeholder_text="Email")
        if gui_backend.session.email_address: e_ent.insert(0, gui_backend.session.email_address)
        e_ent.pack(fill="x", padx=20, pady=2)
        
        p_ent = ctk.CTkEntry(sys_frame, placeholder_text="Password", show="*")
        if gui_backend.session.email_password: p_ent.insert(0, gui_backend.session.email_password)
        p_ent.pack(fill="x", padx=20, pady=2)

        # Server URL
        ctk.CTkLabel(sys_frame, text="KM Server URL:").pack(anchor="w", padx=20)
        url_ent = ctk.CTkEntry(sys_frame)
        url_ent.insert(0, current_settings.get("system", {}).get("server_url", "http://127.0.0.1:8000"))
        url_ent.pack(fill="x", padx=20, pady=5)
        
        # Toggles
        auto_dec_var = ctk.BooleanVar(value=current_settings.get("system", {}).get("auto_decrypt", True))
        ctk.CTkCheckBox(sys_frame, text="Auto-Decrypt Messages", variable=auto_dec_var).pack(anchor="w", padx=20, pady=5)
        
        log_var = ctk.BooleanVar(value=current_settings.get("system", {}).get("enable_logging", True))
        ctk.CTkCheckBox(sys_frame, text="Enable Session Logging", variable=log_var).pack(anchor="w", padx=20, pady=5)

        def save():
            new_settings = {
                "security": {
                    "encryption_algorithm": enc_var.get(),
                    "digital_signature": sig_var.get(),
                    "hash_algorithm": hash_var.get(),
                    "key_size": "256"
                },
                "ui": {
                    "theme": theme_var.get(),
                    "font_size": font_var.get(),
                    "layout": "Comfortable"
                },
                "system": {
                    "server_url": url_ent.get(),
                    "auto_decrypt": auto_dec_var.get(),
                    "enable_logging": log_var.get(),
                    "blockchain_logging": False
                }
            }
            settings_manager.save_settings(new_settings)
            gui_backend.session.set_email_config(e_ent.get(), p_ent.get())
            messagebox.showinfo("Config Saved", "System settings and provider identity synced.")
            self.log("Settings persisted to config.json")

        def reset():
            settings_manager.save_settings(settings_manager.DEFAULT_SETTINGS)
            self.show_settings()
            self.log("Settings reset to factory defaults")

        btn_frame = ctk.CTkFrame(settings_scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        ctk.CTkButton(btn_frame, text="Reset to Defaults", command=reset, fg_color="gray").pack(side="left", padx=20, expand=True)
        ctk.CTkButton(btn_frame, text="Save Settings", command=save, fg_color="green").pack(side="right", padx=20, expand=True)

    def sync(self):
        self.log("Polling KM and Email Nodes...")
        self.show_inbox()

if __name__ == "__main__":
    app = QuMailApp()
    app.mainloop()