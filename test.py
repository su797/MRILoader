from MRILoader import MRILoader,MultipleMRILoader

"""
示例路径为在与test文件同级中，有一个名为data的文件夹，里面有多个子文件夹，子文件夹内有多个nii.gz文件，只读取T1W开头的文件的情况。
"""
#因为save方法基本上会调用绝大部分的核心处理方法，因此使用save方法进行测试。

# 加载单一MRI文件时
MRIPath='./data/CC001/T1w_bscorr_SS.nii.gz'#请自行更改MRI文件地址
loader = MRILoader(MRIPath)
arr=loader.getMultiplePositionSlices()

loader.display(150,arr[0])

# loader.save()#默认存储到save文件夹
#
# # 加载多个MRI文件时
# MRIPath='./data/*/T1w*.nii*'#请自行更改MRI文件路径，注意这里是glob格式的路径，而不是文件夹路径
# # 提示：*.nii 代表后缀名为nii的文件，*.nii*代表，包含.nii的文件，例如.nii、.nii.gz。
# # 例如我们想要获取data文件夹（与当前文件在同一文件夹时）下所有子文件夹里的nii和nii.gz文件时，就可以使用 ./data/*/*.nii*
#
# loaders = MultipleMRILoader(MRIPath)  # 这里的路径需要使用glob表达式传入需要的文件，可以使用*作为通配符，不能直接传入文件夹路径
# # 保存全部切片
# loaders.save()



