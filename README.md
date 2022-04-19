# MRILoader
<h1>MRILoader</h1>
<h2>介绍</h2>
<p>
  本项目主要解决nii、nii.gz格式的MRI图像单通道，且没有被归一化的问题，进一步封装，让数据更规整更容易解析。同时提供了一些辅助函数。
</p>
<h2>准备</h2>
<p>依赖及环境</p>
<code>
  Python 3.7、
  opencv、
  numpy、
  SimpleITK
</code>
<p>
由于是一个轻量级项目，直接提供了MRILoader.py文件，放入项目适当的文件夹内即可。之后在适当的文件内进行引用。
</p>
<code>
from MRILoader import MRILoader,MultipleMRILoader
</code>
<p>
  <br/>
引入后可以使用test.py文件对类进行测试。
</p>
<h2>方法</h2>
<h3>MRILoader类（适用于读取单一MRI文件）</h3>
<h4>构造函数</h4>
<p>
 我们在初始化MRILoader对象时，直接将MRI的文件。路径传递给MRILoader，就会自动读取对应文件。
</p>
<code>
  loader = MRILoader('./data/CC003/T1w_bscorr_SS.nii.gz')
  </code>
  
  <h4>.normalize() </h4>
   <p>
  本方法通常会被自动调用，一般无需手动调用。
  对读取到数据进行归一化，归一化后值变为0~255，但这时还不能输出，
会被getNormalizeSlices(self)、normalizeSlicesToTernary(self)自动调用
</p>

   <h4>.normalizeSlicesToTernary()</h4>
   <p>
  本方法通常会被自动调用，一般无需手动调用。
  因为单纯对读取到的数据进行归一化，归一化后值只是变为0~255，但这时还不能输出，
将归一化数据转为三通道（RGB），如果没有进行归一化，会自动进行归一化，会被
getNormalizeSlicesTernary(self)、display(self,num=0)、save(self, savePath="./save/",r=None,fileName="", suffix=".jpg")
自动调用
</p>

<h4>.getNormalizeSlices()</h4>
   <p>
  获取归一化后的MRI切片图，如果没有归一化会自动进行归一化
</p>
<code>
  normalize=loader.getNormalizeSlices()
  </code>
  
<h4>.getNormalizeSlicesTernary()</h4>
   <p>
  获取三通道化后的MRI切片图，如果没有三通道化会自动进行三通道化（同样如果没有归一化，会先进行归一化再进行三通道化）

</p>
<code>
  normalizeSlicesTernary=loader.getNormalizeSlicesTernary()
  </code>
  
  <h4>.display(num=0)</h4>
   <p>
  用于显示读取的MRI图片，无需提前调用其他方法，如果检测到未将图片处理为RGB会自动先进行处理。num为显示第num张MRI图。

</p>
<code>
  loader.display()
  </code>
   <h4>.save(savePath="./save/", r=None, folderName="", fileName="", suffix=".jpg", num=None, black=True)</h4>
   <p>
  用于保存MRI图片
savePath   存储路径<br/>
r          范围，默认是全部，传入数字就是第n张，数组就是范围，如果数组中有多个值，那会用第一个和最后一个作为范围<br/>
fileName   文件名,不填就用MRI（单张时）或序号（多张时）做文件名（填写的话会用名字_序号作为文件名），如果只保存一张则不会添加序号<br/>
suffix     文件后缀名<br/>
black        是否包含纯黑的切片，如果包含的话就是True（默认），如果希望不包含的话就是False。如果是其他情况需要判断是否是纯黑切片请参照loader.blackMap ，这个内部数组内存储了纯黑图片的下标<br/>

</p>
<code>
  loader.save()
  </code>
  <h3>MultipleMRILoader类（适用于读取复数MRI文件）</h3>
  <h4>构造函数</h4>
  <p>
  这里的路径需要使用glob表达式传入需要的文件，可以使用*作为通配符，不能直接传入文件夹路径。<br/>
  提示：*.nii 代表后缀名为nii的文件，*.nii*代表，包含.nii的文件，例如.nii、.nii.gz。<br/>
  例如我们想要获取data文件夹（与当前文件在同一文件夹时）下所有子文件夹里的nii和nii.gz文件时，就可以使用 ./data/*/*.nii*。
</p>
  <code>
  loaders = MultipleMRILoader('./data/*/T1w*.nii*')
  </code>
<h4>.getNormalizeSlicesTernary()</h4>
   <p>
  获取三通道化后的MRI切片图，如果没有三通道化会自动进行三通道化（同样如果没有归一化，会先进行归一化再进行三通道化）
拿到的图片数据列表维度是以(文件序号,切片序号,w，h)的方式排列的
</p>
<code>
  normalizeSlicesTernary=loaders.getNormalizeSlicesTernary()
  </code>
  
  <h4>.save(savePath="./save/", r=None, folderName="", fileName="", suffix=".jpg", num=None, black=True)</h4>
   <p>
  用于批量保存MRI图片<br/>
savePath   存储路径<br/>
r           范围，默认是全部，传入数字就是第n张，数组就是范围，如果数组中有多个值，那会用第一个和最后一个作为范围。<br/>
folderName  文件夹名，每个MRI文件的切片都分别创建文件夹存储，文件夹名为folderName序号，如果不设置则用序号作为各组MRI切片的文件夹名。要注意如果只保存一个MRI文件的话，默认不会额外为此MRI的切片创建文件夹，但是如果设置了文件夹名则会进行创建。<br/>
fileName   文件名,不填就用MRI（单张时）或序号（多张时）做文件名（填写的话会用名字_序号作为文件名），如果只保存一张则不会添加序号。<br/>
suffix     文件后缀名。<br/>
num          指定只保存第num个MRI文件，超出上限会自动改为最后一个。<br/>
black        是否包含纯黑的切片，如果包含的话就是True（默认），如果希望不包含的话就是False。如果是其他情况需要判断是否是纯黑切片请参照loader.blackMap ，这个内部数组内存储了纯黑图片的下标。<br/>
</p>
<code>
  loaders.save()
  </code>
