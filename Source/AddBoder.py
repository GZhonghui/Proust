from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
import sys, string, os

shadowBackgroundColour = (255, 255, 255, 0)
shadowColour = (32, 32, 32, 255)
shadowOffset = (36, 36)
shadowBorder = 64
shadowIterations = 32

mainSize = 0.94

finalSize = (800, 1200)

fontRatio = 0.24
Ratio = (3 - fontRatio) / 2

textHeight = int(finalSize[1] * fontRatio / 3)
finalSizeWithoutText = (finalSize[0], finalSize[1] - textHeight)

def expandImage(width, height, ratio):
  size_1 = (width, int(width * ratio))
  size_2 = (int(height / ratio), height)
  return [max(size_1[0],size_2[0]), max(size_1[1],size_2[1])]

def makeShadow(image):
  fullWidth  = image.size[0] + abs(shadowOffset[0]) + 2*shadowBorder
  fullHeight = image.size[1] + abs(shadowOffset[1]) + 2*shadowBorder
  shadow = Image.new(image.mode, (fullWidth, fullHeight), shadowBackgroundColour)
  shadowL = shadowBorder + max(shadowOffset[0], 0)
  shadowT = shadowBorder + max(shadowOffset[1], 0)
  shadow.paste(shadowColour,[shadowL, shadowT, shadowL+image.size[0], shadowT+image.size[1]])
  for i in range(shadowIterations):
    shadow = shadow.filter(ImageFilter.BLUR)
  imgLeft = shadowBorder - min(shadowOffset[0], 0)
  imgTop  = shadowBorder - min(shadowOffset[1], 0)
  shadowData = shadow.load()
  for i in range(fullWidth):
    for j in range(fullHeight):
      pixel = list(shadowData[i,j])
      pixel[3] = 255 - pixel[0]
      shadowData[i,j] = tuple(pixel)
  shadow.paste(image, (imgLeft, imgTop), image)
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
  return image.filter(ImageFilter.GaussianBlur(12))

def addText(image, Text):
  font_size = 64
  font_path = os.path.join('.', 'Assets', '云书法家杨永志瘦金正楷简.ttf')
  font = ImageFont.truetype(font_path, font_size)
  text_size = font.getsize(Text)
  draw = ImageDraw.Draw(image)
  text_coordinate = (image.size[0]-text_size[0])//2, image.size[1]-text_size[1]-16
  draw.text(text_coordinate, Text,(0,0,0), font=font)
  
def main():
  image = Image.open(sys.argv[1])
  circle = circleCorner(image, 16)
  #shadow = makeShadow(circle)
  shadow = circle
  backgroundSize = expandImage(image.size[0],image.size[1], Ratio)
  backgroundSize[0] = (int(backgroundSize[0] / mainSize) - image.size[0])//2*2 + image.size[0]
  backgroundSize[1] = (int(backgroundSize[1] / mainSize) - image.size[1])//2*2 + image.size[1]
  pasteLocation = ((backgroundSize[0]-image.size[0])//2-shadowBorder,(backgroundSize[1]-image.size[1])//2-shadowBorder)
  imageTargetSize = expandImage(backgroundSize[0], backgroundSize[1], image.size[1]/image.size[0])
  backImage = image.resize(imageTargetSize, Image.ANTIALIAS)
  enhancer = ImageEnhance.Brightness(backImage)
  backImage = enhancer.enhance(1.5)
  background = Image.new('RGB', backgroundSize, color=(255,255,255))
  background.paste(backImage,(0,0))
  background = blurBackground(background)
  background.paste(shadow, pasteLocation, shadow)
  background = background.resize(finalSizeWithoutText, Image.ANTIALIAS)
  backgroundText = Image.new('RGB', finalSize, color=(255,255,255))
  backgroundText.paste(background,(0,0))
  addText(backgroundText,sys.argv[2])
  backgroundText.show()
  backgroundText.save('02.png')

if __name__ == "__main__":
  main()