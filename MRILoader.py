import cv2
import numpy as np
import SimpleITK as sitk
import os
# glob在方法内被引用

#version 1.2 2022/4/19

class MRILoader:
    # path，nii数据的路径
    def __init__(self, path):
        # 初始化成员
        self.imageObj = sitk.ReadImage(path)  # 获取图片数据（nii）
        self.slices = sitk.GetArrayViewFromImage(self.imageObj)  # 从视图中获取所有图片
        self.normalizeSlices = None         # 存储归一化后的切片图片数组（MRI单层图）
        self.normalizeSlicesTernary = None  # 存储三通道化（RGB三通道）后的切片数组（MRI单层图）
        self.blackMap = []                  # 存储了纯黑切片的下标

    # 对读取到的图片进行归一化
    # 因为我们拿到的nii图片是单通道，且像素值不定，超过255，因此对每张图片都需要进行归一化处理
    def normalize(self):
        print("Start normalization...")
        self.normalizeSlices = np.zeros(self.slices.shape)  # 初始化，创建一个同样大小的数组存储归一化后的值
        # 获取第一个维度，进行遍历
        for s in range(self.slices.shape[0]):
            # 获取当前切片
            thisSlice = self.slices[s, :, :]  # 获取单张切片（MRI图）
            # 依次对进行归一化
            # +0.000001是避免分母为0（最大值与最小值为0）的情况导致出错，因为最后要求整，不会对整体造成太大影响，可以维持在噪声在范围
            # 方法1
            # thisSlice = (thisSlice - thisSlice.min()) / (thisSlice.max() - thisSlice.min() + 0.000001) * 255
            # 方法2
            max = thisSlice.max()  # 获取最大值
            weight = 0  # 设置权重
            if max > 0:  # 如果max大于0,则可以计算权重，否则就是0
                weight = 255 / max
            else:
                self.blackMap.append(s)  # 记录纯黑的下标
            thisSlice = thisSlice * weight  # 为切片加权
            self.normalizeSlices[s, :, :] = thisSlice.astype(np.uint8)  # 转换为uint8 0~255
        print("Complete normalization!")  # 完成归一

    # 转换为三通道图片
    def normalizeSlicesToTernary(self):
        # 判断是否已经归一化，如果没有则先进行归一化
        if self.normalizeSlices is None:
            self.normalize()
        print("Start Ternization...")
        dimension = list(self.slices.shape)  # 获取切片数据维度
        dimension.append(3)  # 增加颜色通道
        self.normalizeSlicesTernary = np.zeros(dimension)  # 三通道化的图片数组（RGB三通道），但是因为是单通道转多通道，所以通道顺序无所谓
        # 遍历切片
        for s in range(self.slices.shape[0]):
            # 获取当前切片
            thisSlice = self.normalizeSlices[s, :, :]
            # 融合新的三通道
            self.normalizeSlicesTernary[s] = cv2.merge((thisSlice, thisSlice, thisSlice))
        self.normalizeSlicesTernary = self.normalizeSlicesTernary.astype(
            np.uint8)  # 转换为无符号int 8（0~255），必须要注意，这里如果不转换opencv等无法识别
        print("Complete Ternization!")

    # 显示指定的图片，num为切片序号
    def display(self, num=0):
        # 如果没有进行正则三通道化，就先进行
        if self.normalizeSlicesTernary is None:
            self.normalizeSlicesToTernary()
        # 显示图片
        cv2.imshow("MRI", self.normalizeSlicesTernary[num])
        cv2.waitKey()
        cv2.destroyAllWindows()

    # 保存图片
    # savePath   存储路径，如果不存在会自动创建
    # range      范围，默认是全部，传入数字就是第n张，数组就是范围，如果数组中有多个值，那会用第一个和最后一个作为范围
    # fileName   文件名,不填就用MRI（单张时）或序号（多张时）做文件名（填写的话会用名字_序号作为文件名），如果只保存一张则不会添加序号
    # suffix     存储的文件后缀名，一般为jpg或png
    # black        是否包含纯黑的切片，如果包含的话就是True（默认），如果希望不包含的话就是False
    def save(self, savePath="./save/", r=None, fileName="", suffix=".jpg", black=True):
        # 如果没有进行正则三通道化，就先进行
        if self.normalizeSlicesTernary is None:
            self.normalizeSlicesToTernary()
        print("Save Images....")  # 开始保存图片
        # 判断是否有路径，没有的话自动添加
        if not os.path.exists(savePath):
            print("Not found save path.make the path....")
            os.makedirs(savePath)
            print("Created path:" + savePath)
        # 如果r是元组的话，转为list
        if r is isinstance(r, tuple):
            r = list(r)  # 避免是元组
        # 判断后缀名中是否有.，没有的话则添加上
        if "." not in suffix:
            suffix = "." + suffix
        # 如果r是none，就代表全部保存
        if r is None:
            if fileName is not "":
                fileName = fileName + "_"
            # 全部保存
            for i in range(self.slices.shape[0]):
                if black is False and i in self.blackMap:
                    continue
                cv2.imwrite(os.path.join(savePath, fileName + str(i) + suffix), self.normalizeSlicesTernary[i])
        elif isinstance(r, int):
            # 如果是某一张的情况
            if fileName is "":
                fileName = "MRI"

            if black is False and r in self.blackMap:
                print(
                    "This slice is a black Image！Please change parameter 'black' to True if you want to save this slice .")
                return
            # 保存图片
            cv2.imwrite(os.path.join(savePath, fileName + suffix), self.normalizeSlicesTernary[r])
        elif isinstance(r, list):
            # 如果是范围的情况
            if fileName is not "":
                fileName = fileName + "_"
            # 如果范围超过了最大上限，那就设为最大上限
            if r[-1] > self.slices.shape[0]:
                r[-1] = self.slices.shape[0]
            # 如果范围小于0，那就设为0
            if r[0] < 0:
                r[0] = 0
            # 保存图片
            for i in range(r[0], r[-1]):
                if black is False and i in self.blackMap:
                    continue
                cv2.imwrite(os.path.join(savePath, fileName + str(i) + suffix), self.normalizeSlicesTernary[i])
        print("Success! ")

    # ----------------Getter-----------------------------
    # 这里的getter用于节约步骤和流程，公共成员不使用getter也可以调用
    # 建议使用getter来访问这些数组，确保这些数组已经被初始化，或自行调用方法进行处理
    # 获取归一化后的数组
    def getNormalizeSlices(self):
        # 如果没被归一化，则需要先归一化
        if self.normalizeSlices is None:
            self.normalize()
        # 返回归一化后的数组
        return self.normalizeSlices

    # 获取三通道化后的数组
    def getNormalizeSlicesTernary(self):
        # 如果没被三通道化，就进行三通道化
        if self.normalizeSlicesTernary is None:
            self.normalizeSlicesToTernary()
        # 返回归一化后的数组
        return self.normalizeSlicesTernary


