import os
import copy
import shutil
import json

# 注意, remove函数要慎用!

down_dir=r'D:/转换前-崔庆才python视频' #down for download
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
        copy_filename_list=copy.deepcopy(filename_list)
        aid=root.split(os.sep)[-2] # root结构大概是这样:['D:/转换前-两个python视频', '14184325', '182']
        assert aid in aids
        assert aid in aids_epis
        '''<这里定义三个完全一样的变量>'''
        parent_dirname=root.split(os.sep)[-1] # 结构大概是这样:['D:/转换前-两个python视频', '14184325', '182']
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
                shutil.copy(os.path.abspath(filename),os.path.join(tar_dir,aid,filename))
            if filename.endswith('.flv'):
                os.chdir(root) # 写两遍因为不知道info和flv哪个先读取到
                # print(aid,flv_idx)
                if not '{}_{}_whole.flv'.format(aid,flv_idx) in os.listdir(root):
                    with open(apath_inputs,'a',encoding='utf-8') as f:
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
                        print('Sight!')
                        apath_new_whole=os.path.join(tar_dir,aid,whole_flvname)
                        os.chdir(root)
                        # print(os.path.exists(os.path.join(tar_dir,aid)))
                        if not os.path.exists(os.path.join(tar_dir,aid)):
                            os.mkdir(os.path.join(tar_dir,aid))
                        if not os.path.isfile(apath_new_whole): 
                            os.rename(apath_whole_flv,apath_new_whole)
            

for aid in aids:
    cnt=0
    flv_dir=os.path.join(tar_dir,aid)
    os.chdir(flv_dir)
    for filename in os.listdir(flv_dir):
        copy_flv_dir=copy.deepcopy(os.listdir(flv_dir))
        # print('Copy:',copy_flv_dir)
        if filename.endswith('.info'):
            apath_old_flv=os.path.abspath(filename).replace('.info','')+'_whole.flv'
            flv_idx=filename.split('_')[-1].replace('.info','')
            # print('flv_idx',flv_idx)
            with open(filename,'r',encoding='utf-8') as f: # 怎么老爱忘encoding呀
                reader=f.read()
                reader_dict=json.loads(reader)
                flv_title,flv_partname=reader_dict['Title'],reader_dict['PartName'] # title 是大标题; partname是小标题
                # 靠, 我de了半天发现是人家原来标题就有下划线, 赣!
                # print(flv_title,flv_partname)
                if '_' in flv_title:
                    flv_title=flv_title.replace('_','c')
                if '_' in flv_partname:
                    flv_partname=flv_partname.replace('_','c') # c for connection.
                # 此时title和partname中没有_了
                new_flv_name='_'.join(('第{}集'.format(flv_idx),flv_partname))+'.flv' # 注意, join只接受一个传参, 你要把这些括在一个元组里
                apath_new_flv=os.path.join(flv_dir,new_flv_name)
                if os.path.exists(apath_old_flv) and not os.path.exists(apath_new_flv):
                    os.rename(apath_old_flv,apath_new_flv)
                file_idx=copy_flv_dir.index(filename)
                del copy_flv_dir[file_idx]
            os.remove(filename)
        
        if filename.endswith('.flv'):
            file_idx=copy_flv_dir.index(filename)
            del copy_flv_dir[file_idx]
        # if not copy_flv_dir: # 表示读到了末尾
    os.chdir(tar_dir)
    os.rename('./{}'.format(aid),'./{}'.format(flv_title))
print('ter')        


        
        
                    

