from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
import sys, string, os

mainSize = 0.94

finalSize = (800, 1200)

fontRatio = 0.24
ratioWidth = 2.0
ratioHeight = 3.0
Ratio = (ratioHeight - fontRatio) / ratioWidth

mainOffsetY = 0.01

textBelow = 26
textHeight = int(finalSize[1] * fontRatio / ratioHeight)
finalSizeWithoutText = (finalSize[0], finalSize[1] - textHeight)

fontSize = 56
fontPath = os.path.join('.', 'Assets', '方正宋刻本秀楷简体.TTF')

shadowBackgroundColour = (255, 255, 255)
shadowColour = (32, 32, 32)
shadowOffset = (24, 24)
shadowBorder = 32
shadowIterations = 48

blurRadious = 9

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
  
procCnt = 0
def Proc(fileName,Text=None):
  if not len(fileName):
    return
  global procCnt
  procCnt += 1
  Text = fileName if Text is None else Text
  print('[%03d] Procing :'%procCnt,fileName,'[%s]'%Text)
  fileName = fileName + '.png'
  image = Image.open(fileName)
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
  addText(backgroundText,Text)
  backgroundText.save('P02_'+fileName)

def main():
  '''
  Proc('')

  Proc('82年生的金智英') # 0001
  Proc('GRIS')
  Proc('东京日和')
  Proc('人间失格')
  Proc('人间有味')
  Proc('仙剑奇侠传 第三季','仙剑奇侠传 (三)')
  Proc('伊豆的舞女')
  Proc('伤心咖啡馆之歌')
  Proc('作为意志和表象的世界')
  Proc('你的名字')
  Proc('凯瑟琳 Full Body')
  Proc('千与千寻 新','千与千寻')
  Proc('只狼 影逝二度')
  Proc('垫底辣妹')
  Proc('塞尔达传说 荒野之息','塞尔达传说:荒野之息')
  Proc('失乐园')
  Proc('女神异闻录5 皇家版')
  Proc('对马岛之鬼')
  Proc('小森林 冬春篇')
  Proc('小森林 夏秋篇')
  Proc('小森林')
  Proc('情书 (书籍)','情书')
  Proc('情书 (电影)','情书')
  Proc('房思琪的初恋乐园')
  Proc('新战神')
  Proc('旋涡')
  Proc('星际穿越')
  Proc('权力的游戏')
  Proc('权力的游戏2', '权力的游戏 (二)')
  Proc('权力的游戏3', '权力的游戏 (三)')
  Proc('极限竞速 地平线4','极限竞速:地平线4')
  Proc('梦与狂想的王国')
  Proc('灿烂千阳')
  Proc('白夜行')
  Proc('白鹿原')
  Proc('看见')
  Proc('破晓传说')
  Proc('秘密森林')
  Proc('秘密森林2', '秘密森林 (二)')
  Proc('红辣椒')
  Proc('绯红结系')
  Proc('艾希 B', '艾希')
  Proc('苏菲的世界')
  Proc('菜穗子')
  Proc('请回答 1988')
  Proc('起风了')
  Proc('这个杀手不太冷')
  Proc('追忆似水年华')
  Proc('追风筝的人')
  Proc('雪国') # 0050
  
  Proc('18岁的天空','18岁的天空') # 0051
  Proc('1984','1984')
  Proc('82年生的金智英','82年生的金智英')
  Proc('ABZÛ','ABZU')
  Proc('AI 梦境档案','AI 梦境档案')
  Proc('C Primer Plus','C Primer Plus')
  Proc('Dota 2','Dota 2')
  Proc('Florence','Florence')
  Proc('Mirror','Mirror')
  Proc('一个人的朝圣','一个人的朝圣')
  Proc('三傻大闹宝莱坞','三傻大闹宝莱坞')
  Proc('三體','三体')
  Proc('不能说的秘密','不能说的秘密')
  Proc('东京爱情故事','东京爱情故事')
  Proc('人生的智慧','人生的智慧')
  Proc('人类星球','人类星球')
  Proc('仁王','仁王')
  Proc('仁王2','仁王2')
  Proc('今际之国的闯关者','今际之国的闯关者')
  Proc('仙剑奇侠传5','仙剑奇侠传5')
  Proc('仙剑奇侠传7','仙剑奇侠传7')
  Proc('伟大的孤独','伟大的孤独')
  Proc('传说之下','传说之下')
  Proc('你当像鸟飞往你的山','你当像鸟飞往你的山')
  Proc('兄弟','兄弟')
  Proc('入殓师 A','入殓师')
  Proc('入殓师 B','入殓师')
  Proc('八方旅人','八方旅人')
  Proc('切尔诺贝利','切尔诺贝利')
  Proc('初恋','初恋')
  Proc('刺客信条：奥德赛','刺客信条:奥德赛')
  Proc('刺客信条：起源','刺客信条:起源')
  Proc('十三机兵防卫圈','十三机兵防卫圈')
  Proc('同桌的你','同桌的你')
  Proc('后会无期','后会无期')
  Proc('告白','告白')
  Proc('命运石之门','命运石之门')
  Proc('哥德尔、艾舍尔、巴赫','哥德尔、艾舍尔、巴赫')
  Proc('喷射战士2','喷射战士2')
  Proc('地平线 零之曙光','地平线:零之曙光')
  Proc('地狱之刃 塞娜的献祭','地狱之刃 塞娜的献祭')
  Proc('地铁 离乡','地铁:离乡')
  Proc('塞尔达传说 织梦岛','塞尔达传说:织梦岛')
  Proc('大神','大神')
  Proc('大话西游之大圣娶亲','大话西游之大圣娶亲')
  Proc('大话西游之月光宝盒','大话西游之月光宝盒')
  Proc('大雄的牧场物语','大雄的牧场物语')
  Proc('大鱼海棠','大鱼海棠')
  Proc('天气之子','天气之子')
  Proc('头号玩家','头号玩家')
  Proc('奇异人生','奇异人生')
  Proc('奥日与萤火意志','奥日与萤火意志')
  Proc('奥日与黑暗森林','奥日与黑暗森林')
  Proc('奥林匹斯星传','奥林匹斯星传')
  Proc('女神异闻录5 乱战','女神异闻录5 乱战')
  Proc('女神异闻录5','女神异闻录5')
  Proc('对马岛之鬼','对马岛之鬼')
  Proc('小丑之花','小丑之花')
  Proc('小妇人 A','小妇人')
  Proc('小妇人 B','小妇人')
  Proc('小姐','小姐')
  Proc('少年派的奇幻漂流','少年派的奇幻漂流')
  Proc('尸战朝鲜 第二季','尸战朝鲜 (二)')
  Proc('尸战朝鲜','尸战朝鲜')
  Proc('尼尔：人工生命','尼尔:人工生命')
  Proc('尼尔：机械纪元','尼尔:机械纪元')
  Proc('岁月神偷','岁月神偷')
  Proc('崖上的波妞','崖上的波妞')
  Proc('左耳','左耳')
  Proc('巨龙的黄昏','巨龙的黄昏')
  Proc('巨龙的黎明','巨龙的黎明')
  Proc('巫师3 狂猎','巫师3 狂猎')
  Proc('异度之刃2','异度之刃2')
  Proc('异度神剑 终极版','异度之刃 终极版')
  Proc('异界锁链','异界锁链')
  Proc('弹丸破论','弹丸破论')
  Proc('彗星来的那一夜','彗星来的那一夜')
  Proc('影子战术：将军之刃','影子战术 将军之刃')
  Proc('心是孤独的猎手','心是孤独的猎手')
  Proc('心花路放','心花路放')
  Proc('怪物猎人：世界','怪物猎人:世界')
  Proc('怪物猎人：崛起','怪物猎人:崛起')
  Proc('恶魔之魂','恶魔之魂')
  Proc('我不是药神','我不是药神')
  Proc('我的大叔','我的大叔')
  Proc('战争之潮','战争之潮')
  Proc('战争机器4','战争机器4')
  Proc('戴森球计划','戴森球计划')
  Proc('挪威的森林','挪威的森林')
  Proc('控制','控制')
  Proc('文明6','文明6')
  Proc('方根书简','方根书简')
  Proc('方根胶卷','方根胶卷')
  Proc('旅途','旅途')
  Proc('无声告白','无声告白')
  Proc('无姓之人','无姓之人')
  Proc('无路之旅','无路之旅')
  Proc('时间简史','时间简史')
  Proc('星露谷物语','星露谷物语')
  Proc('暗黑破坏神3','暗黑破坏神3')
  Proc('暴雨 超凡双生','暴雨 超凡双生')
  Proc('最终幻想15','最终幻想15')
  Proc('月亮与六便士 A','月亮与六便士')
  Proc('月亮与六便士 B','月亮与六便士')
  Proc('杀人回忆','杀人回忆')
  Proc('权力的游戏4','权力的游戏 (四)')
  Proc('权力的游戏5','权力的游戏 (五)')
  Proc('权力的游戏6','权力的游戏 (六)')
  Proc('权力的游戏7','权力的游戏 (七)')
  Proc('权力的游戏8','权力的游戏 (八)')
  Proc('来自星星的你','来自星星的你')
  Proc('极乐迪斯科','极乐迪斯科')
  Proc('查拉图斯特拉如是说','查拉图斯特拉如是说')
  Proc('桥本奈奈未的恋爱文学：冬之旅','奈奈未的恋爱文学:冬之旅')
  Proc('桥本奈奈未的恋爱文学：夏之旅','奈奈未的恋爱文学:夏之旅')
  Proc('梨泰院Class','梨泰院Class')
  Proc('楚门的世界','楚门的世界')
  Proc('檀香刑','檀香刑')
  Proc('步履不停','步履不停')
  Proc('武林外传','武林外传')
  Proc('死亡搁浅','死亡搁浅')
  Proc('永隔一江水','永隔一江水')
  Proc('求生之路','求生之路')
  Proc('求生之路2','求生之路2')
  Proc('汐','汐')
  Proc('泰坦陨落2','泰坦陨落2')
  Proc('海洋天堂','海洋天堂')
  Proc('海蒂和爷爷','海蒂和爷爷')
  Proc('海边的曼彻斯特','海边的曼彻斯特')
  Proc('深入理解计算机系统','深入理解计算机系统')
  Proc('火焰纹章：风花雪月','火焰纹章:风花雪月')
  Proc('灵魂献祭','灵魂献祭')
  Proc('熔炉','熔炉')
  Proc('爱在午夜降临前','爱在午夜降临前')
  Proc('爱在日落黄昏时','爱在日落黄昏时')
  Proc('爱在黎明破晓前','爱在黎明破晓前')
  Proc('爱情公寓','爱情公寓')
  Proc('爱情公寓2','爱情公寓2')
  Proc('爱情公寓3','爱情公寓3')
  Proc('爱情公寓4','爱情公寓4')
  Proc('甜蜜家园','甜蜜家园')
  Proc('生活蒙太奇','生活蒙太奇')
  Proc('画中世界','画中世界')
  Proc('百年孤独','百年孤独')
  Proc('盗梦空间','盗梦空间')
  Proc('目送','目送')
  Proc('看火人','看火人')
  Proc('神舞幻想','神舞幻想')
  Proc('秒速五厘米','秒速五厘米')
  Proc('空洞骑士','空洞骑士')
  Proc('第三极','第三极')
  Proc('等一个人咖啡','等一个人咖啡')
  Proc('红花坂上的海','红花坂上的海')
  Proc('纵身入山海','纵身入山海')
  Proc('纽约的一个雨天','纽约的一个雨天')
  Proc('绿皮书','绿皮书')
  Proc('肖申克的救赎','肖申克的救赎')
  Proc('艾迪芬奇的记忆','艾迪芬奇的记忆')
  Proc('茶杯头','茶杯头')
  Proc('荒野大镖客 救赎2','荒野大镖客 救赎2')
  Proc('莱莎的炼金工坊2','莱莎的炼金工坊2')
  Proc('菊次郎的夏天','菊次郎的夏天')
  Proc('蜂鸟','蜂鸟')
  Proc('蜜桃成熟时','蜜桃成熟时')
  Proc('血源','血源')
  Proc('被偷走的那五年','被偷走的那五年')
  Proc('见证者','见证者')
  Proc('解忧杂货店','解忧杂货店')
  Proc('言叶之庭','言叶之庭')
  Proc('赤痕：夜之仪式','赤痕:夜之仪式')
  Proc('赤痕：月之诅咒','赤痕:月之诅咒')
  Proc('返校','返校')
  Proc('还愿','还愿')
  Proc('远山淡影','远山淡影')
  Proc('迪迦奥特曼','迪迦奥特曼')
  Proc('送你一颗子弹','送你一颗子弹')
  Proc('送我上青云','送我上青云')
  Proc('逃避虽可耻但有用','逃避虽可耻但有用')
  Proc('长安十二时辰 上','长安十二时辰 (上)')
  Proc('长安十二时辰 下','长安十二时辰 (下)')
  Proc('长日将尽','长日将尽')
  Proc('阳光姐妹淘 日本','阳光姐妹淘')
  Proc('阳光姐妹淘 韩国','阳光姐妹淘')
  Proc('阳光普照','阳光普照')
  Proc('阿丽塔 战斗天使','阿丽塔 战斗天使')
  Proc('阿甘正传','阿甘正传')
  Proc('陷阵之志','陷阵之志')
  Proc('隐形守护者','隐形守护者')
  Proc('集合啦！动物森友会','集合啦!动物森友会')
  Proc('霍乱时期的爱情','霍乱时期的爱情')
  Proc('霸王别姬','霸王别姬')
  Proc('风来之国','风来之国')
  Proc('鬼泣5','鬼泣5')
  Proc('麦田里的守望者','麦田里的守望者')
  Proc('黑暗之魂1 重制版','黑暗之魂 重制版')
  Proc('黑暗之魂2','黑暗之魂2')
  Proc('黑暗之魂3','黑暗之魂3')
  Proc('龙樱','龙樱')
  Proc('龙猫 新','龙猫')
  Proc('龙猫','龙猫') # 0250
  ''' 

'''
import os
Sum = 0
for i in os.listdir('.'):
  if i.split('.')[-1] == 'png':
    print('Proc(\'%s\',\'%s\')'%(i[:-4],i[:-4]))
    Sum+=1
'''

if __name__ == "__main__":
  main()