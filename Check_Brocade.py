#!/usr/bin/env python
#_*_ coding:utf-8 _*_
'''
Created on 2017年5月12日

@author: Alex
@version: v 1.0.0.1
@license: GPL v2
插件用于监控博科系列的光钎交换机
建议在交换机上创建一个普通用户的权限进行监控，创建命令如下
userconfig --add 用户名  -r user -p 密码

可监控的项目如下，通过-参数指定
UPTIME  监控设备运行的天数，默认小于1天进行告警，执行的命令为：uptime
                        通过--uptime-crit执行报警阀值
CPU     监控设备的CPU利用率，默认取15分钟的平均值，执行的命令为：uptime
        --cpu-warn  警告阀值
        --cpu-crit  严重阀值
FAN     监控设备风扇状态，执行的命令为：fanshow
TEMP    监控设备的温度传感状态，执行的命令为：tempshow
PS      监控设备的电源状态，执行的命令为：psshow
PORTOnline 端口使用状态，检测端口Online数量，执行的命令为：switchshow
        --PORTOnline-crit  指定现在使用的接口数量，如数量不一致报警
Monitor 监控设备的硬件状态，通过执行switchstatusshow命令查看HEALTHY数量
        --Monitor-HEALTHY  设备HEALTHY正常数量，如不一至报警
PORTERR 监控端口具体错误状态 ，执行的命令 porterrshow
        --PORTERR-CRC-warn    CRC校验失败的阀值
        --PORTERR-C3-warn     disc C3  丢包数量阀值
        --PORTERR-Link-fail    链路失败阀值
'''
if __name__ != '__main__':
    print "程序不可被调用，这是主程序"
    exit(1)
    
import telnetlib,optparse,sys,re 


optp = optparse.OptionParser()
optp.add_option('-H', help=u'博科交换机设备地址', dest='host',metavar='10.0.0.1')
optp.add_option('-u', help=u'设备连接用户名、建议使用只读用户', dest='user', metavar='admin')
optp.add_option('-p', help=u'连接用户的用户密码',default=23, dest='passwd', metavar='password')
optp.add_option('-P', help=u'设定端Telnet连接端口,默认为23', dest='port', metavar='23')
optp.add_option('-o', help=u'监控项目:UPTIME|CPU|FAN|TEMP|PS|PORTOnline|Monitor|PORTERR', dest='option', metavar='CPU')
optp.add_option('--uptime-crit', help=u'设备启动时间小于指定天报警，默认1天',default=1,dest='uptime_crit', metavar='1')
optp.add_option('--cpu-warn', help=u'cpu告警阀值，默认50%', default=50,dest='cpu_warn', metavar='50')
optp.add_option('--cpu-crit', help=u'cpu严重阀值，默认70%', default=70,dest='cpu_crit', metavar='70')
optp.add_option('--PORTOnline-crit', help=u'Online接口的数量,默认0', default=0,dest='Online_crit', metavar='number')
optp.add_option('--Monitor-HEALTHY', help=u'各硬件状态使用switchstatusshow命令查看HEALTHY的数量,默认8', default=8,dest='Monitor_crit', metavar='number')
optp.add_option('--PORTERR-CRC-warn', help=u'CRC校验错误警告阀值，默认为0', default=0,dest='crc_warn', metavar='3')
optp.add_option('--PORTERR-C3-warn', help=u'C3丢包数量警告阀值，默认为50',default=50,dest='c3_warn', metavar='50')
optp.add_option('--PORTERR-Link-fail', help=u'Link-fail数量，默认为5',default=5,dest='Link_fail', metavar='50')
opts, args = optp.parse_args()
if opts.host is None or opts.user is None or opts.passwd is None:
    print u"必要的参数未指定，无法运行"
    optp.print_help()
    sys.exit(1)
STATUS_OK=0
STATUS_WARNING=1
STATUS_CRITCAL=2
STATUS_Unknown=3

def Read_ReAll_Str(CompileStr,msg):
    reall=re.findall(CompileStr, msg)
    if len(reall) ==0:
        return False 
    else:
        return reall
    
def Read_RE_All_Str(CompileStr,msg,res="single"):
    '''
    通过正则表达式，匹配执行两个字符间的内容
    '''
    result = re.findall(CompileStr,msg)
    if res == "single":
        for x in result:
            if x is not None:
                return x
        return False
    else:
        if len(result) <> 0:
            return result
        else:
            return False

