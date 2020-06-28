import xlrd
from xlutils.copy import  copy
import logging
log = logging.getLogger("__file__")
class OperationExcel:
    def __init__(self,**kwargs):
        self.kwargs = kwargs
        filename = self.kwargs.get("case_filepath", '')
        sheetid = self.kwargs.get("case_sheetid", 0)
        try:
            if filename:
                self.filename = filename
            else:
                self.filename = ''
            self.sheetid = int(sheetid)
            self.sheet_obj = self.get_sheet(self.filename,self.sheetid)
            self.rows = self.sheet_obj.nrows
            self.cols = self.sheet_obj.ncols
        except Exception as e:
            log.error("操作EXCEL表类初始化异常，异常原因：{}".format(e))


    def get_sheet(self,filename=None,sheetid=0):
        '''
        获取指定excel表格指定sheet页的内容对像
        :param filename: excel表格全路径
        :param sheetid:  sheetID
        :return: sheet页内容对像
        '''
        try:
            if filename:
                self.filename = filename
            if sheetid:
                self.sheetid = sheetid
            self.sheet_obj = xlrd.open_workbook(self.filename).sheet_by_index(self.sheetid)
            return self.sheet_obj
        except Exception as e:
            log.error("操作EXCEL表类获取sheet页内容异常，异常原因：{}".format(e))
            return None

    def get_sheet_rows(self):
        '''
        获取指定sheet页的有效内容行数
        :return:
        '''
        rows = None
        try:
            rows = self.sheet_obj.nrows
        except Exception as e :
            log.error("操作EXCEL表类获取行数异常，异常原因：{}".format(e))
        return rows

    def get_cell_value(self,row,col):
        '''
        根据输入的行和列获取指定单元格内容
        :param row: 行
        :param col: 列
        :return: 单元格内容
        '''
        try:
            return self.sheet_obj.cell_value(row,col)
        except Exception as e :
            log.error("操作EXCEL表类获取单元格内容异常，异常原因：{}".format(e))

    def writer_data(self,row,col,data):
        '''
        根据行和列向指定单元格写入内容
        :param row: 行
        :param col: 列
        :param data: 写入数据
        :return:
        '''

        try:
            read_data = xlrd.open_workbook(self.filename)
            copy_data = copy(read_data)
            sheet_data = copy_data.get_sheet(self.sheetid)
            sheet_data.write(row,col,data)
            copy_data.save(self.filename)
            flag = True
        except Exception as e:
            log.error("操作EXCEL表类写入数据异常，异常原因：{}".format(e))
            flag = False
        return flag

    def get_cols_data(self,col_num=0):
        '''
        根据列号获取指定列内容
        :param col_num:
        :return: 列内容列表
        '''
        try:
            return self.sheet_obj.col_values(col_num)
        except Exception as e:
            log.error("操作EXCEL表类获取列数据异常，异常原因：{}".format(e))
            return None

    def get_row_num_for_value(self,value,col=None):
        '''
        根据传入值获取所在行号，如果传入列号，直接执行if下语句，如果未传列号，循环所有行和列比对值，第一个相同值即返回，不再循环
        :param value: 需要查找的查单元格值
        :param col: 列号
        :return: 行号
        '''
        try:
            if col:
                row_num = None
                for index,data in enumerate(self.get_cols_data(col)):
                    if data == value:
                        row_num = index
                return row_num
            else:
                for row in range(0,self.rows):
                    for col in range(0,self.cols):
                        if value == self.get_cell_value(row,col):
                            return row
        except Exception as e:
            log.error("操作EXCEL表类获取值对应的行号出现异常，异常原因：{}".format(e))
        return None

    def get_col_num_for_value(self,value):
        '''
        根据指定内容获取列号
        :param value: 单元格内容
        :return: 行号
        '''
        cols_data = self.get_cols_data()
        try:
            row_num = None
            for index,data in enumerate(self.get_cols_data(1)):
                if data == value:
                    row_num = index
            return row_num
        except Exception as e:
            log.error("操作EXCEL表类获取值对应的行号出现异常，异常原因：{}".format(e))
            return None

    def get_row_col_list(self,**kwargs):
        '''
        获取指定行内容
        :param start:开始行
        :param rows:结束行，如默认表示所有行
        :return:行列表
        '''
        start = self.kwargs.get("case_start_rownum",1)
        end   = self.kwargs.get("case_end_rownum",0)
        row_col_list = []
        try:
            if end !=0 and end>start:
                self.rows=end
            elif end == -1:  # 等于-1表示获取全部记录
                self.rows = self.sheet_obj.nrows
            elif end == 0:  # 等于0表示仅获取一条记录
                self.rows = start + 1

            for row in range(int(start),int(self.rows)):
                col_list = self.get_sheet().row_values(row)
                row_col_list.append(col_list)
            return row_col_list
        except Exception as e :
            log.error("操作EXCEL表类获取值对应的行号出现异常，异常原因：{}".format(e))
            row_col_list = None
        return row_col_list

    def get_row_col_list_param_name(self,**kwargs):
        '''
        获取指定行内容
        :param start:开始行
        :param rows:结束行，如默认表示所有行
        :return:行列表
        '''
        if kwargs:
            self.kwargs = kwargs
        start = self.kwargs.get("case_param_name_start",1)
        end   = self.kwargs.get("case_param_name_end",0)
        row_col_list = []
        try:
            if end !=0 and end !=-1 and end>start:
                self.rows=end
            elif end == -1: #等于-1表示获取全部记录
                self.rows = self.sheet_obj.nrows
            elif end == 0: #等于0表示仅获取一条记录
                self.rows = start+1

            for row in range(int(start),int(self.rows)):
                col_list = self.get_sheet().row_values(row)
                row_col_list.append(col_list)
            return row_col_list
        except Exception as e :
            log.error("操作EXCEL表类获取值对应的行号出现异常，异常原因：{}".format(e))
            row_col_list = None
        return row_col_list


if __name__ == '__main__':
    oe = OperationExcel()
    #print(oe.get_cell_value(1,2))
    oe.get_col_num_for_value()