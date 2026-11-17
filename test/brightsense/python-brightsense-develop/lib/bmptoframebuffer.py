import framebuf

class BMPToFramebuffer:    
    def parse_bmp_header(self, bmp_data):
        """
        Parse BMP header to extract image information
        Returns: (pixel_data_offset, width, height, bits_per_pixel)
        """
        if len(bmp_data) < 54:
            raise ValueError("Invalid BMP file - too small")
        
        # Check BMP signature
        if bmp_data[0:2] != b'BM':
            raise ValueError("Not a valid BMP file")
        
        # Extract header information
        pixel_data_offset = int.from_bytes(bmp_data[10:14], 'little')
        width = int.from_bytes(bmp_data[18:22], 'little')
        height = int.from_bytes(bmp_data[22:26], 'little')
        bits_per_pixel = int.from_bytes(bmp_data[28:30], 'little')
        
        print(f"BMP Info: {width}x{height}, {bits_per_pixel} bpp, data offset: {pixel_data_offset}")
        
        return pixel_data_offset, width, height, bits_per_pixel
    
    def convert_bmp_to_mono_buffer(self, bmp_data):
        """
        Convert BMP data to 1-bit monochrome buffer for e-paper display
        Returns framebuffer compatible with IL0373
        """
        try:
            # Parse BMP header
            offset, width, height, bpp = self.parse_bmp_header(bmp_data)
            
            # Extract pixel data
            pixel_data = bmp_data[offset:]
            
            # Calculate row padding (BMP rows are padded to 4-byte boundaries)
            if bpp == 1:
                # 1-bit BMP (already monochrome)
                bytes_per_row = (width + 7) // 8
                padded_bytes_per_row = (bytes_per_row + 3) & ~3  # Round up to 4-byte boundary
                
                # Create buffer for framebuffer (no padding needed for framebuffer)
                fb_buffer = bytearray((width * height) // 8)
                
                # Copy pixel data, removing padding and flipping vertically
                for y in range(height):
                    src_row_start = (height - 1 - y) * padded_bytes_per_row  # BMP is bottom-up
                    dst_row_start = y * bytes_per_row
                    
                    for x in range(bytes_per_row):
                        if src_row_start + x < len(pixel_data):
                            fb_buffer[dst_row_start + x] = pixel_data[src_row_start + x]
                
            elif bpp == 24:
                # 24-bit BMP - convert to monochrome
                bytes_per_pixel = 3
                bytes_per_row = width * bytes_per_pixel
                padded_bytes_per_row = (bytes_per_row + 3) & ~3
                
                fb_buffer = bytearray((width * height) // 8)
                
                for y in range(height):
                    src_row_start = (height - 1 - y) * padded_bytes_per_row
                    
                    for x in range(width):
                        pixel_offset = src_row_start + x * bytes_per_pixel
                        
                        if pixel_offset + 2 < len(pixel_data):
                            # BMP uses BGR order
                            b = pixel_data[pixel_offset]
                            g = pixel_data[pixel_offset + 1]
                            r = pixel_data[pixel_offset + 2]
                            
                            # Convert to grayscale and threshold
                            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                            is_black = gray < 128  # Threshold at 128
                            
                            # Set bit in framebuffer
                            byte_idx = (y * width + x) // 8
                            bit_idx = 7 - ((y * width + x) % 8)  # MSB first
                            
                            if is_black:
                                fb_buffer[byte_idx] |= (1 << bit_idx)
            
            else:
                raise ValueError(f"Unsupported BMP format: {bpp} bits per pixel")
            
            # Create framebuffer
            fb = framebuf.FrameBuffer(fb_buffer, width, height, framebuf.MONO_HLSB)
            return fb
            
        except Exception as e:
            raise Exception(f"Error occured while processing BMP: {e}")