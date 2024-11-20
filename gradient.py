from playwright.async_api import async_playwright, expect
import asyncio, random
from fake_useragent import UserAgent
from loguru import logger
from config import HEADLESS
import os, imaplib
from bs4 import BeautifulSoup
import email, json
from email.policy import default

EXTENTION_PATH = os.path.join(os.getcwd(), '1.0.5_0')
#caacbgbklghmpodbdafajbgdnegacfmo

class Gradient:
    all_stats = []
    def __init__(self, mail: str, email_password: str, proxy: str, number_of_list: int, ):
        self.mail = mail.strip()
        self.proxy = proxy.strip()
        self.number_of_list = number_of_list
        self.email_password = email_password.strip()


    @staticmethod
    def extract_verification_code_from_html(html_body):
        soup = BeautifulSoup(html_body, "html.parser")
        code_divs = soup.find_all("div", class_="pDiv")
        verification_code = ''.join(div.get_text(strip=True) for div in code_divs if not "empty" in div.get("class", []))
        return verification_code if verification_code else None


    async def connect_to_email(self, imap_server='imap.firstmail.ltd', imap_port=993, retry=0):
        idx = "Connect the email"
        sender_email = "noreply@gradient.network"
        try:
            logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Logging in email")
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            mail.login(self.mail, self.email_password)
            logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Login successful")
            mail.select("INBOX")

            status, messages = mail.search(None, f'FROM "{sender_email}"')
            if status != 'OK' or not messages[0]:
                logger.error(f"{self.number_of_list} | {self.mail} | {idx} | No emails found from {sender_email}.")
                return

            mail_ids = messages[0].split()
            latest_email_id = mail_ids[-1]
            status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
            if status != 'OK':
                logger.error(
                    f"{self.number_of_list} | {self.mail} | {idx} | Error fetching the latest email from {sender_email}.")
                return None

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1], policy=default)
                    subject = msg['subject']
                    from_ = msg['from']
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body = part.get_payload(decode=True).decode()
                                code = self.extract_verification_code_from_html(body)
                                logger.info(
                                    f"{self.number_of_list} | {self.mail} | {idx} | Subject: {subject} | From: {from_} | Code: {code}")
                                return code
                    else:
                        body = msg.get_payload(decode=True).decode()
                        code = self.extract_verification_code_from_html(body)
                        logger.info(
                            f"{self.number_of_list} | {self.mail} | {idx} | Subject: {subject} | From: {from_} | Code: {code}")
                        return code

        except Exception as error:
                retry += 1
                if retry > 5:
                    logger.error(f"{self.number_of_list} | {self.mail} | {idx} | UNSUCCESSFULLY GETTING CODE!")
                    return

                logger.error(f"{self.number_of_list} | {self.mail} | {idx} | Error: {error}")
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Delay 20 seconds")
                await asyncio.sleep(20)
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Starting {retry}/5 time")
                await self.connect_to_email(imap_server, imap_port, retry=retry)


    async def registration(self, ref_code: str, retry=0):
        idx = "Starting browser"
        async with async_playwright() as p:
            proxy = self.proxy.split(':')
            username, password, host, port = proxy
            logger.info(f"{self.number_of_list} | {self.mail} | Creating the new context")
            try:
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Creating browser...")
                context = await p.chromium.launch_persistent_context(
                    '',
                    headless=HEADLESS,
                    proxy={'server': f'http://{host}:{port.strip()}',
                           'username': username,
                           'password': password},
                    user_agent=UserAgent().chrome,
                    args=[ "--disable-blink-features=AutomationControlled"] + (['--headless=new']) if HEADLESS else [],
                )
                logger.info(
                    f"{self.number_of_list} | {self.mail} | {idx} | Successfully creating browser")

            except Exception as error:
                retry += 1
                if retry > 5:
                    logger.error(f"{self.number_of_list} | {self.mail} | {idx} | UNSUCCESSFULLY STARTING BROWSER!")
                    return
                logger.error(
                    f"{self.number_of_list} | {self.mail} | {idx} | Unsuccessfully starting browser! Error: {error}")
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Delay 20 seconds")
                await asyncio.sleep(20)
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Starting {retry}/5 time")
                await context.close()
                await self.registration(ref_code)

            idx = "Registration in Gradient.network"
            try:
                await asyncio.sleep(2)
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Go to the website..")
                page = await context.new_page()
                await page.goto('https://app.gradient.network/signup')
                await page.wait_for_load_state()
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Successfully connect to website")

            except Exception as error:
                if retry > 5:
                    logger.error(f"{self.number_of_list} | {self.mail} | {idx} | UNSUCCESSFULLY CONNECT TO WEBSITE!")
                    return
                logger.error(
                    f"{self.number_of_list} | {self.mail} | {idx} | Unsuccessfully connect to website! Error: {error}")
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Delay 20 seconds")
                await asyncio.sleep(20)
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Starting {retry}/5 time")
                await context.close()
                await self.registration(ref_code)

            try:
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Registration...")

                inputs = page.get_by_placeholder("Enter Email")
                await expect(inputs).to_be_visible()
                await inputs.type(self.mail)
                await asyncio.sleep(1)
                button_confirm = page.locator('//html/body/div[1]/div[2]/div/div/div/div[2]/button[1]')
                await expect(button_confirm).to_be_visible()
                await button_confirm.click()
                try:
                    if await page.locator('//html/body/div[1]/div[2]/div/div/div/div[2]/div[2]/div/span[1]').text_content() == "Email already registered,":
                        logger.warning(f"{self.number_of_list} | {self.mail} | {idx} | Account already registered!")
                        return
                except:
                    pass
                inputs_ref_code = page.locator('//html/body/div[1]/div[2]/div/div/div/div[3]/div[1]/input[1]')
                await expect(inputs_ref_code).to_be_visible()
                await inputs_ref_code.type(ref_code)

                button_get_boosted = page.locator('//html/body/div[1]/div[2]/div/div/div/button')
                await expect(button_get_boosted).to_be_visible()
                await button_get_boosted.click()

                inputs_create_password = page.get_by_placeholder("Enter Password")
                await expect(inputs_create_password).to_be_visible()
                await inputs_create_password.type(self.email_password)

                inputs_confirm_password = page.get_by_placeholder("Confirm Password")
                await expect(inputs_confirm_password).to_be_visible()
                await inputs_confirm_password.type(self.email_password)

                element = page.locator('svg.mr-1')
                await expect(element).to_be_visible()
                await element.click()

                button_sign_up = page.locator("//html/body/div[1]/div[2]/div/div/div/div[4]/button")
                await expect(button_sign_up).to_be_visible()
                await button_sign_up.click()
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Waiting for getting code...")
                await asyncio.sleep(7)
                screen_width = await page.evaluate("window.innerWidth")
                await page.mouse.click(screen_width * 0.9, 300)
                email_code = await self.connect_to_email()
                if email_code:
                    inputs_email_code = page.locator('//html/body/div[1]/div[2]/div/div/div/div[4]/div/input[1]')
                    await expect(inputs_email_code).to_be_visible()
                    await inputs_email_code.type(email_code)

                    button_verify = page.locator('//html/body/div[1]/div[2]/div/div/div/button[1]')
                    await expect(button_verify).to_be_visible()
                    await button_verify.click()

                    await asyncio.sleep(random.randint(3, 6))
                    button = page.locator('//html/body/div[1]/div[2]/div/div/div/div[2]/button')
                    await expect(button).to_be_visible()
                    await button.click()

                    await asyncio.sleep(3)
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(3)
                    logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Successfully registration")
                    return context

                else:
                    await asyncio.sleep(5)

                    await page.goto("https://app.gradient.network/")
                    await asyncio.sleep(1)

                    inputs = page.get_by_placeholder("Enter Email")
                    await expect(inputs).to_be_visible()
                    await inputs.type(self.mail)

                    inputs2 = page.get_by_placeholder("Enter Password")
                    await expect(inputs2).to_be_visible()
                    await inputs2.type(self.email_password)
                    await asyncio.sleep(random.randint(1, 3))

                    button = page.locator('//html/body/div[1]/div[2]/div/div/div/div[4]/button[1]')
                    await expect(button).to_be_visible()
                    await button.click()

                    inputs_ref_code = page.locator('//html/body/div[3]/div/div[2]/div/div[2]/div/div/div/div[2]/div[1]/input[1]')
                    await expect(inputs_ref_code).to_be_visible()
                    await inputs_ref_code.type(ref_code)

                    button_get_boosted = page.locator('//html/body/div[3]/div/div[2]/div/div[2]/div/div/div/button')
                    await expect(button_get_boosted).to_be_visible()
                    await button_get_boosted.click()
                    logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Waiting for getting code...")
                    await asyncio.sleep(15)
                    screen_width = await page.evaluate("window.innerWidth")
                    await page.mouse.click(screen_width * 0.9, 300)
                    email_code = await self.connect_to_email()
                    inputs_email_code = page.locator('//html/body/div[1]/div[2]/div/div/div/div[4]/div/input[1]')
                    await expect(inputs_email_code).to_be_visible()
                    await inputs_email_code.type(email_code)

                    button_verify = page.locator('//html/body/div[1]/div[2]/div/div/div/button[1]')
                    await expect(button_verify).to_be_visible()
                    await button_verify.click()

                    await asyncio.sleep(random.randint(3, 6))
                    button = page.locator('//html/body/div[1]/div[2]/div/div/div/div[2]/button')
                    await expect(button).to_be_visible()
                    await button.click()
                    await asyncio.sleep(3)
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(3)
                    logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Successfully registration")
                    return context

            except Exception as error:
                if retry > 5:
                    logger.error(f"{self.number_of_list} | {self.mail} | {idx} | UNSUCCESSFULLY REGISTRATION!")
                    return context
                logger.error(
                    f"{self.number_of_list} | {self.mail} | {idx} | Unsuccessfully registration! Error: {error}")
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Starting {retry}/5 time")
                await context.close()
                await self.registration(ref_code)


    async def perform_farming_actions(self, ref_code: str, retry = 0):
        idx = "Logging to Gradient.network"
        async with async_playwright() as p:
            proxy = self.proxy.split(':')
            username, password, host, port = proxy
            try:
                context = await p.chromium.launch_persistent_context(
                    '',
                    headless=HEADLESS,
                    proxy={'server': f'http://{host}:{port.strip()}',
                           'username': username,
                           'password': password},
                    user_agent=UserAgent().chrome,
                    args=[
                        '--disable-extensions-except=' + EXTENTION_PATH,
                        '--load-extension=' + EXTENTION_PATH,
                    ] + (['--headless=new'] if HEADLESS else []),
                )
            except Exception as error:
                retry += 1
                if retry > 5:
                    logger.error(f"{self.number_of_list} | {self.mail} | {idx} | UNSUCCESSFULLY STARTING BROWSER!")
                    return
                logger.error(
                    f"{self.number_of_list} | {self.mail} | {idx} | Unsuccessfully starting browser! Error: {error}")
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Delay 20 seconds")
                await asyncio.sleep(20)
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Starting {retry}/5 time")
                await context.close()
                await self.perform_farming_actions(ref_code)

            idx = "Logining in Gradient.network"
            try:
                await asyncio.sleep(2)
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Go to the website..")
                page = await context.new_page()
                await page.goto('https://app.gradient.network/')
                await page.bring_to_front()
                await page.wait_for_load_state()
                await asyncio.sleep(random.randint(2, 6))
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Successfully connect to website")

            except Exception as error:
                if retry > 5:
                    logger.error(f"{self.number_of_list} | {self.mail} | {idx} | UNSUCCESSFULLY CONNECT TO WEBSITE!")
                    return
                logger.error(
                    f"{self.number_of_list} | {self.mail} | {idx} | Unsuccessfully connect to website! Error: {error}")
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Delay 20 seconds")
                await asyncio.sleep(20)
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Starting {retry}/5 time")
                await context.close()
                await self.perform_farming_actions(ref_code, retry=retry)

            try:
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Logining...")
                await page.bring_to_front()
                inputs = page.get_by_placeholder("Enter Email")
                await expect(inputs).to_be_visible()
                await inputs.type(self.mail)
                inputs2 = page.get_by_placeholder("Enter Password")
                await expect(inputs2).to_be_visible()
                await inputs2.type(self.email_password)
                await asyncio.sleep(random.randint(2, 6))
                button = page.locator('//html/body/div[1]/div[2]/div/div/div/div[4]/button[1]')
                await expect(button).to_be_visible()
                await button.click()
                try:
                    if await page.locator('//html/body/div[3]/div/div[2]/div/div[2]/div/div/div/button', timeout=3000).text_content() == "Get Boosted":
                        inputs_ref_code = page.locator(
                            '//html/body/div[3]/div/div[2]/div/div[2]/div/div/div/div[2]/div[1]/input[1]')
                        await expect(inputs_ref_code).to_be_visible()
                        await inputs_ref_code.type(ref_code)

                        button_get_boosted = page.locator('//html/body/div[3]/div/div[2]/div/div[2]/div/div/div/button')
                        await expect(button_get_boosted).to_be_visible()
                        await button_get_boosted.click()
                        logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Waiting for getting code...")
                        await asyncio.sleep(15)
                        screen_width = await page.evaluate("window.innerWidth")
                        await page.mouse.click(screen_width * 0.9, 300)
                        email_code = await self.connect_to_email()
                        inputs_email_code = page.locator('//html/body/div[1]/div[2]/div/div/div/div[4]/div/input[1]')
                        await expect(inputs_email_code).to_be_visible()
                        await inputs_email_code.type(email_code)

                        button_verify = page.locator('//html/body/div[1]/div[2]/div/div/div/button[1]')
                        await expect(button_verify).to_be_visible()
                        await button_verify.click()

                        await asyncio.sleep(random.randint(3, 6))
                        button = page.locator('//html/body/div[1]/div[2]/div/div/div/div[2]/button')
                        await expect(button).to_be_visible()
                        await button.click()
                        await asyncio.sleep(3)
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(3)
                        logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Successfully loging")

                except:
                    pass
                await asyncio.sleep(3)
                await page.keyboard.press('Escape')
                await asyncio.sleep(3)
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Successfully loging")

            except Exception as error:
                if retry > 5:
                    logger.error(f"{self.number_of_list} | {self.mail} | {idx} | UNSUCCESSFULLY LOGING!")
                    return
                logger.error(
                    f"{self.number_of_list} | {self.mail} | {idx} | Unsuccessfully loging! Error: {error}")
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Delay 20 seconds")
                await asyncio.sleep(20)
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Starting {retry}/5 time")
                await self.perform_farming_actions(ref_code, retry=retry)

            try:
                page2 = await context.new_page()
                await page2.goto("chrome-extension://caacbgbklghmpodbdafajbgdnegacfmo/popup.html")
                button_got_it = page2.locator('//html/body/div[2]/div/div[2]/div/div[2]/div/div/div/button')
                await expect(button_got_it).to_be_visible()
                await button_got_it.click()
                await asyncio.sleep(3)
                await page2.keyboard.press('Escape')
                await page.bring_to_front()
                await page.goto('https://app.gradient.network/dashboard/node')
            except:
                pass
            while True:
                idx = 'Farming'
                check = False
                try:
                    logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Start farming..")
                    try:
                        # await asyncio.wait_for(page.reload(), timeout=10)
                        await asyncio.wait_for(
                            page.goto('https://app.gradient.network/dashboard/node'),
                            timeout=10
                        )

                    except asyncio.TimeoutError:
                        await asyncio.sleep(3)

                    try:
                        # await asyncio.wait_for(page.reload(), timeout=10)
                        await asyncio.wait_for(
                            page2.goto('chrome-extension://caacbgbklghmpodbdafajbgdnegacfmo/popup.html'),
                            timeout=10
                        )

                    except asyncio.TimeoutError:
                        await asyncio.sleep(5)
                    # status, points = await self.get_status(page2)
                    # status, points = await self.dashboard_node(page)
                    # logger.info(
                    #     f"{self.number_of_list} | {self.mail} | {idx} | Status node: {status}; Points: {points}")
                    delay = random.randint(600, 700)
                    logger.info(
                        f"{self.number_of_list} | {self.mail} | {idx} | Waiting {delay}s for the updating ...")
                    check = True
                    await asyncio.sleep(delay)

                except asyncio.CancelledError:
                    if check:
                        await asyncio.sleep(delay)
                    else:
                        logger.info(
                            f"{self.number_of_list} | {self.mail} | {idx} | Waiting 20s for the updating...")
                        await asyncio.sleep(20)

                except Exception as error:
                    logger.error(f"{self.number_of_list} | {self.mail} | {idx} | Error: {error}")
                    await asyncio.sleep(20)
                    await self.perform_farming_actions(ref_code)


    async def get_stats(self, retry = 0):
        idx = "STATS"
        async with async_playwright() as p:
            proxy = self.proxy.split(':')
            username, password, host, port = proxy
            try:
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Waiting for getting the stats...")
                context = await p.chromium.launch_persistent_context(
                    '',
                    headless=HEADLESS,
                    proxy={'server': f'http://{host}:{port.strip()}',
                           'username': username,
                           'password': password},
                    user_agent=UserAgent().chrome,
                    args=["--disable-blink-features=AutomationControlled"] + (['--headless=new']) if HEADLESS else [],
                )

            except Exception as error:
                retry += 1
                if retry > 4:
                    logger.error(f"{self.number_of_list} | {self.mail} | {idx} | UNSUCCESSFULLY GETTING THE STATS: {error}")
                    return
                await asyncio.sleep(20)
                await context.close()
                await self.get_stats(retry=retry)

            try:
                await asyncio.sleep(2)
                page = await context.new_page()
                await page.goto('https://app.gradient.network/')
                await page.bring_to_front()
                await page.wait_for_load_state()
                await asyncio.sleep(random.randint(2, 6))

            except Exception as error:
                retry+=1
                if retry > 5:
                    logger.error(f"{self.number_of_list} | {self.mail} | {idx} | UNSUCCESSFULLY CONNECT TO WEBSITE! Error: {error}")
                    return
                await context.close()
                await self.get_stats(retry=retry)

            try:
                logger.info(f"{self.number_of_list} | {self.mail} | {idx} | Logining...")
                await page.bring_to_front()
                inputs = page.get_by_placeholder("Enter Email")
                await expect(inputs).to_be_visible()
                await inputs.type(self.mail)
                inputs2 = page.get_by_placeholder("Enter Password")
                await expect(inputs2).to_be_visible()
                await inputs2.type(self.email_password)
                await asyncio.sleep(random.randint(2, 6))
                button = page.locator('//html/body/div[1]/div[2]/div/div/div/div[4]/button[1]')
                await expect(button).to_be_visible()
                await button.click()
                await asyncio.sleep(random.randint(2, 6))

                await page.goto('https://app.gradient.network/dashboard/node')
            except:
                pass

            try:
                status, points = await self.dashboard_node(page)

                logger.info(
                    f"{self.number_of_list} | {self.mail} | {idx} | Status node: {status}; Points: {points}")
            except Exception as error:
                logger.error(
                    f"{self.number_of_list} | {self.mail} | {idx} | Something wrong! Try again after 20 seconds.. Error: error {error}")
                await context.close()
                await asyncio.sleep(20)
                await self.get_stats()


    async def dashboard_node(self, page):
            if page.is_closed():
                return "Page is closed"
            try:
                points = page.locator('//html/body/div[1]/div[1]/div[2]/header/div/div[2]/div[2]/div[2]')
                await expect(points).to_be_visible()
            except:
                pass
            try:
                status = page.locator('//html/body/div[1]/div[1]/div[2]/main/div/div/div/div/div/div[2]/table/tbody/tr[1]/td[2]/div/span')

            except:
                try:
                    status = page.locator(
                        '//html/body/div[1]/div[1]/div[2]/main/div/div/div/div/div/div[2]/table/tbody/tr/td[2]/div/span')
                except:
                    status = page.locator(
                        '//html/body/div[1]/div[1]/div[2]/main/div/div/div/div/div/div[2]/div/span')
                    logger.warning(f"{self.number_of_list} | {self.mail} | While extension doesnt add to the list..")
                    status, points = "NON"
                    return status, points
            await expect(status).to_be_visible()
            try:
                points = await asyncio.wait_for(points.inner_text(), timeout=10)
                status = await asyncio.wait_for(status.inner_text(), timeout=10)

            except asyncio.TimeoutError:
                status, points = "Unknown"
            await page.close()
            return status, points
