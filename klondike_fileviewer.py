"""
Klondike Archiver - Enhanced File Viewer Module
Provides advanced file viewing capabilities for different file types
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tempfile
import subprocess
import os
import sys
from pathlib import Path
import json
import base64

class EnhancedFileViewer:
    """
    Enhanced file viewer that can display various file types
    with syntax highlighting, image preview, and more
    """
    
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.temp_files = []  # Track temporary files for cleanup
        
        # Supported text file extensions with syntax highlighting
        self.text_extensions = {
            '.py': 'python',
            '.js': 'javascript', 
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml',
            '.md': 'markdown',
            '.txt': 'text',
            '.log': 'text',
            '.csv': 'csv',
            '.sql': 'sql',
            '.ini': 'ini',
            '.cfg': 'config',
            '.conf': 'config'
        }
        
        # Image extensions
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
        
        # Binary file extensions that shouldn't be viewed as text
        self.binary_extensions = {'.exe', '.dll', '.so', '.dylib', '.zip', '.rar', '.7z', 
                                '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.pdf', '.doc', '.docx'}
    
    def view_file(self, filename, file_data):
        """
        Open enhanced viewer for a file
        
        Args:
            filename: Name of the file
            file_data: Raw file data
        """
        if not file_data:
            messagebox.showerror("Error", f"Could not load data for {filename}")
            return
        
        file_ext = Path(filename).suffix.lower()
        
        # Determine how to view the file
        if file_ext in self.text_extensions:
            self._view_text_file(filename, file_data, file_ext)
        elif file_ext in self.image_extensions:
            self._view_image_file(filename, file_data)
        elif file_ext in self.binary_extensions:
            self._view_binary_file(filename, file_data, file_ext)
        else:
            # Try to view as text, fallback to hex if not valid
            self._view_unknown_file(filename, file_data)
    
    def _view_text_file(self, filename, file_data, file_ext):
        """View text file with syntax highlighting"""
        try:
            # Try to decode as text
            text_content = file_data.decode('utf-8', errors='replace')
            
            # Create viewer window
            viewer = tk.Toplevel(self.parent_app.root)
            viewer.title(f"📝 Text Viewer - {filename}")
            viewer.geometry("900x700")
            viewer.minsize(600, 400)
            
            # Set icon
            try:
                if hasattr(self.parent_app, 'set_app_icon'):
                    viewer.iconbitmap(self.parent_app.root.iconbitmap())
            except:
                pass
            
            # Create main frame
            main_frame = ttk.Frame(viewer, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            viewer.columnconfigure(0, weight=1)
            viewer.rowconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=1)
            main_frame.rowconfigure(1, weight=1)
            
            # Header with file info
            header_frame = ttk.Frame(main_frame)
            header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            header_frame.columnconfigure(1, weight=1)
            
            ttk.Label(header_frame, text=f"📄 {filename}", 
                     font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
            
            # File statistics
            lines = text_content.count('\n') + 1
            chars = len(text_content)
            size_str = self.parent_app.format_file_size(len(file_data))
            
            stats_text = f"Lines: {lines:,} | Characters: {chars:,} | Size: {size_str}"
            ttk.Label(header_frame, text=stats_text, 
                     font=("Segoe UI", 9), foreground="gray").grid(row=0, column=1, sticky=tk.E)
            
            # Toolbar
            toolbar_frame = ttk.Frame(main_frame)
            toolbar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            ttk.Button(toolbar_frame, text="💾 Save As...", 
                      command=lambda: self._save_file_as(filename, file_data)).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(toolbar_frame, text="🔍 Find...", 
                      command=lambda: self._show_find_dialog(text_widget)).pack(side=tk.LEFT, padx=5)
            ttk.Button(toolbar_frame, text="📋 Copy All", 
                      command=lambda: self._copy_to_clipboard(text_content)).pack(side=tk.LEFT, padx=5)
            
            # Text widget with scrollbars
            text_frame = ttk.Frame(main_frame)
            text_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)
            
            text_widget = tk.Text(text_frame, wrap=tk.NONE, font=("Consolas", 10),
                                 relief=tk.SUNKEN, borderwidth=2)
            text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            text_widget.configure(yscrollcommand=v_scrollbar.set)
            
            h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
            h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
            text_widget.configure(xscrollcommand=h_scrollbar.set)
            
            # Insert text
            text_widget.insert(1.0, text_content)
            text_widget.configure(state=tk.DISABLED)  # Read-only
            
            # Apply basic syntax highlighting
            self._apply_syntax_highlighting(text_widget, text_content, file_ext)
            
            # Status bar
            status_frame = ttk.Frame(main_frame)
            status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
            
            status_text = f"File type: {self.text_extensions.get(file_ext, 'text')} | Encoding: UTF-8"
            ttk.Label(status_frame, text=status_text, font=("Segoe UI", 8), 
                     relief=tk.SUNKEN, padding="5").grid(row=0, column=0, sticky=(tk.W, tk.E))
            status_frame.columnconfigure(0, weight=1)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not display text file: {str(e)}")
    
    def _view_image_file(self, filename, file_data):
        """View image file with basic image viewer"""
        try:
            # Create temporary file
            temp_file = self._create_temp_file(filename, file_data)
            if not temp_file:
                return
            
            # Try to use PIL for better image handling
            try:
                from PIL import Image, ImageTk
                self._view_image_with_pil(filename, temp_file)
            except ImportError:
                # Fallback to basic Tkinter PhotoImage
                self._view_image_basic(filename, temp_file)
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not display image: {str(e)}")
    
    def _view_image_with_pil(self, filename, temp_file_path):
        """View image using PIL for better format support"""
        from PIL import Image, ImageTk
        
        # Open image
        image = Image.open(temp_file_path)
        
        # Create viewer window
        viewer = tk.Toplevel(self.parent_app.root)
        viewer.title(f"🖼️ Image Viewer - {filename}")
        
        # Get image dimensions
        img_width, img_height = image.size
        
        # Calculate window size (max 800x600, maintain aspect ratio)
        max_width, max_height = 800, 600
        if img_width > max_width or img_height > max_height:
            ratio = min(max_width / img_width, max_height / img_height)
            display_width = int(img_width * ratio)
            display_height = int(img_height * ratio)
            image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        else:
            display_width, display_height = img_width, img_height
        
        viewer.geometry(f"{display_width + 40}x{display_height + 120}")
        
        # Main frame
        main_frame = ttk.Frame(viewer, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        viewer.columnconfigure(0, weight=1)
        viewer.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text=f"🖼️ {filename}", 
                 font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
        
        # Image info
        size_str = self.parent_app.format_file_size(len(open(temp_file_path, 'rb').read()))
        info_text = f"{img_width}x{img_height} pixels | {size_str}"
        ttk.Label(header_frame, text=info_text, 
                 font=("Segoe UI", 9), foreground="gray").grid(row=0, column=1, sticky=tk.E)
        
        # Toolbar
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="💾 Save As...", 
                  command=lambda: self._save_temp_file_as(filename, temp_file_path)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="🔍 Zoom Fit", 
                  command=lambda: None).pack(side=tk.LEFT, padx=5)  # Placeholder
        
        # Image display
        photo = ImageTk.PhotoImage(image)
        image_label = ttk.Label(main_frame, image=photo)
        image_label.image = photo  # Keep a reference
        image_label.grid(row=2, column=0, pady=10)
        
    def _view_image_basic(self, filename, temp_file_path):
        """Basic image viewer using Tkinter PhotoImage"""
        viewer = tk.Toplevel(self.parent_app.root)
        viewer.title(f"🖼️ Image Viewer - {filename}")
        
        try:
            # Try to load image
            photo = tk.PhotoImage(file=temp_file_path)
            
            # Calculate window size
            img_width = photo.width()
            img_height = photo.height()
            viewer.geometry(f"{img_width + 40}x{img_height + 80}")
            
            # Main frame
            main_frame = ttk.Frame(viewer, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            ttk.Label(main_frame, text=f"🖼️ {filename}", 
                     font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))
            
            # Image
            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo  # Keep reference
            image_label.pack()
            
        except tk.TclError:
            messagebox.showerror("Error", f"Unsupported image format for {filename}")
            viewer.destroy()
    
    def _view_binary_file(self, filename, file_data, file_ext):
        """View binary file with hex dump and file info"""
        viewer = tk.Toplevel(self.parent_app.root)
        viewer.title(f"🔧 Binary Viewer - {filename}")
        viewer.geometry("900x600")
        viewer.minsize(600, 400)
        
        # Main frame
        main_frame = ttk.Frame(viewer, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        viewer.columnconfigure(0, weight=1)
        viewer.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text=f"🔧 {filename}", 
                 font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
        
        size_str = self.parent_app.format_file_size(len(file_data))
        ttk.Label(header_frame, text=f"Binary file | {size_str}", 
                 font=("Segoe UI", 9), foreground="gray").grid(row=0, column=1, sticky=tk.E)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="View Options", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(options_frame, text="💾 Save As...", 
                  command=lambda: self._save_file_as(filename, file_data)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(options_frame, text="🚀 Open with System Default", 
                  command=lambda: self._open_with_system(filename, file_data)).pack(side=tk.LEFT, padx=10)
        
        # Hex dump
        hex_frame = ttk.LabelFrame(main_frame, text="Hex Dump (First 1KB)", padding="10")
        hex_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        hex_frame.columnconfigure(0, weight=1)
        hex_frame.rowconfigure(0, weight=1)
        
        hex_text = tk.Text(hex_frame, wrap=tk.NONE, font=("Consolas", 9),
                          relief=tk.SUNKEN, borderwidth=2)
        hex_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars for hex dump
        v_scrollbar = ttk.Scrollbar(hex_frame, orient=tk.VERTICAL, command=hex_text.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hex_text.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(hex_frame, orient=tk.HORIZONTAL, command=hex_text.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        hex_text.configure(xscrollcommand=h_scrollbar.set)
        
        # Generate hex dump
        hex_dump = self._generate_hex_dump(file_data[:1024])  # First 1KB only
        hex_text.insert(1.0, hex_dump)
        hex_text.configure(state=tk.DISABLED)
    
    def _view_unknown_file(self, filename, file_data):
        """View unknown file type - try text first, then binary"""
        try:
            # Try to decode as UTF-8 text
            text_content = file_data.decode('utf-8')
            # If successful, treat as text file
            self._view_text_file(filename, file_data, '')
        except UnicodeDecodeError:
            # If can't decode as text, treat as binary
            self._view_binary_file(filename, file_data, '')
    
    def _apply_syntax_highlighting(self, text_widget, content, file_ext):
        """Apply basic syntax highlighting"""
        text_widget.configure(state=tk.NORMAL)
        
        # Define some basic highlighting colors
        text_widget.tag_configure("comment", foreground="#008000")  # Green
        text_widget.tag_configure("string", foreground="#FF6600")   # Orange
        text_widget.tag_configure("keyword", foreground="#0000FF", font=("Consolas", 10, "bold"))  # Blue
        text_widget.tag_configure("number", foreground="#FF0000")   # Red
        
        lines = content.split('\n')
        
        if file_ext == '.py':
            self._highlight_python(text_widget, lines)
        elif file_ext == '.js':
            self._highlight_javascript(text_widget, lines)
        elif file_ext == '.json':
            self._highlight_json(text_widget, content)
        # Add more syntax highlighting as needed
        
        text_widget.configure(state=tk.DISABLED)
    
    def _highlight_python(self, text_widget, lines):
        """Basic Python syntax highlighting"""
        python_keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 
                          'import', 'from', 'return', 'and', 'or', 'not', 'in', 'is', 'with', 'as']
        
        for line_num, line in enumerate(lines, 1):
            # Comments
            if '#' in line:
                comment_start = line.find('#')
                start_pos = f"{line_num}.{comment_start}"
                end_pos = f"{line_num}.end"
                text_widget.tag_add("comment", start_pos, end_pos)
            
            # Keywords
            words = line.split()
            col = 0
            for word in words:
                if word in python_keywords:
                    start_pos = f"{line_num}.{col}"
                    end_pos = f"{line_num}.{col + len(word)}"
                    text_widget.tag_add("keyword", start_pos, end_pos)
                col = line.find(word, col) + len(word)
    
    def _highlight_javascript(self, text_widget, lines):
        """Basic JavaScript syntax highlighting"""
        js_keywords = ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 
                      'return', 'true', 'false', 'null', 'undefined', 'class',
                      'try', 'catch', 'finally', 'throw', 'new', 'this']
        
        for line_num, line in enumerate(lines, 1):
            # Comments
            if '//' in line:
                comment_start = line.find('//')
                start_pos = f"{line_num}.{comment_start}"
                end_pos = f"{line_num}.end"
                text_widget.tag_add("comment", start_pos, end_pos)
            
            # Keywords
            words = line.split()
            col = 0
            for word in words:
                clean_word = word.strip('();{}[]')
                if clean_word in js_keywords:
                    start_pos = f"{line_num}.{col}"
                    end_pos = f"{line_num}.{col + len(word)}"
                    text_widget.tag_add("keyword", start_pos, end_pos)
                col = line.find(word, col) + len(word)
    
    def _highlight_json(self, text_widget, content):
        """Basic JSON syntax highlighting"""
        try:
            # Parse JSON to validate and re-format
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=2)
            
            # Replace content with formatted version
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, formatted)
            
            # Simple highlighting for JSON
            lines = formatted.split('\n')
            for line_num, line in enumerate(lines, 1):
                # String values (in quotes)
                import re
                for match in re.finditer(r'"([^"]*)"', line):
                    start_col = match.start()
                    end_col = match.end()
                    start_pos = f"{line_num}.{start_col}"
                    end_pos = f"{line_num}.{end_col}"
                    text_widget.tag_add("string", start_pos, end_pos)
                
                # Numbers
                for match in re.finditer(r'\b\d+\.?\d*\b', line):
                    start_col = match.start()
                    end_col = match.end()
                    start_pos = f"{line_num}.{start_col}"
                    end_pos = f"{line_num}.{end_col}"
                    text_widget.tag_add("number", start_pos, end_pos)
                    
        except json.JSONDecodeError:
            pass  # If not valid JSON, just display as is
    
    def _generate_hex_dump(self, data):
        """Generate a hex dump representation of binary data"""
        hex_lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            
            # Offset
            offset = f"{i:08X}"
            
            # Hex representation
            hex_part = ' '.join(f"{b:02X}" for b in chunk)
            hex_part = hex_part.ljust(47)  # Pad to fixed width
            
            # ASCII representation
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            
            hex_lines.append(f"{offset}  {hex_part}  |{ascii_part}|")
        
        return '\n'.join(hex_lines)
    
    def _create_temp_file(self, filename, file_data):
        """Create a temporary file with the given data"""
        try:
            # Create temp file with proper extension
            file_ext = Path(filename).suffix
            temp_fd, temp_path = tempfile.mkstemp(suffix=file_ext, prefix="klondike_")
            
            with os.fdopen(temp_fd, 'wb') as temp_file:
                temp_file.write(file_data)
            
            self.temp_files.append(temp_path)
            return temp_path
        except Exception as e:
            messagebox.showerror("Error", f"Could not create temporary file: {str(e)}")
            return None
    
    def _save_file_as(self, filename, file_data):
        """Save file data to user-chosen location"""
        file_path = filedialog.asksaveasfilename(
            title=f"Save {filename} As...",
            initialname=filename,
            defaultextension=Path(filename).suffix,
            filetypes=[
                ("All files", "*.*"),
                (f"{Path(filename).suffix.upper()} files", f"*{Path(filename).suffix}")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                messagebox.showinfo("Success", f"File saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def _save_temp_file_as(self, filename, temp_file_path):
        """Save temporary file to user-chosen location"""
        file_path = filedialog.asksaveasfilename(
            title=f"Save {filename} As...",
            initialname=filename,
            defaultextension=Path(filename).suffix,
            filetypes=[
                ("All files", "*.*"),
                (f"{Path(filename).suffix.upper()} files", f"*{Path(filename).suffix}")
            ]
        )
        
        if file_path:
            try:
                import shutil
                shutil.copy2(temp_file_path, file_path)
                messagebox.showinfo("Success", f"File saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.parent_app.root.clipboard_clear()
            self.parent_app.root.clipboard_append(text)
            messagebox.showinfo("Success", "Text copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy to clipboard: {str(e)}")
    
    def _show_find_dialog(self, text_widget):
        """Show find dialog for text search"""
        find_window = tk.Toplevel(self.parent_app.root)
        find_window.title("Find Text")
        find_window.geometry("400x150")
        find_window.resizable(False, False)
        
        # Make it modal
        find_window.transient(self.parent_app.root)
        find_window.grab_set()
        
        main_frame = ttk.Frame(find_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search input
        ttk.Label(main_frame, text="Find:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        search_var = tk.StringVar()
        search_entry = ttk.Entry(main_frame, textvariable=search_var, width=40)
        search_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        search_entry.focus()
        
        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        case_sensitive_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Case sensitive", 
                       variable=case_sensitive_var).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=tk.E)
        
        def find_text():
            search_term = search_var.get()
            if not search_term:
                return
            
            # Clear previous highlights
            text_widget.tag_remove("search_highlight", 1.0, tk.END)
            
            # Configure highlight tag
            text_widget.tag_configure("search_highlight", background="yellow")
            
            # Get text content
            content = text_widget.get(1.0, tk.END)
            
            if not case_sensitive_var.get():
                content = content.lower()
                search_term = search_term.lower()
            
            # Find all occurrences
            start_pos = 0
            count = 0
            while True:
                pos = content.find(search_term, start_pos)
                if pos == -1:
                    break
                
                # Convert to line.column format
                lines_before = content[:pos].count('\n')
                col = pos - content.rfind('\n', 0, pos) - 1
                
                start_index = f"{lines_before + 1}.{col}"
                end_index = f"{lines_before + 1}.{col + len(search_term)}"
                
                text_widget.tag_add("search_highlight", start_index, end_index)
                count += 1
                start_pos = pos + 1
            
            if count > 0:
                messagebox.showinfo("Find Results", f"Found {count} occurrence(s)")
                # Scroll to first match
                first_match = text_widget.tag_ranges("search_highlight")[0]
                text_widget.see(first_match)
            else:
                messagebox.showinfo("Find Results", "Text not found")
        
        ttk.Button(button_frame, text="Find All", command=find_text).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=find_window.destroy).pack(side=tk.RIGHT)
        
        # Bind Enter key to find
        search_entry.bind('<Return>', lambda e: find_text())
    
    def _open_with_system(self, filename, file_data):
        """Open file with system default application"""
        temp_file = self._create_temp_file(filename, file_data)
        if not temp_file:
            return
        
        try:
            if sys.platform.startswith('win'):
                os.startfile(temp_file)
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', temp_file], check=True)
            else:  # Linux and others
                subprocess.run(['xdg-open', temp_file], check=True)
                
            messagebox.showinfo("File Opened", 
                               f"File opened with system default application.\n"
                               f"Temporary file: {temp_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file with system default: {str(e)}")
    
    def cleanup_temp_files(self):
        """Clean up temporary files created by the viewer"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass  # Ignore cleanup errors
        self.temp_files.clear()

