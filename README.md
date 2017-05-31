# Check_Brocade

Nagios 检查博客光钎交换机脚本

需要python支持，使用telnet方式进行连接

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
