# Check_Brocade

Nagios 检查博客光钎交换机脚本

需要python支持，使用telnet方式进行连接

插件用于监控博科系列的光钎交换机
建议在交换机上创建一个普通用户的权限进行监控，创建命令如下</br>
userconfig --add 用户名  -r user -p 密码

# 使用方式
1、首现把脚本放入nagios的libexec目录</br>
   cp Check_Brocade.py /usr/local/nagios/libexec/Check_Brocade</br>
2、修改文件的权限</br>
   chown nagios:nagios Check_Brocade</br>
   chmod 755 Check_Brocade</br>
3、测试脚本运行,正常会看到帮助信息，请确保安装python解释器</br>
   ./Check_Brocade</br>

可监控的项目如下，通过-参数指定</br>
UPTIME  监控设备运行的天数，默认小于1天进行告警，执行的命令为：uptime</br>
                        通过--uptime-crit执行报警阀值</br>
CPU     监控设备的CPU利用率，默认取15分钟的平均值，执行的命令为：uptime</br>
        --cpu-warn  警告阀值</br>
        --cpu-crit  严重阀值</br>
FAN     监控设备风扇状态，执行的命令为：fanshow</br>
TEMP    监控设备的温度传感状态，执行的命令为：tempshow</br>
PS      监控设备的电源状态，执行的命令为：psshow</br>
PORTOnline 端口使用状态，检测端口Online数量，执行的命令为：switchshow</br>
        --PORTOnline-crit  指定现在使用的接口数量，如数量不一致报警</br>
Monitor 监控设备的硬件状态，通过执行switchstatusshow命令查看HEALTHY数量</br>
        --Monitor-HEALTHY  设备HEALTHY正常数量，如不一至报警</br>
PORTERR 监控端口具体错误状态 ，执行的命令 porterrshow</br>
        --PORTERR-CRC-warn    CRC校验失败的阀值</br>
        --PORTERR-C3-warn     disc C3  丢包数量阀值</br>
        --PORTERR-Link-fail    链路失败阀值</br>
