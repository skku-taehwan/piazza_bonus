###

from collections import defaultdict as dic
import random
import sys
import time

import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

###


def parsingGoods(soup: bs, messageParse: str, studentParse: str) -> str:
    endorseMessage = soup.select(messageParse)
    if endorseMessage:
        endorseStudent = soup.select(studentParse)
        studentName = endorseStudent[0].contents[0].text.strip()
        return studentName


def parsingGoodDiscuss(soup: bs, disccussParse: str, discuss: str, studentParse: str) -> str:
    clarifyingDiscussions = soup.select(disccussParse)
    if clarifyingDiscussions:
        for endorseDiscussion in clarifyingDiscussions:
            discussionAnswer = \
                endorseDiscussion.select(discuss)
            if discussionAnswer:
                studentAnswer = endorseDiscussion.select_one(studentParse)
                studentName = studentAnswer.text.strip()
                return studentName


def main():
    start_time = time.time()

    if len(sys.argv) != 6:
        print("RUN python3 main.py [piazza_class_URL] [start_page_number] \
            [end_page_number] [piazza_ID] [piazza_PASSWD]", file=sys.stderr)
        return

    # Config
    df = dic(list)
    ser = Service("./chromedriver")
    option = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=ser, options=option)

    # Login
    url, start, end, id, passwd = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
    driver.get("{url}?cid={number}".format(url=url, number=start))
    driver.find_element(By.ID, "email_field").send_keys(id)
    driver.find_element(By.ID, "password_field").send_keys(passwd)
    driver.find_element(By.ID, "modal_login_button").click()

    # Page start to end
    for i in range(start, end + 1):
        try:
            # get HTML
            driver.implicitly_wait(300)
            driver.get("{url}?cid={number}".format(url=url, number=i))
            driver.implicitly_wait(300)
            time.sleep(random.randrange(3, 5))
            html = driver.page_source
            driver.implicitly_wait(300)
            soup = bs(html, 'html.parser')

            # parsing good Question
            question = "div#question > div#view_quesiton_note > div.post_region_message_wrapper > \
            div#endorse_text > div > span.endorse_message"
            student = "div#question > div#view_question_note_bar > div.post_region_actions_meta > div"
            goodQuestion = parsingGoods(soup, question, student)
            if goodQuestion:
                df[goodQuestion].append(i)

            # parsing good Note
            note = "div#note > div#view_quesiton_note > div.post_region_message_wrapper > div#endorse_text > \
            div > span.endorse_message"
            student = "div#note > div#view_question_note_bar > div.post_region_actions_meta > div"
            goodNote = parsingGoods(soup, note, student)
            if goodNote:
                df[goodNote].append(i)

            # parsing good Answer
            Answer = "div#member_answer > div > div.post_region_content.view_mode > \
                div.post_region_message_wrapper > div > div > span.endorse_message"
            student = "div#member_answer > div > div.post_region_actions.view_mode > div > div"
            goodAnswer = parsingGoods(soup, Answer, student)
            if goodAnswer:
                df[goodAnswer].append(i)
            driver.implicitly_wait(1000)

            # parsing good Discussion
            discussions = "div#clarifying_discussion > div[data-pats=followups] > div[data-pats=followup]"
            discussion = "div.post_region_message.endorse.show"
            student = "div[data-pats=original_post] > div > a > div"
            goodDiscussion = parsingGoodDiscuss(soup, discussions, discussion, student)
            if goodDiscussion:
                df[goodDiscussion].append(i)

        except Exception:
            continue
        print(df)

    # data to CSV file
    df = {x: df[x] for x in sorted(df.keys())}
    data = pd.DataFrame(list(df.items()), columns=["StudentName", "BonusId"])
    data['Count'] = list(len(x) for x in df.values())
    data = data[['StudentName', 'Count', 'BonusId']]
    data.to_csv("output.csv", mode='w', sep=',')

    # time
    end_time = time.time()
    print("time", end_time - start_time, "seconds")


if __name__ == "__main__":
    main()
