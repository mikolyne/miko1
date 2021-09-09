from selenium import webdriver
import time
import re 
import pandas as pd
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=r"C:\Users\fmiko\other_tool\chromedriver.exe",options=options)
driver.get('https://www.81100.jp/kanto/search/index/?pref=13-14&job=010-011-008-006-007-009-999&hwage=1200&icon=027-031')
#バックグラウンド設定をし、サイトへアクセスする。

time.sleep(3)

wk_num , jikyu , station , wk_time , wk_time_list = [] , [] , [] , [] , []
elems_tds = driver.find_elements_by_tag_name('td')
#サイトから、表の情報を取得する。
time.sleep(3)

h = 0
for td in elems_tds :
    hmod7 = h%7
    if hmod7 == 0:
        text = td.text
        wk_num.append('https://www.81100.jp/kanto/detail/{}/?backto=1 '.format(text[:text.find('\n')]))
    if hmod7 == 2:
        jikyu.append(int(td.text.replace('円','').replace(',','').replace(' ','')))
    if hmod7 == 4:
        station.append(td.text)
    if hmod7 == 5: 
        wk_time_elem = td.text
        wk_time.append(wk_time_elem.replace('\n',''))
        wk_time_list.append([int(i) for i in re.findall(r'\d+', re.sub('（[0-9]）','',wk_time_elem))])
    h += 1
else:
    h = 0
driver.close()
#url、時給、最寄駅、時間など簡単な加工できる情報をリストに保存。


work_time_list , nikkyu = [],[]
for wk_list , jikyu_list in zip(wk_time_list,jikyu):
    pre_work_times,pre_nikkyu_list= [],[]

    for i in range(int(len(wk_list)/4)):
        
        start = wk_list[0 + 4*i] + (wk_list[1 + 4*i])/60
        end = wk_list[2 + 4*i] + (wk_list[3 + 4*i])/60
        if start >= end :
            end+= 24
        work_time = end - start
        if work_time > 6:
            work_time+= -1
            end += -1

        if start <= 22:
            if start <5:
                ext = 5 - start
            elif end <=22:
                ext = 0
            elif end < 29:
                ext = 7
            else:
                ext = end - 22
        else:
            if end <= 29:
                ext = 29 - start
            else:
                ext = end - start

        pre_work_times.append(work_time)
        pre_nikkyu_list.append(int((work_time + ext/4) * jikyu_list))
        
    else:
        work_times = ' '.join([str(k) for k in pre_work_times ])
        work_time_list.append(work_times)
        nikkyu_list = ' '.join([str(k) for k in pre_nikkyu_list])
        nikkyu.append(nikkyu_list)
'''
サイト上の勤務時間の情報で、（1）9:00～18:00（2）18:00～27:00の時間に対し、
それぞれの日給が異なるため、このことに注意し日給のリストを作る。
'''


df = pd.DataFrame({'wk_num':wk_num , 'jikyu':jikyu , 'station':station , 'wk_time':wk_time , 'work_time_list':work_time_list, 'nikkyu':nikkyu})
df.to_csv(r'C:\Users\fmiko\mcode\git_dir\tool_box\data1.csv')
#各リストを、pandasのDataFrameに保存し、csvファイルに出力する。