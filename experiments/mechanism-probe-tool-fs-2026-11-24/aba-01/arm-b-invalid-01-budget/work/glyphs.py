import sys
g=[list(map(int,l.split())) for l in open('/work/gray.txt')]
y0,y1=map(int,sys.argv[1:3])
segs=eval(sys.argv[3])
blocks=[]
for (x0,x1) in segs:
    lines=[]
    for y in range(y0,y1+1):
        s=''
        for x in range(x0,x1+1):
            v=g[y][x]
            s+= '#' if v<100 else ('+' if v<190 else ' ')
        lines.append(s)
    blocks.append(lines)
for i in range(len(blocks[0])):
    print('  '.join(b[i] for b in blocks))
