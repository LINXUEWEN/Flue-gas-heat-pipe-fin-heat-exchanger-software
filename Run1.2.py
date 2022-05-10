# Flue-gas-heat-pipe-fin-heat-exchanger-software
本科毕业大论文
import sys
import untitled
from PyQt5 import QtCore, QtGui
from PyQt5.Qt import *
import CoolProp.CoolProp as CP
import pinyin.cedict
import math
import pandas as pd
from docx import *

class Calculate(QMainWindow, untitled.Ui_MainWindow):
    def __init__(self, parent=None):
        self.app = QApplication(sys.argv)
        super(Calculate, self).__init__(parent)
        self.setupUi(self)          # 直接继承界面类

        excel_file = './钢制压力容器材料的许用应力（GB 150-1998）.xlsx'  # 导入excel数据
        self.data_stress = pd.read_excel(excel_file, index_col='钢号')
        excel_file_2 = './烟气的物性参数.xlsx'

        self.doc = Document()
        self.table = self.doc.add_table(rows=26, cols=3, style='Table Grid')

        self.data_smoke = pd.read_excel(excel_file_2, index_col=0)
        self.phy_pro_param_smoke = Physical_property_parameter_smoke()
        self.phy_pro_param_cooler = Physical_property_parameter_cooler()
        self.pushButton.clicked.connect(self.heatCalculate)
        self.pushButton_2.clicked.connect(self.phy_pro_param_cooler.textBrowser_4.clear)
        self.pushButton_2.clicked.connect(self.phy_pro_param_smoke.textBrowser_3.clear)
        self.pushButton_2.clicked.connect(self.textBrowser_2.clear)
        self.pushButton_3.clicked.connect(self.textBrowser_2.clear)
        self.pushButton_4.clicked.connect(self.finnedTube)
        self.pushButton_5.clicked.connect(self.designTubeShell)
        self.treeWidget.doubleClicked.connect(self.showMsg_2)
        self.ControlBoard()

        self.actionClose_2.triggered.connect(self.app.quit)
        self.actionOutput.triggered.connect(self.Output)



    def Output(self):
        try:
            fluid1 = self.table.cell(0, 0)
            fluid2 = self.table.cell(1, 0)
            fluid = fluid1.merge(fluid2)
            fluid.text = '一、流体'
            self.table.cell(0, 1).text = '热流体壳侧'
            self.table.cell(0, 2).text = '冷流体管侧'
            self.table.cell(1, 1).text = '烟气'
            self.table.cell(1, 2).text = self.comboBox.currentText()

            data = self.table.cell(2, 0).merge(self.table.cell(2, 2))
            data.text = '二、原始数据'
            self.table.cell(3, 0).text = '入口温度（℃）'
            self.table.cell(3, 1).text = str('%.2f' % self.smoke_in_temp)
            self.table.cell(3, 2).text = str('%.2f' % self.cooler_in_temp)
            self.table.cell(4, 0).text = '出口温度（℃）'
            self.table.cell(4, 1).text = str('%.2f' % self.smoke_out_temp)
            self.table.cell(4, 2).text = str('%.2f' % self.cooler_out_temp)
            self.table.cell(5, 0).text = '工作压力（MPa）'
            self.table.cell(5, 1).text = self.lineEdit_4.text()
            self.table.cell(5, 2).text = self.lineEdit_9.text()
            self.table.cell(6, 0).text = '允许压力降（kPa）'
            self.table.cell(6, 1).text = self.lineEdit_5.text()
            self.table.cell(6, 2).text = self.lineEdit_10.text()
            self.table.cell(7, 0).text = '质量流量（kg/s）'
            self.table.cell(7, 1).text = str('%.2f' % self.smoke_6)
            self.table.cell(7, 2).text = str('%.2f' % self.cooler_11)

            calcu = self.table.cell(8, 0).merge(self.table.cell(8, 2))
            calcu.text = '三、热量衡算'
            self.table.cell(9, 0).text = '传热量（W）'
            Q = self.table.cell(9, 1).merge(self.table.cell(9, 2))
            Q.text = str('%.2f' % self.cap_heat_trans)
            self.table.cell(10, 0).text = '传热温差（K）'
            delta_T = self.table.cell(10, 1).merge(self.table.cell(10, 2))
            delta_T.text = str('%.2f' % self.delta_heat_temper)

            para = self.table.cell(11, 0).merge(self.table.cell(11, 2))
            para.text = '四、结构参数'
            self.table.cell(12, 0).text = '基管外径（mm）'
            tube_exdia = self.table.cell(12, 1).merge(self.table.cell(12, 2))
            tube_exdia.text = self.lineEdit_13.text()
            self.table.cell(13, 0).text = '基管内径（mm）'
            tube_india = self.table.cell(13, 1).merge(self.table.cell(13, 2))
            tube_india.text = self.lineEdit_14.text()
            self.table.cell(14, 0).text = '翅片高度（mm）'
            fin_height = self.table.cell(14, 1).merge(self.table.cell(14, 2))
            fin_height.text = self.lineEdit_15.text()
            self.table.cell(15, 0).text = '翅片厚度（mm）'
            fin_thick = self.table.cell(15, 1).merge(self.table.cell(15, 2))
            fin_thick.text = self.lineEdit_16.text()
            self.table.cell(16, 0).text = '翅片间距（mm）'
            fin_demg = self.table.cell(16, 1).merge(self.table.cell(16, 2))
            fin_demg.text = self.lineEdit_18.text()
            self.table.cell(17, 0).text = '翅片排列方式'
            fin_arrag = self.table.cell(17, 1).merge(self.table.cell(17, 2))
            if self.radioButton.isChecked():  # 叉排
                fin_arrag.text = '叉排'
            elif self.radioButton_2.isChecked():  # 顺排
                fin_arrag.text = '顺排'
            self.table.cell(18, 0).text = '流动方式'
            flow_arrag = self.table.cell(18, 1).merge(self.table.cell(18, 2))
            if self.radioButton_3.isChecked():
                flow_arrag.text = '逆流'
            elif self.radioButton_4.isChecked():
                flow_arrag.text = '顺流'
            self.table.cell(19, 0).text = '翅片导热系数（W/(㎡·K)）'
            fin_heat_para = self.table.cell(19, 1).merge(self.table.cell(19, 2))
            fin_heat_para.text = self.lineEdit_22.text()

            check_cal = self.table.cell(20, 0).merge(self.table.cell(20, 2))
            check_cal.text = '五、校核计算'
            self.table.cell(21, 0).text = '面积裕度（%）'
            area_mar = self.table.cell(21, 1).merge(self.table.cell(21, 2))
            area_mar.text = str('%.2f' % self.area_margin)
            self.table.cell(22, 0).text = '壳侧出口温度（℃）'
            THO = self.table.cell(22, 1).merge(self.table.cell(22, 2))
            THO.text = str('%.2f' % self.THO)
            self.table.cell(23, 0).text = '管侧出口温度（℃）'
            TCO = self.table.cell(23, 1).merge(self.table.cell(23, 2))
            TCO.text = str('%.2f' % self.TCO)

            delta_P = self.table.cell(24, 0).merge(self.table.cell(24, 2))
            delta_P.text = '六、压力降'
            self.table.cell(25, 0).text = 'ΔP（Pa）'
            self.table.cell(25, 1).text = str('%.2f' % self.press_drop_smoke)
            self.table.cell(25, 2).text = str('%.2f' % self.press_drop_cooler)

            self.doc.save('设计报表.docx')
        except Exception as e:
            print(e)

    # 传热量计算
    def heatCalculate(self):
        if self.lineEdit_7.text() == '' or self.lineEdit_2.text() == '' or \
                self.lineEdit_8.text() == '' or self.lineEdit_3.text() == '' or \
                self.lineEdit_6.text() == '' or self.lineEdit_11.text() == '' or \
                self.lineEdit_5.text() == '' or self.lineEdit_9.text() == '' or \
                self.lineEdit_4.text() == '' or self.lineEdit_10.text() == '' or self.lineEdit_12.text() == '':
            print('请输入热量衡算的值')
            # QMessageBox.information(self, '错误', '请输入值')
        else:
            print('热量衡算已计算')
            # print(pinyin.cedict.translate_word(self.comboBox.currentText())[0].title())
            if self.comboBox.currentText() == 'R22':
                self.cooler = self.comboBox.currentText()
            else:
                self.cooler = pinyin.cedict.translate_word(self.comboBox.currentText())[0].title()
            # print(self.cooler)
            cooler_parameter = self.CoolerProp()
            cooler_C = cooler_parameter[0]  # cooler的比热容
            self.cooler_C = cooler_C
            cooler_D = cooler_parameter[1]  # cooler的密度
            cooler_L = cooler_parameter[2]  # cooler的导热系数
            cooler_U = cooler_parameter[3]  # cooler的粘度
            cooler_Pr = cooler_parameter[4] # cooler的Pr数

            smoke_para = self.SmokeProp()
            smoke_L = smoke_para[1]  # smoke的导热系数
            smoke_U = smoke_para[2]  # smoke的粘度
            smoke_Pr = smoke_para[3]  # smoke的Pr数
            smoke_D = smoke_para[0]  # smoke的密度
            smoke_C = smoke_para[4]  # smoke的比热容
            self.smoke_C = smoke_C

            if float(self.lineEdit_7.text()) == 0 or float(self.lineEdit_8.text()) == 0 or float(self.lineEdit_11.text()) == 0:
                cooler_delta_temp = abs(float(self.lineEdit_2.text()) - float(self.lineEdit_3.text()))  # smoke的
                cooler_mass_flow = float(self.lineEdit_6.text())
                cooler_C = smoke_C*1000
            elif float(self.lineEdit_2.text()) == 0 or float(self.lineEdit_3.text()) == 0 or float(self.lineEdit_6.text()) == 0:
                cooler_delta_temp = abs(float(self.lineEdit_7.text()) - float(self.lineEdit_8.text()))  #cooler的进出口温差
                cooler_mass_flow = float(self.lineEdit_11.text())                                       #cooler的质量流量

            self.cap_heat_trans = cooler_C * cooler_mass_flow * cooler_delta_temp                        # 传热量
            if float(self.lineEdit_3.text()) == 0:
                self.smoke_out_temp = float(self.lineEdit_2.text()) - self.cap_heat_trans / (
                        smoke_para[4] * 10 ** 3 * float(self.lineEdit_6.text()))
                self.textBrowser_2.append('烟气的出口温度：%.1f ℃' % self.smoke_out_temp)
            else:
                self.smoke_out_temp = float(self.lineEdit_3.text())
            if float(self.lineEdit_2.text()) == 0:
                self.smoke_in_temp = float(self.lineEdit_3.text()) + self.cap_heat_trans / (
                        smoke_para[4] * 10 ** 3 * float(self.lineEdit_6.text()))
                self.textBrowser_2.append('烟气的进口温度：%.1f ℃' % self.smoke_in_temp)
            else:
                self.smoke_in_temp = float(self.lineEdit_2.text())
            if float(self.lineEdit_6.text()) == 0:
                self.smoke_6 = self.cap_heat_trans / (smoke_para[4]*10**3*(float(self.lineEdit_2.text()) - float(self.lineEdit_3.text())))
                self.textBrowser_2.append('烟气的质量流量：%.1f kg/s' % self.smoke_6)
            else:
                self.smoke_6 = float(self.lineEdit_6.text())

            if float(self.lineEdit_7.text()) == 0:
                self.cooler_in_temp = float(self.lineEdit_8.text()) - self.cap_heat_trans / (
                        cooler_parameter[0] * float(self.lineEdit_11.text()))
                self.textBrowser_2.append('冷却剂的进口温度：%.1f ℃' % self.cooler_in_temp)
            else:
                self.cooler_in_temp = float(self.lineEdit_7.text())
            if float(self.lineEdit_8.text()) == 0:
                self.cooler_out_temp = float(self.lineEdit_7.text()) + self.cap_heat_trans / (
                        cooler_parameter[0] * float(self.lineEdit_11.text()))
                self.textBrowser_2.append('冷却剂的出口温度：%.1f ℃' % self.cooler_out_temp)
            else:
                self.cooler_out_temp = float(self.lineEdit_8.text())
            if float(self.lineEdit_11.text()) == 0:
                self.cooler_11 = self.cap_heat_trans / (cooler_parameter[0]*(float(self.lineEdit_8.text()) - float(self.lineEdit_7.text())))
                self.textBrowser_2.append('冷却剂的质量流量：%.1f kg/s' % self.cooler_11)
            else:
                self.cooler_11 = float(self.lineEdit_11.text())

            self.textBrowser_2.append('传热量：%.2f W' % self.cap_heat_trans)
            self.textBrowser_2.append('冷却剂的比热容：%.2f J/(kg·K)' % cooler_C)
            self.textBrowser_2.append('冷却剂的密度：%.2f kg/m³' % cooler_D)
            self.textBrowser_2.append('冷却剂的导热系数：%.3f W/m·K' % cooler_L)
            self.textBrowser_2.append('冷却剂的粘度：%.1f' % (cooler_U*10**6) + 'x10^6 kg/(m·s)')
            self.textBrowser_2.append('冷却剂的Pr数：%.2f' % cooler_Pr)

            self.phy_pro_param_cooler.textBrowser_4.append('传热量：%.2f W' % self.cap_heat_trans)
            self.phy_pro_param_cooler.textBrowser_4.append('冷却剂的比热容：%.2f J/(kg·K)' % cooler_C)
            self.phy_pro_param_cooler.textBrowser_4.append('冷却剂的密度：%.2f kg/m³' % cooler_D)
            self.phy_pro_param_cooler.textBrowser_4.append('冷却剂的导热系数：%.2f W/m·K' % cooler_L)
            self.phy_pro_param_cooler.textBrowser_4.append('冷却剂的粘度：%.1f' % (cooler_U*10**6) + 'x10^6 kg/(m·s)')
            self.phy_pro_param_cooler.textBrowser_4.append('冷却剂的Pr数：%.2f' % cooler_Pr)

            self.textBrowser_2.append('烟气的比热容：%.2f kJ/(kg·K)' % smoke_para[4])
            self.textBrowser_2.append('烟气的密度：%.2f kg/m³' % smoke_D)
            self.textBrowser_2.append('烟气的导热系数：%.2f' % (smoke_L * 100) + 'x10^2 W/m·K')
            self.textBrowser_2.append('烟气的粘度：%.1f' % (smoke_U * 10 ** 6) + 'x10^6 kg/(m·s)')
            self.textBrowser_2.append('烟气的Pr数：%.2f' % smoke_Pr)
            self.textBrowser_2.append('-----------------------------')

            self.phy_pro_param_smoke.textBrowser_3.append('烟气的比热容：%.2f kJ/(kg·K)' % smoke_para[4])
            self.phy_pro_param_smoke.textBrowser_3.append('烟气的密度：%.2f kg/m³' % smoke_D)
            self.phy_pro_param_smoke.textBrowser_3.append('烟气的导热系数：%.2f' % (smoke_L * 100) + 'x10^2 W/m·K')
            self.phy_pro_param_smoke.textBrowser_3.append('烟气的粘度：%.1f' % (smoke_U * 10 ** 6) + 'x10^6 kg/(m·s)')
            self.phy_pro_param_smoke.textBrowser_3.append('烟气的Pr数：%.2f' % smoke_Pr)

    # 翅片管传热相关计算
    def finnedTube(self):
        if self.lineEdit_13.text() == '' or self.lineEdit_14.text() == '' or \
                self.lineEdit_15.text() == '' or self.lineEdit_16.text() == '' or \
                self.lineEdit_17.text() == '' or self.lineEdit_18.text() == '' or \
                self.lineEdit_24.text() == '' or self.lineEdit_19.text() == '' or \
                self.lineEdit_22.text() == '' or self.lineEdit_23.text() == '' or \
                not(self.radioButton.isChecked() or self.radioButton_2.isChecked()) or \
                not(self.radioButton_3.isChecked() or self.radioButton_4.isChecked()):
            print('请输入翅片管设计的值')
            # QMessageBox.information(self, '错误', '请输入值')
        else:
            print('翅片管设计计算已完成')
            tube_ex = self.TubeExHeatCoefficient()
            tube_ex_heat = tube_ex[0]                   # 管外换热系数
            fin_prop = tube_ex[1]                       # 翅化比
            fin_efficient = tube_ex[2]                  # 翅片效率
            drag_coefficient_1 = tube_ex[3]             # 烟气侧阻力系数
            tube_in = self.TubeInHeatCoefficient()
            tube_in_heat = tube_in[0]                   # 管内换热系数

            tube_ex_R0 = 1/tube_ex_heat
            # print('管外换热热阻：%.6f' % tube_ex_R0)
            tube_exin_prop = float(self.lineEdit_13.text()) / float(self.lineEdit_14.text())    # 基管的外径与内径的比
            tube_in_Ri = tube_exin_prop/tube_in_heat
            # print('管内换热热阻：%.6f' % tube_in_Ri)
            tube_wall_Rw = float(self.lineEdit_13.text()) * math.log(tube_exin_prop, math.e) / (2000*float(self.lineEdit_22.text()))
            # print('管壁热阻：%.6f' % tube_wall_Rw)
            tube_ex_Rfi = float(self.lineEdit_23.text())            # 管内污垢热阻
            tube_in_Rf0 = tube_ex_Rfi/(fin_prop * fin_efficient)    # 管外污垢热阻
            # print('管外污垢热阻：%.6f' % tube_in_Rf0)
            tube_total_R = tube_ex_R0 + tube_in_Ri + tube_wall_Rw + tube_ex_Rfi + tube_in_Rf0   # 总传热热阻
            tube_heat = 1/tube_total_R  # 传热系数
            # print('总传热热阻：%.7f' % tube_total_R)
            # print('传热系数：%.2f' % tube_heat)
            self.textBrowser_2.append('传热系数：%.2f W/(㎡·K)' % tube_heat)

            # 传热温差
            if self.radioButton_3.isChecked():
                max_delta_temper = abs(self.smoke_in_temp - self.cooler_out_temp)
                min_delta_temper = abs(self.smoke_out_temp - self.cooler_in_temp)
            elif self.radioButton_4.isChecked():
                max_delta_temper = abs(self.smoke_in_temp - self.cooler_in_temp)
                min_delta_temper = abs(self.smoke_out_temp - self.cooler_out_temp)
            delta_aver_temper = (max_delta_temper - min_delta_temper) / math.log(max_delta_temper/min_delta_temper, math.e)
            self.delta_heat_temper = delta_aver_temper*self.doubleSpinBox.value()
            # print('传热温差：%.2f' % delta_heat_temper)
            self.textBrowser_2.append('传热温差：%.2f ℃' % self.delta_heat_temper)
            heat_trans = self.cap_heat_trans
            area_heat = self.doubleSpinBox_2.value()*heat_trans/(tube_heat*self.delta_heat_temper)
            # print('传热量：%.2f' % heat_trans)
            # print('传热面积：%.2f' % area_heat)
            fin_num_N = area_heat*1000/(math.pi*float(self.lineEdit_13.text())*tube_in[1])
            # print('fin_num_N: %f' % fin_num_N)
            self.fin_vert_num = math.ceil(fin_num_N/tube_in[2])    # 纵向管数
            self.fin_cross_num = tube_in[2]
            self.textBrowser_2.append("横向管排数：%d 排" % self.fin_cross_num)
            self.textBrowser_2.append("纵向管排数：%d 排" % self.fin_vert_num)
            fin_num_true = self.fin_vert_num*self.fin_cross_num            # 实际管子数
            # print('实际管数:%d' % fin_num_true)
            self.textBrowser_2.append('实际管数:%d 个' % fin_num_true)
            area_heat_true = math.pi*float(self.lineEdit_13.text())*tube_in[1]*fin_num_true*1e-3
            # print('实际传热面积：%.2f' % area_heat_true)
            self.textBrowser_2.append('换热面积：%.2f' % area_heat + '㎡')
            # 换热面积裕度
            self.area_margin = (area_heat_true/area_heat - 1)*100
            self.textBrowser_2.append('面积裕度：%.2f' % self.area_margin + '%')
            # ε——NTU校核
            C_smoke = float(self.lineEdit_6.text())*self.smoke_C*1000
            C_cooler = float(self.lineEdit_11.text())*self.cooler_C
            if C_smoke < C_cooler:
                C_min = C_smoke
                C_max = C_cooler
                NTU = area_heat*tube_heat/C_smoke
            else:
                C_min = C_cooler
                C_max = C_smoke
                NTU = area_heat*tube_heat/C_cooler
            # print(NTU)
            if self.radioButton_3.isChecked():
                epsilon = (1-math.exp(-NTU*(1-C_min/C_max)))/(1-(C_min/C_max)*math.exp(-NTU*(1-C_min/C_max)))
            elif self.radioButton_4.isChecked():
                epsilon = (1-math.exp(-NTU*(1-C_min/C_max)))/(1+(C_min/C_max))
            # print(epsilon)
            Q = epsilon*(self.smoke_in_temp - self.cooler_in_temp)*C_min
            self.THO = self.smoke_in_temp - Q/C_smoke
            self.TCO = self.cooler_in_temp + Q/C_cooler
            self.textBrowser_2.append("ε——NTU校核的烟气出口温度：%.2f ℃" % self.THO)
            self.textBrowser_2.append("ε——NTU校核的冷却剂出口温度：%.2f ℃" % self.TCO)

            self.press_drop_smoke = drag_coefficient_1 * self.fin_vert_num      # 烟气压力降(Pa)
            # print("烟气压力降：%.2f" % press_drop_smoke)
            self.textBrowser_2.append("烟气压力降：%.2f Pa" % self.press_drop_smoke)
            self.textBrowser_2.append('-----------------------------')

    # 管外传热系数相关计算
    def TubeExHeatCoefficient(self):
        finnedTube_exDiameter = float(self.lineEdit_17.text())          # 翅片外径
        mainTube_exDiameter = float(self.lineEdit_13.text())            # 基管外径
        fin_height = (finnedTube_exDiameter - mainTube_exDiameter) / 2  # 翅片高
        fin_thick = float(self.lineEdit_16.text())                      # 翅片的厚度
        fin_distance = float(self.lineEdit_18.text())                   # 翅节距
        tube_cross_distance = float(self.lineEdit_24.text())            # 翅片管横向节距
        mass_flow_windward_side = float(self.lineEdit_19.text())        # 迎风面质量流量
        finned_proportion = (math.pi / 2 * (finnedTube_exDiameter ** 2 - mainTube_exDiameter ** 2) + math.pi *
                             finnedTube_exDiameter * fin_thick + math.pi * mainTube_exDiameter * (
                                         fin_distance - fin_thick)) \
                            / (math.pi * mainTube_exDiameter * fin_distance)  # 翅化比
        # print("翅化比：%.1f" % finned_proportion)
        self.textBrowser_2.append("翅化比：%.1f" % finned_proportion)
        flow_area_smoke = fin_distance * (tube_cross_distance - mainTube_exDiameter) - 2 * fin_height * fin_thick
        windward_side = fin_distance * tube_cross_distance                      # 迎风面
        mass_flow_smoke = mass_flow_windward_side * windward_side / flow_area_smoke  # 截面质量流速
        # print("管外最窄截面质量流速：%.3f" % mass_flow_smoke)

        smoke_para = self.SmokeProp()
        smoke_L = smoke_para[1]  # smoke的导热系数
        smoke_U = smoke_para[2]  # smoke的粘度
        smoke_Pr = smoke_para[3]  # smoke的Pr数
        smoke_D = smoke_para[0]     #smoke的密度

        smoke_Re = mass_flow_smoke * (mainTube_exDiameter * 1e-3) / smoke_U  # smoke的雷诺数 2000~10000
        # print("烟气雷诺数：%.f" % smoke_Re)
        self.textBrowser_2.append('烟气的Re数：%.f' % smoke_Re)

        if self.radioButton.isChecked():      # 叉排
            if finnedTube_exDiameter / mainTube_exDiameter < 1.7:  # 低翅片管束的换热系数
                smoke_heat_coefficient = 0.1507 * (smoke_L * 1000 / mainTube_exDiameter) * (smoke_Re ** 0.667) * (
                        smoke_Pr ** (1 / 3)) * ((fin_distance / fin_height) ** 0.164) * (
                                                 (fin_distance / fin_thick) ** 0.075)
            else:  # 高翅片管束的换热系数
                smoke_heat_coefficient = 0.1378 * (smoke_L * 1000 / mainTube_exDiameter) * (smoke_Re ** 0.718) * (
                        smoke_Pr ** (1 / 3)) * ((fin_distance / fin_height) ** 0.296)
        elif self.radioButton_2.isChecked():    # 顺排
            smoke_heat_coefficient = 0.104*(smoke_L/fin_distance)*(mainTube_exDiameter/fin_distance)**(-0.54)*(fin_height/fin_distance)**(-0.14)*(mass_flow_smoke*fin_distance/smoke_U)**(0.72)
        # print("烟气换热系数：%.3f" % smoke_heat_coefficient)

        fin_heat_coefficient = float(self.lineEdit_22.text())  # 翅片的换热系数
        mL_function = (fin_height * 1e-3) * (
                    (2 * smoke_heat_coefficient * 1000 / (fin_heat_coefficient * fin_thick)) ** 0.5) * \
                      ((1 + fin_height / mainTube_exDiameter) ** 0.5)  # 函数mL
        # print("函数mL：%.2f" % mL_function)
        fin_efficient = math.tanh(mL_function) / mL_function  # 翅片效率
        # print("翅片效率：%.2f" % fin_efficient)
        tube_ex_heat_coefficient = smoke_heat_coefficient * fin_efficient * finned_proportion  # 基管外表面换热系数
        # print("管外换热系数：%.2f" % tube_ex_heat_coefficient)
        self.textBrowser_2.append("管外换热系数：%.2f W/(㎡·K)" % tube_ex_heat_coefficient)
        # 烟气侧压力降系数
        if self.radioButton.isChecked():        # 叉排
            drag_coefficient_smoke = 37.86 * smoke_Re ** (-0.316) * (tube_cross_distance/mainTube_exDiameter)**(-0.927)
        elif self.radioButton_2.isChecked():    # 顺排
            drag_coefficient_smoke = 3.68*smoke_Re**(-0.120)*(fin_distance/fin_height)**(-0.196)*(tube_cross_distance/mainTube_exDiameter)**(-0.823)
        # print("烟气阻力系数：%.4f" % drag_coefficient_smoke)
        drag_coefficient_smoke = drag_coefficient_smoke * (mass_flow_smoke**2)/(2*smoke_D)
        return (tube_ex_heat_coefficient, finned_proportion, fin_efficient, drag_coefficient_smoke)

    # 管内传热系数相关计算
    def TubeInHeatCoefficient(self):
        tube_in_diameter = float(self.lineEdit_14.text())         # 基管内径
        mass_flow_smoke = self.smoke_6                            # 烟气质量流量
        mass_flow_cooler = self.cooler_11                         # 冷却剂质量流量
        mass_flow_windward_side = float(self.lineEdit_19.text())  # 迎风面质量流量
        tube_cross_distance = float(self.lineEdit_24.text())      # 翅片管横向节距
        area_windward = mass_flow_smoke/mass_flow_windward_side   # 迎风面积
        area_height = round(area_windward**0.5 - 0.2, 1)          # 迎风面的高
        area_width = round(area_windward/area_height, 1)          # 迎风面的宽
        if area_height*area_width < area_windward:
            area_width += 0.1
        # print("迎风面尺寸：%.1f (宽)X %.1f (高)" % (area_width, area_height))
        self.textBrowser_2.append("迎风面尺寸：%.1f m(宽)X %.1f m(高)" % (area_width, area_height))
        cross_tube_num = math.ceil(area_height*1000/tube_cross_distance)           # 横向管排数
        if cross_tube_num%2 == 1:
            cross_tube_num += 1
        # print("横向管排数：%d" % cross_tube_num)

        area_flow_cooler = math.pi/4*tube_in_diameter**2*cross_tube_num*1e-6        # 管程流通面积
        # print('管程流通面积：%.4f' % area_flow_cooler)
        tube_in_mass_flow = mass_flow_cooler/area_flow_cooler                       # 管内质量流量
        # print("管内质量流量：%.2f" % tube_in_mass_flow)
        cooler_parameter = self.CoolerProp()
        cooler_D = cooler_parameter[1]  # cooler的密度
        cooler_L = cooler_parameter[2]  # cooler的导热系数
        cooler_U = cooler_parameter[3]  # cooler的粘度
        cooler_Pr = cooler_parameter[4]  # cooler的Pr数
        temp_1 = self.smoke_in_temp
        t = 273.153 + temp_1
        cooler_U_wall = CP.PropsSI('V', 'T', t,  'P', 101325, '%s' % self.cooler)
        cooler_Re = (tube_in_diameter*1e-3)*tube_in_mass_flow/cooler_U
        # print("%s的雷诺数：%.f" % (self.cooler, cooler_Re))
        drag_coefficient_cooler = 0.316*cooler_Re**(-0.25)
        cooler_v = 4*mass_flow_cooler/(cooler_D*math.pi*(tube_in_diameter*1e-3)**2)   # cooler在管内的流速
        # print("管内流体流速：%.2f" % cooler_v)
        if cooler_Re > 10000:
            cooler_heat_coefficient = 0.023*(cooler_L/(tube_in_diameter*1e-3))*cooler_Re**0.8*cooler_Pr**0.4
            self.press_drop_cooler = drag_coefficient_cooler*area_width*cooler_D*cooler_v**2/(2*(tube_in_diameter*1e-3))
        else:
            cooler_heat_coefficient = 1.86*(cooler_L/(tube_in_diameter*1e-3))*(cooler_Re*cooler_Pr)**(1/3)*(cooler_U/cooler_U_wall)**0.14
            self.press_drop_cooler = 32*area_width*cooler_U*cooler_v/((tube_in_diameter*1e-3)**2)
        # 管内换热系数
        # print("管内换热系数：%.2f" % cooler_heat_coefficient)
        self.textBrowser_2.append("管内换热系数：%.2f W/(㎡·K)" % cooler_heat_coefficient)
        # print("管内压力降：%.2f" % press_drop_cooler)
        self.textBrowser_2.append("管内压力降：%.2f Pa" % self.press_drop_cooler)
        return (cooler_heat_coefficient, area_width, cross_tube_num)

    # 冷却剂物性参数
    def CoolerProp(self):
        try:
            if float(self.lineEdit_7.text()) == 0:
                cooler_temper = float(self.lineEdit_8.text())
            elif float(self.lineEdit_8.text()) == 0:
                cooler_temper = float(self.lineEdit_7.text())
            else:
                cooler_temper = (float(self.lineEdit_7.text()) + float(self.lineEdit_8.text())) / 2
            t = 273.153 + cooler_temper
            p = 101325
            C_L = CP.PropsSI('C', 'T', t, 'P', p, '%s' % self.cooler)       # 比热容   [0]
            D_l = CP.PropsSI('D', 'T', t, 'P', p, '%s' % self.cooler)       # 密度     [1]
            L_l = CP.PropsSI('L', 'T', t, 'P', p, '%s' % self.cooler)       # 导热系数  [2]
            U_l = CP.PropsSI('V', 'T', t,  'P', p, '%s' % self.cooler)      # 粘度     [3]
            Prl = CP.PropsSI('Prandtl', 'T', t, 'P', p, '%s' % self.cooler) # 普朗特数  [4]
            return [C_L, D_l, L_l, U_l, Prl]
        except:
            print('请输入合理值')
            self.CoolProp()

    # 烟气物性参数
    def SmokeProp(self):
        if float(self.lineEdit_3.text()) == 0:
            index_1 = self.change_temp_index(float(self.lineEdit_2.text()))
        elif float(self.lineEdit_2.text()) == 0:
            index_1 = self.change_temp_index(float(self.lineEdit_3.text()))
        else:
            index_1 = self.change_temp_index((float(self.lineEdit_2.text()) + float(self.lineEdit_3.text())) / 2)
        smoke_D = self.data_smoke.iloc[index_1, 0]  # 烟气密度
        smoke_L = self.data_smoke.iloc[index_1, 2]  # 烟气导热系数
        smoke_U = self.data_smoke.iloc[index_1, 3]  # 烟气粘度
        smoke_Pr = self.data_smoke.iloc[index_1, 4] # 烟气Pr数
        smoke_C = self.data_smoke.iloc[index_1, 1]  # 烟气的比热容
        return (smoke_D, smoke_L, smoke_U, smoke_Pr, smoke_C)

    def change_temp_index(self, data):
        if data <= 0:
            return 0
        if 0 < data <= 90:
            return 1
        if 90 < data <= 100:
            return 2
        if 100 < data <= 150:
            return 3
        if 150 < data <= 200:
            return 4
        if 200 < data <= 250:
            return 5
        if 250 < data <= 300:
            return 6
        if 300 < data <= 350:
            return 7
        if 350 < data <= 400:
            return 8
        if 400 < data <= 450:
            return 9
        if 450 < data <= 500:
            return 10
        if 500 < data <= 550:
            return 11
        if 550 < data <= 600:
            return 12
        if 600 < data <= 650:
            return 13
        if 650 < data <= 700:
            return 14
        if 700 < data <= 750:
            return 15
        if 750 < data <= 800:
            return 16
        if 800 < data <= 859.33:
            return 17
        if 859.33 < data <= 900:
            return 18
        if 900 < data <= 950:
            return 19
        if 950 < data <= 1000:
            return 20
        if 1000 < data <= 1050:
            return 21
        if 1050 < data <= 1100:
            return 22
        if 1100 < data <= 1150:
            return 23
        if 1150 < data <= 1200:
            return 24

    # 管壳设计
    def designTubeShell(self):
        if self.lineEdit_25.text() == '' or self.lineEdit_26.text() == '' or \
                self.lineEdit_27.text() == '' or self.lineEdit_28.text() == '' or \
                self.lineEdit_29.text() == '' or self.lineEdit_30.text() == '' or \
                self.lineEdit_31.text() == '' or self.lineEdit_32.text() == '':
            print('请输入管壳设计的值')
            # QMessageBox.information(self, '错误', '请输入值')
        else:
            print('管壳设计计算已完成')
            finnedTube_exDiameter = float(self.lineEdit_17.text())  # 翅片外径
            tube_cross_distance = float(self.lineEdit_24.text())    # 翅片管横向节距
            work_pressure = float(self.lineEdit_4.text())   # 工作压力
            work_pressure_2 = float(self.lineEdit_9.text())
            welded_joint_coeff = float(self.lineEdit_30.text()) # 焊缝接头系数
            length = ((self.fin_vert_num-1)*(tube_cross_distance/2)*3**(1/2) + finnedTube_exDiameter)**2
            width = ((self.fin_cross_num-1)*(tube_cross_distance/2)*3**(1/2) + finnedTube_exDiameter)**2
            barrel_diameter = math.ceil((length+width)**(1/2))
            num_1 = barrel_diameter % 100
            barrel_diameter -= num_1              # 筒体直径
            # print("筒体直径：%d" % barrel_diameter)
            self.textBrowser_2.append("筒体直径：%d mm" % barrel_diameter)
            barrel_thick = self.change_diameter_type(barrel_diameter)  # 管壳筒体厚度
            # print("筒体厚度：%d" % barrel_thick)
            self.textBrowser_2.append("筒体厚度：%d mm" % barrel_thick)
            barrel_C1 = self.designer_C1(barrel_thick)      # 厚度负偏差C1
            barrel_C2 = float(self.lineEdit_31.text())  # 腐蚀裕量C2
            barrel_valid_thick = barrel_thick - barrel_C1 - barrel_C2       # 筒体有效厚度

            material = self.comboBox_2.currentText()  # 材料

            temperatureDir = {
                '20': 3,
                '100': 4,
                '150': 5,
                '200': 6,
                '250': 7,
                '300': 8,
                '350': 9,
                '400': 10,
                '425': 11,
                '475': 12,
                '500': 13,
                '525': 14,
                '550': 15,
                '575': 16,
            }
            tempe = self.smoke_in_temp  # 设计温度
            tempe_2 = self.change_temper_type(tempe)
            index_2 = temperatureDir['%d' % tempe_2]

            if material == 'Q235-B':
                if barrel_thick <= 4:
                    index_1 = 1
                elif 4 < barrel_thick <= 16:
                    index_1 = 2
                elif 16 < barrel_thick <= 40:
                    index_1 = 3
                else:
                    print('请输入合理的管壳厚度')
            elif material == 'Q235-C':
                if barrel_thick <= 4:
                    index_1 = 4
                elif 4 < barrel_thick <= 16:
                    index_1 = 5
                elif 16 < barrel_thick <= 40:
                    index_1 = 6
                else:
                    print('请输入合理的管壳厚度')
            elif material == '20R':
                if barrel_thick <= 16:
                    index_1 = 7
                elif 16 < barrel_thick <= 36:
                    index_1 = 8
                elif 36 < barrel_thick <= 60:
                    index_1 = 9
                elif 60 < barrel_thick <= 100:
                    index_1 = 10
                else:
                    print('请输入合理的管壳厚度')
            elif material == '16MnR':
                if barrel_thick <= 16:
                    index_1 = 11
                elif 16 < barrel_thick <= 36:
                    index_1 = 12
                elif 36 < barrel_thick <= 60:
                    index_1 = 13
                elif 60 < barrel_thick <= 100:
                    index_1 = 14
                elif 100 < barrel_thick <= 120:
                    index_1 = 15
                else:
                    print('请输入合理的管壳厚度')
            elif material == '15MnNbR':
                if barrel_thick <= 16:
                    index_1 = 16
                elif 16 < barrel_thick <= 36:
                    index_1 = 17
                elif 36 < barrel_thick <= 60:
                    index_1 = 18
                else:
                    print('请输入合理的管壳厚度')
            elif material == '15MnVR':
                if barrel_thick <= 8:
                    index_1 = 19
                elif 8 < barrel_thick <= 16:
                    index_1 = 20
                elif 16 < barrel_thick <= 36:
                    index_1 = 21
                elif 36 < barrel_thick <= 60:
                    index_1 = 22
                else:
                    print('请输入合理的管壳厚度')
            elif material == '18MnMoNbR':
                if barrel_thick <= 60:
                    index_1 = 23
                elif 60 < barrel_thick <= 100:
                    index_1 = 24
                else:
                    print('请输入合理的管壳厚度')
            elif material == '13MnNiMoNbR':
                if barrel_thick <= 100:
                    index_1 = 25
                elif 100 < barrel_thick <= 120:
                    index_1 = 26
                else:
                    print('请输入合理的管壳厚度')
            elif material == '07MnCrMoVR':
                if 16 <= barrel_thick <= 50:
                    index_1 = 27
                else:
                    print('请输入合理的管壳厚度')
            elif material == '16MnDR':
                if barrel_thick <= 16:
                    index_1 = 28
                elif 16 < barrel_thick <= 36:
                    index_1 = 29
                elif 36 < barrel_thick <= 60:
                    index_1 = 30
                elif 60 < barrel_thick <= 100:
                    index_1 = 31
                else:
                    print('请输入合理的管壳厚度')
            elif material == '07MnNiCrMoVDR':
                if 16 <= barrel_thick <= 50:
                    index_1 = 32
                else:
                    print('请输入合理的管壳厚度')
            elif material == '15MnNiDR':
                if barrel_thick <= 16:
                    index_1 = 33
                elif 16 < barrel_thick <= 36:
                    index_1 = 34
                elif 36 < barrel_thick <= 60:
                    index_1 = 35
                else:
                    print('请输入合理的管壳厚度')
            elif material == '09MnNiDR':
                if barrel_thick <= 16:
                    index_1 = 36
                elif 16 < barrel_thick <= 36:
                    index_1 = 37
                elif 36 < barrel_thick <= 100:
                    index_1 = 38
                else:
                    print('请输入合理的管壳厚度')
            elif material == '15CrMoR':
                if barrel_thick <= 40:
                    index_1 = 39
                elif 40 < barrel_thick <= 100:
                    index_1 = 40
                else:
                    print('请输入合理的管壳厚度')
            elif material == '14Cr1MoR':
                if 16 <= barrel_thick <= 120:
                    index_1 = 41
                else:
                    print('请输入合理的管壳厚度')
            material_per_stress = self.data_stress.iloc[index_1, index_2]  # 设计温度下材料的许用应力
            material_nom_stress = self.data_stress.iloc[index_1, 2]  # 常温强度指标
            # print('设计温度下材料的许用应力:%d' % material_per_stress)
            # print('常温强度指标:%d' % material_nom_stress)
            text_pressure = 1.25*work_pressure          # 试验压力
            text_per_stress = text_pressure*(barrel_diameter+barrel_valid_thick)/(2*barrel_valid_thick) # 试验应力
            text_T = 0.9*welded_joint_coeff*material_nom_stress
            if text_per_stress < text_T:
                print('筒体校核强度安全')
            else:
                print('校核强度不满足')

            head_cal_thick = work_pressure_2*barrel_diameter/(2*material_per_stress*welded_joint_coeff - 0.5*work_pressure_2)

            if head_cal_thick+barrel_C1+barrel_C2 > barrel_thick:
                head_cal_thick = 2 + barrel_thick
            head_cal_thick = max(head_cal_thick, barrel_thick)
            # print('封头厚度：%d' % head_cal_thick)
            self.textBrowser_2.append('封头厚度：%d mm' % head_cal_thick)
            head_valid_thick = head_cal_thick - barrel_C1 - barrel_C2
            work_pressure_2_max = 2*material_per_stress*welded_joint_coeff*head_valid_thick/(barrel_diameter+0.5*head_valid_thick)
            if work_pressure_2 < work_pressure_2_max:
                print("封头符合强度要求")
            else:
                print("封头不符合强度要求")
            self.textBrowser_2.append('-----------------------------')

    def designer_C1(self, data):
        barrel_thick = data             # 管壳筒体厚度
        if barrel_thick <= 2.2:
            barrel_C1 = 0.18
        elif 2.2 < barrel_thick < 2.5:
            barrel_C1 = 0.19
        elif 2.5 <= barrel_thick < 2.8:
            barrel_C1 = 0.20
        elif 2.8 <= barrel_thick <= 3.0:
            barrel_C1 = 0.22
        elif 3.0 < barrel_thick <= 3.5:
            barrel_C1 = 0.25
        elif 3.5 < barrel_thick <= 4.0:
            barrel_C1 = 0.3
        elif 4.0 < barrel_thick <= 5.5:
            barrel_C1 = 0.5
        elif 5.5 < barrel_thick <= 7:
            barrel_C1 = 0.6
        elif 7 < barrel_thick <= 25:
            barrel_C1 = 0.8
        elif 25 < barrel_thick <= 30:
            barrel_C1 = 0.9
        elif 30 < barrel_thick <= 34:
            barrel_C1 = 1.0
        elif 34 < barrel_thick <= 40:
            barrel_C1 = 1.1
        elif 40 < barrel_thick <= 50:
            barrel_C1 = 1.2
        elif 50 < barrel_thick <= 60:
            barrel_C1 = 1.3
        else:
            print('请重新输入合适的管壳厚度')
        return barrel_C1

    def change_temper_type(self, data):
        if data <=50:
            return 20
        if 50 <= data <= 100:
            return 100
        if 100 < data <= 150:
            return 150
        if 150 < data <= 200:
            return 200
        if 200 < data <= 250:
            return 250
        if 350 < data <= 400:
            return 400
        if 400 < data <= 425:
            return 425
        if 425 < data <= 475:
            return 475
        if 475 < data <= 500:
            return 500
        if 500 < data <= 525:
            return 525
        if 525 < data <= 550:
            return 550
        if 550 < data <= 575:
            return 575

    def change_diameter_type(self, data):
        if data<100:
            return 5
        if 100 <= data <=200:
            return 6
        if 200 < data <=400:
            return 7.5
        if 400 < data <=700:
            return 8
        if 700 < data <=1000:
            return 10
        if 1000 < data <=1500:
            return 12
        if 1500 < data <=2000:
            return 14
        if 2000 < data <=3200:
            return 16
        if 3200 < data <=4000:
            return 18

    def ControlBoard(self):
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)

        self.pushButton_2.clicked.connect(self.bClicked)
        self.pushButton_3.clicked.connect(self.bClicked)
        self.pushButton_6.clicked.connect(self.bClicked)

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()

    def bClicked(self):
        """Runs the main function."""
        print('已重置')

    # 树控件
    def showMsg_2(self):
        item = self.treeWidget.currentItem()
        if item.text(0) == '烟气物性参数':
            self.phy_pro_param_smoke.show()
        elif item.text(0) == '冷却剂物性参数':
            self.phy_pro_param_cooler.show()


# 树控件中烟气物性参数子窗口
class Physical_property_parameter_smoke(QWidget, untitled.Ui_MainWindow):
    def __init__(self):
        super(Physical_property_parameter_smoke, self).__init__()
        self.setWindowTitle('烟气物性参数')
        self.resize(300, 200)
        self.setFixedSize(self.width(), self.height())
        self.textBrowser_3 = QTextBrowser(self)
        self.textBrowser_3.setGeometry(QtCore.QRect(0, 0, 280, 240))

# 树控件中冷却剂物性参数子窗口
class Physical_property_parameter_cooler(QWidget, untitled.Ui_MainWindow):
    def __init__(self):
        super(Physical_property_parameter_cooler, self).__init__()
        self.setWindowTitle('冷却剂的物性参数')
        self.resize(300, 200)
        self.setFixedSize(self.width(), self.height())
        self.textBrowser_4 = QTextBrowser(self)
        self.textBrowser_4.setGeometry(QtCore.QRect(0, 0, 280, 240))

# 定义一个发送str的信号
class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))

if __name__ == '__main__':

    myWin = Calculate()
    myWin.show()
    sys.exit(myWin.app.exec())






