# History
A distributed and open source history time line tool.  
  
![image](res/shapshot.png)
  
# Contact me
sleepy_history##163.com
  
# Readme CN   
  
##最近更新
使用严格公元纪元时间绘制时间轴  
> 公元元年1月1日秒数为0，秒数为负则为公元前  
> 考虑大小月及闰年影响  
> 使用上和之前应该没多大区别，但这次更改的程度非常大，程序中时间的使用变得非常严谨  
已知问题：双击查看详情新窗口可能会到后台，可能是pyqt5本身的BUG，正想办法解决  
  
  
如果有任何意见和建议，或者对此项目感兴趣，请给我发送邮件：sleepy_history##163.com  
  
## 起因:  

最近对历史感兴趣，想找一个基于时间线的历史笔记，大致的需求如下：  
1. 可本地编辑，离线使用。  
2. 内容可自由扩展，而不是作者编辑好后大家只读。  
3. 支持在一个坐标轴上同时显示事件以及时间段。 
4. 支持坐标轴缩放。 在不同时间尺度上（万年，世纪，百年，一年，一日） 展示适当的内容。
5. 能识别事件描述中的时间地点人物组织事件，并以此为索引进行关联查找和浏览。  
6. 可以定义多个filter并放置在同一个视图下，如人物朝代及事件，以方便对照查阅。  
7. 多平台浏览编辑以及随身记录。  
8. 最后，布局清晰显示漂亮，自然最好。然而上面的功能优先。  
   
我在网上找了一圈，然而并没有找到理想的软件（或网页）。对于时间线的处理，通常只能显示单点时间或时间段中的一种。无法满足需求。  
所以还是自己动手吧。。。而且虽然很想做网页版的，然而我对web开发不熟。。。人生苦短，还是先py  

## 设计：

### 几个概念：  
1. TimeAxis: 时间轴，即软件的主要界面。时间轴的布局（layout: 水平或垂直）及位置（align：处于中间或某一边）都可以调整，其两边可以放置Thread显示不同内容。
2. Thread: 历史线索，用以展示历史记录。Thread可以放置在时间轴的两边，可以放置任意个，用以显示不同内容（不同文件或不同filter）。
3. Track: 一个Thread上能显示数个Track（轨道），数量由Thread的宽度和Track最小宽度（可设置）确定。在排布历史记录的时候软件会尽量利用空间并使各个记录不会重叠。如果空间不足，其余的记录会排布到最后一个Track上。
4. Depot: 为了管理方便，我们将所有数据放置在软件目录下的depot目录中，depot目录中的每个文件夹称为一个depot。记录文件可以按语言或内容分类放置在不同的depot（文件夹）中。
4. Index: 软件的设计上考虑到在线和分布式的使用场景。由于空间和带宽的限制，展现给客户的不可能是完整的内容。因此软件支持将记录的时间和摘要提取出来作为索引，并指向真正内容。当用户需要查看详情的时候，主要内容才会被加载。
5. Filter: 对于已经加载的内容而言，我们可以对其中的内容进行选择展示。主要应用在PC和移动端，以及index的编辑上。由于index包含的信息过少，所以网页及分布场景我们难以使用filter。这点或许会在以后改进。
  
### 界面说明：  
* 从main.py运行，需要python3 + pyqt5支持
* 坐标轴界面可以按左键沿轴向拖动或鼠标滚轮滑动。CTRL+滚轮可以缩放时间轴。
* 在主界面上任意地方点击右键会弹出菜单，如果鼠标下面没有Thread，可以添加一个新的Thread。
* 在Thread上点击右键可以为其载入文件，depot或打开filter。注意filter只能应用于已载入的记录（File -> Load xxx），而Load Index及Load File同时会载入对应的记录。
* 此外可以调整Track宽度，删除当前Thread，以及在此Thread左右打开一个新的Thread。
* 在展示的Record上双击，可以打开详细信息及编辑器。当前软件在编辑内容后可以不会实时更新，这点会在以后的版本改进。
* File菜单下的Load File可以将单个文件载入内存中，载入后的信息可以通过Filter进行筛选查看。其中Load All会载入depot下所有内容，时间会比较久，界面可能存在长时间不响应的情况。这点也会在后续版本进行改进。
* View菜单下的Historical Record Editor可以打开编辑器。编辑器的左侧下拉列表选择depot，列表选择文件，右侧编辑。点击Apply后保存到文件。
* View菜单下的History Filter Editor可以打开Filter及Index编辑器，根据选择的Filter生成对应的index。
  
### 时间日期说明：
* 程序在为了识别各种不同的时间格式上花费了大量精力，通常文章中直接复制下来的时间文字都能顺利识别。为了严谨起见，在此描述一下标准的时间格式：
> 公元前1000年1月1日 - 公元2000年10月30日
* 其中公元前的日期必须加上“公元前”或“前”的字样，否则程序认为是公元纪年（“公元”可省略）。
* 分隔符可以是“-”或“,”，程序中做了各种匹配，所以一般无需在意全角半角的问题，甚至常用的“~”分隔符也没问题。
* 数字可以是中文或阿拉伯数字，都没关系
* 时间中的“年”是必须的内容，“月”和“日”可选，数字后面如果没有“年”的字样，默认是年。
* 时间不一定是一个范围，可以是一个时间或多个时间。前者会被作为单点事件；而后者将会采用最小及最大的时间来绘制柱形图。
* 如果出现其它的文字，这些文字会被忽略，不会影响时间的解析
* 总之程序中尽量提高容错度以提供录入的方便
  
