import zlib, struct, sys

def read_png(path):
    data = open(path,'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    pos = 8
    idat = b''
    palette = None
    trns = None
    while pos < len(data):
        ln = struct.unpack('>I', data[pos:pos+4])[0]
        typ = data[pos+4:pos+8]
        chunk = data[pos+8:pos+8+ln]
        pos += 12+ln
        if typ == b'IHDR':
            w,h,bd,ct,comp,filt,inter = struct.unpack('>IIBBBBB', chunk)
        elif typ == b'PLTE':
            palette = [tuple(chunk[i:i+3]) for i in range(0,len(chunk),3)]
        elif typ == b'IDAT':
            idat += chunk
        elif typ == b'IEND':
            break
    assert inter == 0, 'interlaced not supported'
    raw = zlib.decompress(idat)
    channels = {0:1,2:3,3:1,4:2,6:4}[ct]
    if bd == 8:
        bpp = channels
        stride = w*channels
    elif bd == 16:
        bpp = channels*2
        stride = w*channels*2
    elif bd in (1,2,4):
        bpp = 1
        stride = (w*bd*channels + 7)//8
    rows = []
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p+stride]); p += stride
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i-bpp]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i-bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i-bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i-bpp] if i >= bpp else 0
                pp = a+b-c
                pa,pb,pc = abs(pp-a),abs(pp-b),abs(pp-c)
                pr = a if (pa<=pb and pa<=pc) else (b if pb<=pc else c)
                line[i] = (line[i] + pr) & 255
        rows.append(bytes(line))
        prev = line
    # expand to pixels (r,g,b) 0-255
    img = []
    for y in range(h):
        line = rows[y]
        row = []
        if bd == 8:
            for x in range(w):
                px = line[x*channels:(x+1)*channels]
                if ct == 0: row.append((px[0],px[0],px[0]))
                elif ct == 2: row.append(tuple(px))
                elif ct == 3: row.append(palette[px[0]])
                elif ct == 4: row.append((px[0],px[0],px[0]))
                elif ct == 6: row.append(tuple(px[:3]))
        elif bd == 16:
            for x in range(w):
                px = line[x*channels*2:(x+1)*channels*2]
                vals = [px[i*2] for i in range(channels)]
                if ct == 0: row.append((vals[0],vals[0],vals[0]))
                elif ct == 2: row.append(tuple(vals[:3]))
                elif ct == 4: row.append((vals[0],vals[0],vals[0]))
                elif ct == 6: row.append(tuple(vals[:3]))
        else:
            for x in range(w):
                bitpos = x*bd
                byte = line[bitpos//8]
                shift = 8 - bd - (bitpos % 8)
                v = (byte >> shift) & ((1<<bd)-1)
                if ct == 3: row.append(palette[v])
                else:
                    v = v * 255 // ((1<<bd)-1)
                    row.append((v,v,v))
        img.append(row)
    return w,h,img,ct,bd

if __name__ == '__main__':
    w,h,img,ct,bd = read_png(sys.argv[1])
    print('size', w, h, 'colortype', ct, 'bitdepth', bd)
    # unique colors count
    colors = {}
    for row in img:
        for p in row:
            colors[p] = colors.get(p,0)+1
    print('unique colors', len(colors))
    for c,n in sorted(colors.items(), key=lambda x:-x[1])[:10]:
        print(c,n)
