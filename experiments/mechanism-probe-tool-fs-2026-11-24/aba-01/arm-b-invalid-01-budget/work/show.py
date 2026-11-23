import sys
g=[list(map(int,l.split())) for l in open('/work/gray.txt')]
y0,y1,x0,x1=map(int,sys.argv[1:5])
step=int(sys.argv[5]) if len(sys.argv)>5 else 1
for y in range(y0,y1+1,step):
    s=''
    for x in range(x0,x1+1):
        v=g[y][x]
        s+= '#' if v<100 else ('+' if v<180 else ('-' if v<230 else ' '))
    print(f'{y:4d} '+s)
