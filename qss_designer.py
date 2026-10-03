# -*- coding: utf-8 -*-
"""
QSS Studio —— 所见即所得的 QSS 可视化设计器
-------------------------------------------
用鼠标点选控件 -> 在右侧面板用鼠标调整颜色 / 边框 / 圆角 / 内边距 / 字体
-> 实时预览 QSS 效果 -> 一键复制 QSS 代码到 PyQt6 / PySide6 项目中使用。

作者注：QSS 语法在 PyQt5 / PyQt6 / PySide2 / PySide6 之间通用，
导出的 .qss 可直接通过 widget.setStyleSheet(qss文本) 或全局
QApplication.instance().setStyleSheet(qss文本) 应用。
"""

import re
import sys

from PySide6.QtCore import (
    Qt, QEvent, QPoint, QRect, QTimer, Signal, QStringListModel, QUrl,
)
from PySide6.QtGui import (
    QColor, QFont, QKeySequence, QShortcut,
    QStandardItemModel, QStandardItem, QDesktopServices,
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QScrollArea, QLabel, QPushButton, QToolButton,
    QLineEdit, QTextEdit, QCheckBox, QRadioButton, QComboBox, QSpinBox,
    QSlider, QProgressBar, QTabWidget, QFrame, QPlainTextEdit, QListWidget, QListWidgetItem,
    QColorDialog, QFileDialog, QMessageBox, QSizePolicy, QInputDialog,
    QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit, QDial, QLCDNumber,
    QFontComboBox, QTableWidget, QTableWidgetItem, QTreeWidget,
    QTreeWidgetItem, QTextBrowser, QToolBox, QCalendarWidget,
    QKeySequenceEdit, QScrollBar, QMenuBar, QStatusBar, QCommandLinkButton,
    QMenu,
    QStackedWidget, QToolBar, QDockWidget, QMdiArea, QMdiSubWindow,
    QListView, QTableView, QTreeView, QColumnView, QTabBar,
    QDialogButtonBox, QSizeGrip,
)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 赞赏 / 捐助链接（爱发电主页地址）
DONATE_URL = "https://afdian.com/a/oflash"

# 伪状态列表：(显示文本, 选择器后缀)
STATE_LIST = [
    ("正常（默认样式）", ""),
    ("鼠标悬停  :hover", "hover"),
    ("鼠标按下  :pressed", "pressed"),
    ("获得焦点  :focus", "focus"),
    ("选中状态  :checked", "checked"),
    ("禁用状态  :disabled", "disabled"),
]

# QSS 属性的固定输出顺序
PROPS_ORDER = [
    "background-color", "background-image", "background-repeat",
    "background-position", "color",
    "border-width", "border-top-width", "border-right-width",
    "border-bottom-width", "border-left-width",
    "border-style", "border-color", "border-top-color", "border-right-color",
    "border-bottom-color", "border-left-color", "border-radius",
    "outline", "margin", "padding", "min-width", "min-height",
    "font-family", "font-size", "font-weight", "font-style",
    "letter-spacing", "word-spacing", "text-decoration", "text-align",
    "selection-color", "selection-background-color",
    "image", "image-position",
]

BACKGROUND_REPEATS = [
    ("默认", None), ("重复平铺 repeat", "repeat"),
    ("横向重复 repeat-x", "repeat-x"), ("纵向重复 repeat-y", "repeat-y"),
    ("不重复 no-repeat", "no-repeat"),
]
BACKGROUND_POSITIONS = [
    ("默认", None), ("左上 left top", "left top"), ("居中 center", "center"),
    ("右上 right top", "right top"), ("左下 left bottom", "left bottom"),
    ("右下 right bottom", "right bottom"),
]
FONT_STYLES = [("默认", None), ("普通 normal", "normal"), ("斜体 italic", "italic")]
TEXT_DECORATIONS = [
    ("默认", None), ("无 none", "none"), ("下划线 underline", "underline"),
    ("删除线 line-through", "line-through"), ("上划线 overline", "overline"),
]
TEXT_ALIGNS = [
    ("默认", None), ("左 left", "left"), ("居中 center", "center"),
    ("右 right", "right"), ("两端对齐 justify", "justify"),
]
IMAGE_POSITIONS = [
    ("默认", None), ("左 left", "left"), ("居中 center", "center"),
    ("右 right", "right"), ("顶部 top", "top"), ("底部 bottom", "bottom"),
]

BORDER_STYLES = [
    ("默认", None), ("solid 实线", "solid"), ("dashed 虚线", "dashed"),
    ("dotted 点线", "dotted"), ("double 双线", "double"),
]

FONT_WEIGHTS = [
    ("默认", None), ("normal 常规", "normal"), ("bold 加粗", "bold"),
]

# 命名样式方案（变体）预设：在 PyQt6 中用
# button.setProperty("variant", "primary") 切换，生成 QPushButton[variant="..."]
VARIANT_PRESETS = ["primary", "success", "warning", "danger", "info"]

# 控件中文名映射：用于"选择控件"下拉框的友好显示
WIDGET_CN_NAMES = {
    # 按钮类
    "pushButton": "普通按钮",
    "checkButton": "可选中按钮",
    "disabledButton": "禁用按钮",
    "menuToolButton": "工具按钮(菜单)",
    "commandLinkButton": "命令链接按钮",
    # 输入框类
    "lineEdit": "单行输入框",
    "textEdit": "多行文本框",
    "plainTextEdit": "纯文本框",
    "textBrowser": "富文本浏览器",
    "comboBox": "下拉框",
    "spinBox": "整数微调框",
    "doubleSpinBox": "小数微调框",
    "fontComboBox": "字体下拉框",
    "dateEdit": "日期编辑",
    "timeEdit": "时间编辑",
    "dateTimeEdit": "日期时间编辑",
    "keySequenceEdit": "快捷键编辑",
    # 显示类
    "label": "文本标签",
    "lcdNumber": "LCD数字",
    "progressBar": "进度条",
    # 勾选类
    "checkBox": "复选框",
    "radioButton": "单选框",
    # 滑块类
    "slider": "滑块",
    "hScrollBar": "横向滚动条",
    "dial": "旋钮",
    # 容器类
    "groupBox": "分组框",
    "demoFrame": "框架",
    "demoWidget": "基础容器",
    "tabWidget": "标签页",
    "toolBox": "工具箱",
    "listWidget": "列表",
    "treeWidget": "树",
    "tableWidget": "表格",
    # 窗口类
    "menuBar": "菜单栏",
    "toolBar": "工具栏",
    "statusBar": "状态栏",
    # variant 演示按钮
    "btn_primary": "主要按钮(primary)",
    "btn_success": "成功按钮(success)",
    "btn_warning": "警告按钮(warning)",
    "btn_danger": "危险按钮(danger)",
    "btn_info": "信息按钮(info)",
}

# 解析规则列表中的选择器：#id / Class / Class[variant="x"]，可选 :state
SELECTOR_RE = re.compile(
    r'^(?P<base>#\w+|[A-Za-z_]\w*'
    r'(?:\[variant="(?P<variant>[^"]*)"\])?)'
    r'(?::(?P<state>[a-z-]+))?$'
)

# 选中高亮框的样式（仅编辑器内部使用，不会输出到最终 QSS）
RUBBER_OBJ = "__selRubber"
RUBBER_QSS = ""  # 占位，已改用 paintEvent 绘制四角括号


