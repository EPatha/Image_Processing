from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from matplotlib import pyplot as plt

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
        except Exception as e:
            print("Error opening image:", e)

def compress_image():
    global compressed_img, compressed_size, img_display_compressed
    try:
        img_cv = cv2.imread(img_path)

        # Ensure the directory exists
        output_dir = "data/result-compressed"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Define the path for the compressed image
        compressed_path = os.path.join(output_dir, "compressed_image.jpg")

        # Compress the image and save it
        cv2.imwrite(compressed_path, img_cv, [int(cv2.IMWRITE_JPEG_QUALITY), 50])  # Compression quality 50%
        
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
        
        # Calculate metrics
        calculate_metrics(img_path, compressed_path)
    except Exception as e:
        print("Error compressing image:", e)

# Add this new function for Hitung button
# def hitung_metrics():
#     if img_path:
#         compress_image()
#     else:
#         print("Please open an image first.")

# Function to calculate the metrics (PSNR, MSE, SSIM, Entropy)
def calculate_metrics(original, compressed):
    global mse_value, psnr_value, ssim_value, entropy_value
    
    original_img = cv2.imread(original, cv2.IMREAD_GRAYSCALE)
    compressed_img = cv2.imread(compressed, cv2.IMREAD_GRAYSCALE)

    # MSE
    mse_value = np.mean((original_img - compressed_img) ** 2)
    # PSNR
    psnr_value = cv2.PSNR(original_img, compressed_img)
    # SSIM
    ssim_value, _ = ssim(original_img, compressed_img, full=True)
    # Entropy
    entropy_value = -np.sum(original_img / 255 * np.log2(original_img / 255 + 1e-10))

    # Update metrics
    entry_psnr.delete(0, END)
    entry_psnr.insert(0, f"{psnr_value:.4f}")

    entry_mse.delete(0, END)
    entry_mse.insert(0, f"{mse_value:.4f}")

    entry_ssim.delete(0, END)
    entry_ssim.insert(0, f"{ssim_value:.4f}")

    entry_entropy.delete(0, END)
    entry_entropy.insert(0, f"{entropy_value:.4f}")

def reset_fields():
    label_original_img.config(image="", bg="gray")
    entry_size_original.delete(0, END)
    label_compressed_img.config(image="", bg="white")
    entry_size_compressed.delete(0, END)
    entry_psnr.delete(0, END)
    entry_mse.delete(0, END)
    entry_ssim.delete(0, END)
    entry_entropy.delete(0, END)

def plot_histogram():
    img_cv = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    plt.hist(img_cv.ravel(), 256, [0, 256])
    plt.title('Histogram')
    plt.xlabel('Pixel Values')
    plt.ylabel('Frequency')
    plt.show()

# Root window setup
root = Tk()
root.title("Image Compression Tool")
root.geometry("1200x800")
root.resizable(False, False)

# Frames for layout (these need to be defined before they are used)
frame_left = Frame(root, padx=10, pady=10)
frame_left.pack(side=LEFT, fill=Y)

frame_center = Frame(root, padx=10, pady=10)
frame_center.pack(side=LEFT)

frame_right = Frame(root, padx=10, pady=10)
frame_right.pack(side=RIGHT)

# Buttons - Left Frame
Label(frame_left, text="Pengolahan", font=("Arial", 12, "bold")).pack(pady=5)
Button(frame_left, text="Buka Citra", width=15, command=open_image).pack(pady=5)
Button(frame_left, text="Kompresi", width=15, command=compress_image).pack(pady=5)
Button(frame_left, text="Histogram", width=15, command=plot_histogram).pack(pady=5)
# Button(frame_left, text="Hitung", width=15, command=hitung_metrics).pack(pady=5)  # Added Hitung button
Button(frame_left, text="Reset", width=15, command=reset_fields).pack(pady=5)

# Original Image - Center Frame
Label(frame_center, text="Citra Asli", font=("Arial", 10, "bold")).pack()
label_original_img = Label(frame_center, width=250, height=250, bg="gray")
label_original_img.pack(pady=5)
Label(frame_center, text="Ukuran Citra Asli").pack()
entry_size_original = Entry(frame_center, width=30)
entry_size_original.pack()

# Compressed Image - Right Frame
Label(frame_right, text="Citra Hasil Kompresi", font=("Arial", 10, "bold")).pack()
label_compressed_img = Label(frame_right, width=250, height=250, bg="white")
label_compressed_img.pack(pady=5)
Label(frame_right, text="Ukuran Citra Hasil Kompresi").pack()
entry_size_compressed = Entry(frame_right, width=30)
entry_size_compressed.pack()

# Metrics Entries
Label(frame_right, text="PSNR").pack()
entry_psnr = Entry(frame_right, width=30)
entry_psnr.pack()

Label(frame_right, text="MSE").pack()
entry_mse = Entry(frame_right, width=30)
entry_mse.pack()

Label(frame_right, text="SSIM").pack()
entry_ssim = Entry(frame_right, width=30)
entry_ssim.pack()

Label(frame_right, text="Entropy").pack()
entry_entropy = Entry(frame_right, width=30)
entry_entropy.pack()

# Run the application
root.mainloop()
