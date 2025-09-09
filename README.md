# NinjiaTag

## Fork 版本

使用 python flask 实现了 server.mjs 相同的功能。对外端口是 3001，运行方式：

```
pip install -r requirements.txt
python app.py
```

## DIY 你自己的 airtag

### DIY your own airtag(longterm record)

DIY 兼容 FindMy 网络的定位标签/设备（长期记录）

> “NinjiaTag”并非拼写错误，而是我们对物联网产品价值的重新定义：它不仅是敏捷的防丢工具（Ninja），更是对下一代分布式物联网（IOT）技术的憧憬，为分布式蓝牙标签（Tag）的新一代解决方案。名称中的 ‘jia’ 也寓意 ‘协作之家’，期待与你共同构建！

服务器端运行 FindMy 网络后台抓取位置数据并存入数据库，无需部署 Mac 电脑或虚拟机，也不需要拥有 iPhone 与其上面的查找 app 即可查看回溯任意时间段内您 DIY 的定位标签/设备的位置、轨迹（注册 Apple-ID 时需要借用一下别人的 iPhone）。
目前实现的功能：

- [x] 服务器端后台运行 request_report 获取位置，定期下载位置数据并储存在本地服务器数据库，储存时间不限（目前市面上主流产品记录时长最多为 7 天），轨迹可永久保存于服务器。
- [x] 支持任意时间段任意物品轨迹查询和显示，支持轨迹点的经纬度和时间点显示，可随意缩放查看，方便回溯。
- [x] 支持热图显示（ Hotspot ），类似地理信息系统的人流密度显示，经常去过的地方颜色更深，不去或偶尔去的地方颜色浅。
- [x] Web 前端支持密钥管理
- [x] 地图采用开源的 Mapbox-GL 三维地图引擎，支持三维地形显示，渲染更加美观。
- [x] 支持选择单/多物品任意时间段 GPX(GPS eXchange Format)文件导出

### [English Readme](README-EN.md)

![UI](asset/UI1.png)

## 目录

