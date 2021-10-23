from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
import sys, string, os

mainSize = 0.94

finalSize = (800, 1200)

fontRatio = 0.24
ratioWidth = 2.0
ratioHeight = 3.0
Ratio = (ratioHeight - fontRatio) / ratioWidth

mainOffsetY = 0.01

textBelow = 20
textHeight = int(finalSize[1] * fontRatio / ratioHeight)
finalSizeWithoutText = (finalSize[0], finalSize[1] - textHeight)

fontSize = 64
fontPath = os.path.join('.', 'Assets', 'FZBWKSJW.TTF') # 方正北魏楷书简体

shadowBackgroundColour = (255, 255, 255)
shadowColour = (32, 32, 32)
shadowOffset = (24, 24)
shadowBorder = 32
shadowIterations = 48

blurRadious = 13

circleCornerSize = 16

def expandImage(width, height, ratio):
  size_1 = (width, int(width * ratio))
  size_2 = (int(height / ratio), height)
  return [max(size_1[0],size_2[0]), max(size_1[1],size_2[1])]

def cropCenter(image, newSize):
  W,H,newW,newH = *image.size,*newSize
  L = (W - newW) // 2
  T = (H - newH) // 2
  R = L + newW
  B = T + newH
  return image.crop((L,T,R,B))

def makeSideShadow(image):
  fullWidth  = image.size[0] + abs(shadowOffset[0]) + 2*shadowBorder
  fullHeight = image.size[1] + abs(shadowOffset[1]) + 2*shadowBorder
  shadow = Image.new('RGB', (fullWidth, fullHeight), shadowBackgroundColour)
  shadowL = shadowBorder + max(shadowOffset[0], 0)
  shadowT = shadowBorder + max(shadowOffset[1], 0)
  shadow.paste(shadowColour,[shadowL, shadowT, shadowL+image.size[0], shadowT+image.size[1]])
  for i in range(shadowIterations):
    shadow = shadow.filter(ImageFilter.BLUR)
  alpha = Image.new('L', (fullWidth, fullHeight), 255)
  alphaData,SD = alpha.load(),shadow.load()
  for i in range(fullWidth):
    for j in range(fullHeight):
      alphaData[i,j] = 255 - (SD[i,j][0]+SD[i,j][1]+SD[i,j][2])//3
  shadow = shadow.convert("RGBA")
  shadow.putalpha(alpha)
  imgLeft = shadowBorder - min(shadowOffset[0], 0)
  imgTop  = shadowBorder - min(shadowOffset[1], 0)
  shadow.paste(image, (imgLeft, imgTop), image)
  return shadow

def makeShadow(image):
  fullWidth  = image.size[0] + shadowOffset[0]*2 + 2*shadowBorder
  fullHeight = image.size[1] + shadowOffset[1]*2 + 2*shadowBorder
  shadow = Image.new('RGB', (fullWidth, fullHeight), shadowBackgroundColour)
  shadowL,shadowT = shadowBorder,shadowBorder
  shadowR = shadowBorder + shadowOffset[0]*2 + image.size[0]
  shadowB = shadowBorder + shadowOffset[1]*2 + image.size[1]
  shadow.paste(shadowColour,[shadowL, shadowT, shadowR, shadowB])
  for i in range(shadowIterations):
    shadow = shadow.filter(ImageFilter.BLUR)
  alpha = Image.new('L', (fullWidth, fullHeight), 255)
  alphaData,SD = alpha.load(),shadow.load()
  for i in range(fullWidth):
    for j in range(fullHeight):
      alphaData[i,j] = 255 - (SD[i,j][0]+SD[i,j][1]+SD[i,j][2])//3
  shadow = shadow.convert("RGBA")
  shadow.putalpha(alpha)
  imgLeft = shadowBorder + shadowOffset[0]
  imgTop  = shadowBorder + shadowOffset[1]
  shadow.paste(image, (imgLeft, imgTop), image)
  return shadow

def circleCorner(image, R):
  R,image = R*4,image.resize((image.size[0]*4, image.size[1]*4), Image.ANTIALIAS)
  Circle = Image.new('L', (R * 2, R * 2), 0)
  Draw = ImageDraw.Draw(Circle)
  Draw.ellipse((0, 0, R * 2, R * 2), fill=255)
  image = image.convert("RGBA")
  alpha = Image.new('L', image.size, 255)
  alpha.paste(Circle.crop((0, 0, R, R)), (0, 0))
  alpha.paste(Circle.crop((R, 0, R * 2, R)), (image.size[0] - R, 0))
  alpha.paste(Circle.crop((R, R, R * 2, R * 2)), (image.size[0] - R, image.size[1] - R))
  alpha.paste(Circle.crop((0, R, R, R * 2)), (0, image.size[1] - R))
  image.putalpha(alpha)
  return image.resize((image.size[0]//4, image.size[1]//4), Image.ANTIALIAS)

def blurBackground(image):
  return image.filter(ImageFilter.GaussianBlur(blurRadious))

def addText(image, Text):
  Font = ImageFont.truetype(fontPath, fontSize)
  textSize = Font.getsize(Text)
  Draw = ImageDraw.Draw(image)
  textCoordinate = (image.size[0]-textSize[0])//2, image.size[1]-textSize[1]-textBelow
  Draw.text(textCoordinate, Text, (255,255,255), font=Font)
  
def main():
  image = Image.open(sys.argv[1])
  Circle = circleCorner(image, circleCornerSize)
  Shadow = makeShadow(Circle)
  backgroundSize = expandImage(image.size[0],image.size[1], Ratio)
  backgroundSize[0] = (int(backgroundSize[0] / mainSize) - image.size[0])//2*2 + image.size[0]
  backgroundSize[1] = (int(backgroundSize[1] / mainSize) - image.size[1])//2*2 + image.size[1]
  pasteLocationX = (backgroundSize[0]-image.size[0])//2-shadowBorder-shadowOffset[0]
  pasteLocationY = (backgroundSize[1]-image.size[1])//2-shadowBorder-shadowOffset[1]
  pasteLocationY = pasteLocationY + int(mainOffsetY*backgroundSize[1])
  imageTargetSize = expandImage(backgroundSize[0], backgroundSize[1], image.size[1]/image.size[0])
  backImage = image.resize(imageTargetSize, Image.ANTIALIAS)
  backImage = cropCenter(backImage, backgroundSize)
  Enhancer = ImageEnhance.Brightness(backImage)
  backImage = Enhancer.enhance(1.4)
  backImage = blurBackground(backImage)
  background = Image.new('RGB', backgroundSize, color=(255,255,255))
  background.paste(backImage,(0,0))
  background.paste(Shadow, (pasteLocationX,pasteLocationY), Shadow)
  background = background.resize(finalSizeWithoutText, Image.ANTIALIAS)
  backgroundText = Image.new('RGB', finalSize, color=(0,0,0))
  backgroundText.paste(background,(0,0))
  addText(backgroundText,sys.argv[2])
  backgroundText.show()
  backgroundText.save('./Output/'+sys.argv[1])

if __name__ == "__main__":
  main()