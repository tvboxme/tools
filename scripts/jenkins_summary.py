import json
import sys
import urllib,urllib2
import time
import os
import re
#swengineering@synnex.com
#${JELLY_SCRIPT,template="__${JOB_NAME}${BUILD_NUMBER}"}
def get_status(jobName, current_time, time_period = 24*60*60, debug=False):
    summary_hour = 5
    summary_time_mode = 'PM'
    ##jenkinsUrl= os.environ["JENKINS_URL"]+'job/'
    #print jenkinsUrl
    if debug:
        os.environ["JOB_URL"] = 'http://hyve-rt.synnex.org/job'
    jenkinsUrl = os.environ["JOB_URL"]
    while not jenkinsUrl.endswith('job'):
        jenkinsUrl = os.path.dirname(jenkinsUrl)
    jenkinsUrl_display = jenkinsUrl
    jenkinsUrl=jenkinsUrl.replace('hyve-rt.synnex.org', '127.0.0.1:8080')
    today_status = []
    latest_build_status = None
    last_day = None
    try:
        print jenkinsUrl_display+'/'+jobName
        job_page = urllib.urlopen(jenkinsUrl+'/'+jobName).read()

        #matches = re.findall(r"/job/"+jobName+r'/(\d+)/">(.{4,7}),(.{15,19}M)',job_page)
        matches = re.findall(r"/job/"+jobName+r'/(\d+)/">(.{4,7},.{15,19}M)',job_page)
        max_build_id = 0
        for i in matches:
            build_id = i[0]
            
            build_time = i[1]
            build_time_struct = time.strptime(build_time,'%b %d, %Y %I:%M:%S %p')
            jenkinsStream   = urllib.urlopen( jenkinsUrl +'/'+ jobName + "/" + build_id + "/api/json" )
            buildStatusJson = json.load( jenkinsStream )
            if int(build_id) > int(max_build_id):

                max_build_id = build_id
                latest_build_status = {'job':jobName,'result':buildStatusJson.pop("result",'FAILURE'), 'build_id': max_build_id,
                                     'build time': '%s' % (build_time) ,
                                     'link': jenkinsUrl_display+'/'+jobName + '/' + max_build_id
                                     }
            build_sec = time.mktime(build_time_struct)
            try:
                current_time_struct = time.strptime(current_time, '%a %b %d %H:%M:%S %Y')
                current_time_sec = time.mktime(current_time_struct)
            except:
                print 'using time.time() as base time'
                current_time_sec = time.time()
            if build_sec >= current_time_sec - (time_period):
                #print 'reading build ', build_id, ' of job', jobName
                #print jenkinsUrl +'/'+ jobName + "/" + build_id + "/api/json"
                change_url = jenkinsUrl+'/'+jobName + '/' + build_id + '/changes'
                changes_page   = urllib.urlopen(change_url).read()
                changes = re.findall(r'<li>([^(]+).{1,5}\<a href=([^>]+)(\w{40}).+\3', changes_page)
                new_changes = []
                for change in changes:
                    commit_number = change[2]
                    commit_author = re.findall( r'%s\n\s*by <a href=[^<>]+>([^/<>]*)</a>' % commit_number, changes_page)
                    temp_change = list(change)
                    temp_change.extend(commit_author)
                    new_changes.append(temp_change)
                today_status.append({'job':jobName,'result':buildStatusJson.pop("result",'FAILURE'), 'build_id': build_id,
                                     'build time': '%s' % (build_time),
                                     'changes': new_changes
                                     })
        print jenkinsUrl_display+'/'+jobName + '/' + latest_build_status['build_id'] + '/changes'
        return today_status, latest_build_status
    except urllib2.HTTPError, e:
        print e
        print "URL Error: " + str(e.code)
        print "      (job name [" + jobName + "] probably wrong)"
        sys.exit(2)

