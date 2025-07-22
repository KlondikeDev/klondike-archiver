import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import struct
import threading
import time
from pathlib import Path
from collections import defaultdict

class NuggetCompression:
    """Ultimate Klondike compression - The most advanced algorithm on Earth"""
    
    @staticmethod
    def compress(data):
        if len(data) < 30:
            return b'\x00' + data
        
        # Try multiple ultra-advanced compression techniques
        techniques = [
            NuggetCompression._compress_ultimate_lzma,
            NuggetCompression._compress_advanced_lz77,
            NuggetCompression._compress_bwt_mtf,
            NuggetCompression._compress_context_modeling,
            NuggetCompression._compress_huffman_plus,
            NuggetCompression._compress_arithmetic_coding
        ]
        
        best_result = data
        best_technique = 0
        best_ratio = 1.0
        
        for i, technique in enumerate(techniques):
            try:
                result = technique(data)
                ratio = len(result) / len(data)
                if ratio < best_ratio:
                    best_result = result
                    best_technique = i + 1
                    best_ratio = ratio
            except:
                continue
        
        # Always compress - let it crinkle even with no gains!
        return bytes([best_technique]) + best_result
    
    @staticmethod
    def _compress_ultimate_lzma(data):
        """LZMA-style compression with advanced dictionary"""
        import zlib
        # Use Python's built-in zlib with maximum compression
        compressed = zlib.compress(data, level=9)
        return compressed
    
    @staticmethod
    def _compress_advanced_lz77(data):
        """Advanced LZ77 with larger windows and better matching"""
        if len(data) < 100:
            raise ValueError("Too small")
        
        window_size = min(65536, len(data) // 2)  # Larger window
        lookahead_size = min(1024, len(data) // 5)  # Larger lookahead
        
        compressed = bytearray()
        i = 0
        
        while i < len(data):
            best_length = 0
            best_distance = 0
            
            window_start = max(0, i - window_size)
            
            # Enhanced matching with suffix arrays concept
            for distance in range(1, min(i - window_start + 1, window_size)):
                match_start = i - distance
                if match_start < 0:
                    break
                
                length = 0
                max_length = min(lookahead_size, len(data) - i)
                
                # Advanced matching with overlapping support
                while (length < max_length and 
                       match_start + (length % distance) < i and
                       data[match_start + (length % distance)] == data[i + length]):
                    length += 1
                
                if length > best_length and length >= 4:  # Higher threshold
                    best_length = length
                    best_distance = distance
            
            if best_length >= 4:
                # Enhanced encoding with variable length
                if best_distance < 256 and best_length < 64:
                    # Short format: [flag][distance][length]
                    compressed.extend([255, best_distance, best_length])
                else:
                    # Long format: [flag][254][distance_high][distance_low][length_high][length_low]
                    compressed.extend([255, 254, 
                                     (best_distance >> 8) & 0xFF, best_distance & 0xFF,
                                     (best_length >> 8) & 0xFF, best_length & 0xFF])
                i += best_length
            else:
                byte_val = data[i]
                if byte_val == 255:
                    compressed.extend([254, 255])
                elif byte_val == 254:
                    compressed.extend([254, 254])
                else:
                    compressed.append(byte_val)
                i += 1
        
        return bytes(compressed)
    
    @staticmethod
    def _compress_bwt_mtf(data):
        """Burrows-Wheeler Transform + Move-to-Front + RLE"""
        if len(data) < 200:
            raise ValueError("Too small for BWT")
        
        # Simplified BWT implementation
        def bwt_encode(s):
            rotations = [s[i:] + s[:i] for i in range(len(s))]
            rotations.sort()
            last_column = [rotation[-1] for rotation in rotations]
            original_index = rotations.index(s)
            return bytes(last_column), original_index
        
        def mtf_encode(data):
            alphabet = list(range(256))
            encoded = []
            
            for byte in data:
                index = alphabet.index(byte)
                encoded.append(index)
                # Move to front
                alphabet = [byte] + alphabet[:index] + alphabet[index+1:]
            
            return encoded
        
        def rle_encode(data):
            if not data:
                return []
            
            encoded = []
            current = data[0]
            count = 1
            
            for i in range(1, len(data)):
                if data[i] == current and count < 255:
                    count += 1
                else:
                    if count == 1:
                        encoded.append(current)
                    else:
                        encoded.extend([current, 256 + count])  # Special RLE marker
                    current = data[i]
                    count = 1
            
            if count == 1:
                encoded.append(current)
            else:
                encoded.extend([current, 256 + count])
            
            return encoded
        
        # Apply transformations
        try:
            bwt_data, original_index = bwt_encode(data)
            mtf_data = mtf_encode(bwt_data)
            rle_data = rle_encode(mtf_data)
            
            # Pack result
            result = bytearray()
            result.extend(original_index.to_bytes(4, 'little'))
            result.extend(len(rle_data).to_bytes(4, 'little'))
            
            for val in rle_data:
                if val < 256:
                    result.append(val)
                else:
                    result.extend([255, val - 256])  # RLE encoding
            
            return bytes(result)
        except:
            raise ValueError("BWT failed")
    
    @staticmethod
    def _compress_context_modeling(data):
        """Context-based compression with prediction"""
        if len(data) < 150:
            raise ValueError("Too small for context modeling")
        
        context_size = min(4, len(data) // 50)
        predictions = {}
        result = bytearray()
        
        # Build context model
        for i in range(context_size, len(data)):
            context = data[i-context_size:i]
            next_byte = data[i]
            
            if context not in predictions:
                predictions[context] = defaultdict(int)
            predictions[context][next_byte] += 1
        
        # Encode with predictions
        result.append(context_size)
        i = 0
        
        # Store first bytes as-is
        while i < context_size:
            result.append(data[i])
            i += 1
        
        # Predict remaining bytes
        while i < len(data):
            context = data[i-context_size:i]
            current_byte = data[i]
            
            if context in predictions:
                # Find most likely prediction
                sorted_predictions = sorted(predictions[context].items(), 
                                          key=lambda x: x[1], reverse=True)
                
                # If current byte is the top prediction
                if sorted_predictions and sorted_predictions[0][0] == current_byte:
                    result.append(255)  # Prediction hit marker
                else:
                    # Store byte normally
                    if current_byte == 255:
                        result.extend([254, 255])
                    else:
                        result.append(current_byte)
            else:
                # No context, store normally
                if current_byte == 255:
                    result.extend([254, 255])
                elif current_byte == 254:
                    result.extend([254, 254])
                else:
                    result.append(current_byte)
            
            i += 1
        
        return bytes(result)
    
    @staticmethod
    def _compress_huffman_plus(data):
        """Enhanced Huffman coding with adaptive tables"""
        if len(data) < 100:
            raise ValueError("Too small")
        
        # Count frequencies
        frequencies = defaultdict(int)
        for byte in data:
            frequencies[byte] += 1
        
        # Build Huffman tree (simplified)
        import heapq
        
        heap = [[freq, [[byte, ""]]] for byte, freq in frequencies.items()]
        heapq.heapify(heap)
        
        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            
            for pair in lo[1]:
                pair[1] = "0" + pair[1]
            for pair in hi[1]:
                pair[1] = "1" + pair[1]
                
            heapq.heappush(heap, [lo[0] + hi[0]] + [lo[1] + hi[1]])
        
        # Extract codes
        codes = {}
        if heap:
            for pair in heap[0][1]:
                codes[pair[0]] = pair[1] if pair[1] else "0"
        
        # Encode data
        encoded_bits = ""
        for byte in data:
            encoded_bits += codes.get(byte, format(byte, '08b'))
        
        # Pack bits into bytes
        result = bytearray()
        result.append(len(codes))
        
        # Store codebook
        for byte, code in codes.items():
            result.append(byte)
            result.append(len(code))
            code_bytes = int(code.ljust(8, '0')[:8], 2) if code else 0
            result.append(code_bytes)
        
        # Store encoded data length
        result.extend(len(encoded_bits).to_bytes(4, 'little'))
        
        # Pack encoded bits
        for i in range(0, len(encoded_bits), 8):
            byte_bits = encoded_bits[i:i+8].ljust(8, '0')
            result.append(int(byte_bits, 2))
        
        return bytes(result)
    
    @staticmethod
    def _compress_arithmetic_coding(data):
        """Simplified arithmetic coding simulation"""
        if len(data) < 80:
            raise ValueError("Too small")
        
        # Frequency analysis
        frequencies = defaultdict(int)
        for byte in data:
            frequencies[byte] += 1
        
        total = len(data)
        
        # Create probability ranges (simplified)
        ranges = {}
        cumulative = 0
        
        for byte in sorted(frequencies.keys()):
            prob = frequencies[byte] / total
            ranges[byte] = (cumulative, cumulative + prob)
            cumulative += prob
        
        # Arithmetic encoding simulation (simplified to byte-level)
        result = bytearray()
        
        # Store probability table
        result.append(len(ranges))
        for byte, (low, high) in ranges.items():
            result.append(byte)
            result.append(int(low * 255))
            result.append(int(high * 255))
        
        # Simplified encoding using range differences
        for byte in data:
            if byte in ranges:
                low, high = ranges[byte]
                # Encode as scaled value
                encoded_val = int((low + high) * 127.5)
                result.append(min(255, max(0, encoded_val)))
            else:
                result.append(byte)
        
        return bytes(result)
    
    @staticmethod
    def decompress(data):
        if len(data) == 0:
            return b''
        
        technique = data[0]
        compressed_data = data[1:]
        
        if technique == 0:
            return compressed_data
        elif technique == 1:
            return NuggetCompression._decompress_ultimate_lzma(compressed_data)
        elif technique == 2:
            return NuggetCompression._decompress_advanced_lz77(compressed_data)
        elif technique == 3:
            return NuggetCompression._decompress_bwt_mtf(compressed_data)
        elif technique == 4:
            return NuggetCompression._decompress_context_modeling(compressed_data)
        elif technique == 5:
            return NuggetCompression._decompress_huffman_plus(compressed_data)
        elif technique == 6:
            return NuggetCompression._decompress_arithmetic_coding(compressed_data)
        else:
            raise ValueError(f"Unknown compression technique: {technique}")
    
    @staticmethod
    def _decompress_ultimate_lzma(data):
        import zlib
        return zlib.decompress(data)
    
    @staticmethod
    def _decompress_advanced_lz77(data):
        """Decompress advanced LZ77"""
        result = bytearray()
        i = 0
        
        while i < len(data):
            if data[i] == 255:  # Match marker
                if i + 1 < len(data) and data[i + 1] == 254:  # Long format
                    if i + 5 >= len(data):
                        break
                    distance = (data[i + 2] << 8) | data[i + 3]
                    length = (data[i + 4] << 8) | data[i + 5]
                    
                    # Copy with overlapping support
                    for _ in range(length):
                        if len(result) >= distance:
                            result.append(result[-distance])
                    
                    i += 6
                else:  # Short format
                    if i + 2 >= len(data):
                        break
                    distance = data[i + 1]
                    length = data[i + 2]
                    
                    for _ in range(length):
                        if len(result) >= distance:
                            result.append(result[-distance])
                    
                    i += 3
            elif data[i] == 254:  # Escaped byte
                if i + 1 < len(data):
                    result.append(data[i + 1])
                    i += 2
                else:
                    i += 1
            else:
                result.append(data[i])
                i += 1
        
        return bytes(result)
    
    @staticmethod
    def _decompress_bwt_mtf(data):
        """Decompress BWT+MTF+RLE"""
        try:
            if len(data) < 8:
                return b''
            
            original_index = int.from_bytes(data[0:4], 'little')
            rle_length = int.from_bytes(data[4:8], 'little')
            
            # Decode RLE
            rle_data = []
            i = 8
            while i < len(data) and len(rle_data) < rle_length:
                if i < len(data) and data[i] == 255:
                    if i + 1 < len(data):
                        count = data[i + 1]
                        if len(rle_data) > 0:
                            rle_data.extend([rle_data[-1]] * count)
                        i += 2
                    else:
                        break
                else:
                    rle_data.append(data[i])
                    i += 1
            
            # Reverse MTF
            alphabet = list(range(256))
            mtf_decoded = []
            
            for index in rle_data:
                if 0 <= index < len(alphabet):
                    byte = alphabet[index]
                    mtf_decoded.append(byte)
                    alphabet = [byte] + alphabet[:index] + alphabet[index+1:]
            
            # Reverse BWT (simplified)
            if not mtf_decoded:
                return b''
                
            # Simple BWT reversal
            table = [''] * len(mtf_decoded)
            for _ in range(len(mtf_decoded)):
                table = sorted(chr(mtf_decoded[i]) + table[i] for i in range(len(mtf_decoded)))
            
            if 0 <= original_index < len(table):
                return table[original_index].encode('latin1')
            else:
                return bytes(mtf_decoded)
                
        except:
            return b''
    
    @staticmethod
    def _decompress_context_modeling(data):
        """Decompress context modeling"""
        if len(data) < 2:
            return b''
        
        context_size = data[0]
        result = bytearray()
        
        # Get initial bytes
        for i in range(1, min(context_size + 1, len(data))):
            result.append(data[i])
        
        i = context_size + 1
        while i < len(data):
            if data[i] == 255:  # Prediction hit
                # Use most common byte in context (simplified)
                if len(result) >= context_size:
                    result.append(result[-1])  # Simple prediction
                i += 1
            elif data[i] == 254:  # Escaped byte
                if i + 1 < len(data):
                    result.append(data[i + 1])
                    i += 2
                else:
                    i += 1
            else:
                result.append(data[i])
                i += 1
        
        return bytes(result)
    
    @staticmethod
    def _decompress_huffman_plus(data):
        """Decompress Huffman coding"""
        if len(data) < 5:
            return b''
        
        try:
            num_codes = data[0]
            pos = 1
            
            # Read codebook
            codes = {}
            for _ in range(num_codes):
                if pos + 2 >= len(data):
                    break
                byte = data[pos]
                code_len = data[pos + 1]
                code_byte = data[pos + 2]
                
                # Reconstruct code (simplified)
                code = format(code_byte, '08b')[:code_len] if code_len > 0 else "0"
                codes[code] = byte
                pos += 3
            
            # Read data length
            if pos + 4 > len(data):
                return b''
            
            data_length = int.from_bytes(data[pos:pos+4], 'little')
            pos += 4
            
            # Decode bits
            bit_string = ""
            for i in range(pos, len(data)):
                bit_string += format(data[i], '08b')
            
            bit_string = bit_string[:data_length]
            
            # Decode using codebook
            result = bytearray()
            i = 0
            while i < len(bit_string):
                found = False
                for length in range(1, 9):  # Try different code lengths
                    if i + length <= len(bit_string):
                        code = bit_string[i:i+length]
                        if code in codes:
                            result.append(codes[code])
                            i += length
                            found = True
                            break
                
                if not found:
                    # Fallback: interpret as raw byte
                    if i + 8 <= len(bit_string):
                        byte_val = int(bit_string[i:i+8], 2)
                        result.append(byte_val)
                        i += 8
                    else:
                        break
            
            return bytes(result)
        except:
            return b''
    
    @staticmethod
    def _decompress_arithmetic_coding(data):
        """Decompress arithmetic coding"""
        if len(data) < 4:
            return b''
        
        try:
            num_ranges = data[0]
            pos = 1
            
            # Read probability ranges
            ranges = {}
            for _ in range(num_ranges):
                if pos + 2 >= len(data):
                    break
                byte = data[pos]
                low = data[pos + 1] / 255.0
                high = data[pos + 2] / 255.0
                ranges[byte] = (low, high)
                pos += 3
            
            # Decode data
            result = bytearray()
            while pos < len(data):
                encoded_val = data[pos] / 255.0
                
                # Find matching byte
                found = False
                for byte, (low, high) in ranges.items():
                    if low <= encoded_val <= high:
                        result.append(byte)
                        found = True
                        break
                
                if not found:
                    result.append(data[pos])  # Fallback
                
                pos += 1
            
            return bytes(result)
        except:
            return b''

class KlondikeArchiver:
    def __init__(self, root):
        self.root = root
        self.root.title("Klondike Archiver")
        self.root.geometry("1100x750")
        self.root.minsize(800, 600)
        
        # Set custom icon
        self.set_app_icon()
        
        # Current archive data
        self.archive_data = {}
        self.current_archive_file = None
        self.current_directory = Path.cwd()
        self.unsaved_changes = False
        
        # Configure style
        self.setup_styles()
        self.setup_ui()
        self.refresh_file_list()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Check if a file was passed as command line argument
        if len(sys.argv) > 1:
            file_to_open = sys.argv[1]
            if file_to_open.endswith('.kc') and Path(file_to_open).exists():
                self.root.after(100, lambda: self.open_specific_archive(file_to_open))
    
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
        # Use the existing open_archive worker logic
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
                    
                    archive_data = {}
                    table_offset = 0
                    data_start = f.tell()
                    
                    for i in range(num_files):
                        progress = 20 + (i / num_files) * 70
                        self.root.after(0, lambda p=progress, idx=i: 
                                      self.update_progress(p, f"Loading file {idx+1}/{num_files}..."))
                        
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
                        
                        f.seek(data_start + data_offset)
                        compressed_data = f.read(compressed_size)
                        
                        original_data = NuggetCompression.decompress(compressed_data)
                        
                        archive_data[filename] = {
                            'data': original_data,
                            'compressed_data': compressed_data,
                            'size': original_size,
                            'compressed_size': compressed_size,
                            'type': file_type
                        }
                        
                        if i % 5 == 0:
                            time.sleep(0.01)
                
                def on_complete():
                    self.hide_progress()
                    self.archive_data = archive_data
                    self.clear_unsaved_changes()
                    self.refresh_archive_tree()
                    self.update_archive_info()
                    
                    archive_name = Path(file_path).name
                    total_files = len(self.archive_data)
                    self.status_var.set(f"📂 Opened '{archive_name}' - {total_files} files loaded successfully!")
                
                self.root.after(0, on_complete)
                
            except Exception as e:
                self.root.after(0, lambda: self.hide_progress())
                self.root.after(0, lambda: messagebox.showerror("Open Error", f"Failed to open archive: {e}"))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
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
        
        title_label = ttk.Label(header_frame, text= "Klondike Archiver", 
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
        """Navigate to home directory"""
        self.current_directory = Path.home()
        self.refresh_file_list()
    
    def add_folder_to_archive(self):
        """Add an entire folder to the archive"""
        folder_path = filedialog.askdirectory(title="Select folder to add to archive")
        if not folder_path:
            return
        
        def worker():
            try:
                folder = Path(folder_path)
                files_to_add = []
                
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
                                      self.update_progress(p, f"Compressing {name}..."))
                        
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                        
                        compressed_data = NuggetCompression.compress(file_data)
                        
                        def add_to_archive():
                            self.archive_data[relative_name] = {
                                'data': file_data,
                                'compressed_data': compressed_data,
                                'size': len(file_data),
                                'compressed_size': len(compressed_data),
                                'type': file_path.suffix or 'file'
                            }
                        
                        self.root.after(0, add_to_archive)
                        added_count += 1
                        
                        if i % 5 == 0:
                            time.sleep(0.01)
                            
                    except Exception as e:
                        self.root.after(0, lambda err=str(e), name=relative_name: 
                                      messagebox.showerror("Error", f"Failed to add {name}: {err}"))
                
                def on_complete():
                    self.hide_progress()
                    if added_count > 0:
                        self.mark_unsaved_changes()
                        self.refresh_archive_tree()
                        self.update_archive_info()
                        self.status_var.set(f"✅ Added {added_count} file(s) from folder with Ultimate compression!")
                
                self.root.after(0, on_complete)
                
            except Exception as e:
                self.root.after(0, lambda: self.hide_progress())
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to add folder: {e}"))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def add_files_to_archive(self):
        """Add selected files to the archive with progress tracking"""
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
        
        if len(files_to_add) > 1:
            def worker():
                try:
                    self.root.after(0, lambda: self.show_progress("Adding files to archive..."))
                    
                    added_count = 0
                    total_files = len(files_to_add)
                    
                    for i, (filename, file_path) in enumerate(files_to_add):
                        try:
                            progress = (i / total_files) * 100
                            self.root.after(0, lambda p=progress, name=filename: 
                                          self.update_progress(p, f"Compressing {name}..."))
                            
                            with open(file_path, 'rb') as f:
                                file_data = f.read()
                            
                            compressed_data = NuggetCompression.compress(file_data)
                            
                            def add_to_archive():
                                self.archive_data[filename] = {
                                    'data': file_data,
                                    'compressed_data': compressed_data,
                                    'size': len(file_data),
                                    'compressed_size': len(compressed_data),
                                    'type': file_path.suffix or 'file'
                                }
                            
                            self.root.after(0, add_to_archive)
                            added_count += 1
                            
                            time.sleep(0.01)
                            
                        except Exception as e:
                            self.root.after(0, lambda err=str(e), name=filename: 
                                          messagebox.showerror("Error", f"Failed to add {name}: {err}"))
                    
                    def on_complete():
                        self.hide_progress()
                        if added_count > 0:
                            self.mark_unsaved_changes()
                            self.refresh_archive_tree()
                            self.update_archive_info()
                            self.status_var.set(f"✅ Added {added_count} file(s) to archive with Ultimate compression!")
                    
                    self.root.after(0, on_complete)
                    
                except Exception as e:
                    self.root.after(0, lambda: self.hide_progress())
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Background operation failed: {e}"))
            
            thread = threading.Thread(target=worker, daemon=True)
            thread.start()
        else:
            # Single file - process immediately
            filename, file_path = files_to_add[0]
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                compressed_data = NuggetCompression.compress(file_data)
                
                self.archive_data[filename] = {
                    'data': file_data,
                    'compressed_data': compressed_data,
                    'size': len(file_data),
                    'compressed_size': len(compressed_data),
                    'type': file_path.suffix or 'file'
                }
                
                self.mark_unsaved_changes()
                self.refresh_archive_tree()
                self.update_archive_info()
                self.status_var.set(f"✅ Added {filename} to archive with Ultimate compression!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add {filename}: {e}")
    
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
        
        extract_dir = filedialog.askdirectory(title="Choose extraction directory")
        if not extract_dir:
            return
        
        extract_path = Path(extract_dir)
        extracted_count = 0
        
        for selection in selections:
            filename = self.archive_tree.item(selection, "text")
            if filename.startswith(("📝", "🖼️", "🎵", "🎬", "📦", "⚙️", "📄")):
                filename = filename[2:].strip()
            
            if filename in self.archive_data:
                try:
                    output_file = extract_path / filename
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'wb') as f:
                        f.write(self.archive_data[filename]['data'])
                    extracted_count += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to extract {filename}: {e}")
        
        if extracted_count > 0:
            self.status_var.set(f"✅ Extracted {extracted_count} file(s) to {extract_dir}")
    
    def extract_all_files(self):
        """Extract all files from archive"""
        if not self.archive_data:
            messagebox.showwarning("Empty Archive", "No files to extract.")
            return
        
        extract_dir = filedialog.askdirectory(title="Choose extraction directory")
        if not extract_dir:
            return
        
        def worker():
            try:
                extract_path = Path(extract_dir)
                extracted_count = 0
                
                self.root.after(0, lambda: self.show_progress("Extracting all files..."))
                total_files = len(self.archive_data)
                
                for i, (filename, file_info) in enumerate(self.archive_data.items()):
                    try:
                        progress = (i / total_files) * 100
                        self.root.after(0, lambda p=progress, name=filename: 
                                      self.update_progress(p, f"Extracting {name}..."))
                        
                        output_file = extract_path / filename
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_file, 'wb') as f:
                            f.write(file_info['data'])
                        extracted_count += 1
                        
                        if i % 3 == 0:
                            time.sleep(0.01)
                            
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
                if filename in self.archive_data:
                    del self.archive_data[filename]
                    removed_count += 1
            
            if removed_count > 0:
                self.mark_unsaved_changes()
                self.refresh_archive_tree()
                self.update_archive_info()
                self.status_var.set(f"🗑️ Removed {removed_count} file(s) from archive")
    
    def refresh_archive_tree(self):
        """Refresh the archive contents tree with enhanced display"""
        self.archive_tree.delete(*self.archive_tree.get_children())
        
        if not self.archive_data:
            self.banner_text.set("📭 Archive is empty - add some files!")
            return
        
        total_original = 0
        total_compressed = 0
        
        for filename, file_info in self.archive_data.items():
            original_size = file_info['size']
            compressed_size = file_info['compressed_size']
            file_type = file_info['type']
            
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
        file_count = len(self.archive_data)
        if total_original > 0:
            overall_ratio = (total_compressed / total_original * 100)
            self.banner_text.set(
                f"📊 {file_count} files • {self.format_file_size(total_original)} → "
                f"{self.format_file_size(total_compressed)} ({overall_ratio:.1f}% compression)"
            )
        else:
            self.banner_text.set(f"📊 {file_count} files in archive")
    
    def update_archive_info(self):
        """Update the archive info display and statistics"""
        if not self.archive_data:
            self.archive_info_var.set("Ready to create or open an archive")
            self.stats_var.set("No files")
            return
        
        file_count = len(self.archive_data)
        total_original = sum(f['size'] for f in self.archive_data.values())
        total_compressed = sum(f['compressed_size'] for f in self.archive_data.values())
        
        if self.current_archive_file:
            filename = Path(self.current_archive_file).name
            self.archive_info_var.set(f"📁 {filename}")
        else:
            self.archive_info_var.set("📝 Unsaved archive")
        
        if total_original > 0:
            overall_ratio = (total_compressed / total_original * 100)
            saved_space = total_original - total_compressed
            self.stats_var.set(
                f"{file_count} files\n"
                f"{self.format_file_size(total_original)} → {self.format_file_size(total_compressed)}\n"
                f"Saved: {self.format_file_size(saved_space)} ({100-overall_ratio:.1f}%)"
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
        
        self.archive_data = {}
        self.current_archive_file = None
        self.clear_unsaved_changes()
        self.refresh_archive_tree()
        self.update_archive_info()
        self.status_var.set("🆕 New archive created - ready for files!")
    
    def save_archive_as(self):
        """Save archive with a new name"""
        if not self.archive_data:
            messagebox.showwarning("Empty Archive", "No files to save. Add some files first!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Klondike Archive As...",
            defaultextension=".kc",
            filetypes=[
                ("Klondike Crinkle", "*.kc"), 
                ("Klondike Archive", "*.ka"), 
                ("Klondike ZIP", "*.kzip"), 
                ("All files", "*.*")
            ],
            initialdir=self.current_directory
        )
        
        if file_path:
            self.current_archive_file = file_path
            self.save_archive()
    
    def save_archive(self):
        """Save archive to file with progress tracking"""
        if not self.archive_data:
            messagebox.showwarning("Empty Archive", "No files to save. Add some files first!")
            return
        
        if not self.current_archive_file:
            self.save_archive_as()
            return
        
        def worker():
            try:
                file_count = len(self.archive_data)
                if file_count > 5:
                    self.root.after(0, lambda: self.show_progress("Saving archive..."))
                
                with open(self.current_archive_file, 'wb') as f:
                    f.write(b'KLONDIKE')
                    f.write(b'ULTIMATE')
                    f.write(struct.pack('<I', len(self.archive_data)))
                    
                    file_table_data = b''
                    file_data_section = b''
                    
                    for i, (filename, file_info) in enumerate(self.archive_data.items()):
                        if file_count > 5:
                            progress = (i / file_count) * 90
                            self.root.after(0, lambda p=progress, name=filename: 
                                          self.update_progress(p, f"Processing {name}..."))
                        
                        compressed_data = file_info['compressed_data']
                        
                        filename_bytes = filename.encode('utf-8')
                        file_table_data += struct.pack('<H', len(filename_bytes))
                        file_table_data += filename_bytes
                        file_table_data += struct.pack('<I', file_info['size'])
                        file_table_data += struct.pack('<I', len(compressed_data))
                        file_table_data += struct.pack('<I', len(file_data_section))
                        
                        file_type_bytes = file_info['type'].encode('utf-8')
                        file_table_data += struct.pack('<H', len(file_type_bytes))
                        file_table_data += file_type_bytes
                        
                        file_data_section += compressed_data
                        
                        if i % 3 == 0:
                            time.sleep(0.001)
                    
                    if file_count > 5:
                        self.root.after(0, lambda: self.update_progress(95, "Writing archive file..."))
                    
                    f.write(struct.pack('<I', len(file_table_data)))
                    f.write(file_table_data)
                    f.write(file_data_section)
                
                def on_complete():
                    if file_count > 5:
                        self.hide_progress()
                    
                    self.clear_unsaved_changes()
                    self.update_archive_info()
                    
                    total_original = sum(f['size'] for f in self.archive_data.values())
                    total_compressed = sum(f['compressed_size'] for f in self.archive_data.values())
                    savings = ((total_original - total_compressed) / total_original * 100) if total_original > 0 else 0
                    
                    self.status_var.set(f"💾 Archive saved! {savings:.1f}% compression achieved with Ultimate Nugget algorithm")
                
                self.root.after(0, on_complete)
                
            except Exception as e:
                def on_error():
                    if file_count > 5:
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
                        
                        archive_data = {}
                        table_offset = 0
                        data_start = f.tell()
                        
                        for i in range(num_files):
                            progress = 20 + (i / num_files) * 70
                            self.root.after(0, lambda p=progress, idx=i: 
                                          self.update_progress(p, f"Loading file {idx+1}/{num_files}..."))
                            
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
                            
                            f.seek(data_start + data_offset)
                            compressed_data = f.read(compressed_size)
                            
                            original_data = NuggetCompression.decompress(compressed_data)
                            
                            archive_data[filename] = {
                                'data': original_data,
                                'compressed_data': compressed_data,
                                'size': original_size,
                                'compressed_size': compressed_size,
                                'type': file_type
                            }
                            
                            if i % 5 == 0:
                                time.sleep(0.01)
                    
                    def on_complete():
                        self.hide_progress()
                        self.archive_data = archive_data
                        self.current_archive_file = file_path
                        self.clear_unsaved_changes()
                        self.refresh_archive_tree()
                        self.update_archive_info()
                        
                        archive_name = Path(file_path).name
                        total_files = len(self.archive_data)
                        self.status_var.set(f"📂 Opened '{archive_name}' - {total_files} files loaded successfully!")
                    
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