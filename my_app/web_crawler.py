import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re# 정규식
from my_app import application
import os
from progress.bar import ChargingBar
#import copy

EMAIL = application.config['LOGIN_EMAIL']
PASSWORD = application.config['LOGIN_PASSWORD']

def print_test():
    print("test")

    return True

def get_chromedriver_path():
    chrome_driver_path = "chromedriver_win32/chromedriver.exe"
    app_root = ""
    app_root_split = application.root_path.split('\\')
    for i in range(len(app_root_split)-1):
        app_root += app_root_split[i] + "\\"
    chrome_driver_path = app_root + chrome_driver_path
    #print(chrome_driver_path)
    return chrome_driver_path

def get_reviews():
    # for headless chrome
    #options = webdriver.ChromeOptions()
    #options.add_argument('headless')
    #options.add_argument('window-size=1920x1080')
    #options.add_argument("disable-gpu")  

    #chrome_driver_path = "../chromedriver_win32/chromedriver.exe"
    #chrome_driver_path = "D:\HoWWWWWhy\web_crawler_trevari\chromedriver_win32\chromedriver.exe"
    chrome_driver_path = get_chromedriver_path()
    
    #driver = webdriver.Chrome(
    #    executable_path = chrome_driver_path,
    #    chrome_options=options
    #)
    driver = webdriver.Chrome(
        executable_path = chrome_driver_path
    )    

    URL = "https://trevari.co.kr"
    driver.get(URL)

    # storing the current window handle to get back to dashbord 
    main_page = driver.current_window_handle 
    #print(main_page)

    # 로그인 화면 -> 로그인
    driver.find_element_by_xpath('//*[@id="__next"]/div/header/div/div/ul/li[6]/span').click()# 로그인 클릭
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="__next"]/div/div[2]/div[1]/div/div/button').click()# 페이스북으로 로그인 클릭
    time.sleep(5)
    #print(driver.current_url)
    # changing the handles to access login page 
    #print(driver.window_handles)
    for handle in driver.window_handles: 
        if handle != main_page: 
            login_page = handle 
            
    # change the control to signin page         
    driver.switch_to.window(login_page) 
    #print(driver.current_url)
    time.sleep(1)

    driver.find_element_by_id("email").send_keys(EMAIL)
    driver.find_element_by_id("pass").send_keys(PASSWORD)
    time.sleep(0.5)
    driver.find_element_by_name("login").click()
    time.sleep(5)
    #print(driver.window_handles)


    # 독서모임 들어가기
    driver.switch_to.window(main_page) 
    driver.find_element_by_xpath('//*[@id="__next"]/div/header/div/div/ul/li[3]/a/span').click()# 독서모임 클릭
    time.sleep(5)

    # 스크롤다운 모든 독서모임 불러오기
    SCROLL_PAUSE_TIME = 3

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    #test_scroll = 1# for test

    tic = time.time()

    while True:
    #for i in range(test_scroll):# for test
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    toc = time.time() - tic
    print("It takes [", toc, "]s to get all clubs.")# 전체 스크롤 시 걸린 시간

    src = driver.page_source
    #print(driver.window_handles)
    #print(driver.current_url)
    soup = BeautifulSoup(src, 'html.parser')
    #soup = bs(html.content, "lxml") # pip install lxml, faster way

    links = soup.find_all("a", "meeting")
    #print(len(links))
    #club_id_list = []
    #club_data = dict()
    club_list = []
    p = re.compile('clubID=(.*)&')#클럽아이디 추출
    for link in links:
        club_id = p.findall(link.get('href', None))
        #club_id_list += club_id
        sub_hierarchy1 = link.find("div")

        sub_hierarchy2 = list(sub_hierarchy1.children)
        sub_hierarchy3 = list(sub_hierarchy2[1].children)
        club_title = sub_hierarchy3[0].contents

        club_list.append({"id": club_id[0], "title": club_title[0]})
        
        #club_data["id"] = club_id[0]
        #club_data["title"] = club_title[0]
        
        #club_id_list.append(copy.deepcopy(club_data))
        #print(link.get('href', None))

    
    #print(club_list)
    
    #print(len(club_list))
    club_id_list = []
    club_title_list = []
    for club in club_list:
        if club["title"] not in club_title_list:
            club_id_list.append(club["id"])
            club_title_list.append(club["title"])

    #print(len(club_id_list))
    club_id_list = list(set(club_id_list))# 클럽 중복 제거
    print("Total Club Count:", len(club_id_list))

    #f = open("clubs.txt", 'w', encoding='UTF8')
    #for club in club_id_list:
    #    data = club + '\n'
    #    f.write(data)
    #f.close()

    # 클럽 하나하나 들어가기
    URL_each_meeting = URL + "/meetings/show?clubID="
    #for club in club_id_list:
    #    print(club)

    #print(URL_each_meeting+club_id_list[0])

    review_data = {}

    # 이 숫자보다 작은 시즌만 불러오기
    # 예: 1909 -> 1909 이전 시즌만 불러오기
    season_start = 1906# 1001 이후 시즌부터 불러오기
    season_end = 1908# 1907 이전 시즌까지 불러오기

    
    f = open("error_log.txt", 'w')

    #test_num_club = 2
    #bar = ChargingBar('Processing', max=test_num_club)# for test
    #for i in range(test_num_club):# for test
    #    driver.get(URL_each_meeting+club_id_list[i])

    bar = ChargingBar('Processing', max=len(club_id_list))  

    for club_id in club_id_list:
        driver.get(URL_each_meeting+club_id)
        time.sleep(5)
        cur_page_src = driver.page_source
        
        cur_page_soup = BeautifulSoup(cur_page_src, 'html.parser')

        club_title = cur_page_soup.find("h1")
        print("\n\n클럽명:", club_title.text)

        books = list(cur_page_soup.find_all("button", "dropdown-item"))# 이 클럽의 지난 책 리스트 불러오기
        seasons = cur_page_soup.find_all("h6", "dropdown-header")# 시즌 불러오기
        season_list = []
        for season in seasons:
            season_list.append(int(season.text.split(" ")[0]))
        #print(season_list)
        
        filtered_season = list(filter(lambda x: season_start < x < season_end, season_list))
        if len(filtered_season)>0:
            index_start = season_list.index(filtered_season[0])
            index_end = season_list.index(filtered_season[-1])
            #book_list = [book.text for book in books]

            #filtered_books = books[index_start*4:(index_end+1)*4]
            #print(filtered_books)

        #print(len(books))
        # print(len(buttons_book))

            click = True
            #for i, book in enumerate(books):  
            for i in range(index_start*4,(index_end+1)*4):   
                book = books[i]
                #print(book)

                if click:
                    driver.find_element_by_css_selector('div.dropdown > button').click()# 드롭다운 버튼 클릭
                    time.sleep(3)    
                    buttons_book = driver.find_elements_by_css_selector('button.dropdown-item')# 이 클럽의 지난 책 리스트 각각의 버튼 불러오기
                    #print(len(buttons_book))
                    time.sleep(1)   
                    click = False
                if len(book.text) > 0:
                    book_title = re.findall('\[(.*)\]',str(book))# 책 이름만 추출
                    book_title = book_title[0]
                    #print("읽을거리:", book_title)
                    buttons_book[i].click()
                    time.sleep(5)
                    click = True
                    cur_page_src = driver.page_source
                    cur_page_soup = BeautifulSoup(cur_page_src, 'html.parser')     
                    try:
                        review_links = cur_page_soup.find("div", "bookreview-list").find_all("a")
                        # key 존재 여부 확인
                        if book_title not in review_data.keys(): 
                            review_data[book_title]=[]
                        for review_link in review_links:
                            if review_link.text.strip() != "첨부 파일 다운로드":
                                URL_cur_review = URL+str(review_link.get('href', None))
                                #print('링크:', URL_cur_review)
                                review_title = review_link.find("div", "bookreview-title")
                                #print("독후감 제목:", review_title.text) 
                                review_title_text = review_title.text
                                if len(review_title_text)==0:
                                    review_title_text = "No Title"

                                review_data[book_title].append({"url": URL_cur_review, "title": review_title_text})
                                #driver.get(URL+str(review_link.get('href', None)))
                                #time.sleep(3)
                                #review_page_src = driver.page_source
                                #review_page_soup = BeautifulSoup(review_page_src, 'html.parser')
                                #a = review_page_soup.find("div", "bookreview-page-content").select("div")[1]
                                #print(a.text)
                            #else:
                            #    print("첨부 파일 링크입니다.")
                        #print('\n')
                        if len(review_data[book_title])==0:
                            waiting_book_title = review_data.pop("book_title", None) 
                            #print(waiting_book_title, "에는 아직 제출된 독후감이 없습니다.")

                    except AttributeError:
                        print("AttributeError\n")
                        print(driver.current_url)
                        print("\n")
                        f.write("AttributeError: ")
                        f.write(driver.current_url)
                        f.write('\n')
                        driver.back()# 뒤로 가기
                        time.sleep(5)  


        bar.next()
    bar.finish()
    driver.close()
    f.close()
    return review_data