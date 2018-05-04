# _*_ encoding=utf-8 _*_
'''
^-^ docs_string
'''
import os
import csv
from PIL import ImageTk, Image
import tkinter as tk
from tkinter import filedialog
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

class Example(tk.Frame):
    #理想值
    ideal_24_lab = np.array(
        [[37.986, 13.55, 14.059],
        [65.711, 18.13, 17.81],
        [49.927, -4.88, -21.925],
        [43.139, -13.095, 21.905],
        [55.112, 8.844, -25.399],
        [70.719, -33.397, -0.199],
        [62.661, 36.067, 57.096],
        [40.02, 10.41, -45.964],
        [1.124, 48.239, 16.248],
        [30.325, 22.976, -21.587],
        [72.532, -23.709, 57.255],
        [71.941, 19.363, 67.857],
        [28.778, 14.179, -50.297],
        [55.261, -38.342, 31.37],
        [42.101, 53.378, 28.19],
        [81.733, 4.039, 79.819],
        [51.935, 49.986, -14.574],
        [51.038, -28.631, -28.638],
        [96.539, -0.425, 1.186],
        [81.257, -0.638, -0.335],
        [66.766, -0.734, -0.504],
        [50.867, -0.153, -0.27],
        [35.656, -0.421, -1.231],
        [20.461, -0.079, -0.973]])
    '''
    ideal_24_lab_cvt = np.zeros_like(ideal_24_lab, dtype=np.float)
    ideal_24_lab_cvt[:,0] = ideal_24_lab[:,0]*2.55
    ideal_24_lab_cvt[:,1:3] = ideal_24_lab[:,1:3]+128
    ideal_24_lab_cvt = np.asarray(ideal_24_lab_cvt, dtype=np.uint8)
    '''
    def __init__(self):
        super().__init__()
        self.pressed = False
        self.initUI()
        self.painted = False#打开文件，默认是没有绘制矩形的
        self.tileScale = 5#tile的比例
    
    def initUI(self):
        self.master.title('color checker')
        w = 900
        h = 600
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        self.master.geometry('%dx%d+%d+%d'%(w, h, (sw-w)//2, (sh-h)//2))

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=1)
        self.rowconfigure(7, weight=1)
        self.rowconfigure(8, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=0)
        self.columnconfigure(5, weight=0)
        self.columnconfigure(6, weight=0)
        #创建scrollbar并放在右侧和底侧
        vscrobar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrobar.grid(row=0, column=3, rowspan=8, sticky=tk.N+tk.S)
        hscrobar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        hscrobar.grid(row=8, column=0, columnspan=3, sticky=tk.W+tk.E)

        self.canvas_img = tk.Canvas(self, width=900, height=600, bg='gray', yscrollcommand=vscrobar.set, xscrollcommand=hscrobar.set, scrollregion=(0, 0, 900, 600))

        self.canvas_img.grid(row=0, column=0, rowspan=8, columnspan=3, sticky=tk.N+tk.S+tk.W+tk.E)
        #scrollbar响应
        vscrobar.config(command=self.canvas_img.yview)
        hscrobar.config(command=self.canvas_img.xview)
        self.canvas_img.bind('<MouseWheel>', self.onMouseWheel)
        self.canvas_img.bind('<ButtonPress-1>', self.startPt)
        self.canvas_img.bind('<ButtonRelease-1>', self.endPt)
        self.canvas_img.bind('<Motion>', self.mouseMove)

        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        fileMenu = tk.Menu(menubar)
        fileMenu.add_command(label='open', command=self.onOpen)
        fileMenu.add_command(label='exit', command=self.onExit)
        menubar.add_cascade(label='File', menu=fileMenu)

        top_up = tk.Button(self, text='up', command=self.topUp, width=8)
        top_up.grid(row=0, column=5, columnspan=1, sticky=tk.S)
        top_down = tk.Button(self, text='down', command=self.topDown, width=8)
        top_down.grid(row=1, column=5, columnspan=1, sticky=tk.N)
        left_left = tk.Button(self, text='left', command=self.leftLeft, width=8)
        left_left.grid(row=2, column=4, columnspan=1, sticky=tk.E+tk.S)
        left_right = tk.Button(self, text='right', command=self.leftRight, width=8)
        left_right.grid(row=3, column=4, columnspan=1, sticky=tk.E+tk.N)
        right_left = tk.Button(self, text='left', command=self.rightLeft, width=8)
        right_left.grid(row=2, column=6, columnspan=1, sticky=tk.W+tk.S)
        right_right = tk.Button(self, text='right', command=self.rightRight, width=8)
        right_right.grid(row=3, column=6, columnspan=1, sticky=tk.W+tk.N)
        bottom_up = tk.Button(self, text='up', command=self.bottomUp, width=8)
        bottom_up.grid(row=4, column=5, columnspan=1, sticky=tk.S)
        bottom_down = tk.Button(self, text='down', command=self.bottomDown, width=8)
        bottom_down.grid(row=5, column=5, columnspan=1, sticky=tk.N)

        tile_scale_up = tk.Button(self, text='scale up', width=8, command=self.tileScaleUp)
        tile_scale_up.grid(row=6, column=5, columnspan=1, sticky=tk.W+tk.E)
        tile_scale_down = tk.Button(self, text='scale down', width=8, command=self.tileScaleDown)
        tile_scale_down.grid(row=6, column=6, columnspan=1, sticky=tk.W+tk.E)

        ready_btn = tk.Button(self, text='OK', width=5, command=self.onOK)
        ready_btn.grid(row=6, column=4, columnspan=1, sticky=tk.E)

        self.pack(fill=tk.BOTH, expand=1)
        self.update()
        self.widthDiff = self.master.winfo_width() - self.canvas_img.winfo_width()
        self.heightDiff = self.master.winfo_height() - self.canvas_img.winfo_height()

    def onOK(self):
        if not self.painted:
            return
        tile_24_lab = np.zeros((24,3), dtype=np.float)#用于存储24个tile最后的平均LAB值
        uint_x = int((self.rectEnd[0]-self.rectStart[0])/6)
        uint_y = int((self.rectEnd[1]-self.rectStart[1])/4)
        os.chdir(self.imgPath)
        idx = self.new_title.rfind('.')
        if not os.path.exists(self.new_title[0:idx]):
            os.mkdir(self.new_title[0:idx])
        os.chdir(self.new_title[0:idx])
        csv_f = open(self.new_title[0:idx]+'.csv', 'w', newline='')
        csv_writer = csv.writer(csv_f)
        for y in range(4):
            for x in range(6):
                x1, y1, x2, y2 = self.rectStart[0]+x*uint_x+int(uint_x/self.tileScale), self.rectStart[1]+y*uint_y+int(uint_y/self.tileScale), \
                    self.rectStart[0]+(x+1)*uint_x-int(uint_x/self.tileScale), self.rectStart[1]+(y+1)*uint_y-int(uint_y/self.tileScale)
                #coord_24.append([x1*self.ratio, y1*self.ration, x2*self.ratio, y2*self.ratio])
                #print('ratio=',self.ratio, ' x1=', x1, ' y1=', y1, ' x2=', x2, ' y2=', y2)
                x1, y1, x2, y2 = int(x1/self.ratio), int(y1/self.ratio), int(x2/self.ratio), int(y2/self.ratio)#实际截取的坐标
                csv_writer.writerow([str(x1), str(y1), str(x2), str(y2)])
                img = self.img[y1:y2, x1:x2]#从图片截取
                img = cv.cvtColor(img, cv.COLOR_RGB2Lab)#转LAB
                img = np.mean(img, axis=0)#计算L/A/B平均值
                img = np.mean(img, axis=0)
                img[0], img[1], img[2] = img[0]/2.55, img[1]-128, img[2]-128 #转换l:0-100 a:-128-127 b:-128-127
                tile_24_lab[y*6+x]=img
        csv_f.close()
        lab_sub = tile_24_lab-Example.ideal_24_lab
        pow_lab_sub = lab_sub*lab_sub
        detal_E = np.sqrt(np.sum(pow_lab_sub, axis=1))
        detal_C = np.sqrt(np.sum(pow_lab_sub[:,1:3], axis=1))
        detal_E_max = np.max(detal_E[0:18])
        detal_E_mean = np.mean(detal_E[0:18])
        detal_C_max = np.max(detal_C[0:18])
        detal_C_mean = np.mean(detal_C[0:18])
        #wb 19-22 tile
        wb_detal_C = np.mean(detal_C[19:23])
        #saturation
        tile_24_lab_pow = tile_24_lab*tile_24_lab
        ideal_24_lab_pow = Example.ideal_24_lab*Example.ideal_24_lab
        tile_24_sat = np.mean(np.sqrt(tile_24_lab_pow[:,1]+tile_24_lab_pow[:,2]), axis=0)
        ideal_24_sat = np.mean(np.sqrt(ideal_24_lab_pow[:,1]+ideal_24_lab_pow[:,2]), axis=0)

        f = plt.figure(1, (7,7))
        img_lab = np.zeros((256,256,3), dtype=np.uint8)
        a, b = np.meshgrid(np.arange(256, dtype=np.uint8), np.arange(256, dtype=np.uint8))
        img_lab[:,:,0]=200
        img_lab[:,:,1]=a
        img_lab[:,:,2]=b
        img_rgb = cv.cvtColor(img_lab, cv.COLOR_Lab2RGB)
        ax1 = f.add_subplot(111)
        ax1.imshow(img_rgb)
        ax1.set_ylim(0,255)
        ax1.set_xlim(0,255)
        ax1.set_xlabel('$a$')
        ax1.set_ylabel('$b$')
        ax1.set_title('18 tile detal-c result')
        ax1.scatter(tile_24_lab[0:18,1]+128, tile_24_lab[0:18,2]+128,c=(1,0,0,0), marker='v', edgecolors='k', linewidths=1, label='actual')
        ax1.scatter(Example.ideal_24_lab[0:18,1]+128, Example.ideal_24_lab[0:18,2]+128,c=(1,0,0,0), marker='o', edgecolors='k', linewidths=1, label='ideal')
        for i in range(18):
            ax1.plot([tile_24_lab[i,1]+128, Example.ideal_24_lab[i,1]+128], [tile_24_lab[i,2]+128, Example.ideal_24_lab[i,2]+128],'k--', linewidth=1)
            ax1.text(tile_24_lab[i,1]+126, tile_24_lab[i,2]+131, str(i+1), fontsize=10)
        ax1.legend(loc='upper left')
        ax1.text(160, 248, 'detal E max=%.2f, mean=%.2f'%(detal_E_max, detal_E_mean), color='black', fontsize=8)
        ax1.text(160, 240, 'detal C max=%.2f, mean=%.2f'%(detal_C_max, detal_C_mean), color='black', fontsize=8)
        ax1.text(160, 232, 'saturation=%.2f'%(100*tile_24_sat/ideal_24_sat)+'%', color='black', fontsize=8)
        ax1.text(160, 224, 'WB detal C(zone 2-5)=%.2f'%wb_detal_C, color='black', fontsize=8)
        #plt.show()
        f.savefig(self.new_title[0:idx]+'.png')
        f.show()
        

        
    def tileScaleUp(self):
        if not self.painted:
            return
        self.tileScale += 1
        if self.tileScale>10:
            self.tileScale=10
        try:
            self.delRectangle()#删除24tile
        except AttributeError:
            print('error: check 24 tile and out rect') 
        self.paintRectangle()
    
    def tileScaleDown(self):
        if not self.painted:
            return
        self.tileScale -= 1
        if self.tileScale<2:
            self.tileScale=2
        try:
            self.delRectangle()#删除24tile
        except AttributeError:
            print('error: check 24 tile and out rect') 
        self.paintRectangle()

    def startPt(self, event):
        try: 
            self.origin_Img
        except AttributeError:
            return
        self.pressed = True
        w = event.widget
        x = int(w.canvasx(event.x))
        y = int(w.canvasy(event.y))
        self.rectStart = [x,y]

    def endPt(self, event):
        self.pressed = False


    def mouseMove(self, event):
        w = event.widget
        x = int(w.canvasx(event.x))
        y = int(w.canvasy(event.y))
        if self.pressed:
            self.rectEnd = [x, y]
            try:
                self.delRectangle()
            except AttributeError:
                pass

            self.paintRectangle()
            self.painted = True

    def topUp(self):#响应上-上按钮
        if not self.painted:#检查是否已经有过绘制24tile，如果没有绘制过，不做响应
            return
        try:
            self.delRectangle()#删除24tile
        except AttributeError:
            print('error: check 24 tile and out rect')
        self.rectStart[1] -= 2#一次升2个像素
        if self.rectStart[1]<0:
            self.rectStart[1] = 0
        self.paintRectangle()

    def topDown(self):
        if not self.painted:#检查是否已经有过绘制24tile，如果没有绘制过，不做响应
            return
        try:
            self.delRectangle()#删除24tile
        except AttributeError:
            print('error: check 24 tile and out rect')
        self.rectStart[1] += 2#一次降2个像素
        if self.rectStart[1]>self.rectEnd[1]:
            self.rectStart[1] = self.rectEnd[1]
        self.paintRectangle()        
    
    def leftLeft(self):
        if not self.painted:#检查是否已经有过绘制24tile，如果没有绘制过，不做响应
            return
        try:
            self.delRectangle()#删除24tile
        except AttributeError:
            print('error: check 24 tile and out rect')
        self.rectStart[0] -= 2#一次左移2个像素
        if self.rectStart[0]<0:
            self.rectStart[0] = 0
        self.paintRectangle()
    
    def leftRight(self):
        if not self.painted:#检查是否已经有过绘制24tile，如果没有绘制过，不做响应
            return
        try:
            self.delRectangle()#删除24tile
        except AttributeError:
            print('error: check 24 tile and out rect')
        self.rectStart[0] += 2#一次右移2个像素
        if self.rectStart[0]>self.rectEnd[0]:
            self.rectStart[0] = self.rectEnd[0]
        self.paintRectangle()

    def rightLeft(self):
        if not self.painted:#检查是否已经有过绘制24tile，如果没有绘制过，不做响应
            return
        try:
            self.delRectangle()#删除24tile
        except AttributeError:
            print('error: check 24 tile and out rect')
        self.rectEnd[0] -= 2#一次左移2个像素
        if self.rectEnd[0]<self.rectStart[0]:
            self.rectEnd[0] = self.rectStart[0]
        self.paintRectangle()

    def rightRight(self):
        if not self.painted:#检查是否已经有过绘制24tile，如果没有绘制过，不做响应
            return
        try:
            self.delRectangle()#删除24tile
        except AttributeError:
            print('error: check 24 tile and out rect')
        self.rectEnd[0] += 2#一次右移2个像素
        if self.rectEnd[0]>self.scale_img.size[0]:
            self.rectEnd[0] = self.scale_img.size[0]
        self.paintRectangle() 
    
    def bottomUp(self):
        if not self.painted:#检查是否已经有过绘制24tile，如果没有绘制过，不做响应
            return
        try:
            self.delRectangle()#删除24tile
        except AttributeError:
            print('error: check 24 tile and out rect')
        self.rectEnd[1] -= 2#一次升2个像素
        if self.rectEnd[1]<0:
            self.rectEnd[1] = 0
        self.paintRectangle()

    def bottomDown(self):
        if not self.painted:#检查是否已经有过绘制24tile，如果没有绘制过，不做响应
            return
        try:
            self.delRectangle()#删除24tile
        except AttributeError:
            print('error: check 24 tile and out rect')
        self.rectEnd[1] += 2#一次升2个像素
        if self.rectEnd[1]>self.scale_img.size[1]:
            self.rectEnd[1] = self.scale_img.size[1]
        self.paintRectangle()

    def onExit(self):
        self.quit()
        self.destroy()
        self.master.destroy()

    def onOpen(self):
        ftypes = [('image file', '*.jpg *.JPG *.png'), ('All files', '*')]
        dlg = tk.filedialog.Open(self, multiple=False, filetypes=ftypes)
        fn = dlg.show()
        if len(fn)>0:
            idx = fn.rfind('/')
            self.new_title = fn[idx+1:]
            self.imgPath = fn[0:idx]
            self.master.title(self.new_title)
            img = cv.imread(fn, cv.IMREAD_COLOR)
            self.img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            self.origin_Img = Image.fromarray(self.img)
            self.imgTk = ImageTk.PhotoImage(image=self.origin_Img)
            self.imgID = self.canvas_img.create_image(0, 0, anchor=tk.NW, image=self.imgTk)
            self.canvas_img.config(scrollregion=(0,0,self.origin_Img.size[0],self.origin_Img.size[1]))
            self.master.maxsize(self.origin_Img.size[0]+self.widthDiff+4, self.origin_Img.size[1]+self.heightDiff+4)
            self.ratio = 1.0

    def onMouseWheel(self, event):
        if not self.origin_Img:
            return
        if event.delta==-120:
            if self.ratio >= 0.5:
                self.ratio -= 0.25
            else:
                return
        if event.delta==120:
            if self.ratio >= 2.0:
                return
            else:
                self.ratio += 0.25
        self.canvas_img.delete(tk.ALL)
        self.painted = False
        w, h = self.origin_Img.size
        self.scale_img = self.origin_Img.resize((int(w*self.ratio), int(h*self.ratio)))
        self.imgTk = ImageTk.PhotoImage(image=self.scale_img)
        self.imgID = self.canvas_img.create_image(0,0, anchor=tk.NW, image=self.imgTk)
        self.canvas_img.config(scrollregion=(0,0,self.scale_img.size[0],self.scale_img.size[1]))
        self.master.maxsize(self.scale_img.size[0]+self.widthDiff+4, self.scale_img.size[1]+self.heightDiff+4)

    def delRectangle(self):
        self.canvas_img.delete(self.rectID)
        for y_id in self.in_rectID:
            for x_id in y_id: 
                self.canvas_img.delete(x_id)
            
    def paintRectangle(self):
        self.rectID = self.canvas_img.create_rectangle(self.rectStart[0],\
            self.rectStart[1], self.rectEnd[0], self.rectEnd[1], outline='green', width=3)
        if self.rectEnd[0]-self.rectStart[0]>120 and self.rectEnd[1]-self.rectStart[1]>40:
            try:
                self.in_rectID
            except AttributeError:
                self.in_rectID = []
                self.in_rectID.append([0,0,0,0,0,0])
                self.in_rectID.append([0,0,0,0,0,0])
                self.in_rectID.append([0,0,0,0,0,0])
                self.in_rectID.append([0,0,0,0,0,0])
            uint_x = int((self.rectEnd[0]-self.rectStart[0])/6)
            uint_y = int((self.rectEnd[1]-self.rectStart[1])/4)
            for y in range(4):
                for x in range(6):
                    self.in_rectID[y][x] = self.canvas_img.create_rectangle(self.rectStart[0]+x*uint_x+int(uint_x/self.tileScale), self.rectStart[1]+y*uint_y+int(uint_y/self.tileScale), \
                        self.rectStart[0]+uint_x*(x+1)-int(uint_x/self.tileScale), self.rectStart[1]+uint_y*(y+1)-int(uint_y/self.tileScale), outline='green', width=2)      
            
root = tk.Tk()
ex = Example()
root.mainloop()