class _SelectionCorner(QWidget):
    """选中控件高亮指示器：四角括号，不遮挡控件本体。

    与旧版 2px 橙色边框相比，四角括号完全不接触控件本身的边框/背景区域，
    用户调边框颜色、圆角、背景色时不会被高亮框干扰判断。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.hide()

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QPen
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#ff8a00"))
        pen.setWidth(3)
        painter.setPen(pen)
        r = self.rect()
        # 四角括号边长
        arm = 10
        m = 1  # 内缩
        # 左上
        painter.drawLine(r.left() + m, r.top() + m, r.left() + m + arm, r.top() + m)
        painter.drawLine(r.left() + m, r.top() + m, r.left() + m, r.top() + m + arm)
        # 右上
        painter.drawLine(r.right() - m, r.top() + m, r.right() - m - arm, r.top() + m)
        painter.drawLine(r.right() - m, r.top() + m, r.right() - m, r.top() + m + arm)
        # 左下
        painter.drawLine(r.left() + m, r.bottom() - m, r.left() + m + arm, r.bottom() - m)
        painter.drawLine(r.left() + m, r.bottom() - m, r.left() + m, r.bottom() - m - arm)
        # 右下
        painter.drawLine(r.right() - m, r.bottom() - m, r.right() - m - arm, r.bottom() - m)
        painter.drawLine(r.right() - m, r.bottom() - m, r.right() - m, r.bottom() - m - arm)


# ---------------------------------------------------------------------------
# 颜色选择行：色块按钮 + 色值文本 + 清除按钮（全程鼠标操作）
# ---------------------------------------------------------------------------

class ColorRow(QWidget):
    """选择/清除一个颜色值，值为 None 表示未设置。"""

    changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        self.swatch = QToolButton()
        self.swatch.setFixedSize(58, 24)
        self.swatch.setAutoRaise(True)
        self.swatch.clicked.connect(self._pick)

        self.value_label = QLabel("未设置")

        # 透明度滑块（0-100%）
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 100)
        self.alpha_slider.setValue(100)
        self.alpha_slider.setFixedWidth(60)
        self.alpha_slider.setToolTip("透明度（100 = 不透明）")
        self.alpha_slider.valueChanged.connect(self._on_alpha_changed)

        self.alpha_label = QLabel("100%")
        self.alpha_label.setFixedWidth(32)
        self.alpha_label.setStyleSheet("color: #666; font-size: 11px;")

        self.clear_btn = QToolButton()
        self.clear_btn.setText("×")
        self.clear_btn.setFixedWidth(24)
        self.clear_btn.setToolTip("清除该颜色")
        self.clear_btn.clicked.connect(lambda: self.set_value(None, emit=True))

        lay.addWidget(self.swatch)
        lay.addWidget(self.value_label, 1)
        lay.addWidget(self.alpha_slider)
        lay.addWidget(self.alpha_label)
        lay.addWidget(self.clear_btn)

        self._value = None
        self._sync_alpha_slider()  # 初始化滑块状态
        self.set_value(None)

    def value(self):
        return self._value

    @staticmethod
    def _parse_color(s):
        """解析颜色字符串，返回 (r, g, b, a) 或 None。"""
        s = s.strip()
        # #rrggbb
        if re.fullmatch(r"#[0-9a-fA-F]{6}", s):
            return (int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16), 255)
        # #aarrggbb
        if re.fullmatch(r"#[0-9a-fA-F]{8}", s):
            return (int(s[3:5], 16), int(s[5:7], 16), int(s[7:9], 16),
                    int(s[1:3], 16))
        # rgba(r, g, b, a)
        m = re.fullmatch(
            r"rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)",
            s
        )
        if m:
            r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
            a_val = float(m.group(4))
            a = int(a_val * 255) if a_val <= 1.0 else int(a_val)
            return r, g, b, a
        return None

    def _sync_alpha_slider(self):
        """根据当前颜色值同步滑块位置。"""
        if not self._value:
            self.alpha_slider.blockSignals(True)
            self.alpha_slider.setValue(100)
            self.alpha_slider.blockSignals(False)
            self.alpha_label.setText("100%")
            return
        parsed = self._parse_color(self._value)
        if parsed:
            alpha_pct = round(parsed[3] / 255 * 100)
            self.alpha_slider.blockSignals(True)
            self.alpha_slider.setValue(alpha_pct)
            self.alpha_slider.blockSignals(False)
            self.alpha_label.setText(f"{alpha_pct}%")
        else:
            self.alpha_slider.blockSignals(True)
            self.alpha_slider.setValue(100)
            self.alpha_slider.blockSignals(False)
            self.alpha_label.setText("100%")

    def _on_alpha_changed(self, value):
        """滑块值改变时更新颜色的 alpha 通道。"""
        self.alpha_label.setText(f"{value}%")
        if not self._value:
            return
        parsed = self._parse_color(self._value)
        if not parsed:
            return
        r, g, b, _ = parsed
        new_alpha = int(value / 100 * 255)
        if new_alpha == 255:
            new_value = f"#{r:02x}{g:02x}{b:02x}"
        else:
            new_value = (f"rgba({r}, {g}, {b}, "
                         f"{new_alpha / 255:.3g})")
        self._value = new_value
        self.swatch.setStyleSheet(
            f"background-color: {new_value}; border: 1px solid #666;"
            " border-radius: 2px;"
        )
        self.value_label.setText(new_value)
        self.changed.emit(new_value)

    def set_value(self, value, emit=False):
        self._value = value
        if value:
            self.swatch.setStyleSheet(
                f"background-color: {value}; border: 1px solid #666;"
                " border-radius: 2px;"
            )
            self.value_label.setText(value)
            self.clear_btn.setEnabled(True)
        else:
            self.swatch.setStyleSheet(
                "background-color: #f0f0f0; border: 1px dashed #999;"
                " border-radius: 2px;"
            )
            self.swatch.setText("")
            self.value_label.setText("未设置")
            self.clear_btn.setEnabled(False)
        self._sync_alpha_slider()
        if emit:
            self.changed.emit(value)

    def _pick(self):
        initial = QColor(self._value) if self._value else QColor("#ffffff")
        color = QColorDialog.getColor(
            initial, self, "选择颜色",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if not color.isValid():
            return
        if color.alpha() == 255:
            value = color.name()
        else:
            # 与 Qt 规范化后的写法保持一致（逗号后带空格）
            value = (f"rgba({color.red()}, {color.green()}, {color.blue()}, "
                     f"{color.alpha() / 255:.3g})")
        self.set_value(value, emit=True)


# ---------------------------------------------------------------------------
# 主窗口
# ---------------------------------------------------------------------------

class QssDesignerWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "QSS Studio —— 所见即所得的 QSS 可视化设计器"
            "（鼠标编辑 · 实时预览 · 一键复制到 PyQt6）"
        )
        self.resize(1920, 1080)
        self.setMinimumSize(1280, 720)

        # 数据模型（候选样式）：
        # cand = {基础选择器: [ {"name": 候选名, "rules": {完整选择器: {属性: 值}}} ]}
        # 同一个控件（如 QPushButton）可以并行维护多套互相独立的备选 QSS，
        # 每套候选的选择器完全相同，按套分别复制；当前正在编辑的那套进入“全部 QSS”。
        self.cand = {}
        self.edit_idx = {}             # {基础选择器: 当前编辑的候选下标}
        self.rules = {}                # 实时指向当前候选的 rules 字典
        self.selectables = []          # 可在预览区被点选的控件
        self.selected = None
        self._loading = False          # 程序化填充面板时屏蔽信号
        self._forced_disabled = None   # 为预览 :disabled 临时禁用的控件
        # 特效模块已移除

        self._build_ui()
        self._wire_signals()

        # 默认选中一个按钮，打开即可开始调色
        self.select_widget(self.push_button)
        self.statusBar().showMessage(
            "就绪：在中间预览区单击控件，用左侧面板调整样式；"
            "可连续设计任意控件与命名方案，最后在右侧一键复制全部 QSS。"
        )

        # 启动后自动加宽属性区，直到正文不再出现横向滚动条
        QTimer.singleShot(0, self._autofit_props_width)
        QTimer.singleShot(250, self._autofit_props_width)

    def _autofit_props_width(self):
        """运行时实测：属性区若有横向滚动条，就从预览区匀出宽度消除它。"""
        try:
            bar = self.props_scroll.horizontalScrollBar()
        except AttributeError:
            return
        overflow = bar.maximum()
        if overflow <= 0:
            return
        sizes = self.main_splitter.sizes()
        if len(sizes) != 3:
            return
        # 预览区至少保留 360px，其余溢出量全部补给属性区
        extra = min(overflow + 4, max(0, sizes[1] - 360))
        if extra <= 0:
            return
        sizes[0] += extra
        sizes[1] -= extra
        self.main_splitter.setSizes(sizes)

    def _open_donate_page(self):
        """用系统默认浏览器打开赞赏页面；完全自愿，不阻断使用。"""
        opened = QDesktopServices.openUrl(QUrl(DONATE_URL))
        if opened:
            self.statusBar().showMessage(
                "感谢你的支持！已在浏览器中打开赞赏页面 ❤", 8000
            )
        else:
            QMessageBox.information(
                self,
                "赞赏支持作者",
                f"无法自动打开浏览器，请手动复制链接访问：\n\n{DONATE_URL}",
            )

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        # 三大板块：左 = 属性编辑区，中 = 控件点选 / 实时预览，右 = QSS 代码区
        self.main_splitter = main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self._build_props_panel())
        main_splitter.addWidget(self._build_canvas())
        main_splitter.addWidget(self._build_code_panel())
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setStretchFactor(2, 0)
        main_splitter.setSizes([500, 860, 560])

        self.setCentralWidget(main_splitter)

        QShortcut(QKeySequence.StandardKey.Save, self, activated=self.save_qss)

    # ---------------- 预览画布

    def _build_canvas(self):
        box = QWidget()
        # 预览内容在滚动区域内，允许整体栏被压窄（宽度优先让给属性区）
        box.setMinimumWidth(320)
        lay = QVBoxLayout(box)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)

        hint = QLabel(
            "实时预览区：单击选中控件；可直接把鼠标悬停 / 按下控件查看交互状态；"
            "底部“方案按钮演示”会随多方案设计实时联动"
        )
        hint.setStyleSheet("color: #666;")
        lay.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.preview = QWidget()
        self.preview.setObjectName("previewWidget")
        self.preview.installEventFilter(self)

        self._populate_preview(self.preview)

        scroll.setWidget(self.preview)
        lay.addWidget(scroll, 1)

        # 选中高亮框（四角括号，覆盖在预览画布上，透传鼠标事件，不遮挡控件本体）
        self.rubber = _SelectionCorner(self.preview)

        return box

    def _add_selectable(self, widget):
        # 给控件本身 + 所有已存在的子控件装过滤器，确保点击控件任意部位都能选中
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)
        self.selectables.append(widget)
        # 同时加入控件选择下拉框：英文名 + 中文名
        obj_name = widget.objectName()
        cls_name = type(widget).__name__
        cn_name = WIDGET_CN_NAMES.get(obj_name, "")
        if cn_name:
            display = f"{cls_name} ({obj_name}) - {cn_name}"
        else:
            display = f"{cls_name} ({obj_name})" if obj_name else cls_name
        self.widget_pick.addItem(display, widget)

    def _populate_preview(self, canvas):
        lay = QVBoxLayout(canvas)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        def hbox(spacing=12):
            row = QHBoxLayout()
            row.setSpacing(spacing)
            return row

        # ---- 行1：按钮类 ----
        self.push_button = QPushButton("普通按钮")
        self.push_button.setObjectName("pushButton")
        self._add_selectable(self.push_button)

        self.check_button = QPushButton("可选中按钮（开）")
        self.check_button.setObjectName("checkButton")
        self.check_button.setCheckable(True)
        self.check_button.setChecked(True)
        self.check_button.toggled.connect(
            lambda on: self.check_button.setText(
                "可选中按钮（开）" if on else "可选中按钮（关）"
            )
        )
        self._add_selectable(self.check_button)

        self.disabled_button = QPushButton("禁用按钮")
        self.disabled_button.setObjectName("disabledButton")
        self.disabled_button.setEnabled(False)
        self._add_selectable(self.disabled_button)

        self.menu_tool_button = QToolButton()
        self.menu_tool_button.setObjectName("menuToolButton")
        self.menu_tool_button.setText("工具按钮")
        self.menu_tool_button.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup
        )
        tool_menu = QMenu(self.menu_tool_button)
        tool_menu.addAction("菜单一")
        tool_menu.addAction("菜单二")
        tool_menu.addSeparator()
        tool_menu.addAction("菜单三")
        self.menu_tool_button.setMenu(tool_menu)
        self._add_selectable(self.menu_tool_button)

        self.command_link_button = QCommandLinkButton(
            "命令链接按钮", "QCommandLinkButton 的说明文字"
        )
        self.command_link_button.setObjectName("commandLinkButton")
        self._add_selectable(self.command_link_button)

        for btn in (
            self.push_button, self.check_button, self.disabled_button,
            self.menu_tool_button, self.command_link_button,
        ):
            btn.setMinimumHeight(36)
            btn.setMinimumWidth(120)

        row = hbox()
        row.addWidget(self.push_button)
        row.addWidget(self.check_button)
        row.addWidget(self.disabled_button)
        row.addWidget(self.menu_tool_button)
        row.addWidget(self.command_link_button)
        lay.addLayout(row)

        # ---- 行2：输入框类 ----
        self.line_edit = QLineEdit()
        self.line_edit.setObjectName("lineEdit")
        self.line_edit.setPlaceholderText("请输入文本…")
        self._add_selectable(self.line_edit)

        self.combo_box = QComboBox()
        self.combo_box.setObjectName("comboBox")
        self.combo_box.addItems(["选项一", "选项二", "选项三"])
        self._add_selectable(self.combo_box)

        self.spin_box = QSpinBox()
        self.spin_box.setObjectName("spinBox")
        self.spin_box.setRange(0, 100)
        self.spin_box.setValue(25)
        self._add_selectable(self.spin_box)

        self.double_spin_box = QDoubleSpinBox()
        self.double_spin_box.setObjectName("doubleSpinBox")
        self.double_spin_box.setRange(0.0, 10.0)
        self.double_spin_box.setSingleStep(0.1)
        self.double_spin_box.setValue(2.5)
        self.double_spin_box.setSuffix(" kg")
        self._add_selectable(self.double_spin_box)

        self.font_combo = QFontComboBox()
        self.font_combo.setObjectName("fontComboBox")
        self._add_selectable(self.font_combo)

        for inp in (
            self.line_edit, self.combo_box, self.spin_box,
            self.double_spin_box, self.font_combo,
        ):
            inp.setMinimumHeight(32)
            inp.setMinimumWidth(180)

        row = hbox()
        row.addWidget(self.line_edit, 1)
        row.addWidget(self.combo_box, 1)
        row.addWidget(self.spin_box, 1)
        row.addWidget(self.double_spin_box, 1)
        row.addWidget(self.font_combo, 1)
        lay.addLayout(row)

        # ---- 行3：日期时间 ----
        self.date_edit = QDateEdit()
        self.date_edit.setObjectName("dateEdit")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self._add_selectable(self.date_edit)

        self.time_edit = QTimeEdit()
        self.time_edit.setObjectName("timeEdit")
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self._add_selectable(self.time_edit)

        self.date_time_edit = QDateTimeEdit()
        self.date_time_edit.setObjectName("dateTimeEdit")
        self.date_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self._add_selectable(self.date_time_edit)

        self.key_sequence_edit = QKeySequenceEdit()
        self.key_sequence_edit.setObjectName("keySequenceEdit")
        self.key_sequence_edit.setKeySequence(QKeySequence("Ctrl+S"))
        self._add_selectable(self.key_sequence_edit)

        for inp in (
            self.date_edit, self.time_edit, self.date_time_edit,
            self.key_sequence_edit,
        ):
            inp.setMinimumHeight(32)
            inp.setMinimumWidth(180)

        row = hbox()
        row.addWidget(self.date_edit, 1)
        row.addWidget(self.time_edit, 1)
        row.addWidget(self.date_time_edit, 1)
        row.addWidget(self.key_sequence_edit, 1)
        lay.addLayout(row)

        # ---- 行4：勾选 / 标签 ----
        self.check_box = QCheckBox("复选框 CheckBox")
        self.check_box.setObjectName("checkBox")
        self.check_box.setChecked(True)
        self._add_selectable(self.check_box)

        self.radio_button = QRadioButton("单选框 RadioButton")
        self.radio_button.setObjectName("radioButton")
        self.radio_button.setChecked(True)
        self._add_selectable(self.radio_button)

        self.label = QLabel("文本标签 Text Label")
        self.label.setObjectName("label")
        self._add_selectable(self.label)

        for w in (self.check_box, self.radio_button, self.label):
            w.setMinimumHeight(28)

        row = hbox(18)
        row.addWidget(self.check_box)
        row.addWidget(self.radio_button)
        row.addWidget(self.label)
        lay.addLayout(row)

        # ---- 行5：滑块类 ----
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setObjectName("slider")
        self.slider.setValue(40)
        self._add_selectable(self.slider)

        self.h_scroll_bar = QScrollBar(Qt.Orientation.Horizontal)
        self.h_scroll_bar.setObjectName("hScrollBar")
        self.h_scroll_bar.setValue(40)
        self._add_selectable(self.h_scroll_bar)

        self.dial = QDial()
        self.dial.setObjectName("dial")
        self.dial.setNotchesVisible(True)
        self.dial.setValue(50)
        self.dial.setFixedSize(80, 80)
        self._add_selectable(self.dial)

        self.lcd_number = QLCDNumber()
        self.lcd_number.setObjectName("lcdNumber")
        self.lcd_number.setDigitCount(5)
        self.lcd_number.display("12:34")
        self._add_selectable(self.lcd_number)

        for w in (self.slider, self.h_scroll_bar, self.lcd_number):
            w.setMinimumHeight(36)

        row = hbox()
        row.addWidget(self.slider, 1)
        row.addWidget(self.h_scroll_bar, 1)
        row.addWidget(self.dial)
        row.addWidget(self.lcd_number)
        lay.addLayout(row)

        # ---- 行6：进度 / 容器 ----
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setValue(60)
        self._add_selectable(self.progress_bar)

        self.group_box = QGroupBox("分组框 GroupBox")
        self.group_box.setObjectName("groupBox")
        # 空容器，不再放组内按钮，避免误点
        self._add_selectable(self.group_box)

        self.demo_frame = QFrame()
        self.demo_frame.setObjectName("demoFrame")
        self.demo_frame.setFrameShape(QFrame.Shape.StyledPanel)
        QVBoxLayout(self.demo_frame).addWidget(QLabel("QFrame 容器示例"))
        self._add_selectable(self.demo_frame)

        # 基础容器 QWidget：必须开启 WA_StyledBackground，QSS 背景色才能绘制出来
        self.demo_widget = QWidget()
        self.demo_widget.setObjectName("demoWidget")
        self.demo_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.demo_widget.setMinimumHeight(80)
        dwl = QVBoxLayout(self.demo_widget)
        dwl.addWidget(QLabel("QWidget 容器示例"))
        self._add_selectable(self.demo_widget)

        self.progress_bar.setMinimumHeight(36)

        row = hbox()
        row.addWidget(self.progress_bar, 1)
        row.addWidget(self.group_box, 1)
        row.addWidget(self.demo_frame, 1)
        row.addWidget(self.demo_widget, 1)
        lay.addLayout(row)

        # ---- 行7：多行文本 ----
        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("textEdit")
        self.text_edit.setPlainText("多行文本框 QTextEdit")
        self.text_edit.setMinimumHeight(90)
        self._add_selectable(self.text_edit)

        self.plain_text_edit = QPlainTextEdit()
        self.plain_text_edit.setObjectName("plainTextEdit")
        self.plain_text_edit.setPlainText("纯文本编辑框 QPlainTextEdit")
        self.plain_text_edit.setMinimumHeight(90)
        self._add_selectable(self.plain_text_edit)

        self.text_browser = QTextBrowser()
        self.text_browser.setObjectName("textBrowser")
        self.text_browser.setMinimumHeight(90)
        self.text_browser.setHtml(
            "<b>QTextBrowser</b>：只读富文本框，支持 <i>HTML</i>"
        )
        self._add_selectable(self.text_browser)

        row = hbox()
        row.addWidget(self.text_edit, 1)
        row.addWidget(self.plain_text_edit, 1)
        row.addWidget(self.text_browser, 1)
        lay.addLayout(row)

        # ---- 行8：列表 / 树 / 表 ----
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("listWidget")
        self.list_widget.addItems([
            "列表项 1", "列表项 2", "列表项 3", "列表项 4", "列表项 5",
        ])
        self.list_widget.setMinimumHeight(140)
        self._add_selectable(self.list_widget)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setObjectName("treeWidget")
        self.tree_widget.setHeaderLabels(["QTreeWidget 树节点"])
        for i in range(1, 3):
            top = QTreeWidgetItem([f"父节点 {i}"])
            top.addChild(QTreeWidgetItem([f"子节点 {i}.1"]))
            top.addChild(QTreeWidgetItem([f"子节点 {i}.2"]))
            self.tree_widget.addTopLevelItem(top)
        self.tree_widget.expandAll()
        self.tree_widget.setMinimumHeight(140)
        self._add_selectable(self.tree_widget)

        self.table_widget = QTableWidget(3, 2)
        self.table_widget.setObjectName("tableWidget")
        self.table_widget.setHorizontalHeaderLabels(["列一", "列二"])
        for r in range(3):
            for c in range(2):
                self.table_widget.setItem(
                    r, c, QTableWidgetItem(f"单元格 {r + 1}-{c + 1}")
                )
        self.table_widget.setMinimumHeight(140)
        self._add_selectable(self.table_widget)

        row = hbox()
        row.addWidget(self.list_widget, 1)
        row.addWidget(self.tree_widget, 1)
        row.addWidget(self.table_widget, 1)
        lay.addLayout(row)

        # ---- 行9：标签页 / 工具箱 ----
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("tabWidget")
        tab1 = QWidget()
        QVBoxLayout(tab1).addWidget(QLabel("第一个标签页的内容"))
        tab2 = QWidget()
        QVBoxLayout(tab2).addWidget(QCheckBox("第二个标签页里的复选框"))
        self.tab_widget.addTab(tab1, "标签一")
        self.tab_widget.addTab(tab2, "标签二")
        self.tab_widget.setMinimumHeight(140)
        self._add_selectable(self.tab_widget)

        self.tool_box = QToolBox()
        self.tool_box.setObjectName("toolBox")
        tool_box_page1 = QWidget()
        QVBoxLayout(tool_box_page1).addWidget(QLabel("第一页的内容"))
        tool_box_page2 = QWidget()
        QVBoxLayout(tool_box_page2).addWidget(QPushButton("第二页里的按钮"))
        self.tool_box.addItem(tool_box_page1, "页签一")
        self.tool_box.addItem(tool_box_page2, "页签二")
        self.tool_box.setMinimumHeight(140)
        self._add_selectable(self.tool_box)

        row = hbox()
        row.addWidget(self.tab_widget, 1)
        row.addWidget(self.tool_box, 1)
        lay.addLayout(row)

        # ---- 行10：菜单 / 工具栏 / 状态栏 ----
        self.menu_bar = QMenuBar()
        self.menu_bar.setObjectName("menuBar")
        file_menu = self.menu_bar.addMenu("文件")
        file_menu.addAction("打开…")
        file_menu.addAction("保存")
        edit_menu = self.menu_bar.addMenu("编辑")
        edit_menu.addAction("复制")
        edit_menu.addAction("粘贴")
        self._add_selectable(self.menu_bar)

        self.tool_bar = QToolBar()
        self.tool_bar.setObjectName("toolBar")
        self.tool_bar.setMovable(False)
        self.tool_bar.setFloatable(False)
        self.tool_bar.addAction("文件")
        self.tool_bar.addAction("编辑")
        self.tool_bar.addSeparator()
        self.tool_bar.addAction("帮助")
        self._add_selectable(self.tool_bar)

        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("statusBar")
        self.status_bar.showMessage("状态条信息 QStatusBar")
        self._add_selectable(self.status_bar)

        for w in (self.menu_bar, self.tool_bar, self.status_bar):
            w.setMinimumHeight(32)

        row = hbox()
        row.addWidget(self.menu_bar, 1)
        row.addWidget(self.tool_bar)
        row.addWidget(self.status_bar, 1)
        lay.addLayout(row)

        lay.addStretch(1)

        # ---- 行11：多方案演示按钮 ----
        self.variant_buttons = []
        variant_row = QHBoxLayout()
        variant_row.setSpacing(6)
        variant_row.addWidget(QLabel("方案演示："))
        for name in VARIANT_PRESETS:
            btn = QPushButton(name)
            btn.setObjectName(f"btn_{name}")
            btn.setProperty("variant", name)
            btn.setToolTip(
                f'此按钮自带 variant="{name}" 属性，\n'
                "在左侧“应用范围”选择“命名方案”即可编辑它的专属样式。"
            )
            variant_row.addWidget(btn)
            self._add_selectable(btn)
            self.variant_buttons.append(btn)
            if name == "primary":
                self.primary_button = btn
        variant_row.addStretch(1)
        lay.addLayout(variant_row)


    # ---------------- 属性面板

    def _build_props_panel(self):
        outer = QWidget()
        outer.setMinimumWidth(400)
        outer_lay = QVBoxLayout(outer)
        outer_lay.setContentsMargins(8, 8, 8, 8)

        title = QLabel("属性编辑区")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        outer_lay.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.props_scroll = scroll
        panel = QWidget()
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(4, 4, 8, 4)
        pl.setSpacing(8)

        # —— 控件选择下拉框 ——
        widget_pick_group = QGroupBox("选择控件")
        wpf = QVBoxLayout(widget_pick_group)
        self.widget_pick = QComboBox()
        self.widget_pick.setPlaceholderText("— 点选预览区控件，或从这里选择 —")
        wpf.addWidget(self.widget_pick)
        pl.addWidget(widget_pick_group)

        # —— 预览尺寸（仅预览，不进 QSS） ——
        pv_group = QGroupBox("🖼  预览尺寸（仅预览，不进 QSS）")
        pv_group.setStyleSheet(
            "QGroupBox { background-color: #f7f8fa; border: 1px solid #d0d5dd;"
            " border-radius: 6px; margin-top: 8px; padding-top: 6px;"
            " font-weight: bold; color: #374151; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px;"
            " padding: 0 4px; }"
        )
        pv = QVBoxLayout(pv_group)
        pv_note = QLabel(
            "QSS 的 min-width/min-height 只是“最小”约束；真实项目里控件"
            "宽高通常用 setFixedSize 设置。这里直接改预览区选中控件的实际"
            "宽高，让圆角/padding 等效果按真实尺寸呈现，但不会写进 QSS。"
        )
        pv_note.setWordWrap(True)
        pv_note.setStyleSheet("color: #666;")
        pv.addWidget(pv_note)
        pv.addWidget(QLabel("预览宽度 px（0 = 跟随布局默认）："))
        self.pv_width = self._make_spin(0, 2000)
        pv.addWidget(self.pv_width)
        pv.addWidget(QLabel("预览高度 px（0 = 跟随布局默认）："))
        self.pv_height = self._make_spin(0, 2000)
        pv.addWidget(self.pv_height)
        pv_reset = QPushButton("恢复默认尺寸")
        pv_reset.clicked.connect(self._reset_preview_size)
        pv.addWidget(pv_reset)
        pl.addWidget(pv_group)

        # —— 编辑目标 ——
        target_group = QGroupBox("编辑目标")
        tf = QVBoxLayout(target_group)

        self.scope_combo = QComboBox()
        self.scope_combo.addItem("① 全部同类控件（如所有 QPushButton）", 0)
        self.scope_combo.addItem(
            "② 命名方案（同类控件做多套样式，如 primary / danger）", 1
        )
        self.scope_combo.addItem("③ 仅当前这一个控件（#objectName）", 2)

        # 命名方案行
        self.variant_row = QWidget()
        vr = QHBoxLayout(self.variant_row)
        vr.setContentsMargins(0, 0, 0, 0)
        vr.addWidget(QLabel("方案名："))
        self.variant_combo = QComboBox()
        self.variant_combo.setEditable(True)
        self.variant_combo.addItems(VARIANT_PRESETS)
        vr.addWidget(self.variant_combo, 1)

        self.variant_hint = QLabel(
            "多方案用法：生成 QPushButton[variant=\"primary\"] 这类选择器；\n"
            "在 PyQt6 中对控件执行 button.setProperty(\"variant\", \"primary\")\n"
            "即可让该控件使用本方案。可做任意多个方案，最后一次全部复制。"
        )
        self.variant_hint.setWordWrap(True)
        self.variant_hint.setStyleSheet("color: #1a5fb4;")

        # 当前正在编辑的完整选择器
        self.selector_preview = QLabel("—")
        self.selector_preview.setWordWrap(True)
        mono = QFont("Consolas, Courier New")
        mono.setStyleHint(QFont.StyleHint.Monospace)
        mono.setPointSize(10)
        self.selector_preview.setFont(mono)
        self.selector_preview.setStyleSheet(
            "background-color: #1e1e1e; color: #4ec9b0; padding: 6px;"
            " border-radius: 4px;"
        )

        self.state_combo = QComboBox()
        self.disabled_hint = QLabel(
            "提示：当前编辑 :disabled，已临时禁用选中控件；切换到其他状态即恢复。"
        )
        self.disabled_hint.setWordWrap(True)
        self.disabled_hint.setStyleSheet("color: #b26a00;")
        self.disabled_hint.hide()

        tf.addWidget(QLabel("应用范围："))
        tf.addWidget(self.scope_combo)
        tf.addWidget(self.variant_row)
        tf.addWidget(self.variant_hint)

        # 候选样式：同一个控件并行做多套备选 QSS，互不覆盖、可分别复制
        tf.addWidget(QLabel("候选样式（同一控件的多套备选，可分别复制）："))
        cand_row = QWidget()
        cr = QHBoxLayout(cand_row)
        cr.setContentsMargins(0, 0, 0, 0)
        cr.setSpacing(4)
        self.cand_combo = QComboBox()
        self.cand_add_btn = QToolButton()
        self.cand_add_btn.setText("＋")
        self.cand_add_btn.setToolTip("新建一套空白候选样式（不影响已有的候选）")
        self.cand_copy_btn = QToolButton()
        self.cand_copy_btn.setText("⧉")
        self.cand_copy_btn.setToolTip("复制当前这套候选的 QSS")
        self.cand_rename_btn = QToolButton()
        self.cand_rename_btn.setText("✏")
        self.cand_rename_btn.setToolTip("重命名当前候选")
        self.cand_del_btn = QToolButton()
        self.cand_del_btn.setText("🗑")
        self.cand_del_btn.setToolTip("删除当前这套候选样式")
        for btn in (self.cand_add_btn, self.cand_copy_btn,
                    self.cand_rename_btn, self.cand_del_btn):
            btn.setFixedWidth(30)
            cr.addWidget(btn)
        cr.addWidget(self.cand_combo, 1)
        # 上面按钮放左、下拉放右，视觉更稳
        tf.addWidget(cand_row)
        self.cand_hint = QLabel(
            "多候选用途：同一个按钮做蓝/红/绿两三套备选，每套选择器相同、"
            "互相不覆盖；右栏“候选样式对比”页可逐套一键复制，看中哪套用哪套。\n"
            "注意：多候选是“多选一备选”；若要让一个窗口里同时存在 primary / "
            "danger 等多种按钮，请用上面的“命名方案”。"
        )
        self.cand_hint.setWordWrap(True)
        self.cand_hint.setStyleSheet("color: #1a5fb4;")
        tf.addWidget(self.cand_hint)

        tf.addWidget(QLabel("当前编辑的选择器："))
        tf.addWidget(self.selector_preview)
        tf.addWidget(QLabel("控件状态："))
        tf.addWidget(self.state_combo)
        tf.addWidget(self.disabled_hint)
        pl.addWidget(target_group)

        GROUP_BOX_QSS = (
            "QGroupBox { background-color: #f7f8fa; border: 1px solid #d0d5dd;"
            " border-radius: 6px; margin-top: 8px; padding-top: 6px;"
            " font-weight: bold; color: #374151; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px;"
            " padding: 0 4px; }"
        )

        # —— 背景颜色 ——
        color_group = QGroupBox("🎨  背景颜色")
        color_group.setStyleSheet(GROUP_BOX_QSS)
        cf = QVBoxLayout(color_group)

        cf.addWidget(QLabel("颜色1（主颜色）："))
        self.bg_color = ColorRow()
        cf.addWidget(self.bg_color)
        cf.addWidget(QLabel("颜色2（可选渐变）："))
        self.bg_grad_start = ColorRow()
        cf.addWidget(self.bg_grad_start)
        cf.addWidget(QLabel("颜色3（可选渐变）："))
        self.bg_grad_3 = ColorRow()
        cf.addWidget(self.bg_grad_3)
        cf.addWidget(QLabel("颜色4（可选渐变）："))
        self.bg_grad_4 = ColorRow()
        cf.addWidget(self.bg_grad_4)
        cf.addWidget(QLabel("渐变方向："))
        self.bg_grad_dir = QComboBox()
        self.bg_grad_dir.addItem("从上到下", "0,0,0,1")
        self.bg_grad_dir.addItem("从左到右", "0,0,1,0")
        self.bg_grad_dir.addItem("从左上到右下", "0,0,1,1")
        self.bg_grad_dir.addItem("从右上到左下", "1,0,0,1")
        cf.addWidget(self.bg_grad_dir)

        bg_hint = QLabel(
            "💡 只设颜色1 → 纯色背景；颜色1+2+3+4 → 最大四色渐变。"
        )
        bg_hint.setWordWrap(True)
        bg_hint.setStyleSheet("color: #1a5fb4;")
        cf.addWidget(bg_hint)
        pl.addWidget(color_group)

        # —— 边框 ——
        border_group = QGroupBox("📐  边框与圆角")
        border_group.setStyleSheet(GROUP_BOX_QSS)
        bf = QVBoxLayout(border_group)
        bf.addWidget(QLabel("边框宽度 border-width："))
        self.border_width = self._make_spin(0, 20)
        bf.addWidget(self.border_width)
        bf.addWidget(QLabel("边框线型 border-style："))
        self.border_style = QComboBox()
        for text, data in BORDER_STYLES:
            self.border_style.addItem(text, data)
        bf.addWidget(self.border_style)
        bf.addWidget(QLabel("边框颜色 border-color（调 Alpha = 边框透明度）："))
        self.border_color = ColorRow()
        bf.addWidget(self.border_color)
        bf.addWidget(QLabel("圆角半径 border-radius："))
        self.border_radius = self._make_spin(0, 100)
        bf.addWidget(self.border_radius)
        radius_hint = QLabel(
            "💡 只设圆角时 Qt 不会画圆角（需配合边框或背景色），"
            "本工具会自动补一个 1px 浅灰边框让圆角生效。"
        )
        radius_hint.setWordWrap(True)
        radius_hint.setStyleSheet("color: #1a5fb4;")
        bf.addWidget(radius_hint)

        # —— 四方向边框单独调整（可选，覆盖上面的统一设置） ——
        # 两行两列紧凑布局：上/右一行，下/左一行，宽度和颜色并排
        side_hint = QLabel(
            "四方向单独调整（留 0 / 空 = 跟随上面统一值）："
        )
        side_hint.setStyleSheet("color: #666; font-size: 11px;")
        bf.addWidget(side_hint)
        side_grid = QGridLayout()
        side_grid.setHorizontalSpacing(6)
        side_grid.setVerticalSpacing(4)
        side_grid.addWidget(QLabel("上"), 0, 0)
        side_grid.addWidget(QLabel("右"), 0, 1)
        side_grid.addWidget(QLabel("下"), 1, 0)
        side_grid.addWidget(QLabel("左"), 1, 1)
        self.border_top_w = self._make_spin(0, 20)
        self.border_right_w = self._make_spin(0, 20)
        self.border_bottom_w = self._make_spin(0, 20)
        self.border_left_w = self._make_spin(0, 20)
        self.border_top_color = ColorRow()
        self.border_right_color = ColorRow()
        self.border_bottom_color = ColorRow()
        self.border_left_color = ColorRow()
        # 宽度 spin 和颜色 ColorRow 并排放在同一个单元格里
        for row_idx, (w, c) in enumerate([
            (self.border_top_w, self.border_top_color),
            (self.border_right_w, self.border_right_color),
            (self.border_bottom_w, self.border_bottom_color),
            (self.border_left_w, self.border_left_color),
        ]):
            cell = QWidget()
            cl = QHBoxLayout(cell)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(4)
            cl.addWidget(w)
            cl.addWidget(c, 1)
            side_grid.addWidget(cell, row_idx // 2 + 2, row_idx % 2)
        bf.addLayout(side_grid)
        pl.addWidget(border_group)

        # —— 字体 ——
        font_group = QGroupBox("🔤  文字与字体")
        font_group.setStyleSheet(GROUP_BOX_QSS)
        ff = QVBoxLayout(font_group)
        ff.addWidget(QLabel("字体 font-family："))
        font_row = QWidget()
        fr = QHBoxLayout(font_row)
        fr.setContentsMargins(0, 0, 0, 0)
        fr.setSpacing(4)
        self.font_family = QFontComboBox()
        self.font_family.setCurrentFont(QFont("Microsoft YaHei UI"))
        self.font_clear_btn = QToolButton()
        self.font_clear_btn.setText("×")
        self.font_clear_btn.setFixedWidth(26)
        self.font_clear_btn.setToolTip("不指定字体（跟随系统默认）")
        fr.addWidget(self.font_family, 1)
        fr.addWidget(self.font_clear_btn)
        ff.addWidget(font_row)
        ff.addWidget(QLabel("文字颜色 color："))
        self.fg_color = ColorRow()
        ff.addWidget(self.fg_color)
        ff.addWidget(QLabel("字号 font-size："))
        self.font_size = self._make_spin(0, 72)
        ff.addWidget(self.font_size)
        # 字间距与词间距：QSS 支持 letter-spacing / word-spacing
        ff.addWidget(QLabel("字间距 letter-spacing："))
        self.letter_spacing = self._make_spin(-10, 30)
        ff.addWidget(self.letter_spacing)
        ff.addWidget(QLabel("词间距 word-spacing："))
        self.word_spacing = self._make_spin(-10, 30)
        ff.addWidget(self.word_spacing)
        ff.addWidget(QLabel("字重 font-weight："))
        self.font_weight = QComboBox()
        for text, data in FONT_WEIGHTS:
            self.font_weight.addItem(text, data)
        ff.addWidget(self.font_weight)
        ff.addWidget(QLabel("斜体 font-style："))
        self.font_style = QComboBox()
        for text, data in FONT_STYLES:
            self.font_style.addItem(text, data)
        ff.addWidget(self.font_style)
        ff.addWidget(QLabel("文字装饰 text-decoration："))
        self.text_decoration = QComboBox()
        for text, data in TEXT_DECORATIONS:
            self.text_decoration.addItem(text, data)
        ff.addWidget(self.text_decoration)
        ff.addWidget(QLabel("文本对齐 text-align："))
        self.text_align = QComboBox()
        for text, data in TEXT_ALIGNS:
            self.text_align.addItem(text, data)
        ff.addWidget(self.text_align)
        pl.addWidget(font_group)

        # —— 选中文字样式 ——
        sel_group = QGroupBox("📝  选中文字样式")
        sel_group.setStyleSheet(GROUP_BOX_QSS)
        sf = QVBoxLayout(sel_group)
        sf.addWidget(QLabel("选中文字颜色 selection-color："))
        self.sel_color = ColorRow()
        sf.addWidget(self.sel_color)
        sf.addWidget(QLabel("选中文字背景 selection-background-color："))
        self.sel_bg_color = ColorRow()
        sf.addWidget(self.sel_bg_color)
        pl.addWidget(sel_group)

        # —— 间距 ——
        spacing_group = QGroupBox("📏  间距与尺寸")
        spacing_group.setStyleSheet(GROUP_BOX_QSS)
        sf = QVBoxLayout(spacing_group)
        sf.addWidget(QLabel("外边距 margin："))
        self.margin = self._make_spin(0, 100)
        sf.addWidget(self.margin)
        sf.addWidget(QLabel("内边距 padding（上下左右）："))
        self.padding = self._make_spin(0, 60)
        sf.addWidget(self.padding)
        sf.addWidget(QLabel("最小宽度 min-width："))
        self.min_width = self._make_spin(0, 2000)
        sf.addWidget(self.min_width)
        sf.addWidget(QLabel("最小高度 min-height："))
        self.min_height = self._make_spin(0, 2000)
        sf.addWidget(self.min_height)
        size_hint = QLabel(
            "💡 圆角半径最好 ≤ 控件高度的一半，圆角太大时可先把"
            " min-height 调大（例如 40px），圆角就有空间显示了。"
        )
        size_hint.setWordWrap(True)
        size_hint.setStyleSheet("color: #1a5fb4;")
        sf.addWidget(size_hint)
        pl.addWidget(spacing_group)

        # —— 背景图片（倒数第二） ——
        bgimg_group = QGroupBox("🖼  背景图片")
        bgimg_group.setStyleSheet(GROUP_BOX_QSS)
        bg = QVBoxLayout(bgimg_group)
        bg.addWidget(QLabel("背景图片 background-image："))
        bgimg_row = QWidget()
        bgr = QHBoxLayout(bgimg_row)
        bgr.setContentsMargins(0, 0, 0, 0)
        bgr.setSpacing(4)
        self.bg_image = QLineEdit()
        self.bg_image.setPlaceholderText("图片路径，如 images/bg.png（留空=无）")
        bgimg_pick = QToolButton()
        bgimg_pick.setText("…")
        bgimg_pick.setFixedWidth(30)
        bgimg_pick.setToolTip("选择图片文件")
        bgimg_pick.clicked.connect(lambda: self._pick_image(self.bg_image,
                                 "background-image"))
        bgimg_clear = QToolButton()
        bgimg_clear.setText("×")
        bgimg_clear.setFixedWidth(26)
        bgimg_clear.clicked.connect(lambda: self.bg_image.setText(""))
        bgr.addWidget(self.bg_image, 1)
        bgr.addWidget(bgimg_pick)
        bgr.addWidget(bgimg_clear)
        bg.addWidget(bgimg_row)
        bg.addWidget(QLabel("平铺方式 background-repeat："))
        self.bg_repeat = QComboBox()
        for text, data in BACKGROUND_REPEATS:
            self.bg_repeat.addItem(text, data)
        bg.addWidget(self.bg_repeat)
        bg.addWidget(QLabel("对齐位置 background-position："))
        self.bg_position = QComboBox()
        for text, data in BACKGROUND_POSITIONS:
            self.bg_position.addItem(text, data)
        bg.addWidget(self.bg_position)
        pl.addWidget(bgimg_group)

        # —— 图标 / 图片（最后） ——
        icon_group = QGroupBox("🎭  图标 / 图片")
        icon_group.setStyleSheet(GROUP_BOX_QSS)
        ic = QVBoxLayout(icon_group)
        ic.addWidget(QLabel("图标 image（url）："))
        icon_row = QWidget()
        icr = QHBoxLayout(icon_row)
        icr.setContentsMargins(0, 0, 0, 0)
        icr.setSpacing(4)
        self.image_url = QLineEdit()
        self.image_url.setPlaceholderText("图标路径，如 icons/ok.png（留空=无）")
        icon_pick = QToolButton()
        icon_pick.setText("…")
        icon_pick.setFixedWidth(30)
        icon_pick.clicked.connect(lambda: self._pick_image(self.image_url, "image"))
        icon_clear = QToolButton()
        icon_clear.setText("×")
        icon_clear.setFixedWidth(26)
        icon_clear.clicked.connect(lambda: self.image_url.setText(""))
        icr.addWidget(self.image_url, 1)
        icr.addWidget(icon_pick)
        icr.addWidget(icon_clear)
        ic.addWidget(icon_row)
        ic.addWidget(QLabel("图片位置 image-position："))
        self.image_position = QComboBox()
        for text, data in IMAGE_POSITIONS:
            self.image_position.addItem(text, data)
        ic.addWidget(self.image_position)
        icon_hint = QLabel(
            "💡 image 属性对 QPushButton、QCheckBox 指示器、QComboBox 下拉"
            "箭头等有效；具体效果取决于控件类型。"
        )
        icon_hint.setWordWrap(True)
        icon_hint.setStyleSheet("color: #666;")
        ic.addWidget(icon_hint)
        pl.addWidget(icon_group)

        # —— 特效模块已移除（QSS 不支持阴影/发光/透明度，需 Python 代码） ——

        self.delete_rule_btn = QPushButton("删除当前选择器 / 状态的规则")
        self.delete_rule_btn.setEnabled(False)
        pl.addWidget(self.delete_rule_btn)
        pl.addStretch(1)

        scroll.setWidget(panel)
        outer_lay.addWidget(scroll)
        return outer

    @staticmethod
    def _make_spin(minimum, maximum):
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        spin.setSuffix(" px")
        spin.setSpecialValueText("未设置")
        return spin

    # ---------------- 代码区（右栏）

    def _build_code_panel(self):
        outer = QWidget()
        outer.setMinimumWidth(480)
        cl = QVBoxLayout(outer)
        cl.setContentsMargins(8, 8, 8, 8)
        cl.setSpacing(6)

        title = QLabel("生成的 QSS 代码")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        cl.addWidget(title)

        # 所有控件、所有方案的样式都累积在同一份 QSS 中，一次复制
        bar = QHBoxLayout()
        self.copy_btn = QPushButton("⧉  一键复制全部 QSS")
        self.copy_btn.setStyleSheet(
            "QPushButton { background-color: #1a7f37; color: white;"
            " font-weight: bold; padding: 6px 14px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #23944a; }"
        )
        self.save_btn = QPushButton("保存为 .qss 文件")
        self.clear_btn = QPushButton("清空全部样式")
        bar.addWidget(self.copy_btn)
        bar.addWidget(self.save_btn)
        bar.addWidget(self.clear_btn)
        cl.addLayout(bar)

        self.stats_label = QLabel("已设计 0 条规则 · 0 个命名方案")
        self.stats_label.setStyleSheet("color: #555;")
        cl.addWidget(self.stats_label)

        # 上：已定义规则列表；下：完整 QSS 代码
        v_split = QSplitter(Qt.Orientation.Vertical)

        rule_box = QWidget()
        rl = QVBoxLayout(rule_box)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addWidget(QLabel("已定义规则（点击任意一条可跳回继续编辑）："))
        self.rule_list = QListWidget()
        rl.addWidget(self.rule_list, 1)

        mono = QFont("Consolas, Courier New")
        mono.setStyleHint(QFont.StyleHint.Monospace)
        mono.setPointSize(10)

        tabs = QTabWidget()

        # —— 第 1 页：QSS 代码 ——
        qss_tab = QWidget()
        cbl = QVBoxLayout(qss_tab)
        cbl.setContentsMargins(4, 4, 4, 4)
        cbl.addWidget(QLabel("全部控件 / 全部方案合并后的完整 QSS（实时更新）："))
        self.code_edit = QPlainTextEdit()
        self.code_edit.setReadOnly(True)
        self.code_edit.setFont(mono)
        self.code_edit.setPlaceholderText(
            "/* 在中间预览区点选控件，在左侧用鼠标调整属性；\n"
            "   可连续设计任意多个控件、任意多个命名方案；\n"
            "   所有样式会累积合并在这里，最后点上方按钮一次复制即可。 */"
        )
        cbl.addWidget(self.code_edit, 1)
        usage = QLabel(
            "PyQt6 用法：app.setStyleSheet(粘贴的 QSS) 全局生效；"
            "命名方案控件用 button.setProperty(\"variant\", \"primary\") 切换"
        )
        usage.setWordWrap(True)
        usage.setStyleSheet("color: #666; padding: 2px;")
        cbl.addWidget(usage)
        tabs.addTab(qss_tab, "QSS 样式代码")

        # —— 第 2 页：同一控件的多套候选并排对比、逐套复制 ——
        cmp_tab = QWidget()
        cml = QVBoxLayout(cmp_tab)
        cml.setContentsMargins(4, 4, 4, 4)
        cmp_bar = QHBoxLayout()
        cmp_bar.addWidget(QLabel("同一控件的多套备选 QSS（选择器相同，逐套复制即用）："))
        cmp_bar.addStretch(1)
        self.copy_all_cand_btn = QPushButton("⧉  复制全部候选（分段）")
        self.copy_all_cand_btn.setStyleSheet(
            "QPushButton { background-color: #0b6bcb; color: white;"
            " font-weight: bold; padding: 6px 14px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #2b84dd; }"
            "QPushButton:disabled { background-color: #9bb8d3; }"
        )
        cmp_bar.addWidget(self.copy_all_cand_btn)
        cml.addLayout(cmp_bar)
        cmp_scroll = QScrollArea()
        cmp_scroll.setWidgetResizable(True)
        self.cmp_container = QWidget()
        self.cmp_layout = QVBoxLayout(self.cmp_container)
        self.cmp_layout.setContentsMargins(2, 2, 6, 2)
        self.cmp_layout.setSpacing(8)
        self.cmp_layout.addStretch(1)
        cmp_scroll.setWidget(self.cmp_container)
        cml.addWidget(cmp_scroll, 1)
        tabs.addTab(cmp_tab, "候选样式对比（分别复制）")

        v_split.addWidget(rule_box)
        v_split.addWidget(tabs)
        v_split.setStretchFactor(0, 0)
        v_split.setStretchFactor(1, 1)
        v_split.setSizes([210, 600])
        cl.addWidget(v_split, 1)

        # 赞赏按钮：与代码区同宽的醒目彩色大按钮（完全自愿，不弹窗打扰）
        self.donate_btn = QPushButton("❤  如果这个工具帮到了你，请作者喝杯咖啡  ·  赞赏支持")
        self.donate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.donate_btn.setMinimumHeight(42)
        self.donate_btn.setToolTip(
            "完全自愿：点击后用系统浏览器打开爱发电页面，支持一次性或包月赞赏"
        )
        self.donate_btn.setStyleSheet(
            "QPushButton { background-color: #e8590c; color: black;"
            " font-size: 14px; font-weight: bold; border: none;"
            " border-radius: 6px; padding: 8px 12px; }"
            "QPushButton:hover { background-color: #f76707; }"
            "QPushButton:pressed { background-color: #d9480f; }"
        )
        self.donate_btn.clicked.connect(self._open_donate_page)
        cl.addWidget(self.donate_btn)

        return outer

    def _wire_signals(self):
        self.scope_combo.currentIndexChanged.connect(self._on_scope_changed)
        self.variant_combo.currentTextChanged.connect(self._on_variant_changed)
        self.state_combo.currentIndexChanged.connect(self._on_state_changed)

        self.bg_color.changed.connect(lambda _: self._update_background())
        self.bg_grad_start.changed.connect(lambda _: self._update_background())
        self.bg_grad_3.changed.connect(lambda _: self._update_background())
        self.bg_grad_4.changed.connect(lambda _: self._update_background())
        self.bg_grad_dir.currentIndexChanged.connect(lambda _: self._update_background())
        self.fg_color.changed.connect(lambda v: self._edit("color", v))
        self.border_color.changed.connect(
            lambda v: self._edit("border-color", v))
        self.border_top_color.changed.connect(
            lambda v: self._edit("border-top-color", v))
        self.border_right_color.changed.connect(
            lambda v: self._edit("border-right-color", v))
        self.border_bottom_color.changed.connect(
            lambda v: self._edit("border-bottom-color", v))
        self.border_left_color.changed.connect(
            lambda v: self._edit("border-left-color", v))

        self.border_width.valueChanged.connect(
            lambda v: self._edit("border-width", None if v == 0 else f"{v}px"))
        self.border_top_w.valueChanged.connect(
            lambda v: self._edit("border-top-width", None if v == 0 else f"{v}px"))
        self.border_right_w.valueChanged.connect(
            lambda v: self._edit("border-right-width", None if v == 0 else f"{v}px"))
        self.border_bottom_w.valueChanged.connect(
            lambda v: self._edit("border-bottom-width", None if v == 0 else f"{v}px"))
        self.border_left_w.valueChanged.connect(
            lambda v: self._edit("border-left-width", None if v == 0 else f"{v}px"))
        self.border_radius.valueChanged.connect(
            lambda v: self._edit("border-radius", None if v == 0 else f"{v}px"))
        self.padding.valueChanged.connect(
            lambda v: self._edit("padding", None if v == 0 else f"{v}px"))
        self.min_width.valueChanged.connect(
            lambda v: self._edit("min-width", None if v == 0 else f"{v}px"))
        self.min_height.valueChanged.connect(
            lambda v: self._edit("min-height", None if v == 0 else f"{v}px"))
        self.pv_width.valueChanged.connect(lambda _: self._apply_preview_size())
        self.pv_height.valueChanged.connect(lambda _: self._apply_preview_size())
        self.font_size.valueChanged.connect(
            lambda v: self._edit("font-size", None if v == 0 else f"{v}px"))
        self.margin.valueChanged.connect(
            lambda v: self._edit("margin", None if v == 0 else f"{v}px"))
        self.letter_spacing.valueChanged.connect(
            lambda v: self._edit("letter-spacing", None if v == 0 else f"{v}px"))
        self.word_spacing.valueChanged.connect(
            lambda v: self._edit("word-spacing", None if v == 0 else f"{v}px"))

        self.border_style.currentIndexChanged.connect(
            lambda _: self._edit("border-style", self.border_style.currentData()))
        self.font_weight.currentIndexChanged.connect(
            lambda _: self._edit("font-weight", self.font_weight.currentData()))
        self.font_style.currentIndexChanged.connect(
            lambda _: self._edit("font-style", self.font_style.currentData()))
        self.text_decoration.currentIndexChanged.connect(
            lambda _: self._edit("text-decoration", self.text_decoration.currentData()))
        self.text_align.currentIndexChanged.connect(
            lambda _: self._edit("text-align", self.text_align.currentData()))
        self.bg_repeat.currentIndexChanged.connect(
            lambda _: self._edit("background-repeat", self.bg_repeat.currentData()))
        self.bg_position.currentIndexChanged.connect(
            lambda _: self._edit("background-position", self.bg_position.currentData()))
        self.image_position.currentIndexChanged.connect(
            lambda _: self._edit("image-position", self.image_position.currentData()))
        self.sel_color.changed.connect(lambda v: self._edit("selection-color", v))
        self.sel_bg_color.changed.connect(
            lambda v: self._edit("selection-background-color", v))
        self.bg_image.textChanged.connect(self._on_bg_image_changed)
        self.image_url.textChanged.connect(self._on_image_url_changed)
        self.font_family.currentFontChanged.connect(self._on_font_changed)
        self.font_clear_btn.clicked.connect(self._clear_font)

        self.delete_rule_btn.clicked.connect(self._delete_current_rule)
        self.copy_btn.clicked.connect(self.copy_qss)
        self.save_btn.clicked.connect(self.save_qss)
        self.clear_btn.clicked.connect(self.clear_all)
        self.rule_list.itemClicked.connect(self._on_rule_picked)

        # 控件选择下拉框
        self.widget_pick.currentIndexChanged.connect(self._on_widget_picked)

        # 特效模块已移除

        # 候选样式
        self.cand_combo.currentIndexChanged.connect(self._on_cand_switched)
        self.cand_add_btn.clicked.connect(self._candidate_add)
        self.cand_copy_btn.clicked.connect(self._candidate_copy_current)
        self.cand_rename_btn.clicked.connect(self._candidate_rename)
        self.cand_del_btn.clicked.connect(self._candidate_delete)
        self.copy_all_cand_btn.clicked.connect(self.copy_all_candidates)

    # ------------------------------------------------------------ 选择逻辑

    def eventFilter(self, obj, event):
        etype = event.type()
        if etype == QEvent.Type.MouseButtonPress:
            # 统一冒泡：从事件接收者开始向上找最近的 selectable 祖先。
            # 这样无论点中的是控件本体还是控件内部的子控件（QLineEdit 的
            # 内嵌编辑器、QComboBox 的 lineEdit、QGroupBox 的标题、
            # QTabWidget 的 tab 栏、QTextEdit 的 viewport 等），
            # 都能正确选中外层控件。
            target = obj if isinstance(obj, QWidget) else None
            while target is not None and target not in self.selectables:
                # 越过 preview 就停止，避免选中到编辑器自身的面板
                if target is self.preview:
                    break
                target = target.parentWidget() if hasattr(target, 'parentWidget') else None
            if target is not None and target in self.selectables:
                self.select_widget(target)
        elif etype in (QEvent.Type.Resize, QEvent.Type.Move,
                       QEvent.Type.Show, QEvent.Type.Hide,
                       QEvent.Type.LayoutRequest):
            if obj is self.preview or obj in self.selectables:
                self._schedule_rubber()
        return False

    def select_widget(self, widget, scope=None, variant=None, state=""):
        self._restore_preview_state()
        self.selected = widget
        # 保险：补装所有子控件的过滤器（有些子控件是 show 之后才创建的，
        # 例如 QComboBox 的 lineEdit、QAbstractScrollArea 的 viewport 等）
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

        # 未显式指定范围时，若控件本身带 variant 属性（方案演示按钮），
        # 直接进入“命名方案”编辑模式并带入方案名
        if scope is None:
            prop = widget.property("variant")
            if prop:
                scope, variant = 1, str(prop)
            else:
                scope = 0

        # 同步控件选择下拉框
        idx = self.widget_pick.findData(widget)
        if idx >= 0:
            self.widget_pick.blockSignals(True)
            self.widget_pick.setCurrentIndex(idx)
            self.widget_pick.blockSignals(False)

        self._loading = True
        self._rebuild_variant_items(variant)
        self.scope_combo.setCurrentIndex(scope)
        if variant is not None:
            self.variant_combo.setEditText(variant)
        self._sync_mode_ui()
        self._activate_base(self._base_selector())
        self._rebuild_state_items(state)
        self._loading = False

        self._load_editors()
        self._apply_preview_state()
        self._sync_target_ui()
        self._update_rubber()

    def _on_widget_picked(self, idx):
        """从下拉框选择控件时，模拟点选该控件。"""
        if self._loading or idx < 0:
            return
        widget = self.widget_pick.itemData(idx)
        if widget is not None:
            self.select_widget(widget)

    def _on_scope_changed(self):
        if self._loading or self.selected is None:
            return
        # 进入命名方案模式时，若方案名为空，默认给 primary
        if (self.scope_combo.currentData() == 1
                and not self.variant_combo.currentText().strip()):
            self.variant_combo.blockSignals(True)
            self.variant_combo.setEditText("primary")
            self.variant_combo.blockSignals(False)
        self._sync_mode_ui()
        self._loading = True
        self._activate_base(self._base_selector())
        self._rebuild_state_items("")
        self._loading = False
        self._load_editors()
        self._apply_preview_state()
        self._sync_target_ui()

    def _on_variant_changed(self):
        if self._loading or self.selected is None:
            return
        self._loading = True
        self._activate_base(self._base_selector())
        self._rebuild_state_items("")
        self._loading = False
        self._load_editors()
        self._apply_preview_state()
        self._sync_target_ui()

    def _on_state_changed(self):
        if self._loading or self.selected is None:
            return
        self._load_editors()
        self._apply_preview_state()
        self._sync_target_ui()

    @staticmethod
    def _sanitize_variant(name):
        # 属性选择器值中出现引号 / 方括号 / 冒号会破坏 QSS，做轻量清洗
        return re.sub(r'[\[\]":]+', "", (name or "").strip())

    def _variant_name(self):
        return self._sanitize_variant(self.variant_combo.currentText())

    def _base_selector(self):
        cls = type(self.selected).__name__
        mode = self.scope_combo.currentData()
        if mode == 2:
            return f"#{self.selected.objectName()}"
        if mode == 1:
            name = self._variant_name()
            return f'{cls}[variant="{name}"]' if name else cls
        return cls

    def _full_selector(self):
        base = self._base_selector()
        state = self.state_combo.currentData()
        return f"{base}:{state}" if state else base

    # -------------------------------------------------------- 候选样式管理

    def _prune_empty_default_bases(self, keep):
        """清理输入方案名中途产生的临时空目标（单个未设计的默认“候选 1”）。"""
        for b in list(self.cand):
            if b == keep:
                continue
            cands = self.cand[b]
            if (len(cands) == 1 and not cands[0]["rules"]
                    and cands[0]["name"] == "候选 1"):
                del self.cand[b]
                self.edit_idx.pop(b, None)

    def _activate_base(self, base):
        """切换编辑目标时调用：确保候选存在，并让 self.rules 指向当前候选。"""
        self._prune_empty_default_bases(base)
        if base not in self.cand:
            self.cand[base] = [{"name": "候选 1", "rules": {}}]
            self.edit_idx[base] = 0
        idx = self.edit_idx.get(base, 0)
        idx = max(0, min(idx, len(self.cand[base]) - 1))
        self.edit_idx[base] = idx
        self.rules = self.cand[base][idx]["rules"]
        self._refresh_cand_combo()

    def _refresh_cand_combo(self):
        self.cand_combo.blockSignals(True)
        self.cand_combo.clear()
        if self.selected is not None:
            base = self._base_selector()
            cur = self.edit_idx.get(base, 0)
            for i, c in enumerate(self.cand.get(base, [])):
                prefix = "▶ " if i == cur else "    "
                self.cand_combo.addItem(f"{prefix}{i + 1}. {c['name']}")
            self.cand_combo.setCurrentIndex(cur)
        self.cand_combo.blockSignals(False)

    def _candidate_reload(self, state=""):
        """候选增删/切换后统一刷新编辑器、预览、输出。"""
        self._loading = True
        self._rebuild_state_items(state)
        self._loading = False
        self._refresh_cand_combo()
        self._load_editors()
        self._refresh_output()
        self._sync_target_ui()

    def _on_cand_switched(self, idx):
        if self._loading or self.selected is None or idx < 0:
            return
        base = self._base_selector()
        cands = self.cand.get(base, [])
        if idx >= len(cands) or idx == self.edit_idx.get(base):
            return
        self.edit_idx[base] = idx
        self.rules = cands[idx]["rules"]
        self._candidate_reload(self.state_combo.currentData() or "")
        self.statusBar().showMessage(
            f"正在编辑「{cands[idx]['name']}」（其他候选保持不变）", 2500
        )

    def _candidate_add(self):
        if self.selected is None:
            return
        base = self._base_selector()
        cands = self.cand.setdefault(
            base, [{"name": "候选 1", "rules": {}}]
        )
        new_idx = len(cands)
        cands.append({"name": f"候选 {new_idx + 1}", "rules": {}})
        self.edit_idx[base] = new_idx
        self.rules = cands[new_idx]["rules"]
        self._candidate_reload("")
        self.statusBar().showMessage(
            f"已新建空白「{cands[new_idx]['name']}」，开始设计这套备选样式。", 4000
        )

    def _candidate_delete(self):
        if self.selected is None:
            return
        base = self._base_selector()
        cands = self.cand.get(base)
        if not cands:
            return
        idx = self.edit_idx[base]
        target = cands[idx]
        if target["rules"]:
            ret = QMessageBox.question(
                self, "删除候选",
                f"确定删除「{target['name']}」及其全部 {len(target['rules'])} "
                "条状态规则吗？（其他候选不受影响）",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if ret != QMessageBox.StandardButton.Yes:
                return
        del cands[idx]
        if not cands:
            cands.append({"name": "候选 1", "rules": {}})
            idx = 0
        else:
            idx = min(idx, len(cands) - 1)
        self.edit_idx[base] = idx
        self.rules = cands[idx]["rules"]
        self._candidate_reload(self.state_combo.currentData() or "")
        self.statusBar().showMessage("已删除该候选样式", 3000)

    def _candidate_rename(self):
        if self.selected is None:
            return
        base = self._base_selector()
        cands = self.cand[base]
        idx = self.edit_idx[base]
        name, ok = QInputDialog.getText(
            self, "重命名候选", "给这套候选起个好认的名字（如：蓝色主按钮）：",
            text=cands[idx]["name"],
        )
        name = name.strip()
        if ok and name:
            cands[idx]["name"] = name
            self._refresh_cand_combo()
            self._refresh_comparison()

    def _candidate_qss(self, base, idx):
        """单个候选的独立 QSS 文本（带注释头），空候选返回空串。"""
        c = self.cand[base][idx]
        blocks = self._blocks_of(c["rules"])
        if not blocks:
            return ""
        header = f"/* ===== {base} · 候选 {idx + 1}「{c['name']}」" \
                 f"（{len(c['rules'])} 个状态） ===== */"
        return header + "\n" + "\n\n".join(blocks)

    def _candidate_copy_current(self):
        if self.selected is None:
            return
        base = self._base_selector()
        idx = self.edit_idx[base]
        qss = self._candidate_qss(base, idx)
        if not qss:
            self.statusBar().showMessage("这套候选还是空的，先在左侧设计属性。", 3000)
            return
        QApplication.clipboard().setText(qss)
        self.statusBar().showMessage(
            f"已复制「{self.cand[base][idx]['name']}」的完整 QSS，"
            "可直接 app.setStyleSheet() 或 button.setStyleSheet() 使用。", 6000
        )

    def _multi_candidate_bases(self):
        """含有 2 套以上非空候选的目标。"""
        result = []
        for base, cands in self.cand.items():
            if sum(1 for c in cands if c["rules"]) >= 2:
                result.append(base)
        return result

    def copy_all_candidates(self):
        sections = []
        for base in self._multi_candidate_bases():
            for idx, c in enumerate(self.cand[base]):
                qss = self._candidate_qss(base, idx)
                if qss:
                    sections.append(qss)
        if not sections:
            self.statusBar().showMessage(
                "还没有多套候选：在左侧点“＋”为当前控件新建第 2 套候选样式。", 4000
            )
            return
        QApplication.clipboard().setText("\n\n\n".join(sections))
        self.statusBar().showMessage(
            f"已复制 {len(sections)} 套候选 QSS（分段注释、选择器相同），"
            "逐套挑用即可。", 6000
        )

    def _existing_states(self, base):
        result = set()
        for selector in self.rules:
            m = SELECTOR_RE.match(selector)
            if not m:
                continue
            if m.group("base") == base:
                result.add(m.group("state") or "")
        return result

    def _rebuild_state_items(self, active_state=""):
        base = self._base_selector()
        existing = self._existing_states(base)
        self.state_combo.blockSignals(True)
        self.state_combo.clear()
        active_index = 0
        for i, (text, data) in enumerate(STATE_LIST):
            mark = "   ●" if data in existing else ""
            self.state_combo.addItem(text + mark, data)
            if data == active_state:
                active_index = i
        self.state_combo.setCurrentIndex(active_index)
        self.state_combo.blockSignals(False)

    def _used_variants(self):
        names = []
        for cands in self.cand.values():
            for c in cands:
                for selector in c["rules"]:
                    m = SELECTOR_RE.match(selector)
                    if m and m.group("variant"):
                        name = m.group("variant")
                        if name not in names:
                            names.append(name)
        return names

    def _rebuild_variant_items(self, keep=None):
        """合并预设方案与已使用方案；不在打字过程中调用，以免打断输入。"""
        names = list(VARIANT_PRESETS)
        for name in self._used_variants():
            if name not in names:
                names.append(name)
        keep = self._sanitize_variant(keep) if keep is not None else (
            self.variant_combo.currentText()
        )
        self.variant_combo.blockSignals(True)
        self.variant_combo.clear()
        self.variant_combo.addItems(names)
        if keep:
            self.variant_combo.setEditText(keep)
        elif names:
            self.variant_combo.setEditText(names[0])
        self.variant_combo.blockSignals(False)

    def _sync_mode_ui(self):
        is_variant = self.scope_combo.currentData() == 1
        self.variant_row.setVisible(is_variant)
        self.variant_hint.setVisible(is_variant)

    def _sync_target_ui(self):
        self.selector_preview.setText(self._full_selector())
        base = self._base_selector()
        idx = self.edit_idx.get(base, 0)
        self._refresh_rule_list((base, idx, self._full_selector()))
        self._update_delete_btn()

    def _restore_preview_state(self):
        if self._forced_disabled is not None:
            try:
                self._forced_disabled.setEnabled(True)
            except RuntimeError:
                pass
            self._forced_disabled = None
        self.disabled_hint.hide()

    @staticmethod
    def _repolish(widget):
        # 动态属性改变后，必须 unpolish / polish 才能让 QSS 属性选择器立即生效
        try:
            style = widget.style()
            style.unpolish(widget)
            style.polish(widget)
            widget.update()
        except RuntimeError:
            pass

    def _apply_preview_state(self):
        self._restore_preview_state()
        if self.selected is None:
            return
        # 同步 variant 属性：命名方案模式下挂到当前控件，便于即时看到方案效果
        if self.scope_combo.currentData() == 1:
            name = self._variant_name()
            self.selected.setProperty(
                "variant", name if name else None
            )
        else:
            self.selected.setProperty("variant", None)
        self._repolish(self.selected)

        if self.state_combo.currentData() == "disabled":
            self.selected.setEnabled(False)
            self._forced_disabled = self.selected
            self.disabled_hint.show()

    # ------------------------------------------------------------ 属性编辑

    def _load_editors(self):
        if self.selected is None:
            return
        rule = self.rules.get(self._full_selector(), {})
        self._loading = True
        try:
            # 背景色：判断是否为渐变色
            bg_val = rule.get("background-color")
            if bg_val and bg_val.startswith("qlineargradient"):
                # 解析渐变色：提取所有 stop 颜色和方向
                stops = re.findall(
                    r"stop:([\d.]+)\s+(#\w+|rgba?\([^)]+\))", bg_val
                )
                colors = [c for _, c in stops]
                # 按顺序分配到颜色1-4
                if len(colors) >= 1:
                    self.bg_color.set_value(colors[0])
                if len(colors) >= 2:
                    self.bg_grad_start.set_value(colors[1])
                if len(colors) >= 3:
                    self.bg_grad_3.set_value(colors[2])
                if len(colors) >= 4:
                    self.bg_grad_4.set_value(colors[3])
                # 解析方向
                dir_match = re.search(
                    r"x1:([\d.]+),\s*y1:([\d.]+),\s*x2:([\d.]+),\s*y2:([\d.]+)",
                    bg_val
                )
                if dir_match:
                    dir_str = ",".join(dir_match.groups())
                    for i in range(self.bg_grad_dir.count()):
                        if self.bg_grad_dir.itemData(i) == dir_str:
                            self.bg_grad_dir.setCurrentIndex(i)
                            break
            else:
                self.bg_color.set_value(bg_val)
                self.bg_grad_start.set_value(None)
                self.bg_grad_3.set_value(None)
                self.bg_grad_4.set_value(None)
            self.fg_color.set_value(rule.get("color"))
            self.border_color.set_value(rule.get("border-color"))
            self.border_top_color.set_value(rule.get("border-top-color"))
            self.border_right_color.set_value(rule.get("border-right-color"))
            self.border_bottom_color.set_value(rule.get("border-bottom-color"))
            self.border_left_color.set_value(rule.get("border-left-color"))
            self.border_width.setValue(self._px_to_int(rule.get("border-width")))
            self.border_top_w.setValue(self._px_to_int(rule.get("border-top-width")))
            self.border_right_w.setValue(self._px_to_int(rule.get("border-right-width")))
            self.border_bottom_w.setValue(self._px_to_int(rule.get("border-bottom-width")))
            self.border_left_w.setValue(self._px_to_int(rule.get("border-left-width")))
            self.border_radius.setValue(self._px_to_int(rule.get("border-radius")))
            self.padding.setValue(self._px_to_int(rule.get("padding")))
            self.min_width.setValue(self._px_to_int(rule.get("min-width")))
            self.min_height.setValue(self._px_to_int(rule.get("min-height")))
            self.margin.setValue(self._px_to_int(rule.get("margin")))
            self.font_size.setValue(self._px_to_int(rule.get("font-size")))
            self.letter_spacing.setValue(self._px_to_int(rule.get("letter-spacing")))
            self.word_spacing.setValue(self._px_to_int(rule.get("word-spacing")))
            self._set_combo_by_data(self.border_style, rule.get("border-style"))
            self._set_combo_by_data(self.font_weight, rule.get("font-weight"))
            self._set_combo_by_data(self.font_style, rule.get("font-style"))
            self._set_combo_by_data(self.text_decoration, rule.get("text-decoration"))
            self._set_combo_by_data(self.text_align, rule.get("text-align"))
            self._set_combo_by_data(self.bg_repeat, rule.get("background-repeat"))
            self._set_combo_by_data(self.bg_position, rule.get("background-position"))
            self._set_combo_by_data(self.image_position, rule.get("image-position"))
            self.sel_color.set_value(rule.get("selection-color"))
            self.sel_bg_color.set_value(rule.get("selection-background-color"))
            # 图片路径：QSS 里是 url("...")，编辑框里只存纯路径
            self.bg_image.setText(self._url_to_path(rule.get("background-image")))
            self.image_url.setText(self._url_to_path(rule.get("image")))
            fam = rule.get("font-family")
            if fam:
                self.font_family.setCurrentFont(QFont(fam))
        finally:
            self._loading = False
        self._sync_preview_size_spin()

    # -------------------------------------------------------- 预览尺寸（仅预览，不进 QSS）

    def _sync_preview_size_spin(self):
        """切换选中控件时，把控件当前的实际尺寸显示到预览尺寸 spin。"""
        if self.selected is None:
            return
        self.pv_width.blockSignals(True)
        self.pv_height.blockSignals(True)
        self.pv_width.setValue(self.selected.width())
        self.pv_height.setValue(self.selected.height())
        self.pv_width.blockSignals(False)
        self.pv_height.blockSignals(False)

    def _apply_preview_size(self):
        """实时把 spin 里的宽高套用到预览区当前选中的控件上（只影响预览）。"""
        if self._loading or self.selected is None:
            return
        w = self.pv_width.value()
        h = self.pv_height.value()
        # 0 表示恢复跟随布局默认
        self.selected.setFixedWidth(w) if w > 0 else self.selected.setMinimumWidth(0)
        if w <= 0:
            self.selected.setMaximumWidth(16777215)  # QWIDGETSIZE_MAX
        if h > 0:
            self.selected.setFixedHeight(h)
        else:
            self.selected.setMinimumHeight(0)
            self.selected.setMaximumHeight(16777215)

    def _reset_preview_size(self):
        """恢复当前选中控件的默认尺寸。"""
        if self.selected is None:
            return
        self._loading = True
        self.pv_width.setValue(0)
        self.pv_height.setValue(0)
        self._loading = False
        self.selected.setMinimumSize(0, 0)
        self.selected.setMaximumSize(16777215, 16777215)
        self.selected.updateGeometry()
        # 布局重排后把实际尺寸同步回 spin
        QTimer.singleShot(0, self._sync_preview_size_spin)

    @staticmethod
    def _url_to_path(v):
        """QSS 的 url("...") → 纯路径，用于编辑框回显。"""
        if not v:
            return ""
        s = str(v)
        if s.startswith('url('):
            s = s[4:].rstrip(')').strip('"').strip("'")
        return s

    def _on_bg_image_changed(self, text):
        if self._loading:
            return
        t = text.strip()
        self._edit("background-image", f'url("{t}")' if t else None)

    def _on_image_url_changed(self, text):
        if self._loading:
            return
        t = text.strip()
        self._edit("image", f'url("{t}")' if t else None)

    def _pick_image(self, line_edit, prop):
        """文件对话框选图，填入编辑框并写入 QSS。"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.svg *.ico);;所有文件 (*)")
        if not path:
            return
        line_edit.setText(path)

    def _update_background(self):
        """根据颜色1-4的填充情况生成 background-color。"""
        if self._loading:
            return
        c1 = self.bg_color.value()
        c2 = self.bg_grad_start.value()
        c3 = self.bg_grad_3.value()
        c4 = self.bg_grad_4.value()

        if not c1:
            self._edit("background-color", None)
            return

        if not c2:
            self._edit("background-color", c1)
            return

        x1, y1, x2, y2 = self.bg_grad_dir.currentData().split(",")
        stops = f"stop:0 {c1}, stop:1 {c2}"
        if c3:
            if c4:
                stops = f"stop:0 {c1}, stop:0.33 {c2}, stop:0.67 {c3}, stop:1 {c4}"
            else:
                stops = f"stop:0 {c1}, stop:0.5 {c2}, stop:1 {c3}"
        gradient = (
            f"qlineargradient(x1:{x1}, y1:{y1}, x2:{x2}, y2:{y2}, {stops})"
        )
        self._edit("background-color", gradient)

    def _on_font_changed(self, font):
        if self._loading:
            return
        self._edit("font-family", font.family())

    def _clear_font(self):
        if self._loading:
            return
        self._edit("font-family", None)

    @staticmethod
    def _px_to_int(value):
        if not value:
            return 0
        try:
            return int(str(value).replace("px", "").strip())
        except ValueError:
            return 0

    @staticmethod
    def _set_combo_by_data(combo, data):
        for i in range(combo.count()):
            if combo.itemData(i) == data:
                combo.setCurrentIndex(i)
                return
        combo.setCurrentIndex(0)

    def _edit(self, prop, value):
        if self._loading or self.selected is None:
            return
        selector = self._full_selector()
        rule = self.rules.setdefault(selector, {})
        if value in (None, ""):
            rule.pop(prop, None)
        else:
            rule[prop] = value
        if not rule:
            self.rules.pop(selector, None)

        self._refresh_output()
        self._rebuild_state_items(self.state_combo.currentData() or "")
        self._sync_target_ui()

    def _delete_current_rule(self):
        selector = self._full_selector()
        if selector not in self.rules:
            return
        del self.rules[selector]
        self._refresh_output()
        self._rebuild_variant_items()
        self._rebuild_state_items(self.state_combo.currentData() or "")
        self._load_editors()
        self._sync_target_ui()
        self.statusBar().showMessage(f"已删除规则：{selector}", 3000)

    def clear_all(self):
        if not self.rules:
            return
        ret = QMessageBox.question(
            self, "清空全部样式", "确定要删除所有已经设计好的样式规则吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ret != QMessageBox.StandardButton.Yes:
            return
        self.cand.clear()
        self.edit_idx.clear()
        self.rules = {}
        self._restore_preview_state()
        self._rebuild_variant_items()
        self._activate_base(self._base_selector())
        self._rebuild_state_items(self.state_combo.currentData() or "")
        self._load_editors()
        self._refresh_output()
        self._sync_target_ui()
        self.statusBar().showMessage("已清空全部样式（含全部候选）", 3000)

    # ------------------------------------------------------------ QSS 输出

    @staticmethod
    def _blocks_of(rules):
        """把一套候选的 {选择器: {属性: 值}} 序列化为 QSS 块列表。"""
        blocks = []
        for selector, rule in rules.items():
            if not rule:
                continue
            lines = [f"{selector} {{"]
            # 关键修复：Qt/Fusion 下 border-radius 需要同时有可见边框和背景色才会绘制。
            # 只设圆角没设背景色时，Qt 退化为矩形绘制；自动补背景色让圆角生效。
            has_radius = bool(rule.get("border-radius"))
            has_border_w = bool(rule.get("border-width"))
            has_border_c = bool(rule.get("border-color"))
            has_bg = bool(rule.get("background-color"))
            # 有圆角但没背景色时，自动补白色背景（保证圆角绘制）
            if has_radius and not has_bg:
                lines.append("    background-color: #ffffff;")
            for prop in PROPS_ORDER:
                if prop == "border-width":
                    if has_radius and not has_border_w:
                        lines.append("    border-width: 1px;")
                    elif prop in rule:
                        lines.append(f"    {prop}: {rule[prop]};")
                    continue
                if prop == "border-style":
                    if (has_radius and not has_border_w) or rule.get("border-width"):
                        # 圆角或有边框宽时补 solid（QSS 默认 border-style 为 none 不画边框）
                        lines.append("    border-style: solid;")
                    elif prop in rule:
                        lines.append(f"    {prop}: {rule[prop]};")
                    continue
                if prop == "border-color":
                    if (has_radius or has_border_w) and not has_border_c:
                        # 无边框色时用浅灰，保证边框/圆角可见
                        lines.append("    border-color: #b9b9b9;")
                    elif prop in rule:
                        lines.append(f"    {prop}: {rule[prop]};")
                    continue
                if prop in rule:
                    lines.append(f"    {prop}: {rule[prop]};")
            lines.append("}")
            blocks.append("\n".join(lines))
        return blocks

    def build_qss(self):
        # 每个目标只输出“当前正在编辑”的候选；多套备选在“候选对比”页分别复制
        blocks = []
        for base, cands in self.cand.items():
            idx = max(0, min(self.edit_idx.get(base, 0), len(cands) - 1))
            blocks.extend(self._blocks_of(cands[idx]["rules"]))
        return "\n\n".join(blocks)

    def _refresh_output(self):
        qss = self.build_qss()
        self.code_edit.setPlainText(qss)
        # 高亮框样式仅追加在预览应用的样式上，不进入最终输出
        self.preview.setStyleSheet(qss + "\n" + RUBBER_QSS)
        self._refresh_comparison()
        self._refresh_stats()
        self._schedule_rubber()

    def _refresh_stats(self):
        n_all = 0      # 所有候选合计规则数
        n_cand = 0     # 非空候选总数
        for base, cands in self.cand.items():
            for c in cands:
                k = len(c["rules"])
                n_all += k
                if k:
                    n_cand += 1
        n = len(self.rules)   # 当前正在编辑候选的规则数
        variants = self._used_variants()
        multi = self._multi_candidate_bases()
        text = f"当前候选 {n} 条规则 · 全部候选合计 {n_all} 条 · {n_cand} 套候选"
        if multi:
            text += f" · {len(multi)} 个控件有多套备选"
        if variants:
            text += " · 命名方案：" + "、".join(variants)
        self.stats_label.setText(text)
        self.copy_all_cand_btn.setEnabled(bool(multi))

    def _refresh_comparison(self):
        """重建“候选样式对比”页：每个多候选目标一块，逐套显示 + 独立复制。"""
        lay = self.cmp_layout
        while lay.count() > 1:  # 保留末尾 stretch
            item = lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        multi = self._multi_candidate_bases()
        if not multi:
            hint = QLabel(
                "还没有多套候选。\n\n"
                "操作方法：\n"
                "① 中间点选一个控件，左侧调好第 1 套样式；\n"
                "② 点候选行的“＋”新建第 2 套，换一套配色 / 圆角 / 边框；\n"
                "③ 需要 3 套就再点“＋”。每套候选在这里并排显示，"
                "各带一个“复制这套”按钮，看中哪套复制哪套。"
            )
            hint.setWordWrap(True)
            hint.setStyleSheet("color: #666; padding: 16px;")
            lay.insertWidget(0, hint)
            return

        row = 0
        for base in multi:
            cands = self.cand[base]
            cur = self.edit_idx.get(base, 0)
            n_alive = sum(1 for c in cands if c["rules"])
            box = QGroupBox(f"{base}  ——  {n_alive} 套候选")
            bl = QVBoxLayout(box)
            for idx, c in enumerate(cands):
                qss = self._candidate_qss(base, idx)
                if not qss:
                    continue
                head = QHBoxLayout()
                is_cur = idx == cur
                name_lbl = QLabel(
                    ("▶ " if is_cur else "　")
                    + f"候选 {idx + 1}「{c['name']}」"
                    + ("　（当前采用，已进入“QSS 样式代码”总复制）" if is_cur
                       else "　（备选，不会与当前采用的同时写进总 QSS）")
                )
                name_lbl.setWordWrap(True)
                name_lbl.setStyleSheet(
                    "font-weight: bold;" + (" color: #0b6bcb;" if is_cur else "")
                )
                copy_btn = QPushButton("⧉ 复制这套")
                copy_btn.setFixedWidth(110)
                copy_btn.clicked.connect(
                    lambda _=False, b=base, i=idx: self._copy_one_candidate(b, i)
                )
                head.addWidget(name_lbl, 1)
                head.addWidget(copy_btn, 0)
                view = QPlainTextEdit()
                view.setReadOnly(True)
                view.setPlainText(qss)
                view.setFont(self.code_edit.font())
                view.setFixedHeight(136)
                bl.addLayout(head)
                bl.addWidget(view)
            lay.insertWidget(row, box)
            row += 1

    def _copy_one_candidate(self, base, idx):
        qss = self._candidate_qss(base, idx)
        if not qss:
            return
        QApplication.clipboard().setText(qss)
        self.statusBar().showMessage(
            f"已复制 {base} 的「{self.cand[base][idx]['name']}」"
            "候选 QSS，直接粘贴即可使用。", 6000
        )

    def copy_qss(self):
        qss = self.code_edit.toPlainText()
        if not qss.strip():
            self.statusBar().showMessage("还没有任何样式，请先在左侧面板设计。", 3000)
            return
        QApplication.clipboard().setText(qss)
        n_out = sum(
            len(cands[self.edit_idx.get(base, 0)]["rules"])
            for base, cands in self.cand.items()
        )
        multi = self._multi_candidate_bases()
        tip = ""
        if multi:
            tip = (f"\n另：{len(multi)} 个控件做多套候选备选，本页只含当前采用的那套，"
                   "其他候选请到“候选样式对比”页逐套复制。")
        self.statusBar().showMessage(
            f"已一次性复制 {n_out} 条规则（所有控件当前采用的样式，含命名方案）！"
            "在 PyQt6 中 app.setStyleSheet(粘贴的文本) 即可整体应用。" + tip, 8000
        )

    def save_qss(self):
        qss = self.code_edit.toPlainText()
        path, _ = QFileDialog.getSaveFileName(
            self, "保存 QSS 文件", "style.qss", "Qt 样式表 (*.qss)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(qss)
        except OSError as exc:
            QMessageBox.critical(self, "保存失败", str(exc))
            return
        self.statusBar().showMessage(f"已保存：{path}", 5000)

    # ------------------------------------------------------------ 规则列表

    def _refresh_rule_list(self, selected=None):
        self.rule_list.blockSignals(True)
        self.rule_list.clear()
        # 列出全部目标、全部候选的规则；同选择器在不同候选中靠候选名区分
        for base, cands in self.cand.items():
            multi = len(cands) > 1
            for ci, c in enumerate(cands):
                for selector in c["rules"]:
                    text = selector
                    if multi:
                        text += f"   〔{ci + 1}.{c['name']}〕"
                    item = QListWidgetItem(text)
                    item.setData(Qt.ItemDataRole.UserRole, (base, ci, selector))
                    self.rule_list.addItem(item)
                    if (base, ci, selector) == selected:
                        self.rule_list.setCurrentRow(self.rule_list.count() - 1)
        self.rule_list.blockSignals(False)

    def _on_rule_picked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            base, cand_idx, selector = data
            m = SELECTOR_RE.match(selector)
        else:
            selector = item.text()
            m = SELECTOR_RE.match(selector)
            cand_idx = None
        if not m:
            return
        base = m.group("base")
        state = m.group("state") or ""
        variant = m.group("variant")
        candidates = [self.preview] + self.selectables

        if base.startswith("#"):
            scope = 2
            obj_name = base[1:]
            widget = next(
                (w for w in candidates if w.objectName() == obj_name), None
            )
        else:
            cls = base.split("[", 1)[0]
            same = [w for w in candidates if type(w).__name__ == cls]
            if variant:
                scope = 1
                # 优先选中带相同 variant 属性的演示控件
                widget = next(
                    (w for w in same
                     if str(w.property("variant") or "") == variant),
                    same[0] if same else None,
                )
            else:
                scope = 0
                widget = same[0] if same else None

        if widget is None:
            self.statusBar().showMessage(f"预览区中找不到 {base} 对应的控件", 3000)
            return
        self.select_widget(widget, scope=scope, variant=variant, state=state)
        # 跳到该规则所在的具体候选（同一选择器可能有多套候选）
        if cand_idx is not None and base in self.cand:
            cand_idx = max(0, min(cand_idx, len(self.cand[base]) - 1))
            self.edit_idx[base] = cand_idx
            self.rules = self.cand[base][cand_idx]["rules"]
            self._loading = True
            self._rebuild_state_items(state)
            self._loading = False
            self._refresh_cand_combo()
            self._load_editors()
            self._sync_target_ui()

    def _update_delete_btn(self):
        self.delete_rule_btn.setEnabled(self._full_selector() in self.rules)

    # ------------------------------------------------------------ 选中高亮

    def _schedule_rubber(self):
        QTimer.singleShot(0, self._update_rubber)
        QTimer.singleShot(120, self._update_rubber)

    def _update_rubber(self):
        if self.selected is None:
            return
        try:
            if not self.selected.isVisible():
                self.rubber.hide()
                return
            top_left = self.selected.mapTo(self.preview, QPoint(0, 0))
            # 括号外扩 6px，离控件边框远一点，完全不遮挡控件
            rect = QRect(top_left, self.selected.size()).adjusted(-6, -6, 6, 6)
        except RuntimeError:
            return
        self.rubber.setGeometry(rect)
        self.rubber.show()
        self.rubber.raise_()


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    # Fusion 风格对 QSS 的呈现最稳定可预测，便于"所见即所得"
    app.setStyle("Fusion")
    win = QssDesignerWindow()
    # 启动即最大化（铺满屏幕工作区并居中）；用户仍可还原为 1920×1080 窗口自由缩放
    win.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
