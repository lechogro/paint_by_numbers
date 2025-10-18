#from timeit import default_timer as timer
#time_get=timer()

#print("T0:", timer()-time_get)
#time_get=timer()


import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import re

cell_size=20 #pixels
bigcell_width=1 #pixels
bigcell_size=5 #cells
pic_size_x=0 #picture size (pixels)
pic_size_y=0 #picture size (pixels)

Arial_10pt=ImageFont.truetype("arial.ttf", size=13) #1 pt is 4/3 px
Arial_x=ImageFont.truetype("arialbd.ttf", size=10) #Arial bold

window = tk.Tk()
window.title("Paint by Numbers")

panel=ttk.Frame(master=window)
panel.grid(row=0, column=0, sticky="nswe")

#CONSTANTS
#nonremoved_blocks
NRB_beg=0
NRB_end=1
NRB_len=2
NRB_filled_blocks=3
#filled_blocks
FB_beg=0
FB_end=1
FB_len=2
FB_desc_num=3
#row/column
ROW=0
COL=1

def argwhere(vec):
    return np.nonzero(vec)[0].tolist()
def rc_text(rc):
    if rc==ROW:
        return " row "
    else:
        return " column "

#---------------------------------
# Load
#---------------------------------

def load():
    global nums, size, header_size
    global pic_size_x, pic_size_y
    filepath = filedialog.askopenfilename(
        filetypes=[
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
    )
    if not filepath:
        return
    
    nnums=[[],[]]
    
    with open(filepath, 'r') as file:
        text=file.read()
    try:
        sep_list=re.compile("[;.,\\[\\]\\{\\}]") #separators like these...
        text=sep_list.sub(" ",text) #... are replaced to space
        text=[x.strip() for x in text.split(sep="\n")]
        text=[x for x in text if len(x)>0]
        where_we_are=0 #0 - finding rows, 1 - cols, 2 - complete
        i=0
        while i<len(text) and where_we_are<2:
            if text[i][0].isdigit(): #if the first sign is a digit
                j=i
                while j<len(text) and text[j][0].isdigit():
                    if where_we_are==0:
                        nnums[ROW].append([int(x) for x in text[j].split(sep=" ") if len(x)>0]) #if len(x)>0 - serving cases like "2, 3"
                    elif where_we_are==1:
                        nnums[COL].append([int(x) for x in text[j].split(sep=" ") if len(x)>0])
                    j+=1
                i=j-1 #it will be incremented later: i+=1
                where_we_are+=1
            i+=1
        if len(nnums[ROW])==0 or len(nnums[COL])==0:
            raise ValueError("len[nnums]=0")
    except:
        messagebox.showwarning(title="Paint by Numbers", message="Invalid file format. See README for details.")
        return
    #File loaded successfully
    nums=[[],[]]
    nums[ROW]=list(nnums[ROW])
    nums[COL]=list(nnums[COL])

    #removing zeros
    def rem0(x):
        while True:
            try:
                x.remove(0)
            except ValueError:
                break #no zeros remain
        return x
    nums[ROW]=[rem0(x) for x in nums[ROW]]
    nums[COL]=[rem0(x) for x in nums[COL]]

    size=[len(nums[COL]) , len(nums[ROW])] #[ROW,COL]
    header_size=[max([len(x) for x in nums[ROW]]) , max([len(x) for x in nums[COL]])] #[ROW,COL]
    pic_size_x=(header_size[ROW]+size[ROW])*cell_size+2*bigcell_width+1
    pic_size_y=(header_size[COL]+size[COL])*cell_size+2*bigcell_width+1
    canvas.grid(row=0, column=0, sticky="nswe")
    canvas.config( scrollregion=(0,0,pic_size_x+2*cell_size-2*bigcell_width,pic_size_y+2*cell_size-2*bigcell_width) )

    window.title("Paint by Numbers - "+filepath)
    scr_res=( window.winfo_screenheight(), window.winfo_screenwidth() )
    window.geometry(str(pic_size_x+175)+"x"+str(max(pic_size_y,290)+59))
    #Set geometry to NEWGEOMETRY of the form =widthxheight+x+y.

    reload()
    
    #Checking sums
    if sum([sum(x) for x in nums[ROW]]) != sum([sum(x) for x in nums[COL]]):
        for x in disabled_uninit+disabled_nonbrute+disabled_brute:
            x["state"]="disabled"
        messagebox.showwarning(title="Paint by Numbers", message="Sums of numbers from rows and from columns are different. The image file is corrupted.")
    else:
        for x in disabled_uninit: #brute and nonbrute were properly set in "reload" function
            x["state"]="normal"
        
    #A lot of objects in canvas is a slow solution, especially when reshaping the window
    #header_row_cells=[[canvas.create_rectangle((j+1)*cell_size, (header_size[COL]+i+1)*cell_size, (j+2)*cell_size, (header_size[COL]+i+2)*cell_size, fill="white") for i in range(size[COL])] for j in range(header_size[ROW])]
    #header_col_cells=[[canvas.create_rectangle((header_size[ROW]+j+1)*cell_size, (i+1)*cell_size, (header_size[ROW]+j+2)*cell_size, (i+2)*cell_size, fill="white") for j in range(size[ROW])] for i in range(header_size[COL])]
    #cells=[[canvas.create_rectangle((header_size[ROW]+j+1)*cell_size, (header_size[COL]+i+1)*cell_size, (header_size[ROW]+j+2)*cell_size, (header_size[COL]+i+2)*cell_size, fill="#888") for i in range(size[COL])] for j in range(size[ROW])]
    #header_row_texts=[[canvas.create_text((header_size[ROW]-len(rows[i])+j+3/2)*cell_size,(header_size[COL]+i+3/2)*cell_size,  text=rows[i][j], fill="blue", anchor="center", font=("Arial", "10")) for j in range(len(rows[i]))] for i in range(size[COL])]
    #header_col_texts=[[canvas.create_text((header_size[ROW]+j+3/2)*cell_size,(header_size[COL]-len(cols[j])+i+3/2)*cell_size,  text=cols[j][i], fill="blue", anchor="center", font=("Arial", "10")) for i in range(len(cols[j]))] for j in range(size[ROW])]

    #for i in range(size[ROW]):
    #    for j in range(size[COL]):
    #        if (i+j) % 2 == 0:
    #            if i %2 == 0:
    #                canvas.itemconfigure(cells[i][j], fill="white")
    #            else:
    #                canvas.itemconfigure(cells[i][j], fill="#222")

load_btn=ttk.Button(master=panel, text="Load...", command=load)
load_btn.grid(row=0, column=0, padx=cell_size, pady=cell_size)

def select_solution(i): #select solution to show
    global sol_sel
    global desc_row_sel, desc_col_sel
    global compl_row_sel, compl_col_sel
    sol_sel=solutions[i].sol
    desc_row_sel=solutions[i].desc[ROW]
    desc_col_sel=solutions[i].desc[COL]
    compl_row_sel=solutions[i].compl[ROW]
    compl_col_sel=solutions[i].compl[COL]

def reload(nr=0):
    global solutions, brute_use, brute_started
    global image_main
    global bigcells_x, bigcells_y
    
    #The most important - list of solutions :)
    solutions=[Solution()]
    select_solution(nr)
    choose_spb.set("")
    choose_spb["to"]=1
    choose_lab["text"]=""
    brute_use.set(0)
    brute_started=False

    for x in disabled_brute:
        x["state"]="normal"
    for x in disabled_nonbrute:
        x["state"]="disabled"

    image_main=ImageCanvas()
    redraw_headers()

    bigcells_x=[0]+[(j+1)*bigcell_size for j in range(int(size[ROW]/bigcell_size))]
    if bigcells_x[-1]!=size[ROW]:
        bigcells_x.append(size[ROW])
    bigcells_x=[1]+[header_size[ROW]+j+1 for j in bigcells_x]
    bigcells_y=[0]+[(i+1)*bigcell_size for i in range(int(size[COL]/bigcell_size))]
    if bigcells_y[-1]!=size[COL]:
        bigcells_y.append(size[COL])
    bigcells_y=[1]+[header_size[COL]+i+1 for i in bigcells_y]
    update_output()
reload_btn=ttk.Button(master=panel, text="Reload", command=reload, state="disabled")
reload_btn.grid(row=1, column=0, padx=cell_size)

def add_bigcell_width(*args):
    return tuple((x+bigcell_width) for x in args)
def redraw_headers():
    global image_main
    [[image_main.draw.rectangle(add_bigcell_width( j*cell_size, (header_size[COL]+i)*cell_size, (j+1)*cell_size, (header_size[COL]+i+1)*cell_size ), fill="white", outline="black") for i in range(size[COL])] for j in range(header_size[ROW])]
    [[image_main.draw.rectangle(add_bigcell_width( (header_size[ROW]+j)*cell_size, i*cell_size, (header_size[ROW]+j+1)*cell_size, (i+1)*cell_size ), fill="white", outline="black") for j in range(size[ROW])] for i in range(header_size[COL])]
    [[image_main.draw.text(add_bigcell_width( (header_size[ROW]-len(nums[ROW][i])+j+1/2)*cell_size, (header_size[COL]+i+1/2)*cell_size ),  text=str(nums[ROW][i][j]), fill="blue", anchor="mm", font=Arial_10pt) for j in range(len(nums[ROW][i]))] for i in range(size[COL])]
    [[image_main.draw.text(add_bigcell_width( (header_size[ROW]+j+1/2)*cell_size, (header_size[COL]-len(nums[COL][j])+i+1/2)*cell_size ),  text=str(nums[COL][j][i]), fill="blue", anchor="mm", font=Arial_10pt) for i in range(len(nums[COL][j]))] for j in range(size[ROW])]
#---------------------------------
# Update output
#---------------------------------
def update_output(im_main_show=True):
    global image_main
    def get_color(arg):
        if arg==-1:
            return "white"
        elif arg==0:
            return "#888"
        else:
            return "#222"
    [[image_main.draw.rectangle(add_bigcell_width( (header_size[ROW]+j)*cell_size, (header_size[COL]+i)*cell_size, (header_size[ROW]+j+1)*cell_size, (header_size[COL]+i+1)*cell_size ), fill=get_color(sol_sel[i,j]), outline="black") for i in range(size[COL])] for j in range(size[ROW])]
    #big cells
    [[image_main.draw.rectangle(add_bigcell_width( (bigcells_x[j]-1)*cell_size, (bigcells_y[i]-1)*cell_size, (bigcells_x[j+1]-1)*cell_size, (bigcells_y[i+1]-1)*cell_size ), outline="black", width=bigcell_width+1) for i in range(len(bigcells_y)-1)] for j in range(len(bigcells_x)-1)]
    image_main.draw.rectangle(( 0, 0, (header_size[ROW]+size[ROW])*cell_size+2*bigcell_width, (header_size[COL]+size[COL])*cell_size+2*bigcell_width), outline="black", width=bigcell_width+1) #external edge
    #crossing out completed blocks
    [[image_main.draw.text(add_bigcell_width( (header_size[ROW]-len(nums[ROW][i])+j+1/2)*cell_size , (header_size[COL]+i+1/2)*cell_size ),  text="X", fill="red", anchor="mm", font=Arial_x) for j in range(len(nums[ROW][i])) if compl_row_sel[i][j]] for i in range(size[COL])]
    [[image_main.draw.text(add_bigcell_width( (header_size[ROW]+i+1/2)*cell_size , (header_size[COL]-len(nums[COL][i])+j+1/2)*cell_size ),  text="X", fill="orange", anchor="mm", font=Arial_x) for j in range(len(nums[COL][i])) if compl_col_sel[i][j]] for i in range(size[ROW])]

    if im_main_show:
        image_main.show()

def update_output_row():
    global image_row
    update_output(im_main_show=False)
    image_row=ImageCanvas(image_main)
    def uor_text(i,j):
        if desc_row_sel[i,j]>=0:
            return str(nums[ROW][i][desc_row_sel[i,j]])
        else:
            return ""
    [[image_row.draw.text(add_bigcell_width( (header_size[ROW]+j+1/2)*cell_size, (header_size[COL]+i+1/2)*cell_size), text=uor_text(i,j), fill="red", anchor="mm", font=Arial_10pt) for i in range(size[COL])] for j in range(size[ROW])]
    image_row.show()

def update_output_col():
    global image_col
    update_output(im_main_show=False)
    image_col=ImageCanvas(image_main)
    def uoc_text(i,j):
        if desc_col_sel[i,j]>=0:
            return str(nums[COL][j][desc_col_sel[i,j]])
        else:
            return ""
    [[image_col.draw.text(add_bigcell_width( (header_size[ROW]+j+1/2)*cell_size, (header_size[COL]+i+1/2)*cell_size), text=uoc_text(i,j), fill="orange", anchor="mm", font=Arial_10pt) for i in range(size[COL])] for j in range(size[ROW])]
    image_col.show()

#---------------------------------
# Panel - solving part
#---------------------------------

def step_cmd():
    global solutions
    solutions[0].step()
step_btn=ttk.Button(master=panel, text="Step >", command=step_cmd, state="disabled")
step_btn.grid(row=2, column=0, padx=cell_size, pady=cell_size)

def solve_cmd():
    global stage, solutions
    #stage=0 - standard
    #stage=1 - pre-brute-force - loop
    #stage=2 - pre-brute-force - end of loop
    #stage=3 - full brute-force
    #stage=10 - completed
    stage=0
    solutions[0].solve()
    if stage==1:
        global PI_fail_list
        PI_fail_list=[size[COL]*[0],size[ROW]*[0]] #[ROW,COL]
        while stage==1 and brute_use.get(): #brute_use.get, because it can be interrupted at any time
            solutions[0].pre_brute_solve()
        solutions[0].final_check()
    if stage==2 and brute_use.get():
        stage=3
        solutions[0].brute_solve()
    if len(solutions)==0:
        messagebox.showwarning(title="Paint by Numbers", message="No solutions")
        return
    select_solution(0) #previous could have been removed
    update_output()
    if brute_started:
        messagebox.showinfo(title="Paint by Numbers", message="Completed!")
solve_btn=ttk.Button(master=panel, text="Solve >>", command=solve_cmd, state="disabled")
solve_btn.grid(row=3, column=0, padx=cell_size)

def preview_cmd(cur_sol):
    global sol_sel
    global compl_row_sel, compl_col_sel
    sol_sel=cur_sol.sol
    compl_row_sel=cur_sol.compl[ROW]
    compl_col_sel=cur_sol.compl[COL]
    update_output()

preview=tk.IntVar()
preview_chb=ttk.Checkbutton(master=panel, text="Preview", variable=preview, state="disabled")
preview_chb.grid(row=4, column=0, padx=cell_size, pady=cell_size, sticky="w")

brute_use=tk.IntVar()        
brute_frm=ttk.Frame(master=panel)
brute_frm.grid(row=5, column=0, padx=cell_size, sticky="w")
brute_chb=ttk.Checkbutton(master=brute_frm, text="Use also", variable=brute_use, state="disabled")
brute_chb.grid(row=0, column=0, sticky="w")
brute_lab1=ttk.Label(master=brute_frm, text="brute-force", state="disabled")
brute_lab1.grid(row=1, column=0, sticky="w")
brute_lab2=ttk.Label(master=brute_frm, text="approach", state="disabled")
brute_lab2.grid(row=2, column=0, sticky="w")
#Use also brute-force approach

def choose_spb_cmd():
    try:
        sol_nr=int(choose_spb.get())
        sol_nr=max(1,min(sol_nr,choose_spb["to"]))
    except ValueError:
        sol_nr=1
    choose_spb.set(sol_nr)
    select_solution(sol_nr-1)
    update_output()
choose_frm=ttk.Frame(master=panel)
choose_frm.grid(row=6, column=0, padx=cell_size, pady=cell_size)
choose_spb=ttk.Spinbox(master=choose_frm, width=4, command=choose_spb_cmd, from_=1, to=1, state="disabled")
choose_spb.bind('<Return>', lambda x: choose_spb_cmd()) #Enter key
choose_spb.grid(row=0, column=0)
choose_lab=ttk.Label(master=choose_frm, text="", state="disabled")
choose_lab.grid(row=0, column=1)

#---------------------------------
# Canvas - init
#---------------------------------

canvas_scrollbar_frame=ttk.Frame(master=window)
canvas_scrollbar_frame.grid(row=0, column=1, sticky="nswe")
canvas_scrollbar_frame.rowconfigure(0, weight=1) #canvas itself
canvas_scrollbar_frame.columnconfigure(0, weight=1) #canvas itself
window.columnconfigure(1, weight=1)
window.rowconfigure(0, weight=1)
scrollbar_x = ttk.Scrollbar(master=canvas_scrollbar_frame, orient="horizontal")
scrollbar_x.grid(row=1,column=0, sticky="we")
scrollbar_y = ttk.Scrollbar(master=canvas_scrollbar_frame, orient="vertical")
scrollbar_y.grid(row=0,column=1, sticky="ns")
canvas = tk.Canvas(master=canvas_scrollbar_frame, border=0, xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
canv_im=canvas.create_image(cell_size-bigcell_width,cell_size-bigcell_width, anchor="nw")
#canvas.grid(row=0, column=0, sticky="nswe") #no canvas shown until initialzation
def canvas_click(e, button=0): #0 - left, 1 - right
    if brute_started:
        return
    x=e.x+canvas.canvasx(0)
    y=e.y+canvas.canvasy(0)
    j=int(x/cell_size)-header_size[ROW]-1
    i=int(y/cell_size)-header_size[COL]-1
    if i<0 or i>=size[COL] or j<0 or j>=size[ROW]:
        return

    global solutions, sol_sel
    if button:
        sol_sel[i,j]+=1
    else:
        sol_sel[i,j]-=1

    if sol_sel[i,j]==-2:
        sol_sel[i,j]=1
    elif sol_sel[i,j]==2:
        sol_sel[i,j]=-1
    solutions[0]=Solution()
    solutions[0].sol=np.array(sol_sel)
    select_solution(0)
    redraw_headers()
    update_output()

canvas.bind("<B1-ButtonRelease>", lambda e: canvas_click(e, button=0))
canvas.bind("<B3-ButtonRelease>", lambda e: canvas_click(e, button=1))
scrollbar_x.config(command=canvas.xview)
scrollbar_y.config(command=canvas.yview)

class ImageCanvas:
    def __init__(self, img=None):
        if img==None:
            self.image=Image.new(mode="RGB", size=(pic_size_x,pic_size_y), color="white") #RGBA works slow, even though it would be simplier :(
        else:
            self.image=img.image.copy()
        self.draw=ImageDraw.Draw(self.image)
    def show(self):
        self.imtk=ImageTk.PhotoImage(self.image)
        canvas.itemconfig(canv_im, image=self.imtk)

#---------------------------------
# Solving
#---------------------------------

def solv_error(sol_arg,text):
    sol_arg.error=True
    if stage==0:
        messagebox.showwarning(title="Paint by Numbers", icon="warning", message=text)


class Solution:
    
    def __init__(self, other=None):
        if other==None:
            self.sol=np.zeros((size[COL], size[ROW]), dtype=int) #solution: -1 - no, 0 - unknown, 1 - yes
            self.sol[[len(x)==0 for x in nums[ROW]],:]=-1 #empty rows
            self.sol[:,[len(x)==0 for x in nums[COL]]]=-1 #empty cols
            #Cell describing numbers
            self.desc=[[],[]]
            self.desc[ROW]=np.full((size[COL], size[ROW]), -1)
            self.desc[COL]=np.full((size[COL], size[ROW]), -1)
            #Completed numbers
            self.compl=[[],[]]
            self.compl[ROW]=[len(x)*[False] for x in nums[ROW]]
            self.compl[COL]=[len(x)*[False] for x in nums[COL]]
            self.rec_level=0 #recursive level
        else:
            self.sol=np.array(other.sol)
            #Cell describing numbers
            self.desc=[[],[]]
            self.desc[ROW]=np.array(other.desc[ROW])
            self.desc[COL]=np.array(other.desc[COL])
            #Completed numbers
            self.compl=[[],[]]
            self.compl[ROW]=[list(x) for x in other.compl[ROW]]
            self.compl[COL]=[list(x) for x in other.compl[COL]]
            self.rec_level=other.rec_level+1 #recursive level
        
        self.step_type=ROW
        self.step_counter=0
        self.change=False
        self.steps_no_change=0
        self.error=False

    #Updating solution is not direct, because it requires checking for errors
    def sol_update(self, rc, i, j=None, from_=None, to=None, mode=1):
        if from_==None:
            if to==None:
                return #wrong arguments
            else:
                from_=to
        elif to==None:
            to=from_

        if not ( (rc==ROW or rc==COL) and (mode==1 or mode==-1) and from_<=to and from_>=0 and to<size[rc]):
            return #wrong arguments

        if rc==ROW: #one row
            r0=i
            r1=i
            c0=from_
            c1=to
        else: #one col
            r0=from_
            r1=to
            c0=i
            c1=i
        global any0

        any0=False
        def iterf(x):
            global any0
            if mode==1 and x==-1: #for yes, but we already have no
                solv_error(self,"Error when filling area ("+str(r0+1)+","+str(c0+1)+")-("+str(r1+1)+","+str(c1+1)+") - some cells have already been removed.")
                return
            if mode==-1 and x==1: #for no, but we already have yes
                solv_error(self,"Error when removing area ("+str(r0+1)+","+str(c0+1)+")-("+str(r1+1)+","+str(c1+1)+") - some cells have already been filled.")
                return
            if x==0:
                any0=True
        [iterf(x) for x in self.sol[r0:(r1+1),c0:(c1+1)].ravel().tolist() if not self.error]
        if self.error:
            return
        if any0:
            self.change=True
            self.sol[r0:(r1+1),c0:(c1+1)]=mode

        if mode==1 and j!=None:
            any0=False
            def iterf2(x):
                global any0
                if x==-1:
                    any0=True
                elif x!=j:
                    solv_error(self,"Error when filling area ("+str(r0+1)+","+str(c0+1)+")-("+str(r1+1)+","+str(c1+1)+") - some cells have already been filled with other value.")
                    return
            [iterf2(x) for x in self.desc[rc][r0:(r1+1),c0:(c1+1)].ravel().tolist() if not self.error]
            if any0:
                self.change=True
                self.desc[rc][r0:(r1+1),c0:(c1+1)]=j
            #Whole block is found
            if to-from_+1==nums[rc][i][j]:
                self.sol_update(rc=rc, i=i, from_=from_-1, mode=-1)
                self.sol_update(rc=rc, i=i, to=to+1, mode=-1)
                if not self.compl[rc][i][j]:
                    self.change=True
                    self.compl[rc][i][j]=True

    def final_check(self):
        global solutions, brute_started, stage
        any0=False
        for rc in [ROW,COL]:
            for i in range(size[1-rc]): #ROW->COL, COL->ROW
                rc_sel=np.ravel( self.sol[i,:] if rc==ROW else self.sol[:,i] )
                blocks=[]
                j=0
                while j<size[rc]:
                    if rc_sel[j]==0:
                        any0=True
                        break
                    if rc_sel[j]==1:
                        k=j
                        while k<size[rc] and rc_sel[k]==1:
                            k+=1
                        blocks.append(k-j)
                        j=k
                    j+=1
                if any0:
                    break
                if blocks!=nums[rc][i]:
                    solv_error(self,"Final check failed.")
                    return
            if any0:
                break
        if any0:
            if stage==0 and brute_use.get():
                stage=1
            elif brute_started and brute_use.get():
                self.brute_solve()
            return
        #Success
        if brute_started:
            for x in disabled_nonbrute:
                x["state"]="normal"
            if choose_spb.get()=="":
                choose_spb.set(1)
            solutions.append(self)
            choose_spb["to"]=len(solutions)
            choose_lab["text"]="/"+str(len(solutions))
            window.update()
        else:
            update_output()
            stage=10
            messagebox.showinfo(title="Paint by Numbers", message="Completed!")

    def solve(self):
        global stage
        self.steps_no_change=0
        self.error=False #continue solving
        while self.steps_no_change<=1 and not self.error:
            if preview.get() and stage==0:
                self.step(show=True)
                window.update()
            else:
                self.step(show=False)
            if self.change:
                self.steps_no_change=0
            else:
                self.steps_no_change+=1
        if not self.error and stage!=1 and stage!=2: #in stages 1 and 2 we don't know if it's a tested bad solution
            self.final_check()
            
    def step(self, show=True):
        self.error=False
        self.step_counter+=1
        #print("Step:", self.step_counter)
        self.change=False
        for i in range(size[1-self.step_type]): #ROW->COL, COL->ROW
            if not all(self.compl[self.step_type][i]): #if there is something to do
                self.find_blocks(self.step_type,i)
            if self.error:
                break
        if show:
            if self.step_type==ROW:
                update_output_row()
            else: #self.step_type==COL
                update_output_col()
        self.step_type=1-self.step_type #ROW->COL, COL->ROW

    def find_blocks(self,rc,i):
        rc_sel=np.ravel( self.sol[i,:] if rc==ROW else self.sol[:,i] )
        rc_seld=np.ravel( self.desc[rc][i,:] if rc==ROW else self.desc[rc][:,i] )
        #If only no other cells can be filled... - testing sums
        if np.sum(rc_sel==1)==sum(nums[rc][i]):
            for j in range(size[rc]):
                if rc_sel[j]==0:
                    self.sol_update(rc=rc, i=i, from_=j, mode=-1)
                if self.error:
                    return
        #non-removed blocks
        nonremoved_blocks=[]
        j=0
        while j<size[rc]:
            if rc_sel[j]>=0:
                filled_blocks=[] #beg, end, len
                k=j
                while k<size[rc] and rc_sel[k]>=0:
                    #filled blocks
                    t=k
                    if rc_sel[t]==1:
                        desc_num=-1
                        while t<size[rc] and rc_sel[t]==1:
                            if desc_num==-1:
                                desc_num=rc_seld[t]
                            t+=1
                        filled_blocks.append((k,t-1,t-k,desc_num)) #beg, end, len, describing number
                        k=t-1 #it will be incremented later: k+=1
                    k+=1
                nonremoved_blocks.append((j,k-1,k-j,filled_blocks)) #beg, end, len, filled_blocks
                j=k
            j+=1

        #Assignment matrix: describing number --- non-removed block (False - cannot be assigned)
        #in which non-removed blocks the number can be
        if len(nonremoved_blocks)==1: #Trivial, but common case
            assignm=np.full((len(nums[rc][i]),1), True)
            assignv=np.full(len(nums[rc][i]), 0)
        else:
            #When we have the same amounts of describing numbers and filled blocks that cannot be connected...
            if len(nonremoved_blocks)==len(nums[rc][i]) and all([ len(x[NRB_filled_blocks])==1 for x in nonremoved_blocks ]):
                assignm=np.eye( len(nums[rc][i]), dtype=bool )
            else: #... or more complicated assignment matrix
                #By length
                assignm=np.array( [[y[NRB_len]>=x for y in nonremoved_blocks] for x in nums[rc][i]] )
                #Numbers already assigned to filled blocks
                for j in range(len(nonremoved_blocks)):
                    for z in nonremoved_blocks[j][NRB_filled_blocks]:
                        desc_num=z[FB_desc_num]
                        if desc_num>=0:
                            assignm[desc_num,:]=False
                            if self.compl[rc][i][desc_num]: #(*)
                                assignm[:,j]=False #(*)
                            assignm[desc_num,j]=True #Only one cell in this row can be True
                             #(*) If the number is completed, then nothing else can be in this non-removed block
                #Sums in first and last block
                j=len(nums[rc][i])-1
                while j>=0:
                    sel_nrs=np.array(nums[rc][i])[np.ravel(assignm[:,0])]
                    if sum(sel_nrs)+len(sel_nrs)-1>nonremoved_blocks[0][NRB_len]: #theese numbers cannot be together in this block
                        assignm[j,0]=False
                    j-=1
                j=0
                while j<len(nums[rc][i]):
                    sel_nrs=np.array(nums[rc][i])[np.ravel(assignm[:,-1])]
                    if sum(sel_nrs)+len(sel_nrs)-1>nonremoved_blocks[-1][NRB_len]: #theese numbers cannot be together in this block
                        assignm[j,-1]=False
                    j+=1
                #Order of decribing numbers - previous numbers cannot be in next blocks
                #and next numbers cannot be in previous blocks
                for j in range(len(assignm)): #iterate over row numbers
                    indices=np.nonzero(assignm[j])[0] #take this row
                    if len(indices)>0:
                        assignm[:j,indices[-1]+1:]=False
                        assignm[j+1:,:indices[0]]=False
                    else:
                        solv_error(self,"Number "+str(nums[rc][i][j])+" in"+rc_text(rc)+str(i+1)+" cannot be placed.")
                        return

            #Assignment vector: describing number --- one non-removed block
            # -1 - there are more than one
            # >0 - in which non-removed block the number must be
            assignv=np.full(len(nums[rc][i]), -1)
            for j in range(len(nums[rc][i])):
                argwherev=argwhere(assignm[j,:])
                if len(argwherev)==0 and not self.compl[rc][i][j]:
                    solv_error(self,"Number "+str(nums[rc][i][j])+" in"+rc_text(rc)+str(i+1)+" cannot be placed.")
                    return
                elif len(argwherev)==1:
                    assignv[j]=argwherev[0]

        for j in range(len(nonremoved_blocks)):
            self.fill_in_nonrem_blocks(rc,i,nonremoved_blocks[j],argwhere(assignv==j))
            self.new_filled_block(rc,i,nonremoved_blocks[j],argwhere(assignm[:,j]))
            if not np.any(assignm[:,j]): #nothing can be in this non-removed block
                self.sol_update(rc=rc, i=i, from_=nonremoved_blocks[j][NRB_beg], to=nonremoved_blocks[j][NRB_end], mode=-1)
        self.remove_in(rc,i)

    def fill_in_nonrem_blocks(self,rc,i,nonrem_block,desc_num):
        if len(desc_num)==0:
            return
        desc_len=[nums[rc][i][j] for j in desc_num]
        end=nonrem_block[NRB_beg]+desc_len[0]-1
        beg=nonrem_block[NRB_end]-sum(desc_len)-len(desc_len)+2
        self.sol_update(rc=rc, i=i, j=desc_num[0], from_=beg, to=end, mode=1)
        for j in range(1,len(desc_num)):
            end+=desc_len[j]+1
            beg+=desc_len[j-1]+1
            self.sol_update(rc=rc, i=i, j=desc_num[j], from_=beg, to=end, mode=1)

    def new_filled_block(self,rc,i,nonrem_block,desc_num):
        for x in nonrem_block[NRB_filled_blocks]:
            match=-1
            if x[FB_desc_num]==-1:
                matches1=[x[FB_len]<=nums[rc][i][j] for j in desc_num] #the length is proper
                rc_sel=np.ravel( self.sol[i,:] if rc==ROW else self.sol[:,i] )
                if x[FB_beg]>0 and rc_sel[x[FB_beg]-1]==0:
                    sep_0=1 #additional separator before
                else:
                    sep_0=0
                if x[FB_end]<size[rc]-1 and rc_sel[x[FB_end]+1]==0:
                    sep_1=1 #additional separator after
                else:
                    sep_1=0
                matches2=[np.sum(rc_sel[:x[FB_beg]]>=0)>=sum(nums[rc][i][:j])+sep_0 for j in desc_num] #there is enough place for blocks before
                matches3=[np.sum(rc_sel[x[FB_end]+1:]>=0)>=sum(nums[rc][i][(j+1):])+sep_1 for j in desc_num] #there is enough place for blocks after
                matches=[all(x) for x in zip(matches1,matches2,matches3)]
                #Zrobić inne kryteria
                if sum(matches)==1: #only one number matches
                    match=desc_num[argwhere(matches)[0]]
                    self.sol_update(rc=rc, i=i, j=match, from_=x[FB_beg], to=x[FB_end], mode=1)
                else:
                    if sum(matches)==0:
                        solv_error(self,"Matching error in"+rc_text(rc)+str(i+1)+".")
                        return
                    #this block cannot be extended
                    matching_lens=np.array(nums[rc][i])[np.array(desc_num)[matches]]
                    if np.all(matching_lens<=x[FB_len]):
                        self.sol_update(rc=rc, i=i, from_=x[FB_beg]-1, mode=-1)
                        self.sol_update(rc=rc, i=i, from_=x[FB_end]+1, mode=-1)
            else:
                match=x[FB_desc_num]
            if not self.compl[rc][i][match] and match>=0: #bouncing from the borders
                fake_b=max(nonrem_block[NRB_beg],x[FB_end]-nums[rc][i][match]+1)
                fake_e=min(nonrem_block[NRB_end],x[FB_beg]+nums[rc][i][match]-1)
                fake_block=(fake_b,fake_e,fake_e-fake_b+1,[])
                self.fill_in_nonrem_blocks(rc,i,fake_block,[match])
        #2 blocks, 2 describing numbers:
        if len(nonrem_block[NRB_filled_blocks])==2 and len(desc_num)==2:
            if not self.compl[rc][i][desc_num[0]] or not self.compl[rc][i][desc_num[1]]:
                #total length if these blocks can be connected
                tot_len=nonrem_block[NRB_filled_blocks][1][FB_end]-nonrem_block[NRB_filled_blocks][0][FB_beg]+1
                if tot_len>nums[rc][i][desc_num[0]] and tot_len>nums[rc][i][desc_num[1]]:
                    #these blocks cannot be connected
                    self.sol_update(rc=rc, i=i, j=desc_num[0], from_=nonrem_block[NRB_filled_blocks][0][FB_beg], to=nonrem_block[NRB_filled_blocks][0][FB_end], mode=1)
                    self.sol_update(rc=rc, i=i, j=desc_num[1], from_=nonrem_block[NRB_filled_blocks][1][FB_beg], to=nonrem_block[NRB_filled_blocks][1][FB_end], mode=1)


    def remove_in(self,rc,i):
        first_pos=len(nums[rc][i])*[-1]
        last_pos=len(nums[rc][i])*[-1]
        rc_seld=np.ravel( self.desc[rc][i,:] if rc==ROW else self.desc[rc][:,i] )
        j=0
        while j<size[rc]:
            if rc_seld[j]>=0 and first_pos[rc_seld[j]]==-1:
                first_pos[rc_seld[j]]=j
            j+=1
        j=size[rc]-1
        while j>=0:
            if rc_seld[j]>=0 and last_pos[rc_seld[j]]==-1:
                last_pos[rc_seld[j]]=j
            j-=1
        for j in range(len(first_pos)):
            if j==0 and first_pos[j]>=0: #before
                self.sol_update(rc=rc, i=i, from_=0, to=last_pos[j]-nums[rc][i][j], mode=-1)
            if j==len(first_pos)-1 and first_pos[j]>=0: #after
                self.sol_update(rc=rc, i=i, from_=first_pos[j]+nums[rc][i][j], to=size[rc]-1, mode=-1)
            elif first_pos[j]>=0 and first_pos[j+1]>=0: #between
                self.sol_update(rc=rc, i=i, from_=first_pos[j]+nums[rc][i][j], to=last_pos[j+1]-nums[rc][i][j+1], mode=-1)

#---------------------------------
# Brute-force solving
#---------------------------------

    def pre_brute_solve(self):  #no recursion
        global solutions, stage
        global PI_fail_list, something_changed

        stage=2 #to avoid looping
        if preview.get():
            update_output()
        window.update() #to enable interrupt and preview during solving

        PI_list=[]
        for rc in [ROW,COL]:
            for i in range(size[1-rc]): #ROW->COL, COL->ROW
                rc_sel=np.ravel( self.sol[i,:] if rc==ROW else self.sol[:,i] )
                PI_empty=np.sum(rc_sel==0)
                if PI_empty>0:
                    PI_maxlist=np.array(nums[rc][i])[np.array(self.compl[rc][i])==False]
                    if len(PI_maxlist)>0:
                        PI_new=int(np.max(PI_maxlist)-PI_empty)
                        PI_list.append((rc, i, PI_new-size[rc]*PI_fail_list[rc][i]))
        if len(PI_list)==0:
            return #probably completed
        PI_list=np.array(PI_list, dtype=[("rc",int),("i",int),("PI",int)])
        PI_list=np.flip(np.sort(PI_list, order="PI"))
        PI_min=int((PI_list[0]["PI"]+PI_list[-1]["PI"])/2)-1 #to avoid cases when PI is to small
        something_changed=False
        for x in PI_list:
            rc_sel=np.ravel( self.sol[x["i"],:] if x["rc"]==ROW else self.sol[:,x["i"]] )
            first_empty=-1
            case_pos=-1
            i=0
            while i<len(rc_sel):
                if first_empty<0 and rc_sel[i]==0:
                    first_empty=i
                if rc_sel[i]==0 and i+1<len(rc_sel) and rc_sel[i+1]==1:
                    case_pos=i
                    case_no=Solution(self) #duplicating
                    case_no.sol_update(rc=x["rc"], i=x["i"], from_=case_pos, mode=-1) #case: no
                    #print(x["rc"], x["i"], "CASE_NO-L")
                    case_no.solve()
                    if case_no.error:
                        self.sol_update(rc=x["rc"], i=x["i"], from_=case_pos, mode=1) #case: yes
                        if not self.pbs_success(x):
                            return
                        rc_sel=np.ravel( self.sol[x["i"],:] if x["rc"]==ROW else self.sol[:,x["i"]] )
                        #Maybe we should check what is on the left...
                        if i>0:
                            i-=2
                    else:
                        PI_fail_list[x["rc"]][x["i"]]+=1
                elif rc_sel[i]==1 and i+1<len(rc_sel) and rc_sel[i+1]==0:
                    case_pos=i+1
                    case_no=Solution(self) #duplicating
                    case_no.sol_update(rc=x["rc"], i=x["i"], from_=case_pos, mode=-1) #case: no
                    #print(x["rc"], x["i"], "CASE_NO-R")
                    case_no.solve()
                    if case_no.error:
                        self.sol_update(rc=x["rc"], i=x["i"], from_=case_pos, mode=1) #case: yes
                        if not self.pbs_success(x):
                            return
                        rc_sel=np.ravel( self.sol[x["i"],:] if x["rc"]==ROW else self.sol[:,x["i"]] )
                    else:
                        PI_fail_list[x["rc"]][x["i"]]+=1
                i+=1
            if not something_changed and case_pos<0: #Rather unlikely to succeed, so checked only if nothing happened
                case_yes=Solution(self) #duplicating
                case_yes.sol_update(rc=x["rc"], i=x["i"], from_=first_empty, mode=1) #case: yes
                #print(x["rc"], x["i"], "CASE_YES")
                case_yes.solve()
                if case_yes.error:
                    self.sol_update(rc=x["rc"], i=x["i"], from_=first_empty, mode=-1) #case: no
                    if not self.pbs_success(x):
                        return
                else:
                    PI_fail_list[x["rc"]][x["i"]]+=1
                #Maybe we should check what is on the other side...
                first_empty=len(rc_sel)-1
                while first_empty>=0:
                    if rc_sel[first_empty]==0:
                        break
                    first_empty-=1
                case_yes=Solution(self) #duplicating
                case_yes.sol_update(rc=x["rc"], i=x["i"], from_=first_empty, mode=1) #case: yes
                #print(x["rc"], x["i"], "CASE_YES")
                case_yes.solve()
                if case_yes.error:
                    self.sol_update(rc=x["rc"], i=x["i"], from_=first_empty, mode=-1) #case: no
                    if not self.pbs_success(x):
                        return
                else:
                    PI_fail_list[x["rc"]][x["i"]]+=1
            if something_changed and x["PI"]<PI_min:
                stage=1 #loop again
                return

        if something_changed:
            stage=1 #loop again
            return
        #else: exit with stage=2

    def pbs_success(self,x):
        global PI_fail_list, something_changed, stage
        #print(">>>>>>>>SUCCESS")
        PI_fail_list[x["rc"]][x["i"]]=0
        self.solve()
        if preview.get():
            update_output()
        window.update() #to enable interrupt and preview during solving
        if self.error: #both cases are wrong
            messagebox.showwarning(title="Paint by Numbers", message="No solutions")
            stage=10
            return False
        something_changed=True
        return True

    def brute_solve(self):
        global solutions, brute_started
        if not brute_started:
            solutions=[]
            brute_started=True
            for x in disabled_brute:
                x["state"]="disabled"
            #for x in disabled_nonbrute:  #only if success, so in final_check
            #    x["state"]="normal"
        
        PI= -max(size[ROW],size[COL]) #Performance Index ;)
        PI_rc=ROW
        PI_i=0
        for rc in [ROW,COL]:
            for i in range(size[1-rc]): #ROW->COL, COL->ROW
                rc_sel=np.ravel( self.sol[i,:] if rc==ROW else self.sol[:,i] )
                PI_empty=np.sum(rc_sel==0)
                if PI_empty>0:
                    PI_maxlist=np.array(nums[rc][i])[np.array(self.compl[rc][i])==False]
                    if len(PI_maxlist)>0:
                        PI_new=np.max(PI_maxlist)-PI_empty
                        #if rc==ROW:
                            #print(i, PI_new)
                        if PI_new>PI:
                            PI=PI_new
                            PI_rc=rc
                            PI_i=i

        if preview.get():
            preview_cmd(self)
        window.update() #to enable interrupt and preview during solving
        case_no=Solution(self) #duplicating
        rc_sel=np.ravel( self.sol[PI_i,:] if PI_rc==ROW else self.sol[:,PI_i] )
        first_empty=-1
        case_pos=-1
        for i in range(len(rc_sel)):
            if first_empty<0 and rc_sel[i]==0:
                first_empty=i
            if rc_sel[i]==0 and i+1<len(rc_sel) and rc_sel[i+1]==1:
                case_pos=i
                break
            elif rc_sel[i]==1 and i+1<len(rc_sel) and rc_sel[i+1]==0:
                first_empty=i+1
                case_pos=i+1
                break
        #first_empty=np.min(np.arange(size[PI_rc])[rc_sel==0])
        #print(PI_rc,PI_i,PI,first_empty)
        #if len(solutions)>=2000: #PROTECTION VALUE
        #    return
        if case_pos>=0:
            #print("BRUTE_SOLVE - NO - REC. LEVEL:", self.rec_level, rc_text(PI_rc), PI_i+1)
            case_no.sol_update(rc=PI_rc, i=PI_i, from_=case_pos, mode=-1) #case: no
            case_no.solve()
            #print("BRUTE_SOLVE - YES - REC. LEVEL:", self.rec_level, rc_text(PI_rc), PI_i+1)
            self.sol_update(rc=PI_rc, i=PI_i, from_=case_pos, mode=1) #case: yes
            self.solve()
        else:
            #print("BRUTE_SOLVE - YES - REC. LEVEL:", self.rec_level, rc_text(PI_rc), PI_i+1)
            self.sol_update(rc=PI_rc, i=PI_i, from_=first_empty, mode=1) #case: yes
            self.solve()
            #print("BRUTE_SOLVE - NO - REC. LEVEL:", self.rec_level, rc_text(PI_rc), PI_i+1)
            case_no.sol_update(rc=PI_rc, i=PI_i, from_=first_empty, mode=-1) #case: no
            case_no.solve()


#---------------------------------
# Window main loop
#---------------------------------

disabled_uninit=[reload_btn,brute_chb,brute_lab1,brute_lab2,preview_chb]
disabled_brute=[step_btn,solve_btn]
disabled_nonbrute=[choose_spb,choose_lab]
load()
window.mainloop()