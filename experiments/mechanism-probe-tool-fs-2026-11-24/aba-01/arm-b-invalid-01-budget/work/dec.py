import struct,zlib
d=open('/work/inventory.png','rb').read()
i=8; idat=b''
while i<len(d):
    ln=struct.unpack('>I',d[i:i+4])[0]; typ=d[i+4:i+8]
    if typ==b'IHDR':
        w,h,bd,ct,cm,fl,il=struct.unpack('>IIBBBBB',d[i+8:i+21])
    elif typ==b'IDAT': idat+=d[i+8:i+8+ln]
    i+=12+ln
print(w,h,bd,ct)
bpp=3
raw=zlib.decompress(idat)
stride=w*bpp
rows=[]; prev=bytearray(stride); p=0
for y in range(h):
    f=raw[p]; p+=1
    line=bytearray(raw[p:p+stride]); p+=stride
    if f==1:
        for x in range(bpp,stride): line[x]=(line[x]+line[x-bpp])&255
    elif f==2:
        for x in range(stride): line[x]=(line[x]+prev[x])&255
    elif f==3:
        for x in range(stride):
            a=line[x-bpp] if x>=bpp else 0
            line[x]=(line[x]+((a+prev[x])>>1))&255
    elif f==4:
        for x in range(stride):
            a=line[x-bpp] if x>=bpp else 0
            b=prev[x]; c=prev[x-bpp] if x>=bpp else 0
            pa=abs(b-c); pb=abs(a-c); pc=abs(a+b-2*c)
            pr=a if (pa<=pb and pa<=pc) else (b if pb<=pc else c)
            line[x]=(line[x]+pr)&255
    rows.append(line); prev=line
# grayscale
g=[[ (rows[y][x*3]*299+rows[y][x*3+1]*587+rows[y][x*3+2]*114)//1000 for x in range(w)] for y in range(h)]
import json
open('/work/gray.txt','w').write('\n'.join(' '.join(map(str,r)) for r in g))
# ascii downsample
chars='@%#*+=-:. '
for y in range(0,h,6):
    s=''
    for x in range(0,w,4):
        vals=[g[yy][xx] for yy in range(y,min(y+6,h),2) for xx in range(x,min(x+4,w),2)]
        v=sum(vals)//len(vals)
        s+=chars[min(9,v*10//256)]
    print(s)