# 用于多个MRI加载（依赖MRILoader）
class MultipleMRILoader:
    # path，文件路径，支持glob语法
    def __init__(self, path):
        import glob
        # 获取路径下所有nii文件
        self.pathArr = glob.glob(path)  # 获取文件路径
        self.normalizeSlicesTernary = None  # 三通道化对象
        self.loaders = []  # 加载器对象
        for i in range(len(self.pathArr)):  # 为每张图片创建对象
            self.loaders.append(MRILoader(self.pathArr[i]))  # 以此进行初始化，并存储加载器数组

    # 避免在三通道化后重复归一化，在这里不提供归一化后的数组的返回（毕竟一般也用不到）

    # 批量获取三通道化数组
    def getNormalizeSlicesTernary(self):
        if self.normalizeSlicesTernary is None:  # 如果为None就依次进行初始化创建
            self.normalizeSlicesTernary = []
            # 初始化加载器
            for i in range(len(self.loaders)):
                self.normalizeSlicesTernary.append(self.loaders[i].getNormalizeSlicesTernary())  # 以此进行初始化，并存储加载器数组
        return self.normalizeSlicesTernary  # 返回三通道化图数组

    # 多MRI文件时的保存
    # 保存图片
    # savePath     存储路径，如果不存在会自动创建
    # r            范围，默认是全部，传入数字就是第n张，数组就是范围，如果数组中有多个值，那会用第一个和最后一个作为范围
    # folderName  文件夹名，每个MRI文件的切片都分别创建文件夹存储，文件夹名为folderName序号，如果不设置则用序号作为各组MRI切片的文件夹名。
    #             要注意如果只保存一个MRI文件的话，默认不会额外为此MRI的切片创建文件夹，但是如果设置了文件夹名则会进行创建。
    # fileName    文件名,不填就用MRI（单张时）或序号（多张时）做文件名（填写的话会用名字_序号作为文件名），如果只保存一张则不会添加序号
    # suffix      存储的文件后缀名，一般为jpg或png
    # num          指定只保存第num个MRI文件，超出上限会自动改为最后一个
    # black        是否包含纯黑的切片，如果包含的话就是True（默认），如果希望不包含的话就是False。
    def save(self, savePath="./save/", r=None, folderName="", fileName="", suffix=".jpg", num=None, black=True):
        # 如果设置了只存储某一个MRI
        if num is not None:
            # num超限的话自动改为最后一个
            if num >= len(self.loaders):
                num = len(self.loaders) - 1
                print("warning! Index exceeds limit! Changed to max index " + str(num) + ".")
            self.loaders[num].save(os.path.join(savePath, folderName), r, fileName, suffix, black)  # 保存MRI
            return
        # 遍历所有加载器保存图片
        for i in range(len(self.loaders)):
            self.loaders[i].save(os.path.join(savePath, folderName + str(i)), r, fileName, suffix,
                                 black)  # 以此进行初始化，并存储加载器数组


