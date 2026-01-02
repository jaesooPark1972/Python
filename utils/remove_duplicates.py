file_path = "D:\\Music_Sound_Level_UP_setup\\ai_audio_studio_pro.py"

# Read the entire file content
with open(file_path, "r", encoding="utf-8") as f:
    file_content = f.read()

# Define the pattern to search and remove (copied exactly from the file content)
pattern_to_remove = """        # [NEW] Pro Quality Options
        self.enhance_dolby = ctk.CTkCheckBox(enhance_panel, text="💎 Neural Dolby Logic (3D)", font=check_font, fg_color=COLOR_AURA_CYAN)
        self.enhance_dolby.pack(anchor="w", padx=25, pady=8)
        
        self.enhance_hifi = ctk.CTkCheckBox(enhance_panel, text="👑 Hi-Fi Ultra Res", font=check_font, fg_color=COLOR_AURA_CYAN)
        self.enhance_hifi.pack(anchor="w", padx=25, pady=8)
        
        ctk.CTkLabel(enhance_panel, text="Reverb Amount:", font=("Arial", 9, "bold"), text_color="white").pack(anchor="w", padx=15, pady=(10, 2))
        reverb_frame = ctk.CTkFrame(enhance_panel, fg_color="transparent")
        reverb_frame.pack(fill="x", padx=15, pady=(0, 5))
        self.enhance_reverb_amount = ctk.CTkSlider(reverb_frame, from_=0, to=50, number_of_steps=50)
        self.enhance_reverb_amount.set(30)
        self.enhance_reverb_amount.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.enhance_reverb_label = ctk.CTkLabel(reverb_frame, text="30 ms", font=("Arial", 9, "bold"), text_color=COLOR_GOLD, width=40)
        self.enhance_reverb_label.pack(side="left")
        self.enhance_reverb_amount.configure(command=lambda v: self.enhance_reverb_label.configure(text=f"{int(v)} ms"))
        
        self.enhance_process_btn = ctk.CTkButton(
            enhance_panel,
            text="💎 EXECUTE NEURAL MIX",
            font=("Arial", 14, "bold"),
            height=45,
            fg_color=COLOR_AURA_CYAN,
            text_color="black",
            hover_color="#00CCDD",
            command=self.start_vocal_enhancement
        )
        self.enhance_process_btn.pack(fill="x", padx=25, pady=(15, 10))
        
        self.enhance_status_label = ctk.CTkLabel(enhance_panel, text="Ready", font=("Arial", 9, "bold"), text_color="#888")
        self.enhance_status_label.pack(pady=(0, 2))
        
        conversion_panel = ctk.CTkFrame(enhance_panel, fg_color="#0A0A0A", border_color="#1A1A1A", border_width=1)
        conversion_panel.pack(fill="x", padx=20, pady=(5, 15))
        
        ctk.CTkLabel(conversion_panel, text="👤 VOICE CONVERSION (.pth)", font=("Arial", 10, "bold"), text_color=COLOR_AURA_CYAN).pack(anchor="w", padx=15, pady=(8, 5))
        
        self.use_rvc_var = ctk.BooleanVar(value=False)
        self.rvc_checkbox = ctk.CTkCheckBox(conversion_panel, text="ENABLE RVC ENGINE", font=("Arial", 10, "bold"), variable=self.use_rvc_var, fg_color=COLOR_AURA_CYAN)
        self.rvc_checkbox.pack(anchor="w", padx=15, pady=5)
        
        self.select_model_btn = ctk.CTkButton(conversion_panel, text="📁 SELECT MODEL", font=("Arial", 10, "bold"), height=32, fg_color=COLOR_BG, border_color="#333", border_width=1, command=self.select_enhance_model)
        self.select_model_btn.pack(fill="x", padx=15, pady=(5, 5))
        
        self.enhance_model_label = ctk.CTkLabel(conversion_panel, text="No model selected", font=("Arial", 9), text_color=COLOR_TEXT_DIM)
        self.enhance_model_label.pack(anchor="w", padx=15, pady=(0, 10))

        # [NEW] AI Voice Optimization Controls
        ctk.CTkLabel(conversion_panel, text="✨ AI VOICE OPTIMIZATION", font=("Arial", 10, "bold"), text_color=COLOR_GOLD).pack(anchor="w", padx=15, pady=(10, 5))
        
        f0_method_frame = ctk.CTkFrame(conversion_panel, fg_color="transparent")
        f0_method_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(f0_method_frame, text="추출 알고리즘:", font=("Arial", 9), text_color="white").pack(side="left", padx=(0, 10))
        self.f0_method_var = ctk.StringVar(value="RMVPE")
        self.f0_method_option = ctk.CTkSegmentedButton(
            f0_method_frame,
            values=["RMVPE", "Harvest", "Crepe"],
            variable=self.f0_method_var,
            font=("Arial", 9),
            height=26,
            fg_color="#222",
            selected_color=COLOR_AURA_CYAN
        )
        self.f0_method_option.pack(side="left", fill="x", expand=True)

        index_rate_frame = ctk.CTkFrame(conversion_panel, fg_color="transparent")
        index_rate_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(index_rate_frame, text="인덱스 비율:", font=("Arial", 9), text_color="white").pack(side="left", padx=(0, 10))
        self.index_rate_slider = ctk.CTkSlider(index_rate_frame, from_=0.0, to=1.0, number_of_steps=20, button_color=COLOR_GOLD, progress_color=COLOR_GOLD)
        self.index_rate_slider.set(0.4)
        self.index_rate_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.index_rate_label = ctk.CTkLabel(index_rate_frame, text="0.40", font=("Arial", 9, "bold"), text_color=COLOR_GOLD, width=40)
        self.index_rate_label.pack(side="left")
        self.index_rate_slider.configure(command=lambda v: self.index_rate_label.configure(text=f"{v:.2f}"))

        protect_frame = ctk.CTkFrame(conversion_panel, fg_color="transparent")
        protect_frame.pack(fill="x", padx=15, pady=(5, 10))
        ctk.CTkLabel(protect_frame, text="성대 보호:", font=("Arial", 9), text_color="white").pack(side="left", padx=(0, 10))
        self.protect_slider = ctk.CTkSlider(protect_frame, from_=0.0, to=0.5, number_of_steps=50, button_color=COLOR_GOLD, progress_color=COLOR_GOLD)
        self.protect_slider.set(0.33)
        self.protect_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.protect_label = ctk.CTkLabel(protect_frame, text="0.33", font=("Arial", 9, "bold"), text_color=COLOR_GOLD, width=40)
        self.protect_label.pack(side="left")
        self.protect_slider.configure(command=lambda v: self.protect_label.configure(text=f"{v:.2f}"))
"""

# Replace all occurrences of the pattern except the first one
# We need to count the occurrences and replace all but the first.
# Python's str.replace replaces all by default.
# To replace all but the first, we can find the first occurrence,
# then replace subsequent occurrences in the rest of the string.

# Find the index of the first occurrence
first_occurrence_index = file_content.find(pattern_to_remove)

if first_occurrence_index != -1:
    # Keep the part before the first occurrence and the first occurrence itself
    content_before_first = file_content[:first_occurrence_index + len(pattern_to_remove)]
    content_after_first = file_content[first_occurrence_index + len(pattern_to_remove):]
    
    # Replace all occurrences in the rest of the string
    modified_content_after_first = content_after_first.replace(pattern_to_remove, "")
    
    # Combine everything back
    modified_file_content = content_before_first + modified_content_after_first
    
    # Write the modified content back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(modified_file_content)
    print("Successfully removed duplicate UI blocks.")
else:
    print("Pattern not found in the file. No changes made.")