def Check_FSW_Uptime(msg):
    status_return=STATUS_Unknown
    Uptime=Read_RE_All_Str(".*up(.*)days.*",msg)
    if Uptime:
        if int(Uptime) < int(opts.uptime_crit):
            print "CRITCAL-设备在%s天前被重启 |upday=%s" %(Uptime,Uptime)
            status_return=STATUS_CRITCAL
        else:
            print "OK-设备稳定运行:%s天 |upday=%s"%(Uptime,Uptime)
            status_return=STATUS_OK
    return status_return        

def Check_FSW_CPU(msg):
    status_return=STATUS_Unknown
    cpu=Read_RE_All_Str(".*average:(.*)\r\n.*",msg)
    cpus=list(eval(cpu))
    if cpus[2] > opts.cpu_crit:
        print "CRITCAL-15分钟内CPU使用超过s%|1minute=%s;%s;%s 5minute=%s;%s;%s 15minute=%s;%s;%s"%(opts.cpu_crit,cpus[0],opts.cpu_warn,opts.cpu_crit,cpus[1],opts.cpu_warn,opts.cpu_crit,cpus[2],opts.cpu_warn,opts.cpu_crit)
        status_return=STATUS_CRITCAL
    elif cpus[2] > opts.cpu_warn:
        print "WARNING-15分钟内CPU使用超过s%|1minute=%s;%s;%s 5minute=%s;%s;%s 15minute=%s;%s;%s"%(opts.cpu_warn,cpus[0],opts.cpu_warn,opts.cpu_crit,cpus[1],opts.cpu_warn,opts.cpu_crit,cpus[2],opts.cpu_warn,opts.cpu_crit)
        status_return=STATUS_WARNING
    else:
        print "OK-设备负载正常，每分钟平均：%s，每5分钟平均:%s,每15分钟内平均:%s|1minute=%s;%s;%s 5minute=%s;%s;%s 15minute=%s;%s;%s"%(cpus[0],cpus[1],cpus[2],cpus[0],opts.cpu_warn,opts.cpu_crit,cpus[1],opts.cpu_warn,opts.cpu_crit,cpus[2],opts.cpu_warn,opts.cpu_crit)
        status_return=STATUS_OK
    return status_return        
    
def Check_FSW_Fan(msg):
    status_return=True
    log=Read_RE_All_Str("Fan(.*?)RPM",msg,res="all")
    retmsg=[]
    retprf=[]
    for i in log:
        RPM=Read_RE_All_Str("[1-9]\d*", i,res="all")
        if "Ok" not in i:
            retprf.append("FAN%s;%s"%(RPM[0],RPM[1]))
            retmsg.append("CRITCAL-FAN%sRPM"%i)
            status_return=False
        else:
            retprf.append("FAN%s;%s"%(RPM[0],RPM[1]))
            retmsg.append("OK-FAN%sRPM"%i)
    if status_return:
        print "OK-设备风扇运行正常|sfwstatus=0"
        status_return=STATUS_OK
    else:
        print "CRITCAL-设备风扇运行不正常|sfwfanstatus=1"
        status_return=STATUS_CRITCAL
    print "\r\n".join(retmsg)
    print "|"
    print "\r\n".join(retprf)
    return status_return 

def Check_FSW_Temp(msg):
    status_return=True
    log=msg.splitlines()[3:-1]
    retmsg=[]
    retprf=[]
    for i in log:
        ilit=i.split()
        if "State" in i or "ID" in i or "==" in i :
            continue
        if "Ok" not in i:
            retmsg.append("CRITCAL-ID %s is %s"%(ilit[0],ilit[1]))
            retprf.append("Centigrade%s=%s Fahrenheit%s=%s"%(ilit[0],ilit[2],ilit[0],ilit[3]))
            status_return=False
        else:
            retmsg.append("OK-ID %s is %s"%(ilit[0],ilit[1]))
            retprf.append("Centigrade%s=%s Fahrenheit%s=%s"%(ilit[0],ilit[2],ilit[0],ilit[3]))
            
    if status_return:
        print "OK-设备温度传感正常|sfwtempstatus=0"
        status_return=STATUS_OK
    else:
        print "CRITCAL-设备温度传感异常|sfwtempstatus=1"
        status_return=STATUS_CRITCAL
    print "\r\n".join(retmsg)
    print "|"
    print "\r\n".join(retprf)
    return status_return

