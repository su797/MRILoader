import cv2
import numpy as np
import SimpleITK as sitk
import os
# glob在方法内被引用

#version 1.2 2022/4/19

class MRILoader:
    #
    '''
       path nii数据的路径
       postion MRI的切片维度方位，接收值为三个成员的元组或字符串。
                传入元组时，基于numpy的transpose方法，通过调换维度的方式更改MRI切片方向，如果不知道如何调换可以传入字符串由方法自动调换。
                传入元组时可以使用，rot90（基于numpy的rot90方法）、flip（基于numpy的flip方法）参数调节视图方向
                传入字符串时，以下分别代表三个视图
                    axial或transverse    水平断面
                    coronal              冠状面
                    sagittal             矢状面
                但要注意，由于传入数据的不同，可能无法正确读取对应面，请自行确认。
                传入字符串时同样可以使用rot90、flip参数调节视图方向，如果不传入rot90和flip，将由方法内置逻辑对切片方位进行处理。
        rot90   切片旋转，以90度为单位，传入正值为逆时针，负值为顺时针，传入1代表逆时针旋转90度，2代表逆时针旋转180度，-1代表顺时针旋转90度，以此类推。
                但要注意，MRI较为特殊，有时并不会以期待的方式运行，需要自行调节。
        flip    切片翻转，输入值为维度，输入0为上下翻转，输入1为左右翻转。
                但要注意，MRI较为特殊，有时并不会以期待的方式运行，需要自行调节。
    '''
    def __init__(self, path,position=None,rot90=None,flip=None):
        # 初始化成员
        self.imageObj = sitk.ReadImage(path)  # 获取图片数据（nii）
        self.slices = sitk.GetArrayViewFromImage(self.imageObj)  # 从视图中获取所有图片
        if position is not None:
            self.slices=self.changePosition(self.slices, position,rot90,flip)
        self.normalizeSlices = None         # 存储归一化后的切片图片数组（MRI单层图）
        self.noBlackNormalizeSlices=None
        self.normalizeSlicesTernary = None  # 存储三通道化（RGB三通道）后的切片数组（MRI单层图）
        self.noBlackNormalizeSlicesTernary=None

        self.blackMap = []                  # 存储了纯黑切片的下标
    '''
        获取指定方位的MRI图
        slices  MRI切片数组（必须是并未经本方法或其他方法改变数组维度的原始数组）
        postion 维度方位，接收值为三个成员的元组或字符串。
                传入元组时，基于numpy的transpose方法，通过调换维度的方式更改MRI切片方向，如果不知道如何调换可以传入字符串由方法自动调换。
                传入元组时可以使用，rot90（基于numpy的rot90方法）、flip（基于numpy的flip方法）参数调节视图方向
                传入字符串时，以下分别代表三个视图
                    axial或transverse    水平断面
                    coronal              冠状面
                    sagittal             矢状面
                但要注意，由于传入数据的不同，可能无法正确读取对应面，请自行确认。
                传入字符串时同样可以使用rot90、flip参数调节视图方向，如果不传入rot90和flip，将由方法内置逻辑对切片方位进行处理。
        rot90   切片旋转，以90度为单位，传入正值为逆时针，负值为顺时针，传入1代表逆时针旋转90度，2代表逆时针旋转180度，-1代表顺时针旋转90度，以此类推。
                但要注意，MRI较为特殊，有时并不会以期待的方式运行，需要自行调节。
        flip    切片翻转，输入值为维度，输入0为上下翻转，输入1为左右翻转。
                但要注意，MRI较为特殊，有时并不会以期待的方式运行，需要自行调节。
    '''
    def getChangePostionSlices(self,slices,position,rot90=None,flip=None):
        # 以指定方向获取切片
        slices = np.array(np.transpose(slices, position))
        # 如果要进行旋转
        if rot90 is not None:
            slices = np.rot90(slices, rot90)
        # 如果要进行翻转
        if flip is not None:
            slices = np.flip(slices, flip)
        # 返回结果
        return slices
    '''
        更改为指定方位的MRI图
        调用getChangePostionSlices方法，同样可以设置以下参数
        slices  MRI切片数组（必须是并未经本方法或其他方法改变数组维度的原始数组）
        postion 维度方位，接收值为三个成员的元组或字符串。
                传入元组时，基于numpy的transpose方法，通过调换维度的方式更改MRI切片方向，如果不知道如何调换可以传入字符串由方法自动调换。
                传入元组时可以使用，rot90（基于numpy的rot90方法）、flip（基于numpy的flip方法）参数调节视图方向
                传入字符串时，以下分别代表三个视图
                    axial或transverse    水平断面
                    coronal              冠状面
                    sagittal             矢状面
                但要注意，由于传入数据的不同，可能无法正确读取对应面，请自行确认。
                传入字符串时同样可以使用rot90、flip参数调节视图方向，如果不传入rot90和flip，将由方法内置逻辑对切片方位进行处理。
        rot90   切片旋转，以90度为单位，传入正值为逆时针，负值为顺时针，传入1代表逆时针旋转90度，2代表逆时针旋转180度，-1代表顺时针旋转90度，以此类推。
                但要注意，MRI较为特殊，有时并不会以期待的方式运行，需要自行调节。
        flip    切片翻转，输入值为维度，输入0为上下翻转，输入1为左右翻转。
                但要注意，MRI较为特殊，有时并不会以期待的方式运行，需要自行调节。
    '''
    def changePosition(self,slices,position,rot90=None,flip=None):
        # 如果传入的是列表或元组
        if isinstance(position,list) or isinstance(position,tuple):
            return self.getChangePostionSlices(slices,position,rot90,flip)
        elif isinstance(position,str):
            if "axial" in position or "transverse" in position or position=="z":
                #水平面
                return self.getChangePostionSlices(slices, (0,1,2), rot90 if rot90 is not None else 2, flip if flip is not None else 0)
                # return np.array(np.flip(np.rot90(np.transpose(self.slices, (0,1,2)),2),0))
            elif "coronal" in position or position=="x":
                #冠状面
                return self.getChangePostionSlices(slices, (0,1,2), rot90 if rot90 is not None else -1, flip)
                # return np.array(np.rot90(np.transpose(self.slices, (0,1,2)),-1))
            elif "sagittal" in position or position=="y":
                #矢状面
                return self.getChangePostionSlices(slices, (2,0,1), rot90 if rot90 is not None else 2, flip if flip is not None else 2)
                # return np.array(np.flip(np.rot90(np.transpose(self.slices, (2,0,1)),2),2))
            # 如果文本不对
            print("\033[31m MRILoader Warning: illegal field '"+str(position)+"'.Didn't change the orientation of the slice.Please use these parameters postion=[axial、transverse、coronal、sagittal] or [z、x、y].\033[0m")
        print("\033[31m MRILoader Warning:Please check whether the 'position' parameters are wrong.Cannot be "+str(position)+"\033[0m")
        return slices
    # 对读取到的图片进行归一化
    # 因为我们拿到的nii图片是单通道，且像素值不定，超过255，因此对每张图片都需要进行归一化处理
    def normalize(self):
        print("Start normalization...")
        self.normalizeSlices = np.zeros(self.slices.shape)  # 初始化，创建一
        # 个同样大小的数组存储归一化后的值
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
        '''
            深度学习预处理时（需要先归一化）
            使用pytorch的话可以用
            tf=Transform.Compose([
            lambda x:Image.open(x).convert('RGB'),
            transform.toTensor()]
            或
            tf=Transform.Compose([
            transforms.Grayscale(num_output_channels=3),
            transforms.toTensor()]
            进行转换
        '''
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
    # black        是否包含纯黑的切片，如果包含的话就是True（默认），如果希望不包含的话就是False
    def getNormalizeSlices(self,black=True):
        # 如果没被归一化，则需要先归一化
        if self.normalizeSlices is None:
            self.normalize()
        # 如果不要纯黑色切片
        if black == False:
            if self.noBlackNormalizeSlices is None:
                self.noBlackNormalizeSlices=[]
                for i in range(len(self.normalizeSlices)):
                    if i not in self.blackMap:
                        self.noBlackNormalizeSlices.append(self.normalizeSlices[i])
            return self.noBlackNormalizeSlices

        # 返回归一化后的数组
        return self.normalizeSlices

    # 获取三通道化后的数组
    # black        是否包含纯黑的切片，如果包含的话就是True（默认），如果希望不包含的话就是False
    def getNormalizeSlicesTernary(self,black=True):

        # 如果没被三通道化，就进行三通道化
        if self.normalizeSlicesTernary is None:
            self.normalizeSlicesToTernary()
        # 如果不要纯黑色切片
        if black == False:
            if self.noBlackNormalizeSlicesTernary is None:#当前没有三通道去黑色切片的数组
                self.noBlackNormalizeSlicesTernary=[]
                for i in range(len(self.normalizeSlicesTernary)):#遍历三通道化后的数组
                    if i not in self.blackMap:#如果当前不在黑色切片数组内
                        self.noBlackNormalizeSlicesTernary.append(self.normalizeSlicesTernary[i])#添加到去黑色切片数组
            return self.noBlackNormalizeSlicesTernary
        # 返回归一化后的数组
        return self.normalizeSlicesTernary


