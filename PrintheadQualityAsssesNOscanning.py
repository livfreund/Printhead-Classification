#this program counts the number of pixels in a given image 
#in order to classify the quality of a printhead. will count the number of dark pixels 
#in the image a certain printhead produces and compare it do a designated 
#number of pixels that is from a known "good printhead". will assess the quality on a 
#standard deviation basis of the averages. 
 
#creating a user interface in order to draw the boxes over the images needed 
import tkinter as tk
#filedialog is a module in Tkinter to implement file-related actions
#like selecting a file to open, choosing a loc to save a file,&picking a directory. 
from tkinter import filedialog
#PIL stands for Python Imaging Library. 
#importing Image allows us to be able to open an image within the program.
#importing ImageTk allows us to create&manipulate tkinter,referenced earlier. 
from PIL import Image, ImageTk
import numpy as np  

#creating the UI 
class ImageBoxCounter: 
    def __init__(self, root):
        self.root = root
        self.root.title("Printhead Quality Assessor")

        self.canvas = tk.Canvas(root)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image = None
        self.image_tk = None
        self.start_x = None
        self.start_y = None
        self.count_list = [] #stores the counts so we can compare with the standard deviations 
        self.image_count = 0
        
        #a scale for threshold adjustment
        #creating a frame to hold the scale and the text
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)  #pack the frame at the bottom 

        #the scale itself
        self.threshold_scale = tk.Scale(self.control_frame, from_=0, to=255, orient=tk.HORIZONTAL, label ="Darkness Threshold", length = 109)
        self.threshold_scale.set(150)  #set default threshold
        self.threshold_scale.pack() 
        
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Image", command=self.open_image)
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)

        #initializing total pixel count in image text
        self.instr_1 = tk.Label(self.control_frame, text="Please open an image from a designated good printhead.", fg='black', font=("Helvetica", 8, "bold"))
        self.instr_1.pack()

    #function to open the image 
    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if file_path:
            self.load_image(file_path)
            self.image_count += 1
            #calling count_pixels method to count all dark pixels in entire image 
            threshold = self.threshold_scale.get()
            self.count_dark_pixels(threshold)

    #function to load the image 
    def load_image(self, path):
        self.image = Image.open(path).convert("RGB") #preserving the original image 
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

    def count_dark_pixels(self, threshold):                                                                            
        count = 0
        if self.image is not None:
            img_array = np.array(self.image)
            mask = np.all(img_array < threshold, axis=-1)  # Count pixels below threshold across all channels
            count = np.sum(mask)  # Total dark pixels
            self.count_list.append(count)

        if self.image_count < 2:
            #display the result on the UI
            self.instr_1.destroy() 
            self.instr_2 = tk.Label(self.control_frame, text="Now, open an image from the printhead you are looking to assess.", fg='black', font=("Helvetica", 8, "bold"))
            self.instr_2.pack()
        else: 
            self.image_count == 2
            self.instr_2.destroy()
            self.assess_quality() 
        return count       

    def assess_quality(self): 
        std_deviation = np.std(self.count_list)
        self.display_results1 = tk.Label(self.control_frame, text=f"The printhead being assessed is {std_deviation} standard deviations", fg='red') 
        self.display_results2 = tk.Label(self.control_frame, text=f"from being an acceptable quality printhead.", fg='red')
        self.display_results1.pack()
        self.display_results2.pack()
   
#calling the main function 
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBoxCounter(root)
    root.mainloop()