oneday = 24*60*60
time_period = oneday
if time_period/oneday ==1:
    time_name = 'today'
else:
    time_name = 'of last %s days' % (time_period/oneday)
debug = False
if debug:
    jenkins_jobs=["hyve-stress","hyve-bom","hyve-testdash","hyve-stress-burnin"]
    os.environ['JENKINS_HOME'] = '/home/jessiex'
    os.environ["JOB_NAME"] = 'summary'
    os.environ["BUILD_NUMBER"] = '250'
else:
    jenkins_jobs=["hyve-stress","hyve-bom","hyve-testdash","hyve-stress-burnin"]
    print "os.environ['JENKINS_HOME']=",os.environ['JENKINS_HOME']
    print 'os.environ["JOB_NAME"]=',os.environ["JOB_NAME"]
    print 'os.environ["BUILD_NUMBER"]',os.environ["BUILD_NUMBER"]
emailPath=os.environ['JENKINS_HOME']+'/email-templates'
if os.path.isdir(emailPath) == False:
    os.mkdir(emailPath)
else:
    for template in os.listdir(emailPath):
        if template.startswith('__summary'):
            os.remove(os.path.join(emailPath,template))
jelly_path = os.path.join(emailPath, '__'+os.environ["JOB_NAME"]+os.environ["BUILD_NUMBER"]+".jelly")
#jelly_path = '__summary10.jelly'
current_time = time.asctime()
#current_time = current_time.replace('31','30')
w = open(jelly_path, 'w')
w.write('	<html>\
	<body>')
time_simple = re.search('[^ ]{1,4}\s[^ ]{1,4}\s{1,2}\d+',current_time)
if time_simple != None:

    w.write(('<tr><td><h2><font color="#0000FF">Build Status Summary (%s) </font></h2></td></tr>')% time_simple.group())
else:
    w.write(('<tr><td><h2><font color="#0000FF">Build Status Summary (%s) </font></h2></td></tr>')% current_time)
tr_style = 'style="line-height:200%"'
td_style_small = 'style="width:140px"  align="center"'
td_style = 'style="width:160px"  align="center"'
td_style_large = 'style="width:200px"  align="center"'
w.write('<table border="1" style="table-layout:fixed">')
w.write('<tr %s><td %s>Project Name</td><td %s>Build Amount %s</td><td %s>Last Build Result</td><td %s>Last Build Time</td>\
        <td align="center">Changes %s</td></tr>'% (tr_style, td_style_small ,td_style, time_name,td_style, td_style,time_name))
print 'Reading builds within 24 hours before %s' % current_time
is_fix_change = True
job_status_list =[]
for job in jenkins_jobs:
    temp_status =get_status(job, current_time, time_period, debug)
    job_status_list.append(temp_status)
    status = temp_status[0]
    if len(status) != 0:
        for i in status:
            for commit in i['changes']:

                comment = commit[0]
                if len(comment) > 20:
                    is_fix_change = False
                    break

if is_fix_change:
    td_style_changes = 'style="width:200px" align="center"'
else:
    td_style_changes = 'align="left"'
