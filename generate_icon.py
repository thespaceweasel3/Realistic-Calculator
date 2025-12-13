from PIL import Image, ImageDraw

# Create a 64x64 icon resembling the runtime PhotoImage
size = 64
bg = '#2b2b2b'
body = '#111111'
chrome = '#444444'
key = '#d9d9d9'
sym = '#111111'

img = Image.new('RGBA', (size, size), bg)
d = ImageDraw.Draw(img)

# body rounded rectangle
bx0, by0, bx1, by1 = 8, 8, size-9, size-9
# simple rounded rect by drawing rectangle (good enough at small size)
d.rectangle([bx0, by0, bx1, by1], fill=body)

# top chrome strip
for y in range(by0, by0+8):
    d.line([(bx0+2, y), (bx1-1, y)], fill=chrome)

# keys
keys = [ (bx0+8, by0+18), (bx0+28, by0+18), (bx0+8, by0+34), (bx0+28, by0+34) ]
ksize = 10
for (kx, ky) in keys:
    d.rectangle([kx, ky, kx+ksize-1, ky+ksize-1], fill=key)

# plus sign top-left
px, py = keys[0]
cx = px + ksize//2
cy = py + ksize//2
for dx in range(-2, 3):
    d.point((cx+dx, cy), fill=sym)
    d.point((cx, cy+dx), fill=sym)

# minus sign top-right
px, py = keys[1]
cx = px + ksize//2
cy = py + ksize//2
for dx in range(-2, 3):
    d.point((cx+dx, cy), fill=sym)

# multiply bottom-left (X)
px, py = keys[2]
for i in range(ksize):
    d.point((px+i, py+i), fill=sym)
    d.point((px+i, py+ksize-1-i), fill=sym)

# divide bottom-right: dot, line, dot
px, py = keys[3]
cx = px + ksize//2
cy = py + ksize//2
d.point((cx, cy-3), fill=sym)
for dx in range(-2, 3):
    d.point((cx+dx, cy), fill=sym)
d.point((cx, cy+3), fill=sym)

# Save as .ico (Pillow will create multiple sizes inside)
img.save('calculator.ico', format='ICO')
print('Wrote calculator.ico')