- [NinjiaTag](#ninjiatag)
  - [DIY 你自己的 airtag](#diy-你自己的-airtag)
    - [DIY your own airtag(longterm record)](#diy-your-own-airtaglongterm-record)
    - [Enlish Readme](#enlish-readme)
  - [目录](#目录)
  - [硬件 DIY](#硬件-diy)
  - [准备条件：](#准备条件)
  - [硬件设置](#硬件设置)
  - [服务端安装部署](#服务端安装部署)
    - [1. 创建一个 docker 网络](#1-创建一个-docker-网络)
    - [2. 运行 Anisette Server](#2-运行-anisette-server)
    - [3. 下载本项目到本地](#3-下载本项目到本地)
    - [4.放置服务端 key](#4放置服务端-key)
    - [5.安装 python3 相关库](#5安装-python3-相关库)
      - [基础网络和加密组件](#基础网络和加密组件)
      - [创建 python3 venv 虚拟环境(可选)](#创建-python3-venv-虚拟环境可选)
        - [venv 虚拟环境 pip3 安装相关依赖](#venv-虚拟环境-pip3-安装相关依赖)
    - [安装 nodejs](#安装-nodejs)
      - [修改 request_reports.mjs](#修改-request_reportsmjs)
    - [安装 pm2 守护定时执行](#安装-pm2-守护定时执行)
      - [PM2 安装说明](#pm2-安装说明)
      - [PM2 长期运行脚本命令](#pm2-长期运行脚本命令)
        - [启动脚本并命名进程](#启动脚本并命名进程)
        - [长期运行保障措施](#长期运行保障措施)
        - [pm2 常用管理命令(部署时可忽略)](#pm2-常用管理命令部署时可忽略)
    - [6.服务器后端地址远程](#6服务器后端地址远程)
  - [前端页面](#前端页面)
    - [使用方法](#使用方法)
      - [简单使用说明](#简单使用说明)
  - [基于的开源项目](#基于的开源项目)
  - [杂项待开发 convert the data to KML](#杂项待开发-convert-the-data-to-kml)
  - [免责声明](#免责声明)

## 硬件 DIY

硬件 DIY 需要一定门槛，如果你不想自己动手，可以咸鱼搜索 “自制 Airtag”（用户名 Dijkstra 很贪心 ），我会不定时上架一些成品，但建议你自己搭建服务，我提供的服务器带宽有限。

成品使用教程：

- [2032 圆形 Tag 使用教程](./usr_guide/2032_TAG.md)
- [MiniTag 使用教程](./usr_guide/Mini_TAG.md)

## 准备条件：

- 一台 Linux 服务器（任意 Linux）。用来运行 Docker 服务和 Python 脚本。
- 需要一个使用实体 IOS 设备注册的，已启用 2FA (双重认证)的 Apple-ID。
  建议不要使用个人常用的 Apple ID，而是注册一个新的 Apple ID 用于实验目的。 没有 Apple ID 的 可以找朋友借用一下苹果设备（iPad、Macbook、iPhone），注册一个。仅支持短信方式作为双重认证！如果有苹果设备登录着该 Apple ID，最好退出，否则有可能收不到短信验证码。
  您需要在苹果设备上登录过该帐户才可以（获得了 iCloud 的 5G 免费空间才是有效的 Apple ID）。仅在 iCloud 网页上注册的 Apple ID 权限不足。
  Only a free Apple ID is required, with SMS 2FA properly setup. If you don't have any, follow one of the many guides found on the internet.
- 一个蓝牙标签设备，目前支持 nRF5x 蓝牙模块，ST17H66 蓝牙模块，后续会支持更多低成本国产蓝牙模块
  只需要最小系统模块，所以也可以购买 nRF5x ST17H66 芯片自己进行 PCB 打样。

## 硬件设置

1. 下载刷机固件和刷机脚本

   - ST17H66 芯片前往 [Lenze_ST17H66](https://github.com/biemster/FindMy/tree/main/Lenze_ST17H66) 下载所需固件(FindMy.hex)和刷机脚本(flash_st17h66.py)
   - nRF5x 前往 [openhaystack-firmware](https://github.com/acalatrava/openhaystack-firmware/releases) 下载所需固件(nrf51_firmware.bin 或 nrf52_firmware.bin)
   - [TLSR825X 芯片](https://github.com/biemster/FindMy/blob/main/Telink_TLSR825X/README.md)，比如米家温湿度计 2(型号 LYWSD03MMC)也可以刷机成定位标签，但我没有尝试

2. 执行本仓库的 keygen 目录下 `python3 generate_keys.py` 来生成密钥对(在当前目录 6 位随机名称目录下)。(注意: 必须安装依赖 `cryptography` `filelock`. 用 `pip3 install cryptography filelock` 命令安装)
   Windows 或 Linux 下都可以执行。

3. 将固件刷入设备
   说明：generate_keys.py 在原项目上做了修改，支持多物品多密钥自定义批量生成，如生成 5 个密钥的 8 个物品(在不同文件夹)，执行`python3 generate_keys.py -n 5 -i 8`

`generate_keys.py` 可以指定参数 `python3 generate_keys.py -n 50` 来生成包含多个密钥的 keyfile，其中 50 就是个数，可以自己改。不指定则默认单个密钥，也就是定位标签运行过程中只有一个蓝牙 Mac 地址（密钥其实就是加密了的 Mac 地址），而多密钥就是定位标签可以定时更换 Mac 地址(称为滚动密钥，苹果 AirTag 就是这样)。

经过测试，带密钥轮换机制的标签，其位置会被更频繁的上报，即位置更新更频繁，更能被精确定位。推荐使用多密钥的 keyfile。但是，密钥轮换会增加一定功耗。

[nrf5x 烧录教程](flash_guide/nrf5x.md)
[ST17H66 烧录教程](flash_guide/ST17H66.md)

## 服务端安装部署

### 1. 创建一个 docker 网络

在终端中执行以下命令，创建一个新的 docker 网络

```bash
docker network create mh-network
```

### 2. 运行 [Anisette Server](https://github.com/Dadoum/anisette-v3-server)

```bash
docker run -d --restart always --name anisette -p 6969:6969 --volume anisette-v3_data:/home/Alcoholic/.config/anisette-v3/ --network mh-network dadoum/anisette-v3-server
```

注意：首次执行该命令会自动从 docker 官方仓库拉取镜像，因国内网络环境的原因，需要设置镜像仓库。如下修改 docker 的配置文件`/etc/docker/daemon.json`（不存在就新建），增加 `registry-mirrors`：

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://hub.1panel.dev",
    "https://docker.itelyou.cf",
    "http://mirrors.ustc.edu.cn",
    "http://mirror.azure.cn"
  ]
}
```

之后运行如下命令重启 docker 服务：

```bash
systemctl restart docker
# 或者
service docker restart
```

此时，镜像源应该生效了。可以用 `docker info` 命令验证，如果输出末尾有如下`Registry Mirrors`，说明镜像源配置成功了：

```
Registry Mirrors:
  https://docker.1ms.run/
  https://hub.1panel.dev/
  https://docker.itelyou.cf/
  ......
```

### 3. 下载本项目到本地

使用 git clone 或下载 zip 解压

### 4.放置服务端 key

将硬件设置步骤中生成的.key 后缀的文件放置在本项目/keys 文件夹下，后续脚本会自动转化

### 5.安装 python3 相关库

#### 基础网络和加密组件

安装 python3，并使用 pip3 安装相关依赖

```
pip3 install aiohttp requests cryptography pycryptodome srp pbkdf2 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 创建 python3 venv 虚拟环境(可选)

如果成功通过[pip3](#基础网络和加密组件)安装完成依赖，该步骤可忽略

`python3 -m venv ./venv/`

##### venv 虚拟环境 pip3 安装相关依赖

```
./venv/bin/pip3 install aiohttp requests cryptography pycryptodome srp pbkdf2 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

在 python3 venv 环境执行
`./venv/bin/python3 request_reports.py`

或执行`python3 request_reports.py`

开始时会提示输入 Apple ID 和密码，然后是 2FA 短信验证，完成后能正常执行位置数据拉取。

如果输入 Apple ID 及密码后在 2FA 阶段出现`gsa_authenticate`类型的错误

```
r = gsa_authenticated_request({"A2k": A, "ps": ["s2k", "s2k_fo"], "u": username, "o": "init"})
raise InvalidFileException()
plistlib.InvalidFileException: Invalid file
```

可能当前服务器 IP 被 Apple 禁止访问，执行

```
curl -k https://gsa.apple.com/grandslam/GsService2 -v
```

如果返回`401 Authorization Required`字样说明当前 IP 正常,返回`503 Service Temporarily Unavailable`说明当前 IP 被禁，需要更换当前服务器 IP 重试

### 安装 nodejs

执行以下命令安装 nodejs 和 npm 用于提供后端服务

```bash
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"
# Download and install Node.js:
nvm install 22
# Verify the Node.js version:
node -v # Should print "v22.17.1".
nvm current # Should print "v22.17.1".
# Verify npm version:
npm -v # Should print "10.9.2".
```

如果网络有问题可尝试在 nodejs 官网下载安装包进行手动安装，不在本教程范围内，可自行搜索安装教程

完成后在项目目录下执行：

```
npm i
```

安装 node_modules 相关依赖

#### 修改 request_reports.mjs

如果在 python venv 执行，将`request_reports.mjs`文件中

```
python3 request_reports.py
```

修改为

```
./venv/bin/python3 request_reports.py
```

可以通过修改`*/5 * * * *`来修改从 Findmy 服务器获取位置数据的时间间隔，具体参考 Cron 的文档，如`*/5 * * * *`表示每 5 分钟请求一次，不建议修改得太频繁

### 安装 pm2 守护定时执行

长期运行 "server.mjs" 和 "request_reports.mjs" 以保证服务器能定期取回位置数据并存于数据库

#### PM2 安装说明

1. 通过 npm 全局安装

`npm install pm2 -g`

- 验证安装：执行
  "pm2 --version"，输出版本号即安装成功。
- 权限问题（Linux/Mac）：若提示权限不足，可添加
  "sudo" 或执行
  `chmod 777 /usr/local/bin/pm2`授权。

#### PM2 长期运行脚本命令

##### 启动脚本并命名进程

- 运行
  "server.mjs"（数据库查询主服务）：
  `pm2 start server.mjs --name "query-server" --watch`

"--name"：自定义进程名称（便于管理）。
"--watch"：监听文件改动自动重启。

- 运行
  "request_reports.mjs"（抓取位置数据任务）：
  `pm2 start request_reports.mjs --name "report-task" --watch`

##### 长期运行保障措施

1. 保存进程列表
   `pm2 save`

   保存当前运行列表，防止重启后丢失。

2. 设置系统开机自启

   `pm2 startup` 生成启动脚本

   `sudo pm2 startup systemd ` Linux systemd 系统自启动

   `pm2 save` 关联保存的进程列表

   服务器重启后 PM2 自动恢复进程。

3. 日志管理

   - 查看实时日志：

     `pm2 logs web-server # 指定进程名`

##### pm2 常用管理命令(部署时可忽略)

- 查看进程状态
  "pm2 list" 显示所有进程及资源占用
- 停止进程
  "pm2 stop server" 停止指定进程（保留配置）
- 重启进程
  "pm2 restart server" 零停机重载（适用服务更新）
- 监控资源
  "pm2 monit" 实时显示 CPU/内存
- 删除进程
  "pm2 delete server" 彻底移除进程

### 6.服务器后端地址远程

前端页面需访问数据查询服务 url 地址" 形如 `http://服务器ip:3000`。

若要在公网使用，需将本地部署服务公开到公网，可以用 路由器端口映射 或 内网穿透(比如有公网 IP 可使用端口映射+DDNS，或使用反向代理 [ngrok](https://ngrok.com/) 、[节点小宝](https://iepose.com/)、[ZeroNews](https://www.zeronews.cc/) 都有免费版；[花生壳](https://console.hsk.oray.com/) 9 块 9 永久用，每月免费 1G 流量)
或使用 Zerotier tailscale 之类的的方式实现。具体操作不属于本文范畴，请自行搜索。

## 前端页面

前端页面可以自行部署，也可以使用我提供的页面[https://bd8cca.atomgit.net/NinjiaTagPage/](https://bd8cca.atomgit.net/NinjiaTagPage/)，页面只是一个查询框架，建议使用我提供的页面。
前端基于 vue3 框架开发，目前存在少量 bug，但整体能用，欢迎提出 Issue 或 Pr，所有打包的前端页面位于[https://atomgit.com/bd8cca/NinjiaTagPage](https://atomgit.com/bd8cca/NinjiaTagPage) 项目，可自行下载部署

[NinjiaTagPage(http)](http://bd8cca.atomgit.net/NinjiaTagPage/)
[NinjiaTagPage(https)](https://bd8cca.atomgit.net/NinjiaTagPage/)

1. 因浏览器限制，https 的网站只能访问 https 的后台服务。所以如果你选择使用 [Atomgit Page(https)](https://lovelyelfpop.atomgit.net/macless_haystack_pages/)，那么必须将 后端 node 服务部署为 https（需 SSL 证书）。可以反向代理工具，推荐使用[Cloudflare tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)将本地 NAS 或 Linux 服务器端口映射到子域名下。
2. 访问 http 的地址，浏览器可能会自作主张转向 https 的地址，可以地址栏改成 http 再回车

### 使用方法

NinjiaTag 前端页面，使用 Vue3 编写，结合 Mapbox-gl 三维引擎强大的渲染能力，后续可扩展更多的功能（如轨迹导出 KML，多物品时空交错）。

#### 简单使用说明

1.  在前端页面有配置服务器地址选项，填入部署的[服务器远程地址](#6服务器后端地址远程)/query，注意加上/query 后缀，如`http://服务器ip:3000/query`

2.  将 generate_keys.py 硬件设置生成的.json 密钥文件在`物品管理`对话框`解析json密钥文件`导入即可

3.  在`数据选择`对话框选择物品数据和时间段进行查询，有几个选项：

- 轨迹点：历史的轨迹，鼠标悬停或点击可显示详情。

- 热图： 类似地理信息系统的人流密度显示，经常去过的地方颜色更深，不去或偶尔去的地方颜色浅。
- 最新位置： 最新的物品位置，以图标的形式显示。

如果没有获取到位置数据，带着 diy 的 NinjiaTag 到人流密集的地方走一圈，等待后台服务器获取到位置数据库并存入数据库。

## 基于的开源项目

- 查找部分的工作，主要基于 openhaystack 开源项目修改后实现，感谢https://github.com/seemoo-lab/openhaystack/项目的所做工作

- Query Apple's Find My network, based on all the hard work of https://github.com/seemoo-lab/openhaystack/ and @hatomist and @JJTech0130 and @Dadoum

- 并且感谢 JJTech0130 降低部署门槛，目前服务端部署不再需要 mac 设备了
  https://github.com/JJTech0130/pypush
- lovelyelfpop 大佬开发的安卓 apk 也可以用于本项目，感谢他本地化 app 做的很多工作
  [https://gitee.com/lovelyelfpop/macless-haystack](https://gitee.com/lovelyelfpop/macless-haystack)

## 杂项待开发 convert the data to KML

_KML stands for Keyhole Markup Language. It's a file format used to display geographic data in an Earth browser, such as Google Earth, Google Maps, and various other mapping applications._

```bash

./request_reports.py > input.txt

```

It will generate a json like file include main data of coordinate & date & time.

```bash

python3 make_kml.py

```

this script reads input.txt generated with request_reports.py and writes for each key a \*.kml file

## 免责声明

此存储库仅用于研究目的，此代码的使用由您负责。

对于您选择如何使用此处提供的任何源代码，我概不负责。使用此存储库中提供的任何文件，即表示您同意自行承担使用风险。再次重申，此处提供的所有文件仅用于教育和或研究目的。本项目仅用于物品的防丢，严禁用于非法用途，使用时请遵守当地的法律法规。
