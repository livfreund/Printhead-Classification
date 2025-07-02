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
        self.rectangles = []
        self.start_x = None
        self.start_y = None
        self.pixel_counts_list = [] #stores pixel counts for each box created 
        self.average_list = [] #stores average pixel count fro each set so can compare later 
        self.box_count = 0 
        self.set_count = 0
        self.ordinals = ["First", "Second", "Third",  "Fourth", "Fifth"] #for box counting 
        #a scale for threshold adjustment
        #creating a frame to hold the scale and the text
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)  #pack the frame at the bottom 

        #the scale itself
        self.threshold_scale = tk.Scale(self.control_frame, from_=0, to=255, orient=tk.HORIZONTAL, label ="Darkness Threshold", length = 109)
        self.threshold_scale.set(150)  #set default threshold
        self.threshold_scale.pack() 

        #variable to hold the pixel count text 
        #initializing variable that tells how many times we've made the box corresponding to the printhead we're on. will need 5 before averaging
        self.instr_text1 = tk.Label(self.control_frame, text=f"Please open the image output from a designated good printerhead", fg="red")
        self.instr_text2 = tk.Label(self.control_frame, text=f"and drag mouse from top left to bottom right of the image 5 times.", fg="red")
        self.count_text = tk.Label(self.control_frame, text=f"Dark Pixel Count in {self.ordinals[self.box_count]} Box: 0", fg="black")
        self.count_text.pack() 
        self.instr_text1.pack()
        self.instr_text2.pack()
        
        
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Image", command=self.open_image)
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)

    #function to open the image 
    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if file_path:
            self.load_image(file_path)

    #function to load the image 
    def load_image(self, path):
        self.original_image = Image.open(path).convert("RGB") #preserving the original image 
        self.image = Image.open(path).convert() #for display
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

    #what to do upon pressing the button on your mouse 
    def on_button_press(self, event):
        #reset the displayed image back to the original state. no previous blue pixels or red boxes.
        self.rectangles = []
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        self.image = self.original_image.copy()
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.redraw()  #redraw to remove any previous blue highlights

        #starting a new rectangle 
        self.start_x = event.x
        self.start_y = event.y
        self.rectangles.append((self.start_x, self.start_y, self.start_x, self.start_y))
        self.draw_rectangle()

    #what to do upon dragging your mouse 
    def on_mouse_drag(self, event):
        self.rectangles[-1] = (self.start_x, self.start_y, event.x, event.y)
        self.redraw()

    #what to do when releasing the button 
    def on_button_release(self, event):
        self.rectangles[-1] = (self.start_x, self.start_y, event.x, event.y)
        self.redraw()
        #reset the image (remove the blue pixels)
        self.image = self.original_image.copy()  # Reset the image to its original state
        self.image_tk = ImageTk.PhotoImage(self.image)
        #count dark pixels and get the new count
        dark_pixel_count = self.count_dark_pixels(self.threshold_scale.get())  # Pass the current threshold value
        #update the display text with the new count
        self.update_count_text(dark_pixel_count)
        #increment box_count only after the box is completed
        self.box_count += 1
        #if this is the fifth box, add the counts for the set 
        if self.box_count == 5:
            self.add_counts()

    #when you draw the rectangle...
    def draw_rectangle(self):
        x1, y1, x2, y2 = self.rectangles[-1]
        self.canvas.create_rectangle(x1, y1, x2, y2, outline='red')

    #if need to redraw the rectangle...
    def redraw(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        for rect in self.rectangles:
            self.canvas.create_rectangle(rect, outline='red')

    #displaying the number of dark pixels counted on the UI. updated everytime 
    def update_count_text(self, count=0):
        if self.box_count < len(self.ordinals):
            text_to_display = f"Dark Pixel Count in {self.ordinals[self.box_count]} Box: {count}"
            self.count_text.config(text=text_to_display) 
    
    #counting the number of pixels within the designated box 
    def count_dark_pixels(self, threshold):
        count = 0

        if self.original_image is not None:
            img_array = np.array(self.original_image) #use original image array
            
            #get only the last rectangle
            x1, y1, x2, y2 = self.rectangles[-1]
            #ensure coordinates are within bounds
            x1, y1, x2, y2 = max(0, x1), max(0, y1), min(x2, img_array.shape[1]), min(y2, img_array.shape[0])
            box = img_array[y1:y2, x1:x2]

            #count and color dark pixels based on the threshold
            mask = np.all(box < threshold, axis=-1)
            count += np.sum(mask)
            
            #apply color change only to the display image
            #ensure valid selection (i.e., not empty) and there are dark pixels
            if np.any(mask):  # Only apply color change if there are matching pixels
                #if RGBA, convert to RGB (discard alpha channel)
                if img_array.shape[-1] == 4:  # RGBA image
                    img_array = img_array[..., :3]  # Drop the alpha channel

                #apply color change to dark pixels (turn them blue)
                img_array[y1:y2, x1:x2][mask] = [0, 0, 255]  # Set to blue
        
            #update the displayed image 
            self.image = Image.fromarray(img_array)
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.redraw()  # Redraw the canvas with the updated image 

        #print(f"Dark Pixel Count in {self.ordinals[self.box_count]} Box: {count}")
        if self.box_count < len(self.ordinals):
            self.pixel_counts_list.append(count) #adding the count to the list so we can add them all later. 
        return count 

    #adding the counts from all boxes
    def add_counts(self):
        if self.box_count == 5: 
            self.set_count += 1 
        set_average = np.mean(self.pixel_counts_list) 
        self.average_list.append(set_average)

        
        
        if self.set_count == 2:
            self.assess_label = tk.Label(self.control_frame, text=f"Assessing quality of printerhead...", font=("Ariel", 8, "bold"))
            self.assess_label.pack    
        else: 
            self.average1 = tk.Label(self.control_frame, text=f"Average Dark Pixel Count of Set {self.set_count}: {set_average}", font=("Ariel", 8, "bold"))
            self.instr_text3 = tk.Label(self.control_frame, text=f"Please open the image output from the printerhead to be assessed,", fg="red")
            self.instr_text4 = tk.Label(self.control_frame, text=f"and drag mouse from top left to bottom right of the image 5 times.", fg="red")
            self.instr_text1.destroy()
            self.instr_text2.destroy()
            self.average1.pack()
            self.instr_text3.pack()
            self.instr_text4.pack()
            
        self.reset()
        self.assess_quality()                                                                                             
        
    def assess_quality(self):
      if len(self.pixel_counts_list) >= 10:  #calculate standard deviation, and compare. 
        std_deviation = np.std(self.average_list)

        #displaying results 
        self.results1 = tk.Label(self.control_frame, text=f"The average pixel count in the first image is {self.average_list[0]}", fg="red", font=("Ariel", 8, "bold"))
        self.results2 = tk.Label(self.control_frame, text=f"and the average pixel count in the second image is {self.average_list[1]},", fg="red", font=("Ariel", 8, "bold"))
        self.results3 = tk.Label(self.control_frame, text=f"so the printerhead being assessed is {std_deviation} standard", fg="red", font=("Ariel", 8, "bold"))
        self.results4 = tk.Label(self.control_frame, text=f"deviations away from being a good printerhead.", fg="red", font=("Ariel", 8, "bold"))
        self.instr_text3.destroy()
        self.instr_text4.destroy()
        self.average1.destroy()
        self.results1.pack()
        self.results2.pack()
        self.results3.pack()
        self.results4.pack()
        
    #reseting the pixel count for new counting
    def reset(self):
        self.rectangles = []  #clear all rectangles
        self.box_count = 0
        self.count_text.config(text="Dark Pixels Count: 0")  #reset UI count display
        self.redraw()  #redraw the canvas

#calling the main function 
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBoxCounter(root)
    root.mainloop()


