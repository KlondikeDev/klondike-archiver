import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import struct
import threading
import time
import zlib
import tempfile
from pathlib import Path
from collections import defaultdict

COMPRESSED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp3', '.mp4', '.avi', '.mkv', '.zip', '.rar', '.7z', '.gz', '.exe', '.dll', '.pdf', '.apk', '.webp'}

def should_compress(filename):
    return Path(filename).suffix.lower() not in COMPRESSED_EXTENSIONS

class OptimizedCompression:
    """Optimized compression that uses less RAM and handles large files better"""
    
    # Reduced chunk sizes for better memory management
    SMALL_CHUNK = 64 * 1024      # 64KB for compression chunks
    LARGE_CHUNK = 1024 * 1024    # 1MB for file processing
    STREAM_THRESHOLD = 10 * 1024 * 1024  # 10MB threshold for streaming
    
    @staticmethod
    def compress_smart(data, progress_callback=None):
        """Smart compression that adapts to data size and type"""
        if len(data) < 100:
            return b'\x00' + data
        
        # For very large data, use streaming compression
        if len(data) > OptimizedCompression.STREAM_THRESHOLD:
            return OptimizedCompression._compress_streaming(data, progress_callback)
        
        # For medium data, use chunked compression with limited techniques
        if len(data) > OptimizedCompression.LARGE_CHUNK:
            return OptimizedCompression._compress_chunked_smart(data, progress_callback)
        
        # For small data, use fast single-pass compression
        return OptimizedCompression._compress_fast(data, progress_callback)
    
    @staticmethod
    def _compress_streaming(data, progress_callback=None):
        """Stream large files through compression to avoid RAM overload"""
        # Use zlib with streaming for large files
        compressor = zlib.compressobj(level=6, wbits=15)
        compressed_chunks = []
        total_size = len(data)
        processed = 0
        
        # Process in small chunks to keep memory usage low
        chunk_size = OptimizedCompression.SMALL_CHUNK
        
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            compressed_chunk = compressor.compress(chunk)
            if compressed_chunk:
                compressed_chunks.append(compressed_chunk)
            
            processed += len(chunk)
            
            if progress_callback and i % (chunk_size * 10) == 0:  # Update every 10 chunks
                progress = (processed / total_size) * 100
                progress_callback(progress)
        
        # Finalize compression
        final_chunk = compressor.flush()
        if final_chunk:
            compressed_chunks.append(final_chunk)
        
        if progress_callback:
            progress_callback(100)
        
        return b'\x01' + b''.join(compressed_chunks)
    
    @staticmethod
    def _compress_chunked_smart(data, progress_callback=None):
        """Efficient chunked compression for medium-sized files"""
        # Use zlib with good compression but not maximum to save time
        try:
            if progress_callback:
                progress_callback(25)
            
            compressed = zlib.compress(data, level=7)  # Reduced from 9 for speed
            
            if progress_callback:
                progress_callback(100)
            
            return b'\x02' + compressed
        except:
            # Fallback to no compression if zlib fails
            return b'\x00' + data
    
    @staticmethod
    def _compress_fast(data, progress_callback=None):
        """Fast compression for small files"""
        try:
            if progress_callback:
                progress_callback(50)
            
            # Use fast zlib compression
            compressed = zlib.compress(data, level=3)
            
            if progress_callback:
                progress_callback(100)
            
            return b'\x03' + compressed
        except:
            return b'\x00' + data
    
    @staticmethod
    def decompress_smart(data):
        """Smart decompression that handles all compression types"""
        if len(data) == 0:
            return b''
        
        compression_type = data[0]
        compressed_data = data[1:]
        
        if compression_type == 0:  # No compression
            return compressed_data
        elif compression_type in [1, 2, 3]:  # zlib variants
            try:
                return zlib.decompress(compressed_data)
            except:
                # Fallback to raw data if decompression fails
                return compressed_data
        else:
            # Unknown compression type, return raw data
            return compressed_data

