import random, sys
import asyncio
from loguru import logger
from gradient import Gradient
from config import shuffle, delay_min, delay_max
logger.remove()
logger.add(sys.stderr, format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                              '<level>{level: <7}</level> | '
                              '<level>{message}</level>')

logger.add("./logs/app.txt", format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {level} | {message}")

with open('proxy.txt') as f:
    proxy = []
    proxy = f.readlines()

with open('ref_codes.txt') as f:
    ref_codes = []
    ref_codes = f.readlines()
    random.shuffle(ref_codes)

with open('emails.txt') as f:
    lines = []
    lines = f.readlines()

emails = []
passwords = []
gradients = []

for line in lines:
    line = line.strip()
    if ':' in line:
        email, password = line.split(':', 1)
        emails.append(email)
        passwords.append(password)

if len(emails) != len(proxy):
    print("The number of emails is not equal to the number of proxies")
    print("Fill in the files correctly!!")
    sys.exit()

numbers = list(range(len(emails)))
for number in numbers:
    gradients.append(Gradient(emails[number], passwords[number], proxy=proxy[number], number_of_list=number))

if shuffle:
    random.shuffle(numbers)


async def perform_registration():
    tasks = []
    for number in numbers:
        index = gradients[number].number_of_list
        tasks.append(asyncio.create_task(gradients[number].registration(ref_codes[number])))
        delay = random.randint(delay_min, delay_max)
        logger.info(
            f'{index} | {gradients[number].mail} |⏳ Delay between accounts {delay}s')
        await asyncio.sleep(delay)
    await asyncio.gather()


async def perform_start_farming():
    tasks = []
    for number in numbers:
        index = gradients[number].number_of_list
        tasks.append(asyncio.create_task(gradients[number].perform_farming_actions(ref_codes[number])))
        delay = random.randint(delay_min, delay_max)
        logger.info(
            f'{index} | {gradients[number].mail} |⏳ Delay between accounts {delay}s')
        await asyncio.sleep(delay)
    await asyncio.gather()


async def main(mode):
    if mode == 'stats':
        return 0

    elif mode == 'farming':
        await perform_start_farming()

    elif mode == 'registration':
        await perform_registration()
        await perform_start_farming()

    else:
        print(f'No found this mode <{mode}>. Try another mode')


async def start():
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        await main(mode)
    else:
        print("Please add the mode: (python main <mode>)")


if __name__ == '__main__':
    asyncio.run(start())

