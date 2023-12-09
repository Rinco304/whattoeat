import hoshino, random, os, re, filetype
from hoshino import Service, R, priv, aiorequests
from hoshino.config import RES_DIR
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter

sv_help = '''
[今天吃什么] 看看今天吃啥
[今天喝什么] 看看今天喝啥
'''.strip()

sv = Service(
    name = '今天吃喝什么',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #可见性
    enable_on_default = True, #默认启用
    bundle = '娱乐', #分组归类
    help_ = sv_help #帮助说明
    )

_lmt = DailyNumberLimiter(3)
foodpath = os.path.join(os.path.expanduser(RES_DIR), 'img', 'foods')
drinkpath = os.path.join(os.path.expanduser(RES_DIR), 'img', 'drinks')
food_max_msg = (
    "你今天吃的够多了！不许再吃了！",
    "吃吃吃，就知道吃，你都吃饱了！明天再来(▼皿▼#)",
    "(*｀へ´*)你猜我会不会再给你发好吃的图片",
    "没得吃的了，咱的食物都被你这坏蛋吃光了！",
    "你在等我给你发好吃的？做梦哦！你都吃那么多了，不许再吃了！ヽ(≧Д≦)ノ",
    "吃货，你是不是把食物当成爱人了？再吃就是渣男了，悔过吧！",
    "吃得比拳击手打拳还拼命，小心晚上变成食梦者，梦里都是各种美食哦！(¬_¬)",
    "你是米虫吗？今天碳水要爆炸啦！",
    "去码头整点薯条吧🍟",
    "吃得这么猛，你是要参加拔河比赛还是美食节啊？Σ( ° △ °|||)︴"
)
drink_max_msg = (
    "你今天喝的也够多了哦！不要再灌了，小心成了水桶(●°u°●)​ ",
    "喝咖啡都没你喝水认真，再喝下去，你就得住在厕所啦！(｡ì _ í｡)",
    "别再喝了，快变成水球了！(¬_¬)",
    "喝水这么厉害，要不要参加奥运会的饮水比赛？",
    "你是水桶吗？今天糖分要超标啦！",
    "喝太多了，肚子会变成水瓜哦(´∩｡• ᵕ •｡∩`)",
    "你是来挑战喝水界的吗？小心水肿成气球哦(￣Д￣)",
    "哎呀呀，水都快变成你的代号了吧，喝水也要适可而止哦(｡ì _ í｡)",
    "喝水喝得这么猛，是要去找海盗船吗？水手，别再喝了，快回到工作岗位吧！⚓️",
)

@sv.on_rex(r'^(今天|[早中午晚][上饭餐午]|夜宵)吃(什么|啥|点啥)')
async def net_ease_cloud_word(bot,ev:CQEvent):
    uid = ev.user_id
    if not _lmt.check(uid):
        await bot.finish(ev, random.choice(food_max_msg), at_sender=True)
    match = ev['match']
    time = match.group(1).strip()
    food = random.choice(os.listdir(foodpath))
    name = food.split('.')
    to_eat = f'{time}去吃{name[0]}吧~\n'
    try:
        foodimg = R.img(f'foods/{food}').cqcode
        to_eat += str(foodimg)
    except Exception as e:
        hoshino.logger.error(f'读取食物图片时发生错误{type(e)}')
    await bot.send(ev, to_eat, at_sender=True)
    _lmt.increase(uid)
    
    
@sv.on_rex(r'^(今天|[早中午晚][上饭餐午]|夜宵)喝(什么|啥|点啥)')
async def what_to_drink(bot,ev:CQEvent):
    uid = ev.user_id
    if not _lmt.check(uid):
        await bot.finish(ev, random.choice(drink_max_msg), at_sender=True)
    match = ev['match']
    time = match.group(1).strip()
    drink = random.choice(os.listdir(drinkpath))
    name = drink.split('.')
    to_drink = f'{time}去喝{name[0]}吧~\n'
    try:
        drinkimg = R.img(f'drinks/{drink}').cqcode
        to_drink += str(drinkimg)
    except Exception as e:
        hoshino.logger.error(f'读取饮品图片时发生错误{type(e)}')
    await bot.send(ev, to_drink, at_sender=True)
    _lmt.increase(uid)
    

async def download_async(url: str, name: str, type: int):
    resp= await aiorequests.get(url, stream=True)
    if resp.status_code == 404:
        raise ValueError('文件不存在')
    content = await resp.content
    try:
        extension = filetype.guess_mime(content).split('/')[1]
    except:
        raise ValueError('不是有效文件类型')
    if type == 1:
        abs_path = os.path.join(foodpath, f'{name}.{extension}')
    elif type == 2:
        abs_path = os.path.join(drinkpath, f'{name}.{extension}')
    with open(abs_path, 'wb') as f:
        f.write(content)

@sv.on_prefix(('添菜','添加菜品'))
@sv.on_suffix(('添菜','添加菜品'))
async def add_food(bot,ev:CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return
    food = ev.message.extract_plain_text().strip()
    ret = re.search(r"\[CQ:image,file=(.*)?,url=(.*)\]", str(ev.message))
    if not ret:
        await bot.send(ev,'请附带美食图片~')
        return
    url = ret[2]
    await download_async(url, food, 1)
    await bot.send(ev,'食谱已增加~')

@sv.on_prefix(('添饮料','添饮品','添加饮料','添加饮品'))
@sv.on_suffix(('添饮料','添饮品','添加饮料','添加饮品'))
async def add_drink(bot,ev:CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        return
    drink = ev.message.extract_plain_text().strip()
    ret = re.search(r"\[CQ:image,file=(.*)?,url=(.*)\]", str(ev.message))
    if not ret:
        await bot.send(ev,'请附带饮品图片~')
        return
    url = ret[2]
    await download_async(url, drink, 2)
    await bot.send(ev,'饮品已增加~')
