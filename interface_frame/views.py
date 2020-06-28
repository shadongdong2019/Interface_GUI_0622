import datetime
import json
import os
from pathlib import Path

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

from interface_frame.models import ProjectsManage, InterfaceDetails, InterfaceManage

#@transaction.atomic
def main_GUI(request):
    baseDir = os.path.dirname(os.path.abspath(__name__))
    show_path = ""
    file_down = ""
    report_path = ""
    pro_name = ""
    caseFile = ""
    configFile = ""
    pm = ProjectsManage.objects.filter(status=200)#查询状态正常的项目
    im= InterfaceManage.objects.filter(status=200)#查询状态正常的接口
    if request.method == "POST":
        #接口的路径根目录/项目名/接口名称/当前时间/
        nowTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S') #当前时间-用作上传文件后重命名
        pro_name = request.POST.get("pro_name","")  #项目名称
        interface_name = request.POST.get("interface_name", "")  # 接口名称
        caseFile = request.FILES.get('case_file', '')  # 获取上传的测试用例文件，如果没有文件，则默认为''
        configFile = request.FILES.get('config_file', '')  # 获取上传的配置文件，如果没有文件，则默认为''
        imageFile = request.FILES.get('image_file', '')  # 获取上传的图片文件，如果没有文件，则默认为''
        needsFile = request.FILES.get('needs_file', '')  # 获取上传的需求文档，如果没有文件，则默认为''
        pro_path = os.path.join(baseDir,"InterfaceDir/static/project_tree/{}/".format(pro_name))  #项目路径
        interface_path = os.path.join(pro_path, "{}/{}/".format(interface_name,nowTime))  # 接口路径（一个项目下可以有多个接口）

        try:
            pm = pm.get(p_name=pro_name) #确定项目名称是否存在
        except Exception as e:
            pm =  None
        try:
            im = im.get(p_id=pm.id,i_name=interface_name) #确定接口名称是否存在
        except Exception as e:
            im = None

        #创建文件路径
        deal_file_path = {}
        if not caseFile or not configFile:
            return HttpResponse("no files for upload!")
        else:
            if caseFile or configFile:
                fileDict = {
                    "caseFile": caseFile,
                    "configFile": configFile,
                    "imageFile": imageFile,
                    "needsFile": needsFile,
                }
                deal_file_path = pro_dir_deal(interface_path,pro_name, **fileDict)  # 返回测试用例文件路径，配置文件路径
            write_config_path = os.path.join(baseDir, "Interface_Auto_GUI_20200619/static/write_config/run.json")  # 写入配置文件
            with open(write_config_path, "wb") as f:
                f.write(json.dumps(deal_file_path, ensure_ascii=False, indent=4).encode(
                    "utf-8"))  # 字典转成json,字典转换成字符串 加上ensure_ascii=False以后，可以识别中文， indent=4是间隔4个空格显示

        if pm == None:  #如果项目不存在
                #新增项目
                new_pm = ProjectsManage(
                        p_name=pro_name,
                        p_path=pro_path,
                        adder='majing'
                    )
                new_pm.save()
                #新增接口
                new_im = InterfaceManage(
                        p_id=new_pm.id,
                        p_name=new_pm.p_name,
                        i_name=interface_name,
                        p_path=interface_path,
                        adder='majing',
                    )
                new_im.save()

                #将文件路径写入数据库中存储
                InterfaceDetails(
                    p_id=new_pm.id,  # 所属项目ID
                    p_name =new_pm.p_name,  # 所属项目名称
                    i_id = new_im.id,  # 所属接口ID
                    i_name = new_im.i_name,  # 所属接口名称
                    case_path =  deal_file_path['caseFile'], #测试用例路径
                    config_path = deal_file_path['configFile'],  #配置文件路径
                    image_path = deal_file_path['imageFile'], #图片路径
                    needs_path = deal_file_path['needsFile'], #需求文档路径
                    report_path = deal_file_path['report_path'], #测试报告路径
                    download_path = deal_file_path['download_path'], #下载文件路径
                    adder = 'majing',  # (id)操作人用户名；前面应记录用户ID
                ).save()

        else:#如果项目存在
            if im == None: #如果接口不存在
                # 新增接口
                new_im = InterfaceManage(
                    p_id=pm.id,
                    p_name=pm.p_name,
                    i_name=interface_name,
                    p_path=interface_path,
                    adder='majing',
                )
                new_im.save()
                im = new_im
            # 将文件路径写入数据库中存储（接口详情这个表设计为每执行一次测试新增一条记录，目的是为了之后好统计共做过多少次测试，且保存每次的测试报告）
            InterfaceDetails(
                p_id=pm.id,  # 所属项目ID
                p_name=pm.p_name,  # 所属项目名称
                i_id=im.id,  # 所属接口ID
                i_name=im.i_name,  # 所属接口名称
                case_path=deal_file_path['caseFile'],  # 测试用例路径
                config_path=deal_file_path['configFile'],  # 配置文件路径
                image_path=deal_file_path['imageFile'],  # 图片路径
                needs_path=deal_file_path['needsFile'],  # 需求文档路径
                report_path=deal_file_path['report_path'],  # 测试报告路径
                download_path=deal_file_path['download_path'],  # 下载文件路径
                adder='majing',  # (id)操作人用户名；前面应记录用户ID
            ).save()

        from interface_frame import case_test_common
        report_path = case_test_common.main()
        show_path = report_path[report_path.index("/static"):]  # 显示单个测试报告路径
        file_down = '/file_download?report_path={}'.format(report_path)

        # deal_file_path ={}
        # if not caseFile and not os.path.isfile(case_file_path): #get_dir_file
        #     if get_dir_file(case_file_path):
        #         case_file_path = case_file_path+get_dir_file(case_file_path)[0]
        #         deal_file_path["caseFile"] = case_file_path
        #     else:
        #         return HttpResponse("no files for upload!")
        # if not configFile and not os.path.isfile(config_file_path):
        #     if get_dir_file(config_file_path):
        #         config_file_path = config_file_path+get_dir_file(config_file_path)[0]
        #         deal_file_path["configFile"] = config_file_path
        #     else:
        #         return HttpResponse("no files for upload!")



        show_all_path = report_path[:report_path.index("/report")]  # 显示项目下所有测试报告路径


    else:
        pass

    content = {
        'show_path':show_path,
        'file_down':file_down,
        'report_path':report_path,
        'pro_name':pro_name,
        'caseFile':caseFile,
        'configFile':configFile,
        'pm':pm,
        'im':im,
    }
    return render(request,"index.html",content)



