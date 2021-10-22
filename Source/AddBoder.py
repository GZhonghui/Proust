from PIL import Image, ImageFilter, ImageDraw, ImageFont
import sys, string, os

backgroundColour = (255, 255, 255, 0)
shadowColour = (32, 32, 32, 255)

mainSize = 0.9

def makeShadow(image, iterations, border, offset):
  fullWidth  = image.size[0] + abs(offset[0]) + 2*border
  fullHeight = image.size[1] + abs(offset[1]) + 2*border
  
  shadow = Image.new(image.mode, (fullWidth, fullHeight), backgroundColour)
  
  
  shadowLeft = border + max(offset[0], 0) #if <0, push the rest of the image right
  shadowTop  = border + max(offset[1], 0) #if <0, push the rest of the image down
  #Paste in the constant colour
  shadow.paste(shadowColour, 
        [shadowLeft, shadowTop,
         shadowLeft + image.size[0],
         shadowTop  + image.size[1] ])
  
  # Apply the BLUR filter repeatedly
  for i in range(iterations):
    shadow = shadow.filter(ImageFilter.BLUR)

  # Paste the original image on top of the shadow 
  imgLeft = border - min(offset[0], 0) #if the shadow offset was <0, push right
  imgTop  = border - min(offset[1], 0) #if the shadow offset was <0, push down
  shadow.paste(image, (imgLeft, imgTop))

  return shadow

def circleCorner(image, R):
  R = R * 4
  image = image.resize((image.size[0]*4, image.size[1]*4), Image.ANTIALIAS)
  circle = Image.new('L', (R * 2, R * 2), 0)
  draw = ImageDraw.Draw(circle)
  draw.ellipse((0, 0, R * 2, R * 2), fill=255)
  image = image.convert("RGBA")
  w, h = image.size
  alpha = Image.new('L', image.size, 255)
  alpha.paste(circle.crop((0, 0, R, R)), (0, 0))
  alpha.paste(circle.crop((R, 0, R * 2, R)), (w - R, 0))
  alpha.paste(circle.crop((R, R, R * 2, R * 2)), (w - R, h - R))
  alpha.paste(circle.crop((0, R, R, R * 2)), (0, h - R))
  image.putalpha(alpha)
  return image.resize((image.size[0]//4, image.size[1]//4), Image.ANTIALIAS)

def blurBackground(image):
  return image.filter(ImageFilter.GaussianBlur(8))

def addText(image, Text):
  # 背景尺寸
  bg_size = (750, 1334)
  # 生成一张尺寸为 750x1334 背景色为黄色的图片
  bg = Image.new('RGB', bg_size, color=(255,255,0))

  # 字体大小
  font_size = 72
  # 文字内容
  text = '《肖申克的救赎》'

  # 字体文件路径
  font_path = os.path.join('.', '云书法家杨永志瘦金正楷简.ttf')
  # 设置字体
  font = ImageFont.truetype(font_path, font_size)
  # 计算使用该字体占据的空间
  # 返回一个 tuple (width, height)
  # 分别代表这行字占据的宽和高
  text_width = font.getsize(text)
  draw = ImageDraw.Draw(bg)

  # 计算字体位置
  text_coordinate = int((bg_size[0]-text_width[0])/2), int((bg_size[1]-text_width[1])/2)+300
  # 写字
  draw.text(text_coordinate, text,(0,0,0), font=font)

  bg.show()
  
def main():
  image = Image.open(sys.argv[1])
  image = image.convert("RGBA")

  cir = circleCorner(image, 12)
  targetSize = (int(image.size[0]*1.4), int(image.size[1]*1.4))
  #bg = blurBackground(image).resize(targetSize, Image.ANTIALIAS)
  bg = image.resize(targetSize, Image.ANTIALIAS)
  bg.paste(cir, (10,10))
  bg.show()

if __name__ == "__main__":
  main()