for temp_status in job_status_list:

    status = temp_status[0]
    latest_status = temp_status[1]
    w.write((r'	<tr %s><td %s><b><font color="#0"> %s') % (tr_style, td_style, latest_status['job']))
    w.write(' </font></b></td>')
    status = sorted(status, key=lambda d:d['build time'][1])
    #write build amount
    if len(status) == 0:
        w.write(r'<td %s> None </td>' % td_style)
    else:
        w.write(r'<td %s> %s</td>' % (td_style_small, len(status)))
    #Write build status
    if latest_status != None and latest_status['result']!=None:
        i = latest_status
        i['link'] = i['link'].replace(':8080','')
        if "FAIL" in i['result'].upper().strip():
            w.write(r'<td %s><a href="%s"><font color="#FF0000">%s</font></a></td>' % (td_style, i['link'], i['result']))
        elif 'UNSTABLE' in i['result'].upper().strip():
            w.write(r'<td %s><font color="#FFCC00"><a href="%s">%s</a></font></td>' % (td_style, i['link'], i['result']))
        else:
            w.write(r'<td %s><a href="%s">%s</a></td>' % (td_style, i['link'], i['result']))
        w.write(r'<td %s>%s</td>' % (td_style_large, i['build time']))
    else:
        #w.write(r'<td %s><font color="#FFCC00">None</font></td>' % td_style)
        #w.write(r'<td %s><font color="#FFCC00">None</font></td>' % td_style)
        w.write(r'<td %s>None</td>' % td_style)
        w.write(r'<td %s>None</td>' % td_style)
    #no_swap = lambda line:line if len(line)<22 else line[:20]+'...'
    #write changes
    if len(status) == 0:
        w.write(r'<td %s> None </td>' % td_style_changes.replace('left', 'center') )
    else:
        is_no_change = True
        td_style_changes = td_style_changes.replace('left', 'center')
        for i in status:
            for commit in i['changes']:
                if commit[2]!='':
                    td_style_changes = td_style_changes.replace('center', 'left')
        w.write(r'<td %s>  ' % td_style_changes )
        all_change = ''
        author_changes = {}
        author_same_time_commits = []
        print status
        for i in status:

            if len( i['changes']) > 0:
                author = i['changes'][0][3]

                if '@' in author:
                    author = author[:author.find('@')]
                #w.write('<dd>%s by %s</dd>' % (i['build time'], author))
                author_commits = author_changes.pop(author, {})
                #print author
                build_time_struct = time.strptime(i['build time'],'%b %d, %Y %I:%M:%S %p')
                day = '%s-%s-%s'%(build_time_struct.tm_year , build_time_struct.tm_mon , build_time_struct.tm_mday)
                hour_time = '%s:%s:%s'%(build_time_struct.tm_hour, build_time_struct.tm_min , build_time_struct.tm_sec)
                author_day = author_commits.pop(day,{})
                author_same_time_commits = author_day.pop(hour_time,[])
            for commit in i['changes']:
                #w.write('<li><a href="%s%s">%s</a></li>' % (commit[1].replace("'",''), commit[2], commit[0].replace(r'&nbsp;','')))
                author_same_time_commits.append('<a href="%s%s">%s</a>' % (commit[1].replace("'",''), commit[2], commit[0].replace(r'&nbsp;','')))
                all_change = all_change + commit[0]
            if author_same_time_commits != []:
                author_day[hour_time] = author_same_time_commits
                author_commits[day] = author_day
                author_changes[author] = author_commits
            else:
                try:
                    print 'There is empty build information for %s at %s %s, build id %s' % (author,author_day,author_same_time_commits, i['build_id'])
                except:
                    print 'There is empty build information build id %s.' % i['build_id']
        #print author_changes
        for author in author_changes.keys():
            w.write('<li>%s</li>' % (author))
            if time_period > oneday:
                for day in author_changes[author].keys():
                    w.write('<ul style="margin:0px"><li>%s</li></ul>' % day)
                    for hour_time in  author_changes[author][day].keys():
                        for commit in author_changes[author][day][hour_time]:
                            w.write('<ul style="margin:0px"><ul style="margin-top:0px"><li>%s</li></ul></ul>' % commit)
            else:
                for day in author_changes[author].keys():
                    for hour_time in author_changes[author][day].keys():
                        w.write('<ul style="margin:0px"><li>%s</li></ul>' % hour_time)
                        for commit in author_changes[author][day][hour_time]:
                            w.write('<ul style="margin:0px"><ul style="margin-top:0px"><li>%s</li></ul></ul>' % commit)

        if all_change.strip() == '':
            w.write("None")
        w.write('</td>')
    w.write('</tr>')
w.write('</table></body></html>')
w.close()
