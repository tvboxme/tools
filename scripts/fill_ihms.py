from selenium.common.exceptions import NoSuchElementException,ElementNotVisibleException,UnexpectedAlertPresentException
import traceback
import time
def modify_start_end(date_tuple):
    start_date =  time.localtime(time.mktime((date_tuple[0],date_tuple[1],date_tuple[2],9,0,0,0,0,0)))
    dif_days = 0
    if start_date.tm_wday >= 5:
        dif_days = start_date.tm_wday - 4
    start_sec = time.mktime((date_tuple[0],date_tuple[1],date_tuple[2],9,0,0,0,0,0)) - 24*60*60*dif_days
    start_local = time.localtime(start_sec)
    date_tuple = (start_local.tm_year, start_local.tm_mon, start_local.tm_mday)
    return date_tuple
def ihms(browser=None, detail='', end_date_tuple=None, username='', pw='' , start_date_tuple=None):
    # Need wait function for page jump functions.
    from selenium import webdriver
    import re
    start_date_tuple= modify_start_end(start_date_tuple)
    end_date_tuple= modify_start_end(end_date_tuple)
    if browser==None:
        browser = webdriver.Firefox()
        browser.get("http://bjdws.synnex.org/ihms/thirdpart/login.jsp")
    import  time
    time.sleep(2)
    login_name = browser.find_element_by_name("j_username")
    login_name.send_keys(username)

    login_pwd = browser.find_element_by_name('j_password')
    login_pwd.send_keys(pw)
    login_btn = browser.find_element_by_id("loginBtn")
    login_btn.click()

    timesheet = browser.find_element_by_class_name('iconTopMenu')
    timesheet.click()

    mytime=browser.find_element_by_link_text('myTimeSheet')
    mytime.click()

    job_dict = {'general support':'438258'}

    def apply():
        try:
            browser.execute_script('getAddFJDiv()')
        except:
            pass
        time.sleep(0.1)
        check_job=browser.find_element_by_xpath('//input[@value="%s"]' % job_dict['general support'])
        check_job.click()
        browser.execute_script('addFJ()')
        #can only execute one as page will jump
        # addFJ= browser.find_element_by_xpath('//input[@onclick="addFJ();"]')
        # addFJ.click()
        time.sleep(0.1)
        job= browser.find_element_by_id(job_dict['general support'])
        job_type = job.find_element_by_name('jobType')
        while True:
            try:
                job_type.find_element_by_xpath("//option[@value=99]").click()
                break
            except:
                time.sleep(0.2)
                continue
        task_type = job.find_element_by_name('taskType')
        while True:
            try:
                task_type.find_element_by_xpath("//option[@value=115]").click()
                break
            except:
                time.sleep(0.2)
                continue
        hour_fj= job.find_element_by_name('hour_fj')
        hour_fj.send_keys('8')
        detail_fj = job.find_element_by_name('detail_fj')
        detail_fj.send_keys(detail)
        browser.execute_script('tsSubmitAndApply()')
        appy_btn = browser.find_element_by_xpath('//input[@onclick="tsSubmitAndApply();"]')
        appy_btn.click()
        time.sleep(2)
    def jump_date(date_tuple):

        calender = browser.find_element_by_id('anchor1x')
        calender.click()
        browser.execute_script('CP_tmpReturnFunction%s' % str(date_tuple))
        browser.execute_script('CP_hideCalendar("1")')
        browser.execute_script('goDate()')
        print 'browser should jump to date %s' % str(date_tuple)
        #exit()
        time.sleep(2)
    if start_date_tuple is not None:
        jump_date(start_date_tuple)
        try:
            fj_id=browser.find_element_by_name('id_fj')
        except:
            apply()
    if end_date_tuple is not None:
        jump_date(end_date_tuple)
    while True:
        try:
            fj_id=browser.find_element_by_name('id_fj')
            start_day_box = browser.find_element_by_name('date')
            print start_day_box.get_attribute('value')+' is already filled'
            #if start date is specified then check until the start date
            if start_date_tuple is None:
                break
            else:
                start_day_box = browser.find_element_by_name('date')
                current_date = start_day_box.get_attribute('value')
                current_time_list = current_date.split('/')
                year = current_time_list.pop()
                current_time_list.insert(0,year)
                current_time_list = map(int, current_time_list)
                print 'current time is %s' % current_time_list
                if tuple(current_time_list) == start_date_tuple:
                    print 'current page reached specified start date %s' % str(start_date_tuple)
                    break
        except (NoSuchElementException, ElementNotVisibleException,UnexpectedAlertPresentException) as e:
            apply()
        #browser.execute_script("goDate2('previous')") # execute script will not block page
        print 'go previous day'
        browser.find_element_by_xpath('//input[@value="Previous Day"]').click()
        time.sleep(1)
    if end_date_tuple is None:
        browser.execute_script("goToday()")
        def getmon():
            start_day_box = browser.find_element_by_name('date')
            r=re.search('^(\d+)/', start_day_box.get_attribute('value'))
            month = r.group(1)
            return month
        corrent_mon = getmon()
        while True:
            browser.execute_script("goDate2('next')")
            if getmon()==corrent_mon:
                try:
                    fj_id=browser.find_element_by_name('id_fj')
                    start_day_box = browser.find_element_by_name('date')
                    print start_day_box.get_attribute('value')+' is already filled'
                    break
                except (NoSuchElementException, ElementNotVisibleException,UnexpectedAlertPresentException) as e:
                    print traceback.print_exc()
                    print e.stacktrace
                    apply()
            else:
                break
    return browser

