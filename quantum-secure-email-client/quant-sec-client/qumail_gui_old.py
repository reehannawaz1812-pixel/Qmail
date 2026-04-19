import customtkinter as ctk
from tkinter import messagebox
from email_service import EmailService
from security_engine import SecurityEngine
import json
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class QuMailApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QuMail - Quantum Secure Email Client")
        self.geometry("900x600")

        self.email_service = None
        self.security_engine = None
        self.current_user = None

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="QuMail", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=20)

        self.btn_inbox = ctk.CTkButton(self.sidebar_frame, text="Inbox", command=self.show_inbox)
        self.btn_inbox.pack(pady=10, padx=20)

        self.btn_compose = ctk.CTkButton(self.sidebar_frame, text="Compose", command=self.show_compose)
        self.btn_compose.pack(pady=10, padx=20)

        self.btn_settings = ctk.CTkButton(self.sidebar_frame, text="Settings/Login", command=self.show_login)
        self.btn_settings.pack(pady=10, padx=20)

        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginFrame, InboxFrame, ComposeFrame):
            frame = F(self.main_container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_login()

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

    def show_login(self): self.show_frame(LoginFrame)
    def show_inbox(self): 
        if self.email_service:
            self.frames[InboxFrame].refresh_emails()
            self.show_frame(InboxFrame)
        else:
            messagebox.showwarning("Login Required", "Please login first in Settings.")

    def show_compose(self):
        if self.email_service:
            self.show_frame(ComposeFrame)
        else:
            messagebox.showwarning("Login Required", "Please login first in Settings.")

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ctk.CTkLabel(self, text="Account Settings", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=10)

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email (e.g. gmail)")
        self.email_entry.pack(pady=5, padx=50, fill="x")

        self.pwd_entry = ctk.CTkEntry(self, placeholder_text="App Password", show="*")
        self.pwd_entry.pack(pady=5, padx=50, fill="x")

        self.km_entry = ctk.CTkEntry(self, placeholder_text="KM Host (127.0.0.1:8000)")
        self.km_entry.insert(0, "127.0.0.1:8000")
        self.km_entry.pack(pady=5, padx=50, fill="x")

        self.sae_entry = ctk.CTkEntry(self, placeholder_text="Your SAE ID (username)")
        self.sae_entry.pack(pady=5, padx=50, fill="x")

        self.btn_login = ctk.CTkButton(self, text="Save & Connect", command=self.login)
        self.btn_login.pack(pady=20)

    def login(self):
        email = self.email_entry.get()
        pwd = self.pwd_entry.get()
        km = self.km_entry.get()
        sae = self.sae_entry.get()

        if not all([email, pwd, km, sae]):
            messagebox.showerror("Error", "All fields are required")
            return

        # Simplified server detection for simulation
        smtp = "smtp.gmail.com"
        imap = "imap.gmail.com"
        if "yahoo" in email:
            smtp = "smtp.mail.yahoo.com"
            imap = "imap.mail.yahoo.com"

        self.controller.email_service = EmailService(smtp, 587, imap, 993, email, pwd)
        self.controller.security_engine = SecurityEngine(km, sae)
        self.controller.current_user = sae
        
        messagebox.showinfo("Success", "Settings saved!")
        self.controller.show_inbox()

class InboxFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = ctk.CTkLabel(self, text="Inbox", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Recent Emails")
        self.scrollable_frame.pack(padx=20, pady=10, fill="both", expand=True)

    def refresh_emails(self):
        # Clear current list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        success, emails = self.controller.email_service.fetch_emails()
        if success:
            for em in emails:
                sender = em['sender']
                subject = em['subject']
                body = em['body']
                
                # Try to decrypt
                decrypted_body = self.controller.security_engine.decrypt_message(body, sender, self.controller.current_user)
                
                btn = ctk.CTkButton(self.scrollable_frame, text=f"From: {sender}\nSub: {subject}", 
                                    anchor="w", justify="left",
                                    command=lambda b=decrypted_body, s=subject, f=sender: self.show_email_content(f, s, b))
                btn.pack(pady=5, fill="x")
        else:
            ctk.CTkLabel(self.scrollable_frame, text=f"Error: {emails}").pack()

    def show_email_content(self, sender, subject, body):
        top = ctk.CTkToplevel(self)
        top.title(subject)
        top.geometry("600x400")
        
        ctk.CTkLabel(top, text=f"From: {sender}", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        ctk.CTkLabel(top, text=f"Subject: {subject}", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        text_area = ctk.CTkTextbox(top)
        text_area.pack(padx=20, pady=20, fill="both", expand=True)
        text_area.insert("0.0", body)

class ComposeFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ctk.CTkLabel(self, text="Compose New Email", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=10)

        self.to_entry = ctk.CTkEntry(self, placeholder_text="To (Receiver SAE ID / Email)")
        self.to_entry.pack(pady=5, padx=50, fill="x")

        self.sub_entry = ctk.CTkEntry(self, placeholder_text="Subject")
        self.sub_entry.pack(pady=5, padx=50, fill="x")

        self.level_var = ctk.StringVar(value="Level 2: Quantum-aided AES")
        self.level_menu = ctk.CTkOptionMenu(self, values=[
            "Level 1: Quantum Secure (OTP)",
            "Level 2: Quantum-aided AES",
            "Level 3: PQC (Kyber)",
            "Level 4: No Quantum Security"
        ], variable=self.level_var)
        self.level_menu.pack(pady=5)

        self.body_text = ctk.CTkTextbox(self, height=200)
        self.body_text.pack(pady=10, padx=50, fill="both", expand=True)

        self.btn_send = ctk.CTkButton(self, text="Send Secure Email", command=self.send)
        self.btn_send.pack(pady=20)

    def send(self):
        to = self.to_entry.get()
        subject = self.sub_entry.get()
        body = self.body_text.get("0.0", "end")
        level_str = self.level_var.get()
        
        level = 4
        if "Level 1" in level_str: level = 1
        elif "Level 2" in level_str: level = 2
        elif "Level 3" in level_str: level = 3

        # Encrypt
        encrypted_body = self.controller.security_engine.encrypt_message(body, to, level)
        
        success, msg = self.controller.email_service.send_email(to, subject, encrypted_body)
        if success:
            messagebox.showinfo("Success", "Email sent!")
            self.controller.show_inbox()
        else:
            messagebox.showerror("Error", msg)

if __name__ == "__main__":
    app = QuMailApp()
    app.mainloop()
