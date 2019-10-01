# History
A distributed and open history memo


# DONE

(DONE) | 试用了一下，有几个需要改进的地方：  
(DONE) | 1.编辑界面需要加入“在本文件中新建”及“新建到一个新的文件”功能  
(DONE) | 2.编辑界面可以选择倾向，可以是时间、地点、人物、组织、事件  
(DONE) | 	所选择的内容为必填项  
(DONE) | 3.编辑界面需要加入“锁定”功能，锁定的项目在新建的时候不会被消除  
(DONE) | 统一LabelTag、Index及event  
(DONE) | Editor中加入depot与文件浏览界面  
(DONE) | depot的分类和选择  

# TODO:

如何相同时间（约）中发生的事，如前12世纪廪辛康丁，武乙，文丁等人发动的各场战争  
合并文件功能：可以将多个小文件合并成一个大文件  
event combobox显示时间并按时间排序

五要素外其它tags的编辑功能  
viewer可以直接载入event而不仅仅只是index  
改变窗口大小的操作会触发mouse event的问题  

坐标轴的改进：  
	优化zoom in和zoom out功能使之更加自然  
	main scale为年时sub scale应为月（12格），同理月之下为周，周之下为日，日之下为时  
	更好的取整及显示时间单位  

多thread的界面设计  
	使用label:tags格式作为filter  
	可以将filter保存为预设值或通过URL传递  
	可以让用户方便的预设自定义filter  
	嵌入绘图中会增加难度，可以考虑在绘图之外使用控件编辑  

# IDEA：  

对于一些时间比较暧昧事件的处理（特别是远古时代的事件）  
对于一些使用相对时间的事件的处理  
可以使用不同的时间基准（公元，万历，民国等）  

如何使index更小，却能索引更多内容  
或者在这种极小index的设计下，如何检索更多内容  
网页端的展示界面（js）  


使用自然语言处理算法提取四要素tag  
使用类似的方法将提取出来的时间数字化  



