# 新版 Socket 服务器文档

标签（空格分隔）： api

---

**连接地址：ws://localhost:8888/**

总体流程：

进入房间->点歌->上麦询问->演唱->下麦->休息->上麦询问...

房间状态改变、成员进出房间、排麦更新时服务器会主动推送消息给客户端

### 消息体解读：

```
{
    "status":0, # 消息状态， 0 代表成功
    "body":{
        "count":1, # 房间成员数量
        "status":"4", # 房间状态
        "room":"R123", # 房间 id
        "current_time":1527574165, # 当前时间戳
        "start_time":"1527574164", # 此状态开始时间
        "author":"",  # 歌曲作者 （仅演唱状态时不为空）
        "name":"", # 歌曲名称  （仅演唱状态时不为空）
        "nick":"", # 麦上人昵称
        "end_time":"1527660564", # 此状态结束时间
        "members":[ # 房间成员列表
            {
                "nick":"15608059720", # 昵称
                "fullname":"15608059720", # fullname
                "avatar":"15608059720" # 头像地址
            }
        ],
        "sid":"0", # 歌曲 id （仅演唱状态时不为空）
        "duration":"86400", # 此状态持续时长 （演唱时为歌曲时长）
        "fullname":"", # 麦上人 fullname （仅演唱状态时不为空）
        "songs":[ # 麦序

        ]
    },
    "message":"success", # 状态信息
    "timestamp":"1527574165.09" # 消息发送时间戳
}
```



|房间 status 码|含义|
| --------------  | :---: |
|1|演唱中|
|2|上麦询问中|
|3|间隔休息中|
|4|空闲|


# 用户
## **进入房间**
```
action: join
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* body(_Optional_|object)-可选数据



### **Return**
成功
```
{
    "status":0,
    "body":{
        "count":1,
        "status":"4",
        "room":"R123",
        "current_time":1527574165,
        "start_time":"1527574164",
        "author":"",
        "name":"",
        "nick":"",
        "end_time":"1527660564",
        "members":[
            {
                "nick":"15608059720",
                "fullname":"15608059720",
                "avatar":"15608059720"
            }
        ],
        "sid":"0",
        "duration":"86400",
        "fullname":"",
        "songs":[

        ]
    },
    "message":"success",
    "timestamp":"1527574165.09"
}
```
失败
```
```

## **获取房间状态**

ps: 房间主动推送信息格式与此一致

```
action: status
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* body(_Optional_|object)-可选数据



### **Return**
成功
```
{
    "status":0,
    "body":{
        "count":1,
        "status":"4",
        "room":"R123",
        "current_time":1527574165,
        "start_time":"1527574164",
        "author":"",
        "name":"",
        "nick":"",
        "end_time":"1527660564",
        "members":[
            {
                "nick":"15608059720",
                "fullname":"15608059720",
                "avatar":"15608059720"
            }
        ],
        "sid":"0",
        "duration":"86400",
        "fullname":"",
        "songs":[

        ]
    },
    "message":"success",
    "timestamp":"1527574165.09"
}
```
失败
```
```

## **同意上麦**

```
action: ask
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* ack(_Required_|integer)- 是否上麦 1 上 0 不上
* body(_Optional_|object)-可选数据

### **Return**
成功
```
{
    "status":0,
    "body":{
        "count":1,
        "status":"4",
        "room":"R123",
        "current_time":1527574165,
        "start_time":"1527574164",
        "author":"",
        "name":"",
        "nick":"",
        "end_time":"1527660564",
        "members":[
            {
                "nick":"15608059720",
                "fullname":"15608059720",
                "avatar":"15608059720"
            }
        ],
        "sid":"0",
        "duration":"86400",
        "fullname":"",
        "songs":[

        ]
    },
    "message":"success",
    "timestamp":"1527574165.09"
}
```
失败
```
```


## **切歌**

```
action: cut
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* body(_Optional_|object)-可选数据

### **Return**
成功
```
{
    "status":0,
    "body":{
        "count":1,
        "status":"4",
        "room":"R123",
        "current_time":1527574165,
        "start_time":"1527574164",
        "author":"",
        "name":"",
        "nick":"",
        "end_time":"1527660564",
        "members":[
            {
                "nick":"15608059720",
                "fullname":"15608059720",
                "avatar":"15608059720"
            }
        ],
        "sid":"0",
        "duration":"86400",
        "fullname":"",
        "songs":[

        ]
    },
    "message":"success",
    "timestamp":"1527574165.09"
}
```
失败
```
```


## **广播消息**

```
action: boardcast
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* body(_Optional_|object)-可选数据

### **Return**
成功
```
{
    "status":0,
    "body":{
        "count":1,
        "status":"4",
        "room":"R123",
        "current_time":1527574165,
        "start_time":"1527574164",
        "author":"",
        "name":"",
        "nick":"",
        "end_time":"1527660564",
        "members":[
            {
                "nick":"15608059720",
                "fullname":"15608059720",
                "avatar":"15608059720"
            }
        ],
        "sid":"0",
        "duration":"86400",
        "fullname":"",
        "songs":[

        ]
    },
    "message":"success",
    "timestamp":"1527574165.09"
}
```
失败
```
```


# HTTP 接口

## **排麦**

```
POST /api/v2/singer/create
```
### **Parameters**
* room(_Required_|string)-房间
* sid(_Required_|string)- 歌曲 id
* token(_Required_|string)- 用户 token
* duration(_Required_|string)-歌曲 时长 （秒）

### **Return**
成功
```
{
    "body": {},
    "status": 1,
    "msg": "success"
}
```
失败
```
```