def upload_file(uploadFile,filePathDict):
    '''
    :param request:
    :param myFile: 文件流
    :param path: 上传文件存储路径
    :param suffix: 后缀名
    :return:
    '''
    ret_filename = ""
    try:
        for filePath in filePathDict.values():
            filename = os.path.join(filePath, uploadFile.name)
            fobj = open(filename, 'wb')# 打开特定的文件进行二进制的写操作
            for chrunk in uploadFile.chunks():  # 分块写入文件
                fobj.write(chrunk)
            fobj.close()
            if "case_file" in filePath or "config" in filePath :
                ret_filename = filename
    except Exception as e :
        ret_filename = filePath
    return ret_filename


def pro_dir_deal(interface_path,pro_name,**fileDict):
    '''
    创建对应项目和接口目录
    :interface_path: 接口路径地址
    :param pro_name: 项目名称
    :param fileDict: 存入需要创建目录的文件名称字典
    :return: 具体路径的字段
    '''
    deal_file_path = {}
    baseDir = os.path.dirname(os.path.abspath(__name__))
    pro_dir = ''
    filePathDict = {}
    try:

        if pro_name:
            #pro_dir = os.path.join(interface_path, "{}".format(pro_name))
            if not os.path.exists(interface_path):
                os.makedirs(interface_path)
                os.makedirs(os.path.join(interface_path, "config"))
                os.makedirs(os.path.join(interface_path, "case_file"))
                os.makedirs(os.path.join(interface_path, "image"))
                os.makedirs(os.path.join(interface_path, "report"))
                os.makedirs(os.path.join(interface_path, "file_stream")) #用例中使用的图片或其它文件
                os.makedirs(os.path.join(interface_path, "needs")) #需求文档存储
                os.makedirs(os.path.join(interface_path, "download"))  # 存储下载文档

        # filePath1 = os.path.join(baseDir, "static/case")
        # filePathDict["filePath1"] = filePath1
        if interface_path:
            for key  in fileDict.keys():
                if key == "caseFile":
                    filePath2 = os.path.join(interface_path, "case_file")
                    filePathDict["filePath2"]=filePath2
                    filename = upload_file(fileDict.get(key), filePathDict)
                  #  os.rename(filename,)
                    deal_file_path["caseFile"] = filename
                elif key == "configFile":
                    filePath2 = os.path.join(interface_path, "config")
                    filePathDict["filePath2"] = filePath2
                    filename = upload_file(fileDict.get(key), filePathDict)
                    deal_file_path["configFile"] = filename
                elif key == "imageFile":
                    filePath2 = os.path.join(interface_path, "image")
                    filePathDict["filePath2"] = filePath2
                    filename = upload_file(fileDict.get(key), filePathDict)
                    deal_file_path["imageFile"] = filename
                elif key == "needsFile":
                    filePath2 = os.path.join(interface_path, "needs")
                    filePathDict["filePath2"] = filePath2
                    filename = upload_file(fileDict.get(key), filePathDict)
                    deal_file_path["needsFile"] = filename

            deal_file_path["report_path"] = os.path.join(interface_path, "report") #测试报告生成路径
            deal_file_path["download_path"] = os.path.join(interface_path, "download") #下载接口文件生成路径
            return deal_file_path

    except Exception as e :
        pass
    return deal_file_path



def file_down(request,file_path=None):
    file_path = request.GET.get("report_path")
    p = Path(file_path)
    report_name = p.name
    file=open(file_path,'rb')
    response =HttpResponse(file)
    response['Content-Type']='application/octet-stream'
    response['Content-Disposition']='attachment;filename={}'.format(report_name)
    return response



def get_all_path(request,root_path='',file_list=[],dir_list=[]):
    '''
    查询指定目录下所有文件
    :param request:
    :param root_path: 指定路径
    :return: 所有文件路径列表
    '''

    #获取该目录下所有的文件名称和目录名称
    dir_or_files = os.listdir(root_path)
    query_date = request.GET.get("date")
    report_path = request.GET.get("report_path")

    for dir_file in dir_or_files:
        file_opera = []
        #获取目录或者文件的路径
        dir_file_path = os.path.join(root_path,dir_file)
        #判断该路径为文件还是路径
        if os.path.isdir(dir_file_path):
            dir_list.append(dir_file_path)
        else:
            p = Path(dir_file_path)
            report_name = p.name
            show_path = dir_file_path[dir_file_path.index("/static"):]  # 显示单个测试报告路径
            file_down = '/file_download?report_path={}'.format(dir_file_path)
            file_opera.append(report_name)
            file_opera.append(show_path)
            file_opera.append(file_down)
        file_list.append(file_opera)
    return file_list


def get_dir_file(path,type="files"):
    for root, dirs, files in os.walk(path):
        if type == "root":
            return root  # 当前目录路径
        elif type == "dirs":
            return dirs  # 当前路径下所有子目录
        else:
            return files # 当前路径下所有非目录子文件
