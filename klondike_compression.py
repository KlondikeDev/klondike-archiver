"""
Klondike Archiver - Compression Module
Enhanced compression algorithms with memory optimization
"""

import zlib
from pathlib import Path

# File types that are already compressed and shouldn't be compressed again
COMPRESSED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff',
    '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',
    '.zip', '.rar', '.7z', '.gz', '.bz2', '.xz', '.tar',
    '.exe', '.dll', '.msi', '.dmg', '.pkg',
    '.pdf', '.apk', '.ipa'
}

def should_compress(filename):
    """Determine if a file should be compressed based on its extension"""
    return Path(filename).suffix.lower() not in COMPRESSED_EXTENSIONS

class OptimizedCompression:
    """
    Optimized compression system that adapts to file size and type
    Uses different strategies to minimize memory usage while maintaining efficiency
    """
    
    # Memory management thresholds
    SMALL_CHUNK = 64 * 1024        # 64KB for compression chunks
    LARGE_CHUNK = 1024 * 1024      # 1MB for file processing
    STREAM_THRESHOLD = 10 * 1024 * 1024  # 10MB threshold for streaming
    
    @staticmethod
    def compress_smart(data, progress_callback=None):
        """
        Smart compression that adapts to data size and characteristics
        
        Args:
            data: Raw file data to compress
            progress_callback: Optional callback for progress updates
            
        Returns:
            Compressed data with compression type header
        """
        if len(data) < 100:
            # Very small files - no compression overhead
            return b'\x00' + data
        
        # Choose compression strategy based on size
        if len(data) > OptimizedCompression.STREAM_THRESHOLD:
            return OptimizedCompression._compress_streaming(data, progress_callback)
        elif len(data) > OptimizedCompression.LARGE_CHUNK:
            return OptimizedCompression._compress_chunked_smart(data, progress_callback)
        else:
            return OptimizedCompression._compress_fast(data, progress_callback)
    
    @staticmethod
    def _compress_streaming(data, progress_callback=None):
        """
        Stream large files through compression to avoid RAM overload
        Uses zlib streaming compression with memory-efficient chunking
        """
        compressor = zlib.compressobj(level=6, wbits=15)
        compressed_chunks = []
        total_size = len(data)
        processed = 0
        
        chunk_size = OptimizedCompression.SMALL_CHUNK
        
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            compressed_chunk = compressor.compress(chunk)
            if compressed_chunk:
                compressed_chunks.append(compressed_chunk)
            
            processed += len(chunk)
            
            # Update progress every 10 chunks to avoid UI overhead
            if progress_callback and i % (chunk_size * 10) == 0:
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
        """
        Efficient chunked compression for medium-sized files
        Balances compression ratio with speed
        """
        try:
            if progress_callback:
                progress_callback(25)
            
            # Use level 7 compression - good ratio without excessive CPU time
            compressed = zlib.compress(data, level=7)
            
            if progress_callback:
                progress_callback(100)
            
            return b'\x02' + compressed
        except Exception:
            # Fallback to no compression if zlib fails
            return b'\x00' + data
    
    @staticmethod
    def _compress_fast(data, progress_callback=None):
        """
        Fast compression for small files
        Prioritizes speed over compression ratio
        """
        try:
            if progress_callback:
                progress_callback(50)
            
            # Use fast zlib compression (level 3)
            compressed = zlib.compress(data, level=3)
            
            if progress_callback:
                progress_callback(100)
            
            return b'\x03' + compressed
        except Exception:
            return b'\x00' + data
    
    @staticmethod
    def decompress_smart(data):
        """
        Smart decompression that handles all compression types
        
        Args:
            data: Compressed data with type header
            
        Returns:
            Decompressed raw data
        """
        if len(data) == 0:
            return b''
        
        compression_type = data[0]
        compressed_data = data[1:]
        
        if compression_type == 0:
            # No compression - return raw data
            return compressed_data
        elif compression_type in [1, 2, 3]:
            # zlib variants - decompress
            try:
                return zlib.decompress(compressed_data)
            except Exception:
                # Fallback to raw data if decompression fails
                return compressed_data
        else:
            # Unknown compression type - return raw data
            return compressed_data
    
    @staticmethod
    def get_compression_info(data):
        """
        Get information about compressed data
        
        Args:
            data: Compressed data with type header
            
        Returns:
            Dict with compression information
        """
        if len(data) == 0:
            return {'type': 'empty', 'ratio': 0}
        
        compression_type = data[0]
        
        type_names = {
            0: 'none',
            1: 'streaming',
            2: 'chunked',
            3: 'fast'
        }
        
        return {
            'type': type_names.get(compression_type, 'unknown'),
            'compressed_size': len(data) - 1,
            'has_header': True
        }

class CompressionStats:
    """Statistics tracking for compression operations"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all statistics"""
        self.files_processed = 0
        self.total_original_size = 0
        self.total_compressed_size = 0
        self.compression_times = []
        self.file_types = {}
    
    def add_file(self, original_size, compressed_size, file_type, compression_time):
        """Add statistics for a processed file"""
        self.files_processed += 1
        self.total_original_size += original_size
        self.total_compressed_size += compressed_size
        self.compression_times.append(compression_time)
        
        if file_type in self.file_types:
            self.file_types[file_type]['count'] += 1
            self.file_types[file_type]['original_size'] += original_size
            self.file_types[file_type]['compressed_size'] += compressed_size
        else:
            self.file_types[file_type] = {
                'count': 1,
                'original_size': original_size,
                'compressed_size': compressed_size
            }
    
    def get_compression_ratio(self):
        """Get overall compression ratio as percentage"""
        if self.total_original_size == 0:
            return 0
        return (self.total_compressed_size / self.total_original_size) * 100
    
    def get_space_saved(self):
        """Get total space saved in bytes"""
        return self.total_original_size - self.total_compressed_size
    
    def get_average_compression_time(self):
        """Get average compression time"""
        if not self.compression_times:
            return 0
        return sum(self.compression_times) / len(self.compression_times)
    
    def get_stats_summary(self):
        """Get a summary of compression statistics"""
        return {
            'files_processed': self.files_processed,
            'total_original_size': self.total_original_size,
            'total_compressed_size': self.total_compressed_size,
            'compression_ratio': self.get_compression_ratio(),
            'space_saved': self.get_space_saved(),
            'average_time': self.get_average_compression_time(),
            'file_types': self.file_types
        }