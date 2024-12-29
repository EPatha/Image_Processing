from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Functionality placeholders
def open_image():
    global img, img_display, img_path, original_size
    file_path = filedialog.askopenfilename(
            initialdir="data/",
            title="Select an Image File",
            filetypes=[("All Files", "*.*")]  # Show all files for testing
        )

    if file_path:
        try:
            img_path = file_path
            img = Image.open(file_path).convert("RGBA")
            img_display = ImageTk.PhotoImage(img.resize((250, 250)))
            label_original_img.config(image=img_display)
            label_original_img.image = img_display  # Prevent garbage collection
            # Display image size
            original_size = os.path.getsize(file_path) / 1024  # Size in KB
            entry_size_original.delete(0, END)
            entry_size_original.insert(0, f"{original_size:.4f} kb")
            
            # Plot histogram of the original image
            plot_histogram(img_path, "original")
            
            # Display the size difference after compression (if compression happens later)
            entry_size_difference.delete(0, END)
            
        except Exception as e:
            print("Error opening image:", e)

def compress_image():
    global compressed_img, compressed_size, img_display_compressed, compression_quality, algorithm_name
    try:
        img_cv = cv2.imread(img_path)

        # Ensure the directory exists
        output_dir = "data/result-compressed"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Define the path for the compressed image
        compressed_path = os.path.join(output_dir, "compressed_image.jpg")

        # Compression quality (percentage)
        compression_quality = quality_slider.get()  # Get compression quality from slider
        algorithm_name = "JPEG Compression"  # Set the algorithm name

        # Compress the image and save it
        cv2.imwrite(compressed_path, img_cv, [int(cv2.IMWRITE_JPEG_QUALITY), compression_quality])  # Compression quality

        # Get the compressed image size
        compressed_size = os.path.getsize(compressed_path) / 1024  # Size in KB
        
        # Display the compressed image in the UI
        compressed_img = Image.open(compressed_path).resize((250, 250))
        img_display_compressed = ImageTk.PhotoImage(compressed_img)
        label_compressed_img.config(image=img_display_compressed)
        label_compressed_img.image = img_display_compressed

        # Update the size of the compressed image in the UI
        entry_size_compressed.delete(0, END)
        entry_size_compressed.insert(0, f"{compressed_size:.4f} kb")
        
        # Update the size difference between the original and compressed image
        size_difference = original_size - compressed_size
        entry_size_difference.delete(0, END)
        entry_size_difference.insert(0, f"{size_difference:.4f} kb")
        
        # Plot histogram of the compressed image
        plot_histogram(compressed_path, "compressed")
        
        # Calculate metrics for the compressed image
        calculate_metrics(img_path, compressed_path)
    except Exception as e:
        print("Error compressing image:", e)

def plot_histogram(image_path, img_type):
    img_cv = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Create a Matplotlib figure
    fig = Figure(figsize=(6, 3), dpi=100)
    ax = fig.add_subplot(111)
    ax.hist(img_cv.ravel(), bins=256, range=[0, 256])
    ax.set_title(f'{img_type.capitalize()} Image Histogram')
    ax.set_xlabel('Pixel Values')
    ax.set_ylabel('Frequency')

    global canvas_original, canvas_compressed
    
    if img_type == "original":
        if canvas_original:
            canvas_original.get_tk_widget().destroy()  # Clear the existing canvas
        canvas_original = FigureCanvasTkAgg(fig, frame_histogram_original)
        canvas_original.draw()
        canvas_original.get_tk_widget().pack(fill=BOTH, expand=True)

    else:
        if canvas_compressed:
            canvas_compressed.get_tk_widget().destroy()  # Clear the existing canvas
        canvas_compressed = FigureCanvasTkAgg(fig, frame_histogram_compressed)
        canvas_compressed.draw()
        canvas_compressed.get_tk_widget().pack(fill=BOTH, expand=True)

# Function to calculate the metrics (PSNR, MSE, SSIM, Entropy, UACI) only for compressed image
def calculate_metrics(original, compressed):
    global mse_value, psnr_value, ssim_value, entropy_value, uaci_value
    
    original_img = cv2.imread(original, cv2.IMREAD_GRAYSCALE)
    compressed_img = cv2.imread(compressed, cv2.IMREAD_GRAYSCALE)

    # Hanya lakukan perhitungan untuk citra kompresi
    if compressed_img is not None:
        # MSE
        mse_value = np.mean((original_img - compressed_img) ** 2)
        # PSNR
        psnr_value = cv2.PSNR(original_img, compressed_img)
        # SSIM
        ssim_value, _ = ssim(original_img, compressed_img, full=True)
        # UACI
        uaci_value = np.mean(np.abs(original_img - compressed_img) / 255) * 100  # UACI dalam persen
        # Entropy untuk citra kompres
        entropy_value_compressed = -np.sum(compressed_img / 255 * np.log2(compressed_img / 255 + 1e-10))

        # Update metrik untuk citra hasil kompres
        entry_psnr_compressed.delete(0, END)
        entry_psnr_compressed.insert(0, f"{psnr_value:.4f}")
        
        entry_mse_compressed.delete(0, END)
        entry_mse_compressed.insert(0, f"{mse_value:.4f}")

        entry_ssim_compressed.delete(0, END)
        entry_ssim_compressed.insert(0, f"{ssim_value:.4f}")

        entry_uaci_compressed.delete(0, END)
        entry_uaci_compressed.insert(0, f"{uaci_value:.4f}")

        entry_entropy_compressed.delete(0, END)
        entry_entropy_compressed.insert(0, f"{entropy_value_compressed:.4f}")

