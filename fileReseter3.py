import os
def fileReset(bili_root):
    for _1,_2,filenames in os.walk(bili_root):
        # print(filenames)
        for filename in filenames:
            # print(filename)
            filename=_1+'\\'+filename
            if filename.endswith('.txt'):
                os.remove(filename)
            if 'whole' in filename or 'output' in filename:
                os.remove(filename)
    print('done')
if __name__=='__main__':
    bili_root='D:/转换前'
    fileReset(bili_root)