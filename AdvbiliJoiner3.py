import os
import copy
import shutil
import json
import re
#---------------Up is std; Below is self-designed modules.------------------#
import fileReseter3
# 注意, remove函数要慎用!

# upOrHost='host'

down_dir=r'D:/转换前' #down for download
tar_dir=r'D:/转换后' # tar for target
raw_core_comm='ffmpeg -f concat -safe 0 -i inputs.txt -c copy whole.flv'

if not os.path.exists(tar_dir):
    os.mkdir(tar_dir)
aids=[each for each in os.listdir(down_dir) if each.isdigit()]
epi_cnts=[]
for aid in aids:
    epi_cnts.append(0)
    for each in os.listdir(os.path.join(down_dir,aid)):
        if each.isdigit():
            epi_cnts[-1]+=1
    # epi_cnts.append(len(os.listdir(down_dir,aid))-3) # 此处-3是因为一般都有剩下三个文件(不够保险)

print(aids,epi_cnts)
aids_epis=dict(zip(aids,epi_cnts))

cur_aid=-1
# 这个是在单个

for root,dirs,filename_list in os.walk(down_dir):
    # name=没有os-sep, 但是有后缀名
    # apath, 绝对地址, 有后缀名
    if not dirs:
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
                # with open(filename,'r',encoding='utf-8') as f:
                #     if json.loads(f.read())['SeasonId']:
                #         upOrHost='host'
                #     else:
                #         upOrHost='up'
                shutil.copy(os.path.abspath(perfect_infoName),os.path.join(tar_dir,aid,perfect_infoName)) # 注意细节, 这两处要写成per而不是filename
            if filename.endswith('.flv'):
                os.chdir(root) # 写两遍因为不知道info和flv哪个先读取到
                # print(aid,flv_idx)
                if not '{}_{}_whole.flv'.format(aid,flv_idx) in os.listdir(root):
                    with open(apath_inputs,'a+',encoding='utf-8') as f:
                        read_list=f.readlines()
                        read_set=set(read_list)
                        if len(read_list)!=len(read_set):
                            print('出现重写现象!')
                            f.truncate()
                        f.write("file '{}'\n".format(os.path.abspath(filename))) # 注意要用单引号括起来
                else:
                    # print('I break here.')
                    break
            if filename.endswith('.xml') or filename.endswith('.txt') or filename.endswith('.flv') or filename.endswith('.info'): # b站文件还有一个xml;因为会有inputs生成
                file_idx=copy_filename_list.index(filename)
                del copy_filename_list[file_idx]
            # print('whole:{};info:{}'.format(wholes_cnt,info_cnt))
            if not copy_filename_list: # 读到最后一个, 并且肯定已经完成了flv和info的判定; 这里本来想说因为whole文件应该是同步读取的,唉
                # print('Now empty!')
                os.chdir(root)
                core_comm='ffmpeg -f concat -safe 0 -i {} -c copy {}'.format(inputs_filename,whole_flvname)
                os.system(core_comm)
                # assert whole_flvname in os.listdir(root)
                # print(os.listdir(root))
                for file_after in os.listdir(root): # 这里估计不能用filenamelist, 因为生成了新文件, 不知道filenamelist有没有更新
                    if file_after==whole_flvname: 
                        # print('Sight!')
                        # apath_new_whole=os.path.join(tar_dir,aid,whole_flvname)
                        os.chdir(root)
                        with open(whole_flvname.replace('_whole.flv','')+'.info','r',encoding='utf-8') as f:
                            reader=f.read()
                            reader_dict=json.loads(reader)
                            flv_title,flv_partName=reader_dict['Title'],reader_dict['PartName']
                            if flv_partName is None:
                                assert reader_dict['Description']
                                flv_partName=reader_dict['Description']
                                # upOrHost='host'
                            # else:
                                # upOrHost='up'
                            # if flv_idx is None:
                            #     flv_idx=whole_flvname.replace('_whole.flv','').split('_')[-1]
                            new_whole_name='第{}集-'.format(flv_idx)+flv_partName+'.flv'
                            apath_new_whole=os.path.join(tar_dir,flv_title,new_whole_name)
                        # with open()
                        if not os.path.exists(os.path.join(tar_dir,flv_title)):
                            os.mkdir(os.path.join(tar_dir,flv_title))
                        if not os.path.isfile(apath_new_whole): 
                            os.rename(apath_whole_flv,apath_new_whole)
# print(upOrHost)
# if upOrHost=='host':
    # cur_title='-1'
os.chdir(tar_dir)
possible_patt=re.compile('(.*?)\\d{1,2}\.')
for each in os.listdir(tar_dir):
    idf=re.findall(possible_patt,each)
    if bool(idf)==0:
        pass
    else:
        print(idf)
        print(re.findall('(.*?)\\d{1,2}\.',each))
        season_title=re.findall('(.*?)\\d{1,2}\.',each)[0].replace(' ','')
        # season_title.strip()
        # print(season_title.split())
        print('找到番剧, 名字是:{}'.format(season_title))
        if not os.path.exists('./{}'.format(season_title)):
            os.mkdir('./{}'.format(season_title))
        flv_name=os.path.abspath(os.listdir(each)[0]).split(os.sep)[-1]
        # os.chdir()
        print(flv_name)
        print(each)
        print(os.path.abspath(each)) # 妈的这个路径真整死人!

        shutil.move(os.path.abspath(each)+os.sep+flv_name,os.path.join(tar_dir,season_title,flv_name))

#     # common_titles=[re.findall('(.*?)\\d{1,2}\.',each)[0] for each in tar_dir if re.findall('(.*?)\\d{1,2}',each)]
#     # if not title is None:
# # elif upOrHost=='up':
# #     print('up主上传的')
# #     pass
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
                break # 忘记break就会一直报错WinError3
fileReseter3.fileReset(down_dir)