### 详细内容：  
* 请阅读Doc/Design.vsd  
  
### 参考内容：  
光看这个时间轴对从零开始了解一段历史其实作用并不大，最佳食用方法是配合优秀文章书籍对照观看。
下面列出的是本人在学习过程中发现的优秀文章，它们同时也是depot内容的参考文章：  
  
#### 古希腊罗马史
* https://www.zhihu.com/question/34550296
  
#### 中世纪历史
* https://www.zhihu.com/question/39696514/answer/85778739
  
#### 法国历史
* https://www.zhihu.com/question/64400788/answer/219935195
  
### 当前进度与计划：  
由于上下班的班车上不适合阅读，对历史文章主要以听为主。而单纯靠听对记忆和系统理解没有帮助，只是混个耳熟。
而另一方面，真正能够安静阅读和做笔记的时间非常少。  
最近在听世界史，刚听完中世纪前的内容，由于每一集都是一个独立的故事，各个故事发生的时空常常让我一脸蒙逼，
急需做个整理，故中断了中国史去做欧亚大陆史的笔记。  
过段时间继续把中国的朝代兴衰补全。。。  
历史真是个大坑。
  
### 0.4.0计划
* 优化绘制过程，将所有绘制内容的Layout在内容改变/窗口大小改变/设置改变时计算好，在Repaint的时候不需要重新计算。
* Front/Back：完成History Record编辑器的Label Tag Editor功能，将Event Editor和Label Tag Editor分别更名为Front及Back，意为卡片的两面。
* 支持在一个Thread中打多个文件
* 支持关闭一个Thread
* 支持内容改变后实时更新绘制，并在右键中增加刷新功能
* 注：以上三个改进，是因为在初期的设计中，Thread应该导入Index而非直接导入文件；而这种设计在本地浏览时会带来麻烦。
  
## 关于开放协作（虽然应该没人会响应...）  

* 有兴趣的同志们可以fork一份代码，在自己的repo上提交你的record后，再向我提交一个pull request。在record中可以增加一个名为author的label，并填上你的名字。  
* 另外不知道有没有高手可以做一个JS版本的viewer...  
  
-------------------------------------------------------------------------------------------------
  
# Readme EN  
TODO  
  
-------------------------------------------------------------------------------------------------

# Dev Note:  

## DONE

(DONE) | 试用了一下，有几个需要改进的地方：  
(DONE) | 1.编辑界面需要加入“在本文件中新建”及“新建到一个新的文件”功能  
(DONE) | 2.编辑界面可以选择倾向，可以是时间、地点、人物、组织、事件  
(DONE) | 	所选择的内容为必填项  
(DONE) | 3.编辑界面需要加入“锁定”功能，锁定的项目在新建的时候不会被消除  
(DONE) | 统一LabelTag、Index及event  
(DONE) | Editor中加入depot与文件浏览界面  
(DONE) | depot的分类和选择  
(DONE) | 如何处理相同时间（约）中发生的事，如前12世纪廪辛康丁，武乙，文丁等人发动的各场战争  
(DONE) | 文件重命名
(DONE) | 文event combobox显示时间并按时间排序  
(DONE) | Thread放在坐标轴左边
(DONE) | Thread编辑  
(DONE) |     界面支持配置1-10个thread，包括enable，focus label，depot，filter  
(DONE) |     界面根据用户配置生成不同的Index供不同的thread载入  
(DONE) |     在LabelTags层面上支持filter功能  
(DONE) | viewer可以直接载入event而不仅仅只是index  
(DONE) | 优化zoom in和zoom out功能使之更加自然  
(DONE) | 坐标轴的改进：  
(DONE) | 	main scale为年时sub scale应为月（12格），同理月之下为周，周之下为日，日之下为时  
(DONE) | 	更好的取整及显示时间单位  
(DONE) | 支持坐标轴水平显示，在View -> Axis Appearance Setting中设置  

## TODO:

新的想法：将历史记录中的时间段提取出来，作为HistoryStar分布在时间条中，鼠标移上去或双击查看对应时间内容。

Thread Config界面优化（Load，Check）

如何优化一年内多起事件的显示（重叠的问题）  
同一时代人物太多经常导致显示空间不足，如何处理  
  
    
合并文件功能：可以将多个小文件合并成一个大文件  

五要素外其它tags的编辑功能  
改变窗口大小的操作会触发mouse event的问题  

多thread的界面设计  
	使用label:tags格式作为filter  
	可以将filter保存为预设值或通过URL传递  
	可以让用户方便的预设自定义filter  
	嵌入绘图中会增加难度，可以考虑在绘图之外使用控件编辑  

## IDEA：  

对于一些时间比较暧昧事件的处理（特别是远古时代的事件）  
对于一些使用相对时间的事件的处理  
可以使用不同的时间基准（公元，万历，民国等）  

如何使index更小，却能索引更多内容  
或者在这种极小index的设计下，如何检索更多内容  
网页端的展示界面（js）  


使用自然语言处理算法提取四要素tag  
使用类似的方法将提取出来的时间数字化  



