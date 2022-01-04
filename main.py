###

import random
import sys
import time

import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

###


def appendNameToDic(studentName: str, i: int, df: dict) -> dict:
    if studentName in df.keys():
        df[studentName].append(i)
    else:
        df[studentName] = [i]
    return df


def main():
    start_time = time.time()

    if len(sys.argv) != 6:
        print("RUN python3 main.py [piazza_class_URL] [start_page_number] \
            [end_page_number] [piazza_ID] [piazza_PASSWD]", file=sys.stderr)
        return
    # Config
    df = dict()
    ser = Service("./chromedriver")
    option = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=ser, options=option)

    # Login
    url, start, end, id, passwd = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
    driver.get("{url}?cid={number}".format(url=url, number=1))
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
            endorseQuestion = soup.select("div#question > div#view_quesiton_note > \
            div.post_region_message_wrapper > div#endorse_text > \
            div > span.endorse_message")
            if endorseQuestion:
                endorseStudent = soup.select("div#question > \
                div#view_question_note_bar > \
                div.post_region_actions_meta > div")
                studentName = endorseStudent[0].contents[0].text.strip()
                df = appendNameToDic(studentName, i, df)
            else:
                print("no good question")
            # parsing good Note
            endorseNote = soup.select("div#note > div#view_quesiton_note > \
            div.post_region_message_wrapper > div#endorse_text > \
            div > span.endorse_message")
            if endorseNote:
                endorseStudent = soup.select("div#note > div#view_question_note_bar > \
                div.post_region_actions_meta > div")
                studentName = endorseStudent[0].contents[0].text.strip()
                df = appendNameToDic(studentName, i, df)
            else:
                print("no good Note")

            # parsing good Answer
            endorseAnswer = soup.select("div#member_answer > div > \
            div.post_region_content.view_mode > \
                div.post_region_message_wrapper > \
                    div > div > span.endorse_message")
            if endorseAnswer:
                studentAnswer = soup.select("div#member_answer > div > \
                div.post_region_actions.view_mode > div > div")
                studentName = studentAnswer[0].contents[0].text.strip()
                df = appendNameToDic(studentName, i, df)
            else:
                print("no good answer")
            driver.implicitly_wait(1000)

            # parsing good Discussion
            clarifyingDiscussions = soup.select("div#clarifying_discussion > \
            div[data-pats=followups] > div[data-pats=followup]")
            if clarifyingDiscussions:
                for endorseDiscussion in clarifyingDiscussions:
                    discussionAnswer = \
                        endorseDiscussion.select("\
                            div.post_region_message.endorse.show")
                    if discussionAnswer:
                        studentAnswer = endorseDiscussion.select_one("\
                            div[data-pats=original_post] > div > a > div")
                        studentName = studentAnswer.text.strip()
                        df = appendNameToDic(studentName, i, df)
                    else:
                        print("no good discussion")
            else:
                print("no discussion")
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