####################################### 示例教程部分，在引用时，请将下列部分删除后再进行使用 ######################################


###### MRILoader示例 ########

'''
加载单个MRI文件时使用MRILoader类，

方法列表
下面两个方法是用于对图片进行自动处理的，通常不需要手动调用，如果需要获取对应的值请使用Getter函数，或自行访问内部变量


.normalize(self)    
对读取到数据进行归一化，归一化后值变为0~255，但这时还不能输出，
会被getNormalizeSlices(self)、normalizeSlicesToTernary(self)自动调用

.normalizeSlicesToTernary(self)     
将归一化数据转为三通道（RGB），如果没有进行归一化，会自动进行归一化，会被
getNormalizeSlicesTernary(self)、display(self,num=0)、save(self, savePath="./save/",r=None,fileName="", suffix=".jpg")
自动调用

下面的为工具方法
.display(self,num=0)        
用于显示读取的MRI图片，无需提前调用其他方法，如果检测到未将图片处理为RGB会自动先进行处理。
num为显示第num张MRI图

.save(self, savePath="./save/",r=None,fileName="", suffix=".jpg")   
用于保存MRI图片
savePath   存储路径
range      范围，默认是全部，传入数字就是第n张，数组就是范围，如果数组中有多个值，那会用第一个和最后一个作为范围
fileName   文件名,不填就用MRI（单张时）或序号（多张时）做文件名（填写的话会用名字_序号作为文件名），如果只保存一张则不会添加序号
suffix     文件后缀名
black        是否包含纯黑的切片，如果包含的话就是True（默认），如果希望不包含的话就是False。
如果是其他情况需要判断是否是纯黑切片请参照loader.blackMap ，这个内部数组内存储了纯黑图片的下标

下面的为Getter方法
拿到的图片数据列表维度都是以(切片序号,w,h)的方式排列的

.getNormalizeSlices(self)
获取归一化后的MRI切片图，如果没有归一化会自动进行归一化

.getNormalizeSlicesTernary(self)
获取三通道化后的MRI切片图，如果没有三通道化会自动进行三通道化（同样如果没有归一化，会先进行归一化再进行三通道化）


'''

# 加载单一MRI文件时
loader = MRILoader('./data/CC003/T1w_bscorr_SS.nii.gz')  # 初始化读取MRI，尾缀可以是nii或nii.gz

# 获取归一化后的数据（无需提前手动调用归一化函数），这里获取的数据依然是单通道的，只是将像素值进行了0~255的归一化
# normalize=loader.getNormalizeSlices()

# 获取三通道化后的数据（无需提前手动调用三通道化函数），这里获取的数据就是三通道的RGB图像了。
# normalizeSlicesTernary=loader.normalizeSlicesToTernary()

# 显示第150张图片
# loader.display(150)

# 保存全部切片
loader.save()

# 保存第150张切片，其他参数设置参照前面的注释
# loader.save()#保存图片

###### MultipleMRILoader示例 ########
'''
加载多个MRI文件时使用MultipleMRILoader类，

有getNormalizeSlicesTernary和save方法，与MRILoader的使用方法基本相同
save函数的参数稍有不同，具体看方法部分的注释。
拿到的图片数据列表维度是以(文件序号,切片序号,w，h)的方式排列的

'''

# 加载多个MRI文件时
loaders = MultipleMRILoader('./data/*/T1w*.nii*')  # 这里的路径需要使用glob表达式传入需要的文件，可以使用*作为通配符，不能直接传入文件夹路径
# 提示：*.nii 代表后缀名为nii的文件，*.nii*代表，包含.nii的文件，例如.nii、.nii.gz。
# 例如我们想要获取data文件夹（与当前文件在同一文件夹时）下所有子文件夹里的nii和nii.gz文件时，就可以使用 ./data/*/*.nii*

# 获取三通道化后的图片
# normalizeSlicesTernary=loaders.getNormalizeSlicesTernary()#加载

# 保存全部切片
# loaders.save()
