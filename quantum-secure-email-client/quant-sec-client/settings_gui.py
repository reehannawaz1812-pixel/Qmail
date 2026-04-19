import customtkinter as ctk
from tkinter import messagebox
import settings_manager

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.settings = settings_manager.load_settings()

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main scrollable container
        self.scroll_container = ctk.CTkScrollableFrame(self, label_text="Application Settings")
        self.scroll_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self.create_security_section()
        self.create_ui_section()
        self.create_system_section()

        # Save Button
        self.save_btn = ctk.CTkButton(self.scroll_container, text="Save All Settings", command=self.save_all)
        self.save_btn.pack(pady=30, padx=20, fill="x")

    def create_security_section(self):
        # Section Header
        sec_label = ctk.CTkLabel(self.scroll_container, text="1. Security Settings", font=ctk.CTkFont(size=16, weight="bold"))
        sec_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        frame = ctk.CTkFrame(self.scroll_container)
        frame.pack(pady=5, padx=20, fill="x")

        # Encryption Algorithm
        ctk.CTkLabel(frame, text="Encryption Algorithm:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.enc_algo = ctk.CTkOptionMenu(frame, values=["AES", "RSA", "Post-Quantum (Kyber)"])
        self.enc_algo.set(self.settings["security"]["encryption_algorithm"])
        self.enc_algo.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # Digital Signature
        ctk.CTkLabel(frame, text="Enable Digital Signature:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.dig_sig = ctk.CTkSwitch(frame, text="")
        if self.settings["security"]["digital_signature"]: self.dig_sig.select()
        self.dig_sig.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        # Hash Algorithm
        ctk.CTkLabel(frame, text="Hash Algorithm:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.hash_algo = ctk.CTkOptionMenu(frame, values=["SHA-256", "SHA-3"])
        self.hash_algo.set(self.settings["security"]["hash_algorithm"])
        self.hash_algo.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        # Key Size
        ctk.CTkLabel(frame, text="Key Size (bits):").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.key_size = ctk.CTkOptionMenu(frame, values=["128", "256", "512"])
        self.key_size.set(self.settings["security"]["key_size"])
        self.key_size.grid(row=3, column=1, padx=10, pady=10, sticky="e")

    def create_ui_section(self):
        sec_label = ctk.CTkLabel(self.scroll_container, text="2. UI Customization", font=ctk.CTkFont(size=16, weight="bold"))
        sec_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        frame = ctk.CTkFrame(self.scroll_container)
        frame.pack(pady=5, padx=20, fill="x")

        # Theme
        ctk.CTkLabel(frame, text="Appearance Theme:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.theme = ctk.CTkOptionMenu(frame, values=["Light", "Dark"], command=self.change_theme_event)
        self.theme.set(self.settings["ui"]["theme"])
        self.theme.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # Font Size
        ctk.CTkLabel(frame, text="Font Size:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.font_size = ctk.CTkOptionMenu(frame, values=["Small", "Medium", "Large"])
        self.font_size.set(self.settings["ui"]["font_size"])
        self.font_size.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        # Layout
        ctk.CTkLabel(frame, text="Layout Mode:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.layout = ctk.CTkOptionMenu(frame, values=["Compact", "Comfortable"])
        self.layout.set(self.settings["ui"]["layout"])
        self.layout.grid(row=2, column=1, padx=10, pady=10, sticky="e")

    def create_system_section(self):
        sec_label = ctk.CTkLabel(self.scroll_container, text="3. System Configuration", font=ctk.CTkFont(size=16, weight="bold"))
        sec_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        frame = ctk.CTkFrame(self.scroll_container)
        frame.pack(pady=5, padx=20, fill="x")

        # Server URL
        ctk.CTkLabel(frame, text="Server URL:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.server_url = ctk.CTkEntry(frame, width=200)
        self.server_url.insert(0, self.settings["system"]["server_url"])
        self.server_url.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # Auto Decrypt
        ctk.CTkLabel(frame, text="Auto-Decrypt Messages:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.auto_dec = ctk.CTkSwitch(frame, text="")
        if self.settings["system"]["auto_decrypt"]: self.auto_dec.select()
        self.auto_dec.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        # Enable Logging
        ctk.CTkLabel(frame, text="Enable Logging:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.logging = ctk.CTkSwitch(frame, text="")
        if self.settings["system"]["enable_logging"]: self.logging.select()
        self.logging.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        # Blockchain Logging
        ctk.CTkLabel(frame, text="Blockchain Ledger Sync:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.blockchain = ctk.CTkSwitch(frame, text="")
        if self.settings["system"]["blockchain_logging"]: self.blockchain.select()
        self.blockchain.grid(row=3, column=1, padx=10, pady=10, sticky="e")

    def change_theme_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def save_all(self):
        updated_settings = {
            "security": {
                "encryption_algorithm": self.enc_algo.get(),
                "digital_signature": self.dig_sig.get() == 1,
                "hash_algorithm": self.hash_algo.get(),
                "key_size": self.key_size.get()
            },
            "ui": {
                "theme": self.theme.get(),
                "font_size": self.font_size.get(),
                "layout": self.layout.get()
            },
            "system": {
                "server_url": self.server_url.get(),
                "auto_decrypt": self.auto_dec.get() == 1,
                "enable_logging": self.logging.get() == 1,
                "blockchain_logging": self.blockchain.get() == 1
            }
        }
        
        if settings_manager.save_settings(updated_settings):
            messagebox.showinfo("Success", "Settings saved successfully and config.json updated!")
        else:
            messagebox.showerror("Error", "Failed to save settings.")

# Test code to run standalone
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Settings Page Test")
    app.geometry("600x800")
    
    frame = SettingsFrame(app, app)
    frame.pack(fill="both", expand=True)
    
    app.mainloop()
