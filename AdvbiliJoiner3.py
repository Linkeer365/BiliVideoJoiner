import os
import copy
import shutil
import json
import re
# import fileReseter3

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

# down_dir=r'D:/转换前' #down for download
# tar_dir=r'D:/转换后' # tar for target
raw_core_comm='ffmpeg -f concat -safe 0 -i inputs.txt -c copy whole.flv'

def main():
    down_dir=input('初始存储路径:[格式要求-例如:D:/转换前, 要求"转换前"这个文件夹里面放着各个番号文件夹](绝对路径, 英文输入法,正斜杠"/")')
    tar_dir=input('转存路径:(绝对路径,英文输入法,正斜杠"/")')

    if not os.path.exists(tar_dir):
        os.mkdir(tar_dir)
    aids=[each for each in os.listdir(down_dir) if each.isdigit()]
    epi_cnts=[]
    for aid in aids:
        epi_cnts.append(0)
        for each in os.listdir(os.path.join(down_dir,aid)):
            if each.isdigit():
                epi_cnts[-1]+=1
    print(aids,epi_cnts)
    aids_epis=dict(zip(aids,epi_cnts))

    for root,dirs,filename_list in os.walk(down_dir):
        if not dirs:    # name=没有os-sep, 但是有后缀名;apath, 绝对地址, 有后缀名
            print(filename_list)
            copy_filename_list=copy.deepcopy(filename_list)
            aid=root.split(os.sep)[-2] # root结构大概是这样:['D:/转换前-两个python视频', '14184325', '182']
            print(aid)
            assert aid in aids
            assert aid in aids_epis
            '''<这里定义三个完全一样的变量>'''
            parent_dirname=root.split(os.sep)[-1] # 结构大概是这样:['D:/转换前-两个python视频', '14184325', '182']
            print(parent_dirname)
            flv_idx=parent_dirname
            inputs_dirname=parent_dirname # 注意, parent_dirname就是集数, 就是inputs地址
            '''</这里定义三个完全一样的变量>'''
            inputs_filename='{}_{}_inputs.txt'.format(aid,flv_idx)
            whole_flvname='{}_{}_whole.flv'.format(aid,flv_idx)
            apath_inputs=os.path.join(root,inputs_filename)
            apath_whole_flv=os.path.join(root,whole_flvname)

            for filename in filename_list: # 此时已经到了"其中一集"文件夹下
                if filename.endswith('.info'):
                    os.chdir(root) # 进入当前文件夹
                    perfect_infoName='{}_{}.info'.format(aid,parent_dirname)
                    if not filename==perfect_infoName:
                        os.rename(filename,perfect_infoName)
                    if not os.path.exists(os.path.join(tar_dir,aid)):
                        os.makedirs(os.path.join(tar_dir,aid))
                    shutil.copy(os.path.abspath(perfect_infoName),os.path.join(tar_dir,aid,perfect_infoName)) # 注意细节, 这两处要写成per而不是filename
                if filename.endswith('.flv'):
                    os.chdir(root) # 写两遍因为不知道info和flv哪个先读取到
                    if not '{}_{}_whole.flv'.format(aid,flv_idx) in os.listdir(root):
                        with open(apath_inputs,'a+',encoding='utf-8') as f:
                            read_list=f.readlines()
                            read_set=set(read_list)
                            if len(read_list)!=len(read_set):
                                print('出现重写现象!')
                                f.truncate()
                            f.write("file '{}'\n".format(os.path.abspath(filename))) # 注意要用单引号括起来
                    else:
                        break
                if filename.endswith('.xml') or filename.endswith('.txt') or filename.endswith('.flv') or filename.endswith('.info'): # b站文件还有一个xml;因为会有inputs生成
                    file_idx=copy_filename_list.index(filename)
                    del copy_filename_list[file_idx]
                if not copy_filename_list: # 读到最后一个, 并且肯定已经完成了flv和info的判定; 这里本来想说因为whole文件应该是同步读取的,唉
                    os.chdir(root)
                    core_comm='ffmpeg -f concat -safe 0 -i {} -c copy {}'.format(inputs_filename,whole_flvname)
                    os.system(core_comm)
                    for file_after in os.listdir(root): # 这里估计不能用filenamelist, 因为生成了新文件, 不知道filenamelist有没有更新
                        if file_after==whole_flvname: 
                            os.chdir(root)
                            with open(whole_flvname.replace('_whole.flv','')+'.info','r',encoding='utf-8') as f:
                                reader=f.read()
                                reader_dict=json.loads(reader)
                                flv_title,flv_partName=reader_dict['Title'],reader_dict['PartName']
                                forbid_chars=['<','>','/','\\','|',':','"','=','*','?']
                                for char in forbid_chars: # b站题目中存在/这种地址符号的处理
                                    if char in flv_title:
                                        flv_title=flv_title.replace(char,'#')
                                    if not flv_partName is None: # 注意这里要做一个None的判定 照应下面的is None情况
                                        if char in flv_partName:
                                            flv_partName=flv_partName.replace(char,'#')
                                # flv_title=flv_title.replace()
                                # flv_title=''.join([each for each in flv_title if each not in forbid_chars])
                                # flv_partName=''.join([each for each in flv_partName if each in forbid_chars])
                                if flv_partName is None:
                                    assert reader_dict['Description']
                                    flv_partName=reader_dict['Description']
                                    for char in forbid_chars:
                                        if char in flv_partName:
                                            flv_partName=flv_partName.replace(char,'#')
                                    # flv_partName=''.join([each.replace(each,'#') for each in flv_partName if each in forbid_chars])
                                new_whole_name='第{}集-'.format(flv_idx)+flv_partName+'.flv'
                                apath_new_whole=os.path.join(tar_dir,flv_title,new_whole_name)
                            if not os.path.exists(os.path.join(tar_dir,flv_title)):
                                os.mkdir(os.path.join(tar_dir,flv_title))
                            if not os.path.isfile(apath_new_whole): 
                                os.rename(apath_whole_flv,apath_new_whole)
    os.chdir(tar_dir)
    for each in os.listdir(tar_dir):
        idf=re.findall('(.*?)\\d{1,2}\.',each)
        if bool(idf)==0:
            pass
        else:
            # print(idf)
            # print(re.findall('(.*?)\\d{1,2}\.',each))
            season_title=re.findall('(.*?)\\d{1,2}\.',each)[0].replace(' ','')
            # print('找到番剧, 名字是:{}'.format(season_title))
            if not os.path.exists('./{}'.format(season_title)):
                os.mkdir('./{}'.format(season_title))
            flv_name=os.path.abspath(os.listdir(each)[0]).split(os.sep)[-1]
            # print(flv_name)
            # print(each)
            # print(os.path.abspath(each)) # 妈的这个路径真整死人!
            shutil.move(os.path.abspath(each)+os.sep+flv_name,os.path.join(tar_dir,season_title,flv_name))
    os.chdir(tar_dir)        
    for folder in os.listdir(tar_dir):
        if not os.listdir(folder):
            os.rmdir(folder)
        else:
            for each in os.listdir(folder):
                if '.flv' in each:
                    break
                else:
                    shutil.rmtree(folder)
                    break
    fileReset(down_dir)

main()