def Check_FSW_Ps(msg):
    status_return=True
    log=msg.splitlines()[1:-1]
    retmsg=[]
    retprf=[]
    for i in log:
        ilit=i.split("#")
        if "OK" not in i:
            retmsg.append("CRITCAL-PS %s is %s"%(ilit[1]))
            retprf.append("PS%s=1"%(ilit[1][1:2]))
            status_return=False
        else:
            retmsg.append("OK-PS%s"%(ilit[1]))
            retprf.append("PS%s=0"%(ilit[1][1:2]))
    if status_return:
        print "OK-设备电源正常|sfwPSstatus=0"
        status_return=STATUS_OK
    else:
        print "CRITCAL-设备电源异常|sfwPSstatus=1"
        status_return=STATUS_CRITCAL
        
    print "\r\n".join(retmsg)
    print "|"
    print "\r\n".join(retprf)
    return status_return
    
def Check_FSW_Interfaces(msg):
    status_return=STATUS_CRITCAL
    Online=len(re.findall('.*?.Online.*',msg))
    if Online == int(opts.Online_crit):
        print "OK-接口正常，一共Online%s个接口 |portOnline=%s;;%s"%(Online,Online,opts.Online_crit)
        status_return=STATUS_OK 
    else:
        print "CRITCAL-接口Online数量不正确,Online=%s|portOnline=%s;;%s"%(Online,Online,opts.Online_crit)
    return status_return

def Check_FSW_Status(msg):
    status_return=STATUS_CRITCAL
    Status=len(re.findall('.*?.HEALTHY.*',msg))
    if Status == int(opts.Monitor_crit):
        print "OK-硬件正常，HEALTHY数量:%s |HEALTHY=%s;;%s"%(Status,Status,opts.Monitor_crit)
        status_return=STATUS_OK 
    else:
        print "CRITCAL-硬件不正常，HEALTHY数量:%s |HEALTHY=%s;;%s"%(Status,Status,opts.Monitor_crit)
    return status_return

def Check_FSW_PortErr(msg):
    status_return=True
    plist=msg.split("\n")
    retmsg=[]
    for port in plist:
        if opts.user in port or "err" in port or "=" in port or port is None:  continue
        templist= port.split(' ')
        while '' in templist:
            templist.remove('')
        if not templist: continue
        if int(templist[4]) >int(opts.crc_warn):
            retmsg.append("CRITCAL-接口%s有CRC数据帧校验错误产生，CRC错误:%s,enc_out数量：%s"%(templist[0],templist[4],templist[9])) 
            status_return=False
        if 'k' in templist[10]:
            retmsg.append("CRITCAL-接口%s有严重的丢包现象，DISC C3:%s"%(templist[0],templist[10]))
            status_return=False 
        elif int(templist[10])>int(opts.c3_warn):
            retmsg.append("CRITCAL-接口%s有大量的丢包现象，DISC C3数量%s"%(templist[0],templist[10]))
            status_return=False
        if int(templist[11])>int(opts.Link_fail):
            retmsg.append("CRITCAL-接口%s有大量的LR超时，Link-fail:%s,Loss sync:%s,Loss sig:%s"%(templist[0],templist[11],templist[12],templist[13]))
            status_return=False
    if status_return:
        print "ok-端口状态检测正常" 
        status_return=STATUS_OK
    else:
        print "\r\n".join(retmsg)
        status_return=STATUS_CRITCAL
    return status_return      
def Connect(command):
    try: 
        tn = telnetlib.Telnet(opts.host,opts.port)
        tn.read_until('login:')
        tn.write(opts.user + "\n")
        tn.read_until('Password:')
        tn.write(opts.passwd + "\n")
        tn.read_until('%s>'%opts.user)
        tn.write("\n")
        tn.write("%s \n"%command)
        tn.write("exit \n")
        tnret=tn.read_all()
        tn.close()
        return tnret
    except Exception,e:
        print e
        sys.exit(STATUS_Unknown)
 
if opts.option == "UPTIME":
    sys.exit(Check_FSW_Uptime(Connect("uptime")))
elif opts.option == "CPU":
    sys.exit(Check_FSW_CPU(Connect("uptime")))
elif opts.option == "FAN":
    sys.exit (Check_FSW_Fan(Connect("fanshow")))
elif opts.option == "TEMP":
    sys.exit (Check_FSW_Temp(Connect("tempshow")))
elif opts.option == "PS":
    sys.exit (Check_FSW_Ps(Connect("psshow")))
elif opts.option == "PORTOnline":
    sys.exit (Check_FSW_Interfaces(Connect("switchshow")))
elif opts.option == "Monitor":
    sys.exit (Check_FSW_Status(Connect("switchstatusshow")))
elif opts.option == "PORTERR":
    sys.exit (Check_FSW_PortErr(Connect("porterrshow")))
else:
    print "不支持的监控项目"
    sys.exit(STATUS_Unknown)