def reset_fields():
    label_original_img.config(image="", bg="gray")
    entry_size_original.delete(0, END)
    label_compressed_img.config(image="", bg="white")
    entry_size_compressed.delete(0, END)
    entry_psnr_compressed.delete(0, END)
    entry_mse_compressed.delete(0, END)
    entry_ssim_compressed.delete(0, END)
    entry_entropy_compressed.delete(0, END)
    entry_uaci_compressed.delete(0, END)
    entry_size_difference.delete(0, END)
    entry_algorithm_name.delete(0, END)
    entry_compression_quality.delete(0, END)
    if canvas_original:
        canvas_original.get_tk_widget().destroy()
    if canvas_compressed:
        canvas_compressed.get_tk_widget().destroy()

def close_app():
    root.quit()  # Closes the application

# Root window setup (Fullscreen)
root = Tk()
root.title("Image Compression Tool")
root.attributes("-fullscreen", True)  # Set window to fullscreen
root.resizable(True, True)  # Allow resizing

# Frames for layout (adjust for fullscreen)
frame_top = Frame(root, padx=10, pady=10, bg='#2e3d49')
frame_top.pack(side=TOP, fill=X)

frame_left = Frame(root, padx=10, pady=10, bd=2, relief=SOLID)
frame_left.pack(side=LEFT, fill=Y, padx=5, expand=True)

frame_right = Frame(root, padx=10, pady=10, bd=2, relief=SOLID)
frame_right.pack(side=RIGHT, fill=Y, padx=5, expand=True)

# Frames for placing histograms below UACI metrics
frame_histogram_original = Frame(root, padx=10, pady=10, height=300)
frame_histogram_original.pack(side=LEFT, fill=X, padx=5)

frame_histogram_compressed = Frame(root, padx=10, pady=10, height=300)
frame_histogram_compressed.pack(side=RIGHT, fill=X, padx=5)

# Initialize the canvas variables
canvas_original = None
canvas_compressed = None

# Buttons - Top Frame
Button(frame_top, text="Buka Citra", width=15, command=open_image).pack(side=LEFT, padx=5)
Button(frame_top, text="Kompresi", width=15, command=compress_image).pack(side=LEFT, padx=5)

# Compression Quality Slider
Label(frame_top, text="Kualitas Kompresi", bg='#2e3d49', fg='white').pack(side=LEFT, padx=5)
quality_slider = Scale(frame_top, from_=0, to=100, orient=HORIZONTAL)
quality_slider.set(50)  # Default to 50%
quality_slider.pack(side=LEFT, padx=5)

# Reset Button (Closer to the other buttons)
Button(frame_top, text="Reset", width=15, command=reset_fields, bg="yellow", fg="black").pack(side=LEFT, padx=5)

# Close Button (Red "X" in the top right corner)
Button(frame_top, text="X", width=2, height=1, command=close_app, bg="red", fg="white", font=("Arial", 12, "bold")).pack(side=RIGHT, padx=5)

# Original Image - Left Frame
Label(frame_left, text="Citra Asli", font=("Arial", 10, "bold")).pack()
label_original_img = Label(frame_left, width=250, height=250, bg="gray")
label_original_img.pack(pady=5)
Label(frame_left, text="Ukuran Citra Asli").pack()
entry_size_original = Entry(frame_left, width=30)
entry_size_original.pack()

# Citra Asli - Hanya menampilkan ukuran file asli dan perbandingan dengan ukuran hasil kompresi
Label(frame_left, text="Perbedaan Ukuran (Asli - Kompresi)").pack()
entry_size_difference = Entry(frame_left, width=30)
entry_size_difference.pack()

# Compressed Image - Right Frame
Label(frame_right, text="Citra Hasil Kompresi", font=("Arial", 10, "bold")).pack()
label_compressed_img = Label(frame_right, width=250, height=250, bg="white")
label_compressed_img.pack(pady=5)
Label(frame_right, text="Ukuran Citra Hasil Kompresi").pack()
entry_size_compressed = Entry(frame_right, width=30)
entry_size_compressed.pack()

# Metrics for Compressed Image
Label(frame_right, text="PSNR").pack()
entry_psnr_compressed = Entry(frame_right, width=30)
entry_psnr_compressed.pack()

Label(frame_right, text="MSE").pack()
entry_mse_compressed = Entry(frame_right, width=30)
entry_mse_compressed.pack()

Label(frame_right, text="SSIM").pack()
entry_ssim_compressed = Entry(frame_right, width=30)
entry_ssim_compressed.pack()

Label(frame_right, text="Entropy").pack()
entry_entropy_compressed = Entry(frame_right, width=30)
entry_entropy_compressed.pack()

Label(frame_right, text="UACI").pack()
entry_uaci_compressed = Entry(frame_right, width=30)
entry_uaci_compressed.pack()

# Run the application
root.mainloop()
