# MRILoader
<h1>MRILoader</h1>
<h2>介绍</h2>
<p>
  本项目主要解决了nii、nii.gz格式的MRI图像单通道，且没有被归一化的问题，同时提供了一些辅助函数。用于解析MRI核磁共振图像（nii、nii.gz）的包。拥有MRILoader和MultipleMRILoader两个类。
</p>
<h2>准备</h2>
<p>依赖及环境</p>
<code>
  Python 3.7
  opencv
  numpy
  SimpleITK
</code>
<p>
由于是一个轻量级项目，我们直接提供了MRILoader.py文件，放入项目适当的文件夹内即可。之后在适当的文件内进行引用。
</p>
<code>
from MRILoader import MRILoader,MultipleMRILoader
</code>
<p>
可以使用test.py文件对类进行测试。
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
  <h3>MultipleMRILoader类（适用于读取复数MRI文件）</h3>
  <h4>构造函数</h4>
  <p>
  这里的路径需要使用glob表达式传入需要的文件，可以使用*作为通配符，不能直接传入文件夹路径。
  提示：*.nii 代表后缀名为nii的文件，*.nii*代表，包含.nii的文件，例如.nii、.nii.gz。
  例如我们想要获取data文件夹（与当前文件在同一文件夹时）下所有子文件夹里的nii和nii.gz文件时，就可以使用 ./data/*/*.nii*。
</p>
  <code>
  loaders = MultipleMRILoader('./data/*/T1w*.nii*')
  </code>
