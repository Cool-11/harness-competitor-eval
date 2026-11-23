import sys
sys.path.insert(0,'/work/tmp')
from pngread import read_png
w,h,img,ct,bd = read_png('/work/inventory.png')
def dark(p): return sum(p)/3 < 128
x0,x1,y0,y1,sx,sy = map(int, sys.argv[1:7])
for y in range(y0,y1+1):
    line=''
    for x in range(x0,x1+1):
        line += ('#' if dark(img[y][x]) else '.')*sx
    print('\n'.join([line]*sy))
