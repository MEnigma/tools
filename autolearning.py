"""
PROJECT : autolearning
AUTHER : MARK
DATE : 2019/12/09
IDE : Pycharm
"""
import time, re
from selenium.webdriver import Chrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class AutoReader:
    """
    自动阅读
    """
    driverPath = 'chromedriver.exe'
    remote_path = "https://www.qingshuxuetang.com/Degree"
    account = "dlgy20190347"
    passwd = "123456"
    driver: Chrome = None

    def connect(self, url=None):
        if url is None:
            url = self.remote_path
        if self.driver is None:
            self.driver = Chrome(self.driverPath)
        self.driver.get(url)

    def login(self, account: str = None, passwd: str = None):
        if account is None:
            account = self.account
        if passwd is None:
            passwd = self.passwd

        self._waitForElement((By.ID, 'login'))
        self.driver.find_element_by_id('login').click()
        self._waitForElement((By.ID, 'uname'))
        self.driver.find_element_by_id('uname').send_keys(self.account)
        self.driver.find_element_by_id('pwd').send_keys(self.passwd)
        self.driver.find_element_by_id("loginBypwdBtn").click()

    def getListenList(self) -> list:
        if self._waitForElement((By.CLASS_NAME, 'sdudy_btn')):
            _lessons = self.driver.find_elements_by_xpath("//div[@class='sdudy_btn']/a")
            lessUrls = [a.get_attribute("href") for a in _lessons]
            for les in lessUrls:
                print(les)
            return lessUrls
        else:
            print(">>>  获取课程列表失败")
            return []

    def readLessons(self, lessurls: list):
        """
        开始阅读
        :param lessurls:
        :return:
        """
        # url = lessurls[0]
        print("开始阅读课程 :{}个".format(len(lessurls)))
        for url in lessurls:
            self.driver.get(url)
            self._waitForElement((By.ID, 'startStudy'))
            a_s = self.driver.find_elements_by_xpath('//li/a')
            targets = []
            for a in a_s:
                aid = str(a.get_attribute('id'))
                if 'kcjs' in aid:
                    try:
                        spans = a.find_elements_by_xpath('span')
                        if len(spans) >= 2:
                            read_length = spans[1].get_attribute("innerText")
                            if "共" in read_length:
                                total_t_str = read_length.split("共")[1]
                                if self.spanTimeToAccessRead(total_t_str):
                                    print("该文已读({}): {} ".format(total_t_str,spans[0].get_attribute("innerText")))
                                    continue

                            print("该文未满足时长 :{}".format(total_t_str))
                    except Exception as e:
                        print("验证是否已读 错误 {}".format(e))
                        pass

                    targets.append(aid)
                else:
                    pass
            for kid in targets:
                kurl = str(url).replace("CourseStudy", "CourseShow") + '&cw_nodeId=' + kid
                print("课程: {}".format(kurl))
                self.driver.get(kurl)
                print("等待加载...")
                if not self._waitForElement((By.CLASS_NAME, 'player-header')):
                    print("课程内无标识标签")
                try:
                    self._waitForElement((By.TAG_NAME, "video"), time=3)
                    time.sleep(2)
                    video_div = self.driver.find_element_by_xpath("//div[@id='playerContainer']/div/video")
                    if video_div is not None:
                        print("准备点击播放")
                        video_div.click()
                    else:
                        print("未找到视频组件")
                    #
                    # hasloading = self.driver.find_elements_by_xpath('//div/canvas')
                    # if len(hasloading) > 0:
                    #     video = self.driver.find_element_by_xpath('//div/div/video')
                    #     if video is not None:
                    #         video.click()

                except Exception as e:
                    print("查找播放按钮错误 :{}".format(e))
                    pass
                print("开始读课程")
                time.sleep(15 * 60)

    # ------   private    -------
    def _waitForElement(self, locator: tuple, time: int = 30):
        try:
            WebDriverWait(self.driver, time).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except:
            return False

    def spanTimeToAccessRead(self, readtime):
        times = re.findall(r'\d+[分,钟,秒]?', readtime)
        minutes = 0
        seconds = 0
        total_seconds = 0
        try:
            if len(times) > 1:
                minutes = int(re.findall(r'\d+', times[0])[0])
                seconds = int(re.findall(r'\d+', times[1])[0])
            else:
                seconds = int(re.findall(r'\d+', times[0])[0])
            total_seconds = minutes * 60 + seconds

        except Exception as e:
            total_seconds = 0
        return total_seconds >= 15 * 60


if __name__ == "__main__":
    reader = AutoReader()
    reader.connect()
    reader.login()
    reader.readLessons(reader.getListenList())
    input()
