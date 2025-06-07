import os
import shutil
import time
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import dearpygui.dearpygui as dpg
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
import colorsys
from enum import Enum

class ThemeColor(Enum):
    PRIMARY = (0, 120, 215)
    SECONDARY = (100, 150, 220)
    BACKGROUND = (245, 245, 245)
    CARD = (255, 255, 255)
    TEXT = (51, 51, 51)
    TEXT_SECONDARY = (102, 102, 102)
    BORDER = (230, 230, 230)
    HOVER = (240, 240, 240)
    SUCCESS = (46, 204, 113)
    WARNING = (230, 126, 34)
    DANGER = (231, 76, 60)

# File type categories
FILE_CATEGORIES = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Audio': ['.mp3', '.wav', '.ogg', '.flac', '.aac'],
    'Videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'],
    'Code': ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.h', '.json', '.xml'],
    'Executables': ['.exe', '.msi', '.bat', '.sh']
}

class FileOrganizer:
    def __init__(self):
        self.current_dir = str(Path.home() / "Documents")
        self.sort_methods = ["Name (A-Z)", "Name (Z-A)", "Date Modified (Newest)", 
                           "Date Modified (Oldest)", "Size (Largest)", "Size (Smallest)"]
        self.current_sort = self.sort_methods[0]
        self.files: List[Dict] = []
        self.setup_gui()
        dpg.set_primary_window("Primary Window", True)
        
    def get_category(self, filename: str) -> str:
        """Determine the category of a file based on its extension."""
        ext = os.path.splitext(filename)[1].lower()
        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        return 'Other'
        
    def organize_files(self):
        """Organize files in the current directory into subdirectories by category."""
        if not os.path.isdir(self.current_dir):
            return
            
        # Get all files in the current directory
        try:
            items = os.listdir(self.current_dir)
            moved_files = 0
            
            for item in items:
                item_path = os.path.join(self.current_dir, item)
                if os.path.isfile(item_path):
                    # Skip if it's a hidden file or this script
                    if item.startswith('.') or item == os.path.basename(__file__):
                        continue
                        
                    # Get the category and create directory if it doesn't exist
                    category = self.get_category(item)
                    category_dir = os.path.join(self.current_dir, category)
                    os.makedirs(category_dir, exist_ok=True)
                    
                    # Move the file
                    dest_path = os.path.join(category_dir, item)
                    try:
                        # Handle duplicate filenames
                        counter = 1
                        base, ext = os.path.splitext(item)
                        while os.path.exists(dest_path):
                            new_name = f"{base}_{counter}{ext}"
                            dest_path = os.path.join(category_dir, new_name)
                            counter += 1
                            
                        shutil.move(item_path, dest_path)
                        moved_files += 1
                    except Exception as e:
                        print(f"Error moving {item}: {e}")
            
            # Show completion message
            if moved_files > 0:
                tk.messagebox.showinfo(
                    "Organization Complete",
                    f"Successfully organized {moved_files} file(s) into categories."
                )
                self.update_file_list()  # Refresh the file list
            else:
                tk.messagebox.showinfo(
                    "No Files to Organize",
                    "No files were found that needed to be organized."
                )
                
        except Exception as e:
            tk.messagebox.showerror(
                "Error",
                f"An error occurred while organizing files: {str(e)}"
            )

    def get_file_info(self, file_path: str) -> Optional[Dict]:
        try:
            stats = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stats.st_size,
                'modified': stats.st_mtime,
                'is_dir': os.path.isdir(file_path)
            }
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return None

    def list_files(self, directory: str) -> List[Dict]:
        try:
            items = []
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                if file_info := self.get_file_info(full_path):
                    items.append(file_info)
            return items
        except Exception as e:
            print(f"Error listing directory {directory}: {e}")
            return []

    def sort_files(self, files: List[Dict]) -> List[Dict]:
        if not files:
            return []

        # Make a copy to avoid modifying the original list
        sorted_files = files.copy()
        
        if "Name (A-Z)" in self.current_sort:
            sorted_files.sort(key=lambda x: x['name'].lower())
        elif "Name (Z-A)" in self.current_sort:
            sorted_files.sort(key=lambda x: x['name'].lower(), reverse=True)
        elif "Date Modified (Newest)" in self.current_sort:
            sorted_files.sort(key=lambda x: x['modified'], reverse=True)
        elif "Date Modified (Oldest)" in self.current_sort:
            sorted_files.sort(key=lambda x: x['modified'])
        elif "Size (Largest)" in self.current_sort:
            sorted_files.sort(key=lambda x: x['size'], reverse=True)
        elif "Size (Smallest)" in self.current_sort:
            sorted_files.sort(key=lambda x: x['size'])
            
        # Always put directories first when sorting by name
        if "Name" in self.current_sort:
            sorted_files.sort(key=lambda x: not x['is_dir'])
            
        return sorted_files

    def update_file_list(self):
        """Update the file list display with current directory contents."""
        self.files = self.list_files(self.current_dir)
        self.files = self.sort_files(self.files)
        
        if dpg.does_item_exist("file_list"):
            dpg.delete_item("file_list", children_only=True)
            
            # Add header
            with dpg.table_row(parent="file_list"):
                dpg.add_text("Name", width=400)
                dpg.add_text("Size", width=100)
                dpg.add_text("Modified", width=200)
            
            # Add files and directories with better styling
            for file_info in self.files:
                with dpg.table_row(parent="file_list"):
                    # Determine icon based on file type
                    if file_info['is_dir']:
                        icon = "📁"
                        name_color = ThemeColor.PRIMARY.value
                    else:
                        ext = os.path.splitext(file_info['name'])[1].lower()
                        if ext in FILE_CATEGORIES['Images']:
                            icon = "🖼️"
                        elif ext in FILE_CATEGORIES['Documents']:
                            icon = "📄"
                        elif ext in FILE_CATEGORIES['Archives']:
                            icon = "🗜️"
                        elif ext in FILE_CATEGORIES['Audio']:
                            icon = "🎵"
                        elif ext in FILE_CATEGORIES['Videos']:
                            icon = "🎬"
                        elif ext in FILE_CATEGORIES['Code']:
                            icon = "</>"
                        elif ext in FILE_CATEGORIES['Executables']:
                            icon = "⚙️"
                        else:
                            icon = "📄"
                        name_color = ThemeColor.TEXT.value
                    
                    # Add file/directory name with icon
                    with dpg.group(horizontal=True):
                        dpg.add_text(icon)
                        dpg.add_text(file_info['name'], color=name_color)
                    
                    # Add size (formatted)
                    if not file_info['is_dir']:
                        dpg.add_text(self.format_size(file_info['size']), color=ThemeColor.TEXT_SECONDARY.value)
                    else:
                        dpg.add_text("--", color=ThemeColor.TEXT_SECONDARY.value)
                    
                    # Add modified time
                    mod_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(file_info['modified']))
                    dpg.add_text(mod_time, color=ThemeColor.TEXT_SECONDARY.value)
            
            # Update status bar
            file_count = len([f for f in self.files if not f['is_dir']])
            dir_count = len(self.files) - file_count
            dpg.set_value("item_count", f"{len(self.files)} items ({dir_count} folders, {file_count} files)")
    
    def run(self):
        """Run the application."""
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
    
    def on_nav_up(self):
        """Navigate to the parent directory."""
        parent = os.path.dirname(self.current_dir)
        if os.path.exists(parent) and os.path.normpath(parent) != os.path.normpath(self.current_dir):
            self.current_dir = parent
            dpg.set_value("current_dir_input", self.current_dir)
            self.update_file_list()
    
    def on_directory_select(self):
        """Open a directory selection dialog."""
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        root.attributes('-topmost', True)  # Bring dialog to front
        selected_dir = filedialog.askdirectory(
            initialdir=self.current_dir,
            title="Select Folder to Organize"
        )
        if selected_dir:
            self.current_dir = selected_dir
            dpg.set_value("current_dir_input", self.current_dir)
            self.update_file_list()
        root.destroy()  # Clean up the Tkinter window
    
    def on_sort_changed(self, sender, app_data):
        """Handle sort method change."""
        self.current_sort = dpg.get_value(sender)
        self.update_file_list()
    
    def setup_gui(self):
        """Set up the graphical user interface."""
        dpg.create_context()
        dpg.create_viewport(title="File Organizer", width=1000, height=700)
        dpg.setup_dearpygui()
        
        # Set global font
        with dpg.font_registry() as font_registry:
            try:
                # Try to load Segoe UI font
                default_font = dpg.add_font("C:\\Windows\\Fonts\\segoeui.ttf", 14, parent=font_registry, tag="default_font")
                dpg.bind_font(default_font)
            except Exception as e:
                print(f"Warning: Could not load Segoe UI font: {e}")
                # Fall back to default font
                try:
                    default_font = dpg.add_font("roboto.ttf", 14, parent=font_registry, tag="default_font")
                    dpg.bind_font(default_font)
                except Exception as e:
                    print(f"Warning: Could not load fallback font: {e}")
        
        # Set up theme
        theme = self.setup_theme()
        
        # Create main window
        with dpg.window(tag="Primary Window"):
            dpg.bind_theme(theme)
            
            # Header with current directory
            with dpg.group(horizontal=True):
                dpg.add_text("File Organizer")
                dpg.add_spacer()
                dpg.add_input_text(
                    default_value=self.current_dir,
                    width=-1,
                    tag="current_dir_input",
                    readonly=True
                )
            
            # Toolbar with controls
            with dpg.group(horizontal=True):
                # Navigation buttons
                nav_buttons = [
                    ("⬆️ Up", self.on_nav_up, 80),
                    ("📂 Browse", self.on_directory_select, 120),
                    ("🔄 Refresh", lambda: self.update_file_list(), 100),
                    ("🗂️ Organize", self.organize_files, 120)
                ]
                
                for label, callback, width in nav_buttons:
                    dpg.add_button(
                        label=label,
                        callback=callback,
                        width=width,
                        height=30
                    )
                
                dpg.add_spacer()
                
                # Sort dropdown
                with dpg.group(horizontal=True):
                    dpg.add_text("Sort by:", color=(80, 80, 80))
                    dpg.add_combo(
                        items=self.sort_methods,
                        default_value=self.current_sort,
                        width=180,
                        callback=self.on_sort_changed,
                        tag="sort_combo"
                    )
            
            # File list
            with dpg.child_window(
                tag="file_list_container",
                width=-1,
                height=-40,  # Leave space for status bar
                border=False
            ):
                with dpg.table(
                    tag="file_list",
                    header_row=True,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=False,
                    borders_outerV=True,
                    row_background=True,
                    policy=dpg.mvTable_SizingFixedFit,
                    resizable=True,
                    reorderable=True,
                    hideable=True,
                    sort_multi=False,
                    sort_tristate=False,
                    height=-1,
                    width=-1,
                    scrollY=True,
                ):
                    dpg.add_table_column(label="Name", width_stretch=True, init_width_or_weight=0.6)
                    dpg.add_table_column(label="Size", width_fixed=True, init_width_or_weight=0.2)
                    dpg.add_table_column(label="Modified", width_fixed=True, init_width_or_weight=0.2)
            
            # Status bar
            with dpg.group(tag="status_bar", horizontal=True, width=-1, height=30):
                dpg.add_text("Ready", tag="status_text")
                dpg.add_spacer()
                dpg.add_text("0 items", tag="item_count")
        
        # Configure viewport
        dpg.set_primary_window("Primary Window", True)
        dpg.set_viewport_resize_callback(self._on_viewport_resize)
        self._on_viewport_resize(None, None)  # Initial resize
    
    def _on_viewport_resize(self, sender, app_data):
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        dpg.set_item_width("Primary Window", viewport_width)
        dpg.set_item_height("Primary Window", viewport_height)
        
        # Update file list container height
        if dpg.does_item_exist("file_list_container"):
            dpg.set_item_height("file_list_container", viewport_height - 160)  # Adjust based on header and toolbar heights
    
    def _adjust_color(self, color, factor):
        """Adjust color brightness by factor"""
        if isinstance(color, tuple):
            r, g, b = color[:3]
            h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
            l = max(0, min(1, l * factor))
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return (int(r*255), int(g*255), int(b*255))
        return color
    
    def setup_theme(self):
        # Create a custom dark theme with modern colors and rounded corners
        with dpg.theme() as theme:
            # Base colors - dark theme
            colors = {
                'window_bg': (30, 30, 35),          # Dark background
                'child_bg': (40, 40, 45),          # Slightly lighter than window
                'border': (60, 60, 70),            # Dark border
                'text': (220, 220, 220),           # Light text
                'text_secondary': (180, 180, 190),  # Slightly dimmer text
                'primary': (0, 120, 215),           # Blue accent
                'primary_hover': (0, 145, 245),     # Lighter blue on hover
                'primary_active': (0, 95, 180),     # Darker blue when active
                'button': (60, 60, 70),             # Dark button
                'button_hover': (80, 80, 90),        # Lighter on hover
                'button_active': (40, 40, 50),       # Darker when active
                'success': (46, 204, 113),           # Green
                'warning': (255, 193, 7),            # Amber
                'danger': (255, 82, 82),             # Red
            }
            
            # Global styles - apply to all components
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, colors['window_bg'])
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, colors['child_bg'])
                dpg.add_theme_color(dpg.mvThemeCol_Border, colors['border'])
                dpg.add_theme_color(dpg.mvThemeCol_Text, colors['text'])
                dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (120, 120, 120))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (40, 40, 45))
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 6, 6)
                dpg.add_theme_style(dpg.mvStyleVar_IndentSpacing, 20)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 10)
                dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 10)
            
            # Button styles
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, colors['button'])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, colors['button_hover'])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, colors['button_active'])
                dpg.add_theme_color(dpg.mvThemeCol_Text, colors['text'])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 6)
            
            # Input text styles
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (60, 60, 70))
                dpg.add_theme_color(dpg.mvThemeCol_Text, colors['text'])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            
            # Combo box styles
            with dpg.theme_component(dpg.mvCombo):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 4)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (60, 60, 70))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (80, 80, 90))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (100, 100, 110))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (70, 70, 80))
                dpg.add_theme_color(dpg.mvThemeCol_Text, colors['text'])
            
            # Table styles
            with dpg.theme_component(dpg.mvTable):
                dpg.add_theme_color(dpg.mvThemeCol_Header, (50, 50, 60))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (70, 70, 85))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (90, 90, 100))
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, (40, 40, 45))
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (45, 45, 50))
            
            # Selectable styles
            with dpg.theme_component(dpg.mvSelectable):
                dpg.add_theme_color(dpg.mvThemeCol_Header, colors['primary'])
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, self._adjust_color(colors['primary'], 1.1))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, self._adjust_color(colors['primary'], 0.9))
        
        # Apply the theme
        dpg.bind_theme(theme)
        return theme
        

    
    def run(self):
        """Run the application."""
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

if __name__ == "__main__":
    app = FileOrganizer()
    app.run()