class KlondikeArchiver:
    def __init__(self, root):
        self.root = root
        self.root.title("Klondike Archiver (Optimized)")
        self.root.geometry("1100x750")
        self.root.minsize(800, 600)
        
        # Set custom icon
        self.set_app_icon()
        
        # Current archive data - now stores file metadata instead of full data
        self.archive_metadata = {}  # Stores file info without actual data
        self.temp_dir = None        # Temporary directory for large file handling
        self.current_archive_file = None
        
        # Set default directory to Downloads
        self.current_directory = Path.home() / "Downloads"
        if not self.current_directory.exists():
            self.current_directory = Path.home()
        
        self.unsaved_changes = False
        
        # Configure style
        self.setup_styles()
        self.setup_ui()
        self.refresh_file_list()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize temp directory
        self._init_temp_dir()
        
        # Check if a file was passed as command line argument
        if len(sys.argv) > 1:
            file_to_open = sys.argv[1]
            if file_to_open.endswith('.kc') and Path(file_to_open).exists():
                self.root.after(100, lambda: self.open_specific_archive(file_to_open))
    
    def _init_temp_dir(self):
        """Initialize temporary directory for large file operations"""
        try:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="klondike_"))
        except:
            self.temp_dir = Path.cwd() / "temp_klondike"
            self.temp_dir.mkdir(exist_ok=True)
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
            except:
                pass
    
    def set_app_icon(self):
        """Set the application icon"""
        try:
            # Try to find icon file in the same directory as the script
            if getattr(sys, 'frozen', False):
                # If running as exe
                application_path = Path(sys.executable).parent
            else:
                # If running as script
                application_path = Path(__file__).parent
            
            icon_path = application_path / "klondike_icon.ico"
            
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
            else:
                # Fallback: create a simple icon using tkinter
                self.create_fallback_icon()
        except Exception:
            # If all else fails, just use default
            pass
    
    def create_fallback_icon(self):
        """Create a simple fallback icon using tkinter"""
        try:
            # Create a simple icon using PhotoImage
            icon_data = '''
                R0lGODlhEAAQAPIAAAAAAP//AP8A/wAA//8AAP//////////////yH5BAEKAAcALAAAAAAQABAAAAM2eLrc/jDKSWu4OOvNu/9gKI5kSZ5oqqJsC8fyTNf2jef6zvf+DwwKh8Si8YhMKpfMpnNKbTYAADs=
            '''
            import base64
            icon_image = tk.PhotoImage(data=base64.b64decode(icon_data))
            self.root.iconphoto(True, icon_image)
        except Exception:
            pass
    
    def open_specific_archive(self, file_path):
        """Open a specific archive file (for file association)"""
        self.current_archive_file = file_path
        self._open_archive_worker(file_path)
    
    def setup_styles(self):
        """Configure ttk styles for better appearance"""
        style = ttk.Style()
        style.configure('Action.TButton', padding=(10, 5))
        style.configure('Nav.TButton', padding=(8, 4))
    
    def on_closing(self):
        """Handle application closing"""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes", 
                "You have unsaved changes. Would you like to save before closing?"
            )
            if result is True:
                self.save_archive()
                if self.unsaved_changes:
                    return
            elif result is None:
                return
        
        self._cleanup_temp_dir()
        self.root.destroy()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(header_frame, text="Klondike Archiver (Optimized)", 
                               font=("Segoe UI", 20, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        self.archive_info_var = tk.StringVar()
        self.archive_info_var.set("Ready to create or open an archive")
        archive_info = ttk.Label(header_frame, textvariable=self.archive_info_var, 
                               font=("Segoe UI", 10), foreground="gray")
        archive_info.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        # Toolbar section
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # File operations
        file_ops_frame = ttk.LabelFrame(toolbar_frame, text="📁 Archive Operations", padding="10")
        file_ops_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(file_ops_frame, text="🆕 New", command=self.new_archive, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_ops_frame, text="📂 Open", command=self.open_archive, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="💾 Save", command=self.save_archive, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="💾 Save As", command=self.save_archive_as, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        # Quick stats
        self.stats_frame = ttk.LabelFrame(toolbar_frame, text="📊 Statistics", padding="10")
        self.stats_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.stats_var = tk.StringVar()
        self.stats_var.set("No files")
        ttk.Label(self.stats_frame, textvariable=self.stats_var, 
                 font=("Segoe UI", 9, "bold")).pack()
        
        # Main workspace
        workspace = ttk.Frame(main_frame)
        workspace.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        workspace.columnconfigure(0, weight=1)
        workspace.columnconfigure(1, weight=1)
        workspace.rowconfigure(0, weight=1)
        
        # Left panel - File browser
        left_panel = ttk.LabelFrame(workspace, text="📁 File Browser", padding="15")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)
        
        # Navigation bar
        nav_frame = ttk.Frame(left_panel)
        nav_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        nav_frame.columnconfigure(2, weight=1)
        
        ttk.Button(nav_frame, text="⬆️", command=self.go_up_directory, 
                  style='Nav.TButton', width=4).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(nav_frame, text="🏠", command=self.go_home, 
                  style='Nav.TButton', width=4).grid(row=0, column=1, padx=(0, 10))
        
        self.current_path_var = tk.StringVar()
        self.current_path_var.set(str(self.current_directory))
        path_display = ttk.Entry(nav_frame, textvariable=self.current_path_var, 
                               state="readonly", font=("Consolas", 9))
        path_display.grid(row=0, column=2, sticky=(tk.W, tk.E))
        
        # Filter options
        filter_frame = ttk.Frame(left_panel)
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Show:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        self.show_hidden_var = tk.BooleanVar()
        ttk.Checkbutton(filter_frame, text="Hidden files", 
                       variable=self.show_hidden_var, 
                       command=self.refresh_file_list).pack(side=tk.LEFT, padx=(10, 0))
        
        # File list
        list_frame = ttk.Frame(left_panel)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, 
                                      font=("Segoe UI", 10), activestyle='none')
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.file_listbox.bind("<Double-Button-1>", self.on_file_double_click)
        self.file_listbox.bind("<Return>", self.on_file_double_click)
        
        file_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                     command=self.file_listbox.yview)
        file_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)
        
        # Add files section
        add_frame = ttk.Frame(left_panel)
        add_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        add_frame.columnconfigure(0, weight=1)
        
        ttk.Button(add_frame, text="➕ Add Selected to Archive", 
                  command=self.add_files_to_archive, 
                  style='Action.TButton').grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(add_frame, text="📁 Add Entire Folder", 
                  command=self.add_folder_to_archive, 
                  style='Action.TButton').grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Right panel - Archive contents
        right_panel = ttk.LabelFrame(workspace, text="📦 Archive Contents", padding="15")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Archive info banner
        self.archive_banner = ttk.Frame(right_panel, relief='sunken', borderwidth=1)
        self.archive_banner.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.archive_banner.columnconfigure(0, weight=1)
        
        self.banner_text = tk.StringVar()
        self.banner_text.set("📭 Archive is empty - add some files!")
        banner_label = ttk.Label(self.archive_banner, textvariable=self.banner_text, 
                                font=("Segoe UI", 10), padding="10")
        banner_label.grid(row=0, column=0)
        
        # Archive tree
        tree_frame = ttk.Frame(right_panel)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.archive_tree = ttk.Treeview(tree_frame, 
                                       columns=("size", "compressed", "ratio", "type"), 
                                       show="tree headings", height=15)
        self.archive_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Column configuration
        self.archive_tree.heading("#0", text="📄 File Name")
        self.archive_tree.heading("size", text="Original Size")
        self.archive_tree.heading("compressed", text="Compressed")
        self.archive_tree.heading("ratio", text="Ratio")
        self.archive_tree.heading("type", text="Type")
        
        self.archive_tree.column("#0", width=250, minwidth=200)
        self.archive_tree.column("size", width=100, minwidth=80)
        self.archive_tree.column("compressed", width=100, minwidth=80)
        self.archive_tree.column("ratio", width=70, minwidth=60)
        self.archive_tree.column("type", width=80, minwidth=60)
        
        archive_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                        command=self.archive_tree.yview)
        archive_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.archive_tree.configure(yscrollcommand=archive_scrollbar.set)
        
        # Archive actions
        actions_frame = ttk.LabelFrame(right_panel, text="🔧 Actions", padding="10")
        actions_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)
        
        ttk.Button(actions_frame, text="📤 Extract Selected", 
                  command=self.extract_selected_files, 
                  style='Action.TButton').grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(actions_frame, text="📦 Extract All", 
                  command=self.extract_all_files, 
                  style='Action.TButton').grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Button(actions_frame, text="🗑️ Remove Selected", 
                  command=self.remove_selected_files, 
                  style='Action.TButton').grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar()
        self.status_var.set("🎯 Ready! Browse files on the left and add them to your archive")
        
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                             relief=tk.SUNKEN, padding="8", font=("Segoe UI", 9))
        status_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100, mode='determinate')
    
    def show_progress(self, message):
        """Show progress bar with message"""
        self.status_var.set(message)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        self.progress_var.set(0)
        self.root.update_idletasks()
    
    def update_progress(self, value, message=None):
        """Update progress bar value and optionally message"""
        self.progress_var.set(value)
        if message:
            self.status_var.set(message)
        self.root.update_idletasks()
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.grid_remove()
        self.root.update_idletasks()
    
    def refresh_file_list(self):
        """Refresh the file browser list"""
        self.file_listbox.delete(0, tk.END)
        self.current_path_var.set(str(self.current_directory))
        
        try:
            if self.current_directory.parent != self.current_directory:
                self.file_listbox.insert(tk.END, "📁 ..")
            
            for item in sorted(self.current_directory.iterdir()):
                if item.is_dir():
                    if self.show_hidden_var.get() or not item.name.startswith('.'):
                        self.file_listbox.insert(tk.END, f"📁 {item.name}")
            
            for item in sorted(self.current_directory.iterdir()):
                if item.is_file():
                    if self.show_hidden_var.get() or not item.name.startswith('.'):
                        size = item.stat().st_size
                        size_str = self.format_file_size(size)
                        self.file_listbox.insert(tk.END, f"📄 {item.name} ({size_str})")
                        
        except PermissionError:
            self.file_listbox.insert(tk.END, "❌ Permission denied")
            self.status_var.set("Cannot access this directory")
    
    def format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def on_file_double_click(self, event):
        """Handle double-click on file list"""
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        item_text = self.file_listbox.get(selection[0])
        
        if item_text.startswith("📁"):
            dir_name = item_text[2:].strip()
            if dir_name == "..":
                self.go_up_directory()
            else:
                new_path = self.current_directory / dir_name
                if new_path.exists() and new_path.is_dir():
                    self.current_directory = new_path
                    self.refresh_file_list()
    
    def go_up_directory(self):
        """Navigate to parent directory"""
        if self.current_directory.parent != self.current_directory:
            self.current_directory = self.current_directory.parent
            self.refresh_file_list()
    
    def go_home(self):
        """Navigate to Downloads folder"""
        downloads_path = Path.home() / "Downloads"
        if downloads_path.exists():
            self.current_directory = downloads_path
        else:
            self.current_directory = Path.home()
        self.refresh_file_list()
    
    def add_files_to_archive(self):
        """Add selected files to archive with optimized memory usage"""
        selections = self.file_listbox.curselection()
        if not selections:
            messagebox.showwarning("No Selection", "Please select files to add to the archive.")
            return

        files_to_add = []
        for selection in selections:
            item_text = self.file_listbox.get(selection)
            if item_text.startswith("📄"):
                filename = item_text[2:].split(" (")[0].strip()
                file_path = self.current_directory / filename
                if file_path.exists() and file_path.is_file():
                    files_to_add.append((filename, file_path))

        if not files_to_add:
            messagebox.showinfo("No Files", "No valid files selected.")
            return

        def worker():
            added_count = 0
            total_files = len(files_to_add)
            self.root.after(0, lambda: self.show_progress("Adding files to archive..."))

            for i, (filename, file_path) in enumerate(files_to_add):
                try:
                    progress = (i / total_files) * 100
                    self.root.after(0, lambda p=progress, name=filename:
                                    self.update_progress(p, f"Processing {name}..."))

                    file_size = file_path.stat().st_size
                    
                    # Read file data based on size
                    with open(file_path, 'rb') as f:
                        if file_size > OptimizedCompression.STREAM_THRESHOLD:
                            # For very large files, read in chunks
                            file_data = f.read()  # Read all for now, but track size
                        else:
                            # Normal read for smaller files
                            file_data = f.read()
                    
                    # Compress based on file type and size
                    if should_compress(filename):
                        def chunk_progress(comp_progress):
                            self.root.after(0, lambda: None)  # Minimal progress updates
                        
                        compressed_data = OptimizedCompression.compress_smart(
                            file_data, chunk_progress if file_size > OptimizedCompression.LARGE_CHUNK else None
                        )
                    else:
                        compressed_data = b'\x00' + file_data

                    # Store the sizes before cleaning up data
                    original_size = len(file_data)
                    compressed_size = len(compressed_data)
                    
                    # Store metadata instead of keeping full data in memory
                    def add_metadata():
                        self._add_file_metadata(filename, file_path, original_size, compressed_size)
                    
                    self.root.after(0, add_metadata)
                    
                    # Save compressed data to temp file for large files
                    if file_size > OptimizedCompression.LARGE_CHUNK:
                        temp_file = self.temp_dir / f"{filename}.tmp"
                        with open(temp_file, 'wb') as f:
                            f.write(compressed_data)
                    
                    added_count += 1
                    
                    # Clean up memory immediately
                    del file_data
                    del compressed_data

                except Exception as e:
                    self.root.after(0, lambda err=str(e), name=filename:
                                  messagebox.showerror("Error", f"Failed to add {name}: {err}"))

            def on_complete():
                self.hide_progress()
                if added_count > 0:
                    self.mark_unsaved_changes()
                    self.refresh_archive_tree()
                    self.update_archive_info()
                    self.status_var.set(f"✅ Added {added_count} file(s) to archive!")

            self.root.after(0, on_complete)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _add_file_metadata(self, filename, file_path, original_size, compressed_size):
        """Add file metadata to archive without storing full data in memory"""
        self.archive_metadata[filename] = {
            'original_path': str(file_path),
            'size': original_size,
            'compressed_size': compressed_size,
            'type': file_path.suffix or 'file',
            'is_large': original_size > OptimizedCompression.LARGE_CHUNK,
            'temp_file': str(self.temp_dir / f"{filename}.tmp") if original_size > OptimizedCompression.LARGE_CHUNK else None
        }
    
    def add_folder_to_archive(self):
        """Add an entire folder to the archive with memory optimization"""
        folder_path = filedialog.askdirectory(
            title="Select folder to add to archive",
            initialdir=self.current_directory
        )
        if not folder_path:
            return
        
        def worker():
            try:
                folder = Path(folder_path)
                files_to_add = []
                
                # First, collect all files
                for file_path in folder.rglob('*'):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(folder.parent)
                        files_to_add.append((str(relative_path), file_path))
                
                if not files_to_add:
                    self.root.after(0, lambda: messagebox.showinfo("Empty Folder", "No files found in the selected folder."))
                    return
                
                self.root.after(0, lambda: self.show_progress("Adding folder to archive..."))
                
                added_count = 0
                total_files = len(files_to_add)
                
                for i, (relative_name, file_path) in enumerate(files_to_add):
                    try:
                        progress = (i / total_files) * 100
                        self.root.after(0, lambda p=progress, name=file_path.name: 
                                        self.update_progress(p, f"Processing {name}..."))

                        file_size = file_path.stat().st_size
                        
                        # Process file based on size
                        with open(file_path, 'rb') as f:
                            if file_size > OptimizedCompression.STREAM_THRESHOLD:
                                # Large file - read all at once for now (can be optimized further)
                                file_data = f.read()
                            else:
                                # Small file - read normally
                                file_data = f.read()

                        if should_compress(relative_name):
                            compressed_data = OptimizedCompression.compress_smart(file_data)
                        else:
                            compressed_data = b'\x00' + file_data

                        # Store sizes before cleanup
                        original_size = len(file_data)
                        compressed_size = len(compressed_data)

                        # Add to archive metadata
                        def add_metadata():
                            self._add_file_metadata(relative_name, file_path, original_size, compressed_size)
                        
                        self.root.after(0, add_metadata)
                        
                        # Save large files to temp directory
                        if file_size > OptimizedCompression.LARGE_CHUNK:
                            temp_file = self.temp_dir / f"{relative_name.replace('/', '_').replace('\\', '_')}.tmp"
                            temp_file.parent.mkdir(parents=True, exist_ok=True)
                            with open(temp_file, 'wb') as f:
                                f.write(compressed_data)
                        
                        added_count += 1
                        
                        # Clean up memory
                        del file_data
                        del compressed_data
                        
                    except Exception as e:
                        self.root.after(0, lambda err=str(e), name=relative_name: 
                                      messagebox.showerror("Error", f"Failed to add {name}: {err}"))
                
                def on_complete():
                    self.hide_progress()
                    if added_count > 0:
                        self.mark_unsaved_changes()
                        self.refresh_archive_tree()
                        self.update_archive_info()
                        self.status_var.set(f"✅ Added {added_count} file(s) from folder!")
                
                self.root.after(0, on_complete)
                
            except Exception as e:
                self.root.after(0, lambda: self.hide_progress())
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to add folder: {e}"))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def mark_unsaved_changes(self):
        """Mark that there are unsaved changes"""
        self.unsaved_changes = True
        title = self.root.title()
        if not title.endswith("*"):
            self.root.title(title + " *")
    
    def clear_unsaved_changes(self):
        """Clear the unsaved changes flag"""
        self.unsaved_changes = False
        title = self.root.title()
        if title.endswith(" *"):
            self.root.title(title[:-2])
    
    def extract_selected_files(self):
        """Extract selected files from archive"""
        selections = self.archive_tree.selection()
        if not selections:
            messagebox.showwarning("No Selection", "Please select files to extract from the archive.")
            return
        
        extract_dir = filedialog.askdirectory(
            title="Choose extraction directory",
            initialdir=self.current_directory
        )
        if not extract_dir:
            return
        
        def worker():
            try:
                extract_path = Path(extract_dir)
                extracted_count = 0
                
                self.root.after(0, lambda: self.show_progress("Extracting files..."))
                
                for i, selection in enumerate(selections):
                    filename = self.archive_tree.item(selection, "text")
                    if filename.startswith(("📝", "🖼️", "🎵", "🎬", "📦", "⚙️", "📄")):
                        filename = filename[2:].strip()
                    
                    if filename in self.archive_metadata:
                        try:
                            progress = (i / len(selections)) * 100
                            self.root.after(0, lambda p=progress, name=filename: 
                                          self.update_progress(p, f"Extracting {name}..."))
                            
                            # Get file data
                            file_data = self._get_file_data(filename)
                            
                            if file_data:
                                output_file = extract_path / filename
                                output_file.parent.mkdir(parents=True, exist_ok=True)
                                with open(output_file, 'wb') as f:
                                    f.write(file_data)
                                extracted_count += 1
                                
                        except Exception as e:
                            self.root.after(0, lambda err=str(e), name=filename: 
                                          messagebox.showerror("Error", f"Failed to extract {name}: {err}"))
                
                def on_complete():
                    self.hide_progress()
                    if extracted_count > 0:
                        self.status_var.set(f"✅ Extracted {extracted_count} file(s) to {extract_dir}")
                
                self.root.after(0, on_complete)
                
            except Exception as e:
                self.root.after(0, lambda: self.hide_progress())
                self.root.after(0, lambda: messagebox.showerror("Error", f"Extraction failed: {e}"))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def extract_all_files(self):
        """Extract all files from archive with progress tracking"""
        if not self.archive_metadata:
            messagebox.showwarning("Empty Archive", "No files to extract.")
            return
        
        extract_dir = filedialog.askdirectory(
            title="Choose extraction directory",
            initialdir=self.current_directory
        )
        if not extract_dir:
            return
        
        def worker():
            try:
                extract_path = Path(extract_dir)
                extracted_count = 0
                
                self.root.after(0, lambda: self.show_progress("Extracting all files..."))
                total_files = len(self.archive_metadata)
                
                for i, filename in enumerate(self.archive_metadata.keys()):
                    try:
                        progress = (i / total_files) * 100
                        self.root.after(0, lambda p=progress, name=filename: 
                                      self.update_progress(p, f"Extracting {name}..."))
                        
                        file_data = self._get_file_data(filename)
                        
                        if file_data:
                            output_file = extract_path / filename
                            output_file.parent.mkdir(parents=True, exist_ok=True)
                            
                            with open(output_file, 'wb') as f:
                                f.write(file_data)
                                
                            extracted_count += 1
                            
                    except Exception as e:
                        self.root.after(0, lambda err=str(e), name=filename: 
                                      messagebox.showerror("Error", f"Failed to extract {name}: {err}"))
                
                def on_complete():
                    self.hide_progress()
                    if extracted_count > 0:
                        self.status_var.set(f"✅ Extracted all {extracted_count} file(s) to {extract_dir}")
                
                self.root.after(0, on_complete)
                
            except Exception as e:
                self.root.after(0, lambda: self.hide_progress())
                self.root.after(0, lambda: messagebox.showerror("Error", f"Extraction failed: {e}"))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _get_file_data(self, filename):
        """Get decompressed file data from archive or temp storage"""
        if filename not in self.archive_metadata:
            return None
        
        metadata = self.archive_metadata[filename]
        
        try:
            if metadata['is_large'] and metadata['temp_file']:
                # Large file stored in temp directory
                temp_file = Path(metadata['temp_file'])
                if temp_file.exists():
                    with open(temp_file, 'rb') as f:
                        compressed_data = f.read()
                    return OptimizedCompression.decompress_smart(compressed_data)
            else:
                # Small file - re-read and compress from original
                original_path = Path(metadata['original_path'])
                if original_path.exists():
                    with open(original_path, 'rb') as f:
                        return f.read()
        except Exception as e:
            print(f"Error getting file data for {filename}: {e}")
        
        return None
    
    def remove_selected_files(self):
        """Remove selected files from archive"""
        selections = self.archive_tree.selection()
        if not selections:
            messagebox.showwarning("No Selection", "Please select files to remove from the archive.")
            return
        
        filenames_to_remove = []
        for selection in selections:
            filename = self.archive_tree.item(selection, "text")
            if filename.startswith(("📝", "🖼️", "🎵", "🎬", "📦", "⚙️", "📄")):
                filename = filename[2:].strip()
            filenames_to_remove.append(filename)
        
        if messagebox.askyesno("Confirm Removal", 
                              f"Remove {len(filenames_to_remove)} file(s) from archive?"):
            removed_count = 0
            for filename in filenames_to_remove:
                if filename in self.archive_metadata:
                    # Clean up temp file if it exists
                    metadata = self.archive_metadata[filename]
                    if metadata.get('temp_file'):
                        temp_file = Path(metadata['temp_file'])
                        if temp_file.exists():
                            temp_file.unlink()
                    
                    del self.archive_metadata[filename]
                    removed_count += 1
            
            if removed_count > 0:
                self.mark_unsaved_changes()
                self.refresh_archive_tree()
                self.update_archive_info()
                self.status_var.set(f"🗑️ Removed {removed_count} file(s) from archive")
    
    def refresh_archive_tree(self):
        """Refresh the archive contents tree with enhanced display"""
        self.archive_tree.delete(*self.archive_tree.get_children())
        
        if not self.archive_metadata:
            self.banner_text.set("📭 Archive is empty - add some files!")
            return
        
        total_original = 0
        total_compressed = 0
        
        for filename, metadata in self.archive_metadata.items():
            original_size = metadata['size']
            compressed_size = metadata['compressed_size']
            file_type = metadata['type']
            
            total_original += original_size
            total_compressed += compressed_size
            
            if original_size > 0:
                ratio = f"{(compressed_size / original_size * 100):.1f}%"
            else:
                ratio = "0%"
            
            # Add file icon based on type
            if file_type in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                icon = "📝"
            elif file_type in ['.jpg', '.png', '.gif', '.bmp', '.jpeg']:
                icon = "🖼️"
            elif file_type in ['.mp3', '.wav', '.flac', '.ogg']:
                icon = "🎵"
            elif file_type in ['.mp4', '.avi', '.mkv', '.mov']:
                icon = "🎬"
            elif file_type in ['.zip', '.rar', '.7z', '.tar']:
                icon = "📦"
            elif file_type in ['.exe', '.app', '.deb', '.dmg']:
                icon = "⚙️"
            else:
                icon = "📄"
            
            self.archive_tree.insert("", "end", text=f"{icon} {filename}", 
                                   values=(self.format_file_size(original_size),
                                          self.format_file_size(compressed_size),
                                          ratio,
                                          file_type or "file"))
        
        # Update banner with summary
        file_count = len(self.archive_metadata)
        if total_original > 0:
            savings_ratio = (1 - total_compressed / total_original) * 100
            self.banner_text.set(
                f"📊 {file_count} files • {self.format_file_size(total_original)} → "
                f"{self.format_file_size(total_compressed)} ({savings_ratio:.1f}% saved!)"
            )
        else:
            self.banner_text.set(f"📊 {file_count} files in archive")
    
    def update_archive_info(self):
        """Update the archive info display and statistics"""
        if not self.archive_metadata:
            self.archive_info_var.set("Ready to create or open an archive")
            self.stats_var.set("No files")
            return
        
        file_count = len(self.archive_metadata)
        total_original = sum(f['size'] for f in self.archive_metadata.values())
        total_compressed = sum(f['compressed_size'] for f in self.archive_metadata.values())
        
        if self.current_archive_file:
            filename = Path(self.current_archive_file).name
            self.archive_info_var.set(f"📁 {filename}")
        else:
            self.archive_info_var.set("📝 Unsaved archive")
        
        if total_original > 0:
            savings_ratio = (1 - total_compressed / total_original) * 100
            saved_space = total_original - total_compressed
            self.stats_var.set(
                f"{file_count} files\n"
                f"{self.format_file_size(total_original)} → {self.format_file_size(total_compressed)}\n"
                f"Saved: {self.format_file_size(saved_space)} ({savings_ratio:.1f}%)"
            )
        else:
            self.stats_var.set(f"{file_count} files\nEmpty archive")
    
    def new_archive(self):
        """Create a new archive with unsaved changes check"""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes", 
                "You have unsaved changes. Save before creating new archive?"
            )
            if result is True:
                self.save_archive()
                if self.unsaved_changes:
                    return
            elif result is None:
                return
        
        # Clean up temp files
        if self.temp_dir:
            for temp_file in self.temp_dir.glob("*.tmp"):
                try:
                    temp_file.unlink()
                except:
                    pass
        
        self.archive_metadata = {}
        self.current_archive_file = None
        self.clear_unsaved_changes()
        self.refresh_archive_tree()
        self.update_archive_info()
        self.status_var.set("🆕 New archive created - ready for files!")
    
    def save_archive_as(self):
        """Save archive with a new name"""
        if not self.archive_metadata:
            messagebox.showwarning("Empty Archive", "No files to save. Add some files first!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Klondike Archive As...",
            defaultextension=".kc",
            filetypes=[
                ("Klondike Crinkle", "*.kc"), 
                ("All files", "*.*")
            ],
            initialdir=self.current_directory
        )
        
        if file_path:
            self.current_archive_file = file_path
            self.save_archive()
    
    def save_archive(self):
        """Save archive to file with optimized memory usage"""
        if not self.archive_metadata:
            messagebox.showwarning("Empty Archive", "No files to save. Add some files first!")
            return

        if not self.current_archive_file:
            self.save_archive_as()
            return

        def worker():
            try:
                file_count = len(self.archive_metadata)
                self.root.after(0, lambda: self.show_progress("Saving archive..."))

                # Build file table
                file_table_data = b''
                file_data_info = []
                current_offset = 0

                for filename, metadata in self.archive_metadata.items():
                    # Get compressed data size
                    if metadata['is_large'] and metadata['temp_file']:
                        temp_file = Path(metadata['temp_file'])
                        if temp_file.exists():
                            compressed_size = temp_file.stat().st_size
                        else:
                            # Re-compress if temp file missing
                            original_path = Path(metadata['original_path'])
                            with open(original_path, 'rb') as f:
                                data = f.read()
                            compressed_data = OptimizedCompression.compress_smart(data)
                            compressed_size = len(compressed_data)
                            # Save to temp file
                            temp_file = self.temp_dir / f"{filename}.tmp"
                            with open(temp_file, 'wb') as f:
                                f.write(compressed_data)
                    else:
                        compressed_size = metadata['compressed_size']

                    # Build table entry
                    filename_bytes = filename.encode('utf-8')
                    file_type_bytes = metadata['type'].encode('utf-8')
                    
                    file_table_data += struct.pack('<H', len(filename_bytes))
                    file_table_data += filename_bytes
                    file_table_data += struct.pack('<I', metadata['size'])
                    file_table_data += struct.pack('<I', compressed_size)
                    file_table_data += struct.pack('<I', current_offset)
                    file_table_data += struct.pack('<H', len(file_type_bytes))
                    file_table_data += file_type_bytes
                    
                    file_data_info.append((filename, current_offset, compressed_size))
                    current_offset += compressed_size

                # Write archive file
                with open(self.current_archive_file, 'wb') as f:
                    # Write header
                    f.write(b'KLONDIKE')
                    f.write(b'ULTIMATE')
                    f.write(struct.pack('<I', len(self.archive_metadata)))
                    f.write(struct.pack('<I', len(file_table_data)))
                    f.write(file_table_data)

                    # Write file data
                    for i, (filename, offset, size) in enumerate(file_data_info):
                        progress = (i / file_count) * 90
                        self.root.after(0, lambda p=progress, name=filename:
                                        self.update_progress(p, f"Writing {name}..."))
                        
                        metadata = self.archive_metadata[filename]
                        
                        if metadata['is_large'] and metadata['temp_file']:
                            # Copy from temp file
                            temp_file = Path(metadata['temp_file'])
                            if temp_file.exists():
                                with open(temp_file, 'rb') as temp_f:
                                    # Copy in chunks to avoid loading large files into memory
                                    while True:
                                        chunk = temp_f.read(OptimizedCompression.SMALL_CHUNK)
                                        if not chunk:
                                            break
                                        f.write(chunk)
                        else:
                            # Small file - re-compress from original
                            original_path = Path(metadata['original_path'])
                            with open(original_path, 'rb') as orig_f:
                                data = orig_f.read()
                            
                            if should_compress(filename):
                                compressed_data = OptimizedCompression.compress_smart(data)
                            else:
                                compressed_data = b'\x00' + data
                            
                            f.write(compressed_data)

                def on_complete():
                    self.hide_progress()
                    self.clear_unsaved_changes()
                    self.update_archive_info()
                    self.status_var.set("💾 Archive saved successfully!")

                self.root.after(0, on_complete)

            except Exception as e:
                def on_error():
                    self.hide_progress()
                    messagebox.showerror("Save Error", f"Failed to save archive: {e}")

                self.root.after(0, on_error)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def open_archive(self):
        """Open an existing Klondike archive with unsaved changes check"""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes", 
                "You have unsaved changes. Save before opening another archive?"
            )
            if result is True:
                self.save_archive()
                if self.unsaved_changes:
                    return
            elif result is None:
                return
        
        file_path = filedialog.askopenfilename(
            title="Open Klondike Crinkle Archive",
            filetypes=[("Klondike Crinkle", "*.kc"), ("All files", "*.*")],
            initialdir=self.current_directory
        )
        
        if file_path:
            self.current_archive_file = file_path
            self._open_archive_worker(file_path)
    
    def _open_archive_worker(self, file_path):
        """Worker function to open archive with memory optimization"""
        def worker():
            try:
                self.root.after(0, lambda: self.show_progress("Opening archive..."))
                
                with open(file_path, 'rb') as f:
                    signature = f.read(8)
                    if signature != b'KLONDIKE':
                        raise ValueError("Not a valid Klondike archive")
                    
                    compression_marker = f.read(8)
                    is_ultimate = compression_marker == b'ULTIMATE'
                    
                    if not is_ultimate:
                        f.seek(8)
                    
                    num_files = struct.unpack('<I', f.read(4))[0]
                    
                    self.root.after(0, lambda: self.update_progress(20, f"Reading {num_files} files..."))
                    
                    table_size = struct.unpack('<I', f.read(4))[0]
                    table_data = f.read(table_size)
                    
                    archive_metadata = {}
                    table_offset = 0
                    data_start = f.tell()
                    
                    # Clean up existing temp files
                    for temp_file in self.temp_dir.glob("*.tmp"):
                        try:
                            temp_file.unlink()
                        except:
                            pass
                    
                    for i in range(num_files):
                        progress = 20 + (i / num_files) * 70
                        self.root.after(0, lambda p=progress, idx=i: 
                                      self.update_progress(p, f"Loading file {idx+1}/{num_files}..."))
                        
                        # Parse table entry
                        if table_offset + 2 > len(table_data):
                            break
                        filename_len = struct.unpack('<H', table_data[table_offset:table_offset+2])[0]
                        table_offset += 2
                        
                        if table_offset + filename_len > len(table_data):
                            break
                        filename = table_data[table_offset:table_offset+filename_len].decode('utf-8')
                        table_offset += filename_len
                        
                        if table_offset + 12 > len(table_data):
                            break
                        original_size = struct.unpack('<I', table_data[table_offset:table_offset+4])[0]
                        table_offset += 4
                        compressed_size = struct.unpack('<I', table_data[table_offset:table_offset+4])[0]
                        table_offset += 4
                        data_offset = struct.unpack('<I', table_data[table_offset:table_offset+4])[0]
                        table_offset += 4
                        
                        file_type = 'file'
                        if is_ultimate and table_offset + 2 <= len(table_data):
                            type_len = struct.unpack('<H', table_data[table_offset:table_offset+2])[0]
                            table_offset += 2
                            if table_offset + type_len <= len(table_data):
                                file_type = table_data[table_offset:table_offset+type_len].decode('utf-8')
                                table_offset += type_len
                            else:
                                file_type = Path(filename).suffix or 'file'
                        else:
                            file_type = Path(filename).suffix or 'file'
                        
                        # For large files, extract compressed data to temp file
                        if compressed_size > OptimizedCompression.LARGE_CHUNK:
                            temp_file = self.temp_dir / f"{filename.replace('/', '_').replace('\\', '_')}.tmp"
                            temp_file.parent.mkdir(parents=True, exist_ok=True)
                            
                            f.seek(data_start + data_offset)
                            
                            # Copy compressed data to temp file in chunks
                            with open(temp_file, 'wb') as temp_f:
                                remaining = compressed_size
                                while remaining > 0:
                                    chunk_size = min(OptimizedCompression.SMALL_CHUNK, remaining)
                                    chunk = f.read(chunk_size)
                                    if not chunk:
                                        break
                                    temp_f.write(chunk)
                                    remaining -= len(chunk)
                            
                            archive_metadata[filename] = {
                                'original_path': '',  # No original path for opened files
                                'size': original_size,
                                'compressed_size': compressed_size,
                                'type': file_type,
                                'is_large': True,
                                'temp_file': str(temp_file)
                            }
                        else:
                            # Small file - store metadata only
                            archive_metadata[filename] = {
                                'original_path': '',
                                'size': original_size,
                                'compressed_size': compressed_size,
                                'type': file_type,
                                'is_large': False,
                                'temp_file': None,
                                'data_offset': data_start + data_offset,
                                'archive_file': file_path
                            }
                
                def on_complete():
                    self.hide_progress()
                    self.archive_metadata = archive_metadata
                    self.clear_unsaved_changes()
                    self.refresh_archive_tree()
                    self.update_archive_info()
                    
                    archive_name = Path(file_path).name
                    total_files = len(self.archive_metadata)
                    self.status_var.set(f"📂 Opened '{archive_name}' - {total_files} files loaded!")

                self.root.after(0, on_complete)
                
            except Exception as e:
                self.root.after(0, lambda: self.hide_progress())
                self.root.after(0, lambda: messagebox.showerror("Open Error", f"Failed to open archive: {e}"))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = KlondikeArchiver(root)
    root.mainloop()