# 用于多个MRI加载（依赖MRILoader）
class MultipleMRILoader:
    '''
    path，文件路径，支持glob语法
    postion MRI的切片维度方位，接收值为三个成员的元组或字符串。
                传入元组时，基于numpy的transpose方法，通过调换维度的方式更改MRI切片方向，如果不知道如何调换可以传入字符串由方法自动调换。
                传入元组时可以使用，rot90（基于numpy的rot90方法）、flip（基于numpy的flip方法）参数调节视图方向
                传入字符串时，以下分别代表三个视图
                    axial或transverse    水平断面
                    coronal              冠状面
                    sagittal             矢状面
                但要注意，由于传入数据的不同，可能无法正确读取对应面，请自行确认。
                传入字符串时同样可以使用rot90、flip参数调节视图方向，如果不传入rot90和flip，将由方法内置逻辑对切片方位进行处理。
        rot90   切片旋转，以90度为单位，传入正值为逆时针，负值为顺时针，传入1代表逆时针旋转90度，2代表逆时针旋转180度，-1代表顺时针旋转90度，以此类推。
                但要注意，MRI较为特殊，有时并不会以期待的方式运行，需要自行调节。
        flip    切片翻转，输入值为维度，输入0为上下翻转，输入1为左右翻转。
                但要注意，MRI较为特殊，有时并不会以期待的方式运行，需要自行调节。
    '''
    def __init__(self, path,position=None,rot90=None,flip=None):
        import glob
        # 获取路径下所有nii文件
        self.pathArr = glob.glob(path)  # 获取文件路径
        self.normalizeSlicesTernary = None  # 三通道化对象
        self.notBlackNormalizeSlicesTernary = None  # 三通道化对象
        self.normalizeSlices= None  # 归一化对象
        self.notBlackNormalize = None  # 三通道化对象

        self.loaders = []  # 加载器对象
        for i in range(len(self.pathArr)):  # 为每张图片创建对象
            self.loaders.append(MRILoader(self.pathArr[i],position=None,rot90=None,flip=None))  # 以此进行初始化，并存储加载器数组

    # 避免在三通道化后重复归一化，在这里不提供归一化后的数组的返回（毕竟一般也用不到）
    # 批量获取归一化数组
    # black        是否包含纯黑的切片，如果包含的话就是True（默认），如果希望不包含的话就是False
    def getNormalizeSlices(self,black=True):
        #如果不包含纯黑色切片
        if black is False:
            if self.notBlackNormalize is None:  # 如果为None就依次进行初始化创建
                self.notBlackNormalize = []
                # 初始化加载器
                for i in range(len(self.loaders)):
                        self.notBlackNormalize.append(self.loaders[i].getNormalizeSlices(black))
            return self.notBlackNormalize  # 返回三通道化图数组
        else:
            if self.normalizeSlices is None:  # 如果为None就依次进行初始化创建
                self.normalizeSlices = []
                # 初始化加载器
                for i in range(len(self.loaders)):
                        self.normalizeSlices.append(self.loaders[i].getNormalizeSlices(black))
            return self.normalizeSlices  # 返回三通道化图数组
    # 批量获取三通道化数组
    # black        是否包含纯黑的切片，如果包含的话就是True（默认），如果希望不包含的话就是False
    def getNormalizeSlicesTernary(self,black=True):
        #如果不包含纯黑色切片
        if black is False:
            if self.notBlackNormalizeSlicesTernary is None:  # 如果为None就依次进行初始化创建
                self.notBlackNormalizeSlicesTernary = []
                # 初始化加载器
                for i in range(len(self.loaders)):
                    self.notBlackNormalizeSlicesTernary.append(self.loaders[i].getNormalizeSlicesTernary(black))
            return self.notBlackNormalizeSlicesTernary  # 返回三通道化图数组
        else:
            if self.normalizeSlicesTernary is None:  # 如果为None就依次进行初始化创建
                self.normalizeSlicesTernary = []
                # 初始化加载器
                for i in range(len(self.loaders)):
                    self.normalizeSlicesTernary.append(self.loaders[i].getNormalizeSlicesTernary(black))  # 以此进行初始化，并存储加载器数组
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
                                 black)

