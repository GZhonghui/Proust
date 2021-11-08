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

fontSize = 56 #Default 56
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
  Proc('CS GO','CS:GO') #0251
  Proc('Physically Based Rendering 3rd','Physically Based Rendering')
  Proc('Real Time Rendering 4th','Real Time Rendering')
  Proc('Sky光遇','Sky光遇')
  Proc('Train Valley 2','Train Valley 2')
  Proc('一九四二','一九四二')
  Proc('一句顶一万句','一句顶一万句')
  Proc('三位一体','三位一体')
  Proc('三位一体2','三位一体2')
  Proc('三位一体3','三位一体3')
  Proc('上古卷轴5 天际','上古卷轴5 天际')
  Proc('东京物语','东京物语')
  Proc('为奴十二年','为奴十二年')
  Proc('乃木坂46：不知何时，在这里','乃木坂46:不知何时,在这里')
  Proc('乃木坂46：忘记悲伤的方法','乃木坂46:忘记悲伤的方法')
  Proc('乔乔的异想世界','乔乔的异想世界')
  Proc('二之国2：亡灵之国','二之国2 亡灵之国')
  Proc('亲爱的，不要跨过那条江','亲爱的,不要跨过那条江')
  Proc('人在囧途','Lost on Journey') # 字库没有'囧'字 真是囧
  Proc('人生果实','人生果实')
  Proc('仙剑奇侠传','仙剑奇侠传')
  Proc('以撒的结合 重生','以撒的结合:重生')
  Proc('以撒的结合','以撒的结合')
  Proc('任天堂明星大乱斗','任天堂明星大乱斗')
  Proc('伏龙记','伏龙记')
  Proc('伟大的一餐','伟大的一餐')
  Proc('你一生的故事','你一生的故事')
  Proc('信条','信条')
  Proc('健身环大冒险','健身环大冒险')
  Proc('允许自己虚度时光','允许自己虚度时光')
  Proc('克拉拉与太阳','克拉拉与太阳')
  Proc('全局光照技术','全局光照技术')
  Proc('兽人必须死2','兽人必须死2')
  Proc('冰与火之歌卷1 权力的游戏','冰与火之歌卷1 权力的游戏')
  Proc('冰与火之歌卷2 列王的纷争','冰与火之歌卷2 列王的纷争')
  Proc('冰与火之歌卷3 冰雨的风暴','冰与火之歌卷3 冰雨的风暴')
  Proc('冰与火之歌卷4 群鸦的盛宴','冰与火之歌卷4 群鸦的盛宴')
  Proc('冰与火之歌卷5 魔龙的狂舞','冰与火之歌卷5 魔龙的狂舞')
  Proc('功夫','功夫')
  Proc('勇者斗恶龙11','勇者斗恶龙11')
  Proc('南方公园 真理之杖','南方公园:真理之杖')
  Proc('去月球','去月球')
  Proc('变形金刚','变形金刚')
  Proc('古剑奇谭3','古剑奇谭3')
  Proc('古墓丽影：崛起','古墓丽影:崛起')
  Proc('古墓丽影：暗影','古墓丽影:暗影')
  Proc('后天','后天')
  Proc('哆啦A梦','哆啦A梦')
  Proc('哥斯拉','哥斯拉')
  Proc('四月是你的谎言','四月是你的谎言')
  Proc('回到最爱的一天','回到最爱的一天')
  Proc('围城','围城')
  Proc('围攻','围攻')
  Proc('土拨鼠之日','土拨鼠之日')
  Proc('在雪山和雪山之间','在雪山和雪山之间')
  Proc('堡垒','堡垒')
  Proc('墙上的斑点','墙上的斑点')
  Proc('天使爱美丽','天使爱美丽')
  Proc('天空之城','天空之城')
  Proc('太吾绘卷','太吾绘卷')
  Proc('守望先锋','守望先锋')
  Proc('寄生虫','寄生虫')
  Proc('密特罗德 生存恐惧','密特罗德:生存恐惧')
  Proc('小偷家族','小偷家族')
  Proc('小径分岔的花园','小径分岔的花园')
  Proc('尘埃3','尘埃3')
  Proc('尸战朝鲜：北方的阿信','尸战朝鲜:北方的阿信')
  Proc('干物妹 小埋','干物妹!小埋')
  Proc('干物妹 小埋R','干物妹!小埋R')
  Proc('平原上的夏洛克','平原上的夏洛克')
  Proc('幸福终点站','幸福终点站')
  Proc('廊桥遗梦','廊桥遗梦')
  Proc('异域镇魂曲','异域镇魂曲')
  Proc('弱点','弱点')
  Proc('心','心')
  Proc('心灵捕手','心灵捕手')
  Proc('志气','志气')
  Proc('忠犬八公的故事','忠犬八公的故事')
  Proc('怦然心动','怦然心动')
  Proc('恋爱前规则','恋爱前规则')
  Proc('成龙历险记','成龙历险记')
  Proc('我们的留学生活 在日本的日子','我们的留学生活:在日本的日子')
  Proc('我想吃掉你的胰脏','我想吃掉你的胰脏')
  Proc('我是猫','我是猫')
  Proc('我的世界','我的世界')
  Proc('我的世界：故事模式','我的世界 故事模式')
  Proc('战争仪式','战争仪式')
  Proc('摔跤吧 爸爸','摔跤吧!爸爸')
  Proc('撞车','撞车')
  Proc('文化失忆','文化失忆')
  Proc('新古墓丽影','新古墓丽影')
  Proc('旅行到宇宙边缘','旅行到宇宙边缘')
  Proc('无主之地','无主之地')
  Proc('无主之地2','无主之地2')
  Proc('无主之地3','无主之地3')
  Proc('无人深空','无人深空')
  Proc('无依之地','无依之地')
  Proc('无间道','无间道')
  Proc('时空幻境','时空幻境')
  Proc('旺达与巨像','旺达与巨像')
  Proc('星空','星空')
  Proc('普罗米修斯','普罗米修斯')
  Proc('最后的守护者','最后的守护者')
  Proc('最终幻想7 重制版','最终幻想7 重制版')
  Proc('未麻的部屋','未麻的部屋')
  Proc('末代皇帝','末代皇帝')
  Proc('林中之夜','林中之夜')
  Proc('植物大战僵尸','植物大战僵尸')
  Proc('植物大战僵尸：花园战争','植物大战僵尸:花园战争')
  Proc('死亡细胞','死亡细胞')
  Proc('水形物语','水形物语')
  Proc('汉江怪物','汉江怪物')
  Proc('沙之书','沙之书')
  Proc('波斯语课','波斯语课')
  Proc('泰拉瑞亚','泰拉瑞亚')
  Proc('洛丽塔','洛丽塔')
  Proc('活着','活着')
  Proc('流感','流感')
  Proc('海浪','海浪')
  Proc('海街日记','海街日记')
  Proc('海豚湾','海豚湾')
  Proc('海边的卡夫卡','海边的卡夫卡')
  Proc('港诡实录','港诡实录')
  Proc('火星救援','火星救援')
  Proc('火炬之光2','火炬之光2')
  Proc('灵魂只能独行','灵魂只能独行')
  Proc('炉石传说','炉石传说')
  Proc('爱你就像爱生命','爱你就像爱生命')
  Proc('爱死亡机器人','爱死亡机器人')
  Proc('爱死亡机器人2','爱死亡机器人 (二)')
  Proc('猫和老鼠','猫和老鼠')
  Proc('环太平洋','环太平洋')
  Proc('生化危机7','生化危机7')
  Proc('疯狂动物城','疯狂动物城')
  Proc('疯狂的石头','疯狂的石头')
  Proc('疯狂的赛车','疯狂的赛车')
  Proc('白日梦想家','白日梦想家')
  Proc('真女神转生3','真女神转生3')
  Proc('破风','破风')
  Proc('神偷奶爸','神偷奶爸')
  Proc('神偷奶爸2','神偷奶爸2')
  Proc('神偷奶爸3','神偷奶爸3')
  Proc('神界 原罪2','神界:原罪2')
  Proc('神秘海域4','神秘海域4')
  Proc('窗边的小豆豆','窗边的小豆豆')
  Proc('第一视角东京生活记录','第一视角东京生活记录')
  Proc('第八日的蝉','第八日的蝉')
  Proc('算法导论','算法导论')
  Proc('算法竞赛入门经典','算法竞赛入门经典')
  Proc('素媛','素媛')
  Proc('红玫瑰与白玫瑰','红玫瑰与白玫瑰')
  Proc('纸人','纸人')
  Proc('罗生门','罗生门')
  Proc('聪明的一休','聪明的一休')
  Proc('舌尖上的中国','舌尖上的中国')
  Proc('艺伎回忆录','艺伎回忆录')
  Proc('莎莉之定理','莎莉之定理')
  Proc('蓝海传说','蓝海传说')
  Proc('蓝白红三部曲之白','蓝白红三部曲之白')
  Proc('蓝白红三部曲之红','蓝白红三部曲之红')
  Proc('蓝白红三部曲之蓝','蓝白红三部曲之蓝')
  Proc('蔚蓝','蔚蓝')
  Proc('被嫌弃的松子的一生','被嫌弃的松子的一生')
  Proc('请回答 1994','请回答 1994')
  Proc('请回答 1997','请回答 1997')
  Proc('诸神灰烬','诸神灰烬')
  Proc('起风了 (电影)','起风了')
  Proc('超体','超体')
  Proc('超时空通话','超时空通话')
  Proc('超级马里奥：奥德赛','超级马里奥:奥德赛')
  Proc('轩辕剑7','轩辕剑7')
  Proc('辩护人','辩护人')
  Proc('追寻逝去的时光卷1 去斯万家那边','追寻逝去的时光卷1 去斯万家那边') # Font Size = 48
  Proc('追寻逝去的时光卷2 在少女花影下','追寻逝去的时光卷2 在少女花影下') # Font Size = 48
  Proc('都市 天际线','都市 天际线')
  Proc('重庆森林','重庆森林')
  Proc('金陵十三钗','金陵十三钗')
  Proc('釜山行','釜山行')
  Proc('锈湖 天堂岛','锈湖:天堂岛')
  Proc('锈湖 旅馆','锈湖:旅馆')
  Proc('锈湖 树根','锈湖:树根')
  Proc('镜之边缘','镜之边缘')
  Proc('长江七号','长江七号')
  Proc('雪国列车','雪国列车')
  Proc('风','风')
  Proc('风暴英雄','风暴英雄')
  Proc('飘','飘')
  Proc('食神','食神')
  Proc('饥荒 联机版','饥荒 联机版')
  Proc('饥荒','饥荒')
  Proc('马里奥赛车8','马里奥赛车8')
  Proc('魔兽争霸3 冰封王座','魔兽争霸3:冰封王座')
  Proc('魔兽争霸3 混沌之治','魔兽争霸3:混沌之治')
  Proc('魔女宅急便','魔女宅急便')
  Proc('鲁滨逊漂流记','鲁滨逊漂流记')
  Proc('黄金时代','黄金时代')
  Proc('黑暗血统3','黑暗血统3')
  Proc('往日不再','往日不再')
  Proc('消逝的光芒','消逝的光芒')
  Proc('新樱花大战','新樱花大战') # 0450
  Proc('12比6好','12比6好') # 0451
  Proc('C++ Primer Plus','C++ Primer Plus')
  Proc('GTA 5','GTA 5')
  Proc('一次别离','一次别离')
  Proc('不能承受的生命之轻','不能承受的生命之轻')
  Proc('东京教父','东京教父')
  Proc('中土世界：战争之影','中土世界:战争之影')
  Proc('九品芝麻官','九品芝麻官')
  Proc('乱世佳人','乱世佳人')
  Proc('云朋克','云朋克')
  Proc('人生的枷锁','人生的枷锁')
  Proc('人类一败涂地','人类一败涂地')
  Proc('伊利丹','伊利丹')
  Proc('传送门2','传送门2')
  Proc('低俗小说','低俗小说')
  Proc('何以为家','何以为家')
  Proc('侧耳倾听','侧耳倾听')
  Proc('健听女孩','健听女孩')
  Proc('光之子','光之子')
  Proc('全境封锁2','全境封锁2')
  Proc('全裸监督','全裸监督')
  Proc('全面战争：三国','全面战争:三国')
  Proc('勇敢的心：世界大战','勇敢的心 世界大战')
  Proc('勇气默示录2','勇气默示录2')
  Proc('北京爱情故事','北京爱情故事')
  Proc('北国之恋','北国之恋')
  Proc('千年女优','千年女优')
  Proc('博德之门3','博德之门3')
  Proc('名侦探柯南：世纪末的魔术师','名侦探柯南:世纪末的魔术师')
  Proc('名侦探柯南：引爆摩天楼','名侦探柯南:引爆摩天楼')
  Proc('名侦探柯南：瞳孔中的暗杀者','名侦探柯南:瞳孔中的暗杀者')
  Proc('名侦探柯南：贝克街的亡灵','名侦探柯南:贝克街的亡灵')
  Proc('名侦探柯南：迷宫的十字路口','名侦探柯南:迷宫的十字路口')
  Proc('名侦探柯南：通向天国的倒计时','名侦探柯南:通向天国的倒计时')
  Proc('后翼弃兵','后翼弃兵')
  Proc('和博尔赫斯在一起','和博尔赫斯在一起')
  Proc('哆啦A梦：大雄与梦幻三剑士','哆啦A梦:大雄与梦幻三剑士')
  Proc('哆啦A梦：大雄与翼之勇者','哆啦A梦:大雄与翼之勇者')
  Proc('哆啦A梦：大雄的创世日记','哆啦A梦:大雄的创世日记')
  Proc('哆啦A梦：大雄的宇宙小战争','哆啦A梦:大雄的宇宙小战争')
  Proc('哆啦A梦：大雄的平行西游记','哆啦A梦:大雄的平行西游记')
  Proc('哆啦A梦：大雄的恐龙','哆啦A梦:大雄的恐龙')
  Proc('哆啦A梦：大雄的日本诞生','哆啦A梦:大雄的日本诞生')
  Proc('哆啦A梦：大雄的秘密道具博物馆','哆啦A梦:大雄的秘密道具博物馆')
  Proc('哆啦A梦：大雄的魔界大冒险','哆啦A梦:大雄的魔界大冒险')
  Proc('哈尔的移动城堡','哈尔的移动城堡')
  Proc('喜剧之王','喜剧之王')
  Proc('四海兄弟','四海兄弟')
  Proc('困在时间里的父亲','困在时间里的父亲')
  Proc('圣殿春秋 (书籍)','圣殿春秋')
  Proc('圣殿春秋 (游戏)','圣殿春秋')
  Proc('地心浩劫','地心浩劫')
  Proc('地球脉动','地球脉动')
  Proc('地球脉动2','地球脉动 (二)')
  Proc('堂吉诃德','堂吉诃德')
  Proc('塞尔达传说 天空之剑','塞尔达传说:天空之剑')
  Proc('夏目友人帐 剧场版','夏目友人帐 剧场版')
  Proc('夜色温柔','夜色温柔')
  Proc('大侦探皮卡丘','大侦探皮卡丘')
  Proc('天国：拯救','天国 拯救')
  Proc('奇异人生：暴风前夕','奇异人生:暴风前夕')
  Proc('如蝶翩翩','如蝶翩翩')
  Proc('如龙7','如龙7')
  Proc('婚姻故事','婚姻故事')
  Proc('嫌疑人X的献身','嫌疑人X的献身')
  Proc('孤岛惊魂5','孤岛惊魂5')
  Proc('宇宙：时空之旅','宇宙:时空之旅')
  Proc('宇宙：未知世界','宇宙:未知世界')
  Proc('审判之眼：死神的遗言','审判之眼 死神的遗言')
  Proc('寂静之海','寂静之海')
  Proc('富贵再三逼人','富贵再三逼人')
  Proc('富贵再逼人','富贵再逼人')
  Proc('富贵逼人','富贵逼人')
  Proc('寻梦环游记','寻梦环游记')
  Proc('小丑','小丑')
  Proc('少年维特的烦恼','少年维特的烦恼')
  Proc('尤利西斯','尤利西斯')
  Proc('屌丝男士','Diors Man')
  Proc('岁月的童话','岁月的童话')
  Proc('平凡的世界','平凡的世界')
  Proc('幻夜','幻夜')
  Proc('幽灵公主','幽灵公主')
  Proc('当幸福来敲门','当幸福来敲门')
  Proc('彩虹六号：围攻','彩虹六号:围攻')
  Proc('性爱自修室','性爱自修室')
  Proc('怪物猎人物语2','怪物猎人物语2')
  Proc('恶意','恶意')
  Proc('想见你','想见你')
  Proc('我们与恶的距离','我们与恶的距离')
  Proc('我将独自前行','我将独自前行')
  Proc('拥抱逝水年华','拥抱逝水年华')
  Proc('指环王1：护戒使者','指环王1:护戒使者')
  Proc('指环王2：双塔奇兵','指环王2:双塔奇兵')
  Proc('指环王3：王者无敌','指环王3:王者无敌')
  Proc('搏击俱乐部','搏击俱乐部')
  Proc('撒哈拉的故事','撒哈拉的故事')
  Proc('放学后','放学后')
  Proc('教父','教父')
  Proc('敦刻尔克','敦刻尔克')
  Proc('断背山','断背山')
  Proc('新世纪福音战士','新世纪福音战士')
  Proc('无人知晓','无人知晓')
  Proc('春光乍泄','春光乍泄')
  Proc('暗影火炬城','暗影火炬城')
  Proc('最后生还者 重制版','最后生还者 重制版')
  Proc('最后生还者2','最后生还者2')
  Proc('权力的游戏：最后的守夜人','权力的游戏:最后的守夜人')
  Proc('桥梁建筑师 传送门','桥梁建筑师 传送门')
  Proc('步履不停','步履不停')
  Proc('死亡循环','死亡循环')
  Proc('死亡诗社','死亡诗社')
  Proc('比海更深','比海更深')
  Proc('永恒之柱2','永恒之柱2')
  Proc('沉默的羔羊','沉默的羔羊')
  Proc('沙丘','沙丘')
  Proc('泰坦尼克号','泰坦尼克号')
  Proc('浮生一日','浮生一日')
  Proc('浮生一日2020','浮生一日2020')
  Proc('海上钢琴师','海上钢琴师')
  Proc('深夜食堂','深夜食堂')
  Proc('漫长的告别','漫长的告别')
  Proc('火线','火线')
  Proc('火花','火花')
  Proc('灿烂人生','灿烂人生')
  Proc('烧纸','烧纸')
  Proc('煮糊了2','煮糊了2')
  Proc('爱乐之城','爱乐之城')
  Proc('王国之心3','王国之心3')
  Proc('琅琊榜','琅琊榜')
  Proc('瑞克和莫蒂','瑞克和莫蒂')
  Proc('生化危机2 重制版','生化危机2 重制版')
  Proc('生化危机3 重制版','生化危机3 重制版')
  Proc('生活大爆炸','生活大爆炸')
  Proc('瘟疫传说 无罪','瘟疫传说 无罪')
  Proc('白色巨塔','白色巨塔')
  Proc('白门','白门')
  Proc('皮克敏3','皮克敏3')
  Proc('看门狗','看门狗')
  Proc('真女神转生5','真女神转生5')
  Proc('真心半解','真心半解')
  Proc('简爱','简爱')
  Proc('精灵宝可梦 Lets Go 伊布','精灵宝可梦:Lets Go!伊布')
  Proc('精灵宝可梦 Lets Go 皮卡丘','精灵宝可梦:Lets Go!皮卡丘')
  Proc('素食者','素食者')
  Proc('紫与黑','紫与黑')
  Proc('红手指','红手指')
  Proc('绝命毒师','绝命毒师')
  Proc('绿山墙的安妮','绿山墙的安妮')
  Proc('罗马假日','罗马假日')
  Proc('美丽人生','美丽人生')
  Proc('美丽心灵','美丽心灵')
  Proc('群星','群星')
  Proc('色戒','色戒')
  Proc('艾尔登法环','艾尔登法环')
  Proc('花束般的恋爱','花束般的恋爱')
  Proc('花样年华','花样年华')
  Proc('莎木3','莎木3')
  Proc('莫失莫忘','莫失莫忘')
  Proc('萤火之森','萤火之森')
  Proc('蓝色大门','蓝色大门')
  Proc('薄荷糖','薄荷糖')
  Proc('街霸5','街霸5')
  Proc('西西里的美丽传说','西西里的美丽传说')
  Proc('西部世界','西部世界')
  Proc('让子弹飞','让子弹飞')
  Proc('贫民窟的百万富翁','贫民窟的百万富翁')
  Proc('赌神','赌神')
  Proc('赛博朋克2077','赛博朋克2077')
  Proc('超级马里奥制造2','超级马里奥制造2')
  Proc('路易鬼屋3','路易鬼屋3')
  Proc('辉夜姬物语','辉夜姬物语')
  Proc('辐射4','辐射4')
  Proc('辐射76','辐射76')
  Proc('辛德勒的名单','辛德勒的名单')
  Proc('迷托邦','迷托邦')
  Proc('逃学威龙','逃学威龙')
  Proc('逃学威龙2','逃学威龙2')
  Proc('逃生','逃生')
  Proc('部落与弯刀','部落与弯刀')
  Proc('重力异想世界','重力异想世界')
  Proc('看不见的客人','看不见的客人')
  Proc('金银岛','金银岛')
  Proc('闪之轨迹3','闪之轨迹3')
  Proc('阳光灿烂的日子','阳光灿烂的日子')
  Proc('非凡英雄','非凡英雄')
  Proc('飞天红猪侠','飞天红猪侠')
  Proc('飞屋环游记','飞屋环游记')
  Proc('飞越疯人院','飞越疯人院')
  Proc('饮食男女','饮食男女')
  Proc('骑马与砍杀','骑马与砍杀')
  Proc('骑马与砍杀2','骑马与砍杀2')
  Proc('鬼灭之刃','鬼灭之刃')
  Proc('魔兽','魔兽')
  Proc('魔女1：颠覆','魔女')
  Proc('鸟人','鸟人')
  Proc('鹿鼎记','鹿鼎记')
  Proc('鹿鼎记2：神龙教','鹿鼎记2:神龙教')
  Proc('黑客帝国','黑客帝国')
  Proc('黑镜','黑镜')
  Proc('鼠疫','鼠疫') # 0650
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