class FileTypeAnalyzer:
    """
    Utility class to analyze and identify file types
    """
    
    # File signatures (magic numbers) for binary file detection
    FILE_SIGNATURES = {
        b'\x89PNG\r\n\x1a\n': 'PNG Image',
        b'\xff\xd8\xff': 'JPEG Image',
        b'GIF87a': 'GIF Image',
        b'GIF89a': 'GIF Image',
        b'BM': 'Bitmap Image',
        b'RIFF': 'RIFF Container (WAV/AVI)',
        b'%PDF': 'PDF Document',
        b'PK\x03\x04': 'ZIP Archive',
        b'PK\x05\x06': 'ZIP Archive (empty)',
        b'PK\x07\x08': 'ZIP Archive (spanned)',
        b'\x7fELF': 'ELF Executable',
        b'MZ': 'DOS/Windows Executable',
        b'\xca\xfe\xba\xbe': 'Java Class File',
        b'\xfe\xed\xfa': 'Mach-O Executable (macOS)',
        b'\x00\x00\x01\x00': 'Windows Icon',
        b'ID3': 'MP3 Audio',
        b'\x1a\x45\xdf\xa3': 'Matroska Video'
    }
    
    @classmethod
    def analyze_file(cls, filename, file_data):
        """
        Analyze file and return detailed information
        
        Args:
            filename: Name of the file
            file_data: Raw file data
            
        Returns:
            Dictionary with file analysis
        """
        analysis = {
            'filename': filename,
            'size': len(file_data),
            'extension': Path(filename).suffix.lower(),
            'is_text': False,
            'is_binary': False,
            'file_type': 'Unknown',
            'encoding': None,
            'line_count': None,
            'signature': None
        }
        
        # Check file signature
        for signature, file_type in cls.FILE_SIGNATURES.items():
            if file_data.startswith(signature):
                analysis['signature'] = signature.hex()
                analysis['file_type'] = file_type
                analysis['is_binary'] = True
                break
        
        # Try to detect text encoding
        if not analysis['is_binary']:
            try:
                # Try UTF-8
                text_content = file_data.decode('utf-8')
                analysis['is_text'] = True
                analysis['encoding'] = 'UTF-8'
                analysis['line_count'] = text_content.count('\n') + 1
                
                # Determine text file type based on content
                if analysis['extension'] == '.json':
                    try:
                        json.loads(text_content)
                        analysis['file_type'] = 'JSON Document'
                    except json.JSONDecodeError:
                        analysis['file_type'] = 'Text File'
                elif analysis['extension'] in ['.py', '.js', '.html', '.css', '.xml']:
                    analysis['file_type'] = f'{analysis["extension"][1:].upper()} Source Code'
                else:
                    analysis['file_type'] = 'Text File'
                    
            except UnicodeDecodeError:
                try:
                    # Try other encodings
                    encodings = ['latin1', 'cp1252', 'iso-8859-1']
                    for encoding in encodings:
                        try:
                            file_data.decode(encoding)
                            analysis['is_text'] = True
                            analysis['encoding'] = encoding
                            analysis['file_type'] = f'Text File ({encoding})'
                            break
                        except UnicodeDecodeError:
                            continue
                except:
                    pass
        
        # If still unknown, mark as binary
        if not analysis['is_text'] and not analysis['is_binary']:
            analysis['is_binary'] = True
            analysis['file_type'] = 'Binary File'
        
        return analysis
    
    @classmethod
    def get_file_icon(cls, analysis):
        """
        Get appropriate emoji icon for file type
        
        Args:
            analysis: File analysis dictionary
            
        Returns:
            Emoji string representing the file type
        """
        file_type = analysis['file_type'].lower()
        extension = analysis['extension']
        
        if 'image' in file_type or extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return '🖼️'
        elif 'audio' in file_type or extension in ['.mp3', '.wav', '.ogg', '.flac']:
            return '🎵'
        elif 'video' in file_type or extension in ['.mp4', '.avi', '.mkv', '.mov']:
            return '🎬'
        elif 'pdf' in file_type:
            return '📕'
        elif 'zip' in file_type or 'archive' in file_type:
            return '📦'
        elif 'executable' in file_type or extension in ['.exe', '.app']:
            return '⚙️'
        elif analysis['is_text'] or extension in ['.txt', '.md', '.py', '.js', '.html']:
            return '📝'
        else:
            return '📄'