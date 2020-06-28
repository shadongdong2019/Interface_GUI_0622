import json

from jsonpath import jsonpath

from interface_frame.basic_config.common.interface_run import InterfaceRun

import logging
from copy import  deepcopy
import time
from interface_frame.basic_config.utils.ElasticObj import ElasticObj
from interface_frame.basic_config.utils.MongodbObj import MongodbObj
from interface_frame.basic_config.utils.MysqlObj import MysqlObj
#from interface_frame.basic_config.utils.OracleObj import OracleObj
from interface_frame.basic_config.get_data.common_param_dic import  CommonParamDict
log = logging.getLogger(__file__)
class CmpReqRes:
    '''
    对比响应结果后存入的数据与请求数据是否一致
    '''
    def __init__(self,**kwargs):
        self.kwargs = kwargs
        self.option_dict = self.kwargs.get("option_dict", {}) #获取配置文件字典
        self.inter_run = InterfaceRun()
        self.cpd = CommonParamDict()
        database_type = self.kwargs.get("database_type")
        if str(database_type).lower() == "es":
            self.conne = ElasticObj(**self.kwargs)
        elif str(database_type).lower() == "mysql":
            self.conne = MysqlObj(**self.kwargs)
        elif str(database_type).lower() == "oracle":
            self.conne = OracleObj(**self.kwargs)
        elif str(database_type).lower() == "mangodb":
            self.conne = MongodbObj(**self.kwargs)
        else:
            self.conne = None

    def verify_is_pass(self, **kwargs):
        '''
        验证响应结果是否满足预期结果
        :param expect: 预期结果
        :param res: 实际响应结果
        :return:True-代表测试通过，False-代表测试未通过
        '''
        # 是否需要验证数据库存入的数据
        is_verify_database =self.kwargs.get("is_verify_database",False)

        # 是否需要验证回调状态数据
        is_verify_callbackurl = self.kwargs.get("is_verify_callbackurl", False)
        # 是否需要验证下载文件
        is_download_verify = self.kwargs.get("is_download_verify", {})
        is_downlaod_v = is_download_verify.get("is_downlaod_v",False)
        no_request_dict = kwargs.get("no_request_dict",{})
        expect = kwargs.get("expect",None)
        res = kwargs.get("res",None)
        req = kwargs.get("req",None)
        expCallbackFlag = kwargs.get("expCallbackFlag",None)
        no_verify_data_list = kwargs.get("no_verify_data_list", None)
        database_verify_res = {}
        serialNo = None
        verify_res = {} #本方法返回验证结果字典
        expect_res_verify = False
        database_verify_res["database_flag"] = False
        database_verify_res["callbackurl_flag"] = False
        expect_is_database = False  #定义一个变量记录预期结果如果是true，可以进行数据库验证，如要是false请求失败，不进行数据库验证
        is_download = False
        try:
            if '"success":true' in expect and res.json().get("success") == True:
                expect_is_database = True
                verify_data = {
                    "serialNo":serialNo,
                    "req":req,#请求数据
                    "res":res.json(),#响数数据
                    "expCallbackFlag":expCallbackFlag,
                    "no_verify_data_list":no_verify_data_list,
                    "is_verify_database":is_verify_database,
                    "is_verify_callbackurl":is_verify_callbackurl
                }
                if  (expect_is_database and is_verify_database) or  is_verify_callbackurl:
                    #验证数据库中的值是否正确
                    database_verify_res = self.verify_database(**verify_data)
                if is_downlaod_v :
                    downlaod_dict = {
                        "CaseID": no_request_dict.get("CaseID"),  # 获取下载文件存入路径
                        "file_stream":res.json().get("fileData"), # 获取文件流
                        "file_flag":res.json().get("evidenceNo"),# 获取文件标识，用于显示在文件名最前面，如serialNo码
                        "file_type":"pdf", # 获取文件后缀类型 如：jpg/pdf
                        "download_path":self.kwargs.get("downlaod_path"),# 获取下载文件存入路径
                    }
                    is_download = self.cpd.decry(**downlaod_dict)

            expect_res_verify = self.expect_res_ispass(expect,res)
        except Exception as e:
            log.error("测试用例预期结果与实际结果对比方法出现异常，异常原因：{}".format(e))
            flag = None
        verify_res["expect_res_verify"]=expect_res_verify
        verify_res["expect_is_database"] = expect_is_database
        verify_res.update(database_verify_res)
        return verify_res

    def verify_database(self, **kwargs):
        '''
        :param serialNo: 身份标识唯一ID值
        :param req: 请求数据
        :param res: 存入结果
        :param re:  提取json规则
        :return:True-代表一致，False-代表不一致
        '''

        # 是否需要验证数据库存入的数据
        is_verify_database = kwargs.get("is_verify_database", False)

        # 是否需要验证回调状态数据
        is_verify_callbackurl = kwargs.get("is_verify_callbackurl", False)

        #不需要验证字段列表
        no_verify_filed = self.kwargs.get("no_verify_filed",[])
        compare_para_data = self.kwargs.get("compare_para_data",{})
        database_str_hd = ''
        database_str = None
        database_flag = False
        expCallbackFlag = kwargs.get("expCallbackFlag", None)
        req = kwargs.get("req", None)
        res = kwargs.get("res", None)
        try:
            expCF_dict = json.loads(expCallbackFlag)
            expCF_value = expCF_dict.get("callbackFlag")
        except Exception as e:
            expCF_value = expCallbackFlag



        try:

            req_keys = req.keys()
            # 获取数据库查询数据
            # 参数名与数据库名对应列表
            query_filed = self.kwargs.get("query_filed", {})
            query_filed_dict = {}
            if not query_filed:
                query_data_list = self.kwargs.get("query_data_list", [])
                if query_data_list:
                    for query_data in query_data_list:
                        if str(query_data[1]).lower() == 'req':
                            query_filed_dict[query_data[0]] = req.get(query_data[2])
                        else:
                            query_filed_dict[query_data[0]] = res.get(query_data[2])


            database_json = self.conne.get_data(query_con=query_filed_dict,expCF_value=expCF_value)[0]
            database = jsonpath(database_json, "$.._source")[0]
            callbackurl_flag = False
            if is_verify_database:
                for key in req_keys:
                    if key in compare_para_data.keys():
                        data_key = compare_para_data.get(key)
                    else:
                        data_key = key
                    if req.get(key) == str(database.get(data_key)) and req.get(key) not in no_verify_filed:
                        database_flag = True
                        database_str = "数据库存储验证结果：一致（接口请求参数请求值与数据库存储值一致）"
                    else:
                        error_str = "请求参数<{0}={1}>,数据库存储参数<{0}={2}>".format(key, req.get(key), str(res.get(key)))
                        database_str = "数据库存储验证结果：不一致（接口请求参数请求值与数据库存储值不一致,具体不一致原因：{}）".format(error_str)
                        database_flag = False
                        break
            else:
                database_flag = False

            if is_verify_callbackurl:
                if expCF_value != None:
                    if expCF_value == database.get("callbackFlag"):
                        callbackurl_flag = True
                        database_str_hd = "数据库回调状态值与预期状态值一致：回调成功"

                    else:
                        callbackurl_flag = False
                        database_str_hd = "回调结果与预期不一致：回调失败,预期回调结果callbackFlag={}，实际数据库存储callbackFlag={}".format(
                            expCF_value, database.get("callbackFlag"))
                else:
                    callbackurl_flag = True
            else:
                callbackurl_flag = False
        except Exception as e:
            log.error("测试用例请求参数与存储结果对比出现异常，异常原因：{}".format(e))

        database_verify_res = {
            "database_flag": database_flag,
            "callbackurl_flag":callbackurl_flag,
            "database_str": database_str,
            "database_str_hd": database_str_hd
        }
        return database_verify_res


    def download_verify(self,expect, res,req):
        serialNo = req.get("serialNo")
        file_data = res.json().get("data")
        if file_data:
            self.tsa.decry(file_data, serialNo)
            down_su = True
        else:
            down_su = False
        res_verify = self.deal_dict(expect,res)
        if '"success":true' in expect and res.json().get("success") == True:
            if down_su and res_verify:
                return True,serialNo
            else:
                return False,serialNo
        elif res_verify:
            return True,serialNo
        else:
            return False,serialNo

    def expect_res_ispass(self,expect,res):
        try:
            expect_dict = json.loads(expect)
        except Exception as e:
            log.error("预期结果不是字典类型，预期结果为：{}".format(expect))
            expect_dict = expect
        try:
            res_dict = res.json()
        except Exception as e:
            log.error("实际结果不是json类型，预期结果为：{}".format(res))
            res_dict = res
        try:
            expect_keys = expect_dict.keys()
        except Exception as e:
            log.error("预期结果不是字典类型无法取出keys，预期结果为：{}".format(expect))
            expect_keys = []

        if expect_keys == []:
            res_status = res.json().get("status")
            if  expect == str(res_status):
                cmp_res = True
            elif expect in res:
                cmp_res = True
            else:
                cmp_res = False
        else:
            for expect_key in expect_keys:
                if expect_dict.get(expect_key) == res_dict.get(expect_key):
                    cmp_res = True
                else:
                    cmp_res = False
                    break
        return cmp_res

    def download_case(self,partnerID,partnerKey,serialNo,url=None,download_file=None):
        flag = False
        try:
            if url:
                req_url = url
            else:
                req_url = "http://39.107.66.190:9999/v2/api/confirm/downloadOpusCertificate"  # 下载接口
                req_url = "http://ipp.tsa.cn/v2/api/confirm/downloadOpusCertificate"
            data = {}
            salt = self.tsa.make_salt([partnerID,partnerKey,serialNo],partnerKey)
            data["partnerID"]=partnerID
            data["partnerKey"] = partnerKey
            data["serialNo"] = serialNo
            data["salt"] = salt
            start = time.time()
            res = self.inter_run.main_request("post", req_url, data).json()
            end = time.time()
            hs = end -start
            print("下载接口请求响应时间：{}".format(hs))
            res_copy = deepcopy(res) #用于返回结果写入excel表格
            try:
                if res.get("data",None):
                    file_data = res.pop("data")
                else:
                    file_data = None
            except Exception as e:
                log.error("下载接口返回结果中去除掉data出现异常，异常原因".format(e))
                res = res
                file_data=None
            if file_data:
                self.tsa.decry(file_data, data["serialNo"],download_file=download_file)
                flag = True
            else:
                flag = False
        except Exception as e:
            log.error("下载接口获取返回信息异常 ，异常原因：{}".format(e))
            print("下载接口返回结果出现异常,异常原因={}".format(e))
            flag =False
        return flag,req_url,data,res,res_copy
if __name__ == "__main__":
    crr = CmpReqRes()
    crr.cmp_req_res()
