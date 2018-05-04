import cv2 as cv
import numpy as np
import csv
import sys
import matplotlib.pyplot as plt
import os
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

#读待测图片
img = cv.imread(sys.argv[1], cv.IMREAD_COLOR)

#读取csv文件配置的24个块的左上角和右下角坐标
f = open(sys.argv[2])
pos_cordin = list(csv.reader(f))
for i, item in enumerate(pos_cordin):
    pos_cordin[i] = list(map(int, item))
#准备文件夹
idx1 = sys.argv[1].rfind('/')
idx2 = sys.argv[1].rfind('.')
if idx1>0:
    os.chdir(sys.argv[1][0:idx])
    if not os.path.exists(sys.argv[1][idx1:idx2]):
        os.mkdir(sys.argv[1][idx1:idx2])
    os.chdir(sys.argv[1][idx1:idx2])
if idx1<0:
    if not os.path.exists(sys.argv[1][0:idx2]):
        os.mkdir(sys.argv[1][0:idx2])
    os.chdir(sys.argv[1][0:idx2])
#空list用于保存24个块最终的l,a,b的平均值
tile_24_lab = np.zeros((24, 3), dtype=np.float)
for i in range(24):
    a = img[pos_cordin[i][1]:pos_cordin[i][3], pos_cordin[i][0]:pos_cordin[i][2]]
    lab_a = cv.cvtColor(a, cv.COLOR_BGR2Lab)
    lab_a = np.mean(lab_a, axis=0)
    lab_a = np.mean(lab_a, axis=0)
    lab_a[0], lab_a[1], lab_a[2] = lab_a[0]/2.55, lab_a[1]-128, lab_a[2]-128
    tile_24_lab[i] = lab_a
#print(tile_24_lab)
lab_sub = tile_24_lab-ideal_24_lab
power_lab_sub = lab_sub*lab_sub
detal_E = np.sqrt(np.sum(power_lab_sub, axis=1))
detal_C = np.sqrt(np.sum(power_lab_sub[:, 1:3], axis=1))
#print('detal E max =%.4f, detal E mean=%.4f'%(detal_E.max(), detal_E.mean()))
#print('detal C max =%.4f, detal C mean=%.4f'%(detal_C.max(), detal_C.mean()))
detal_E_max = np.max(detal_E[0:18])
detal_E_mean = np.mean(detal_E[0:18])
detal_C_max = np.max(detal_C[0:18])
detal_C_mean = np.mean(detal_C[0:18])

#wb 19-22 tile
wb_detal_C = np.mean(detal_C[19:23])
#saturation
tile_24_lab_pow = tile_24_lab*tile_24_lab
ideal_24_lab_pow = ideal_24_lab*ideal_24_lab
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
ax1.scatter(ideal_24_lab[0:18,1]+128, ideal_24_lab[0:18,2]+128,c=(1,0,0,0), marker='o', edgecolors='k', linewidths=1, label='ideal')
for i in range(18):
    ax1.plot([tile_24_lab[i,1]+128, ideal_24_lab[i,1]+128], [tile_24_lab[i,2]+128, ideal_24_lab[i,2]+128],'k--', linewidth=1)
    ax1.text(tile_24_lab[i,1]+126, tile_24_lab[i,2]+131, str(i+1), fontsize=10)
ax1.legend(loc='upper left')
ax1.text(160, 248, 'detal E max=%.2f, mean=%.2f'%(detal_E_max, detal_E_mean), color='black', fontsize=8)
ax1.text(160, 240, 'detal C max=%.2f, mean=%.2f'%(detal_C_max, detal_C_mean), color='black', fontsize=8)
ax1.text(160, 232, 'saturation=%.2f'%(100*tile_24_sat/ideal_24_sat)+'%', color='black', fontsize=8)
ax1.text(160, 224, 'WB detal C(zone 2-5)=%.2f'%wb_detal_C, color='black', fontsize=8)
#plt.show()
if idx1>0:
    f.savefig(sys.argv[1][idx1:idx2]+'.png')
else:
    f.savefig(sys.argv[1][0:idx2]+'png')    
plt.show()