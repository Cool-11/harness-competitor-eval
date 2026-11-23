import sys
sys.path.insert(0,'/work/tmp')
from pngread import read_png
w,h,img,ct,bd = read_png('/work/inventory.png')
ys=[(129,150),(187,203),(227,243),(267,283),(307,323),(347,363),(387,403),(427,443),(467,483),(507,523),(547,563),(587,603),(627,643)]
for (y0,y1) in ys:
    for (x0,x1) in [(20,110),(215,420),(480,770)]:
        mn=255; cnt=0
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                v=sum(img[y][x])//3
                if v<mn: mn=v
                if v<200: cnt+=1
        print(f'y{y0} x{x0}-{x1}: min={mn} cnt<200={cnt}', end='; ')
    print()
