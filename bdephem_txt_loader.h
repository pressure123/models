/**
 * @file bdephem_txt_loader.h
 * @brief 将 txt 文件中第 2-16 列数据读入 BD_EphemDataStruct 结构体
 *
 * 字段映射关系 (txt 列号 → 结构体成员，按声明顺序):
 *   col  2 → usWeek        (quint16)
 *   col  3 → usZ_Week      (quint16)
 *   col  4 → dSecond       (double)
 *   col  5 → iPRN          (qint32)
 *   col  6 → uiHealth      (quint32)
 *   col  7 → uiAODE        (quint32)
 *   col  8 → uiAODC        (quint32)
 *   col  9 → fToe          (float)
 *   col 10 → dRootA        (double)
 *   col 11 → dEcc          (double)
 *   col 12 → dOmega        (double)
 *   col 13 → dDeltaN       (double)
 *   col 14 → dM0           (double)
 *   col 15 → dOmega0       (double)
 *   col 16 → BD2OrBD3flag  (quint8,  1=BD2  2=BD3)
 *
 * 分隔符: 支持空白(空格/Tab)或英文逗号。
 */

#ifndef BDEPHEM_TXT_LOADER_H
#define BDEPHEM_TXT_LOADER_H

#include <QString>
#include <QVector>
#include <QFile>
#include <QTextStream>
#include <QDebug>

#include <QtGlobal>   // quint16 / quint32 / qint32 / quint8

// ---- 保持原结构体定义不变 ---------------------------------------------------
typedef struct // BD卫星星历结构体（参数转换后的）
{
    quint16 usWeek;
    quint16 usZ_Week;
    double  dSecond;

    qint32  iPRN;
    quint32 uiHealth;

    quint32 uiAODE;        // 星历数据龄期
    quint32 uiAODC;        // 时钟数据龄期

    float   fToe;          // 星历参考时间
    double  dRootA;        // 长半轴的平方根
    double  dEcc;          // 偏心率
    double  dOmega;        // 近地点幅角
    double  dDeltaN;       // 卫星平均运动速度与计算值之差
    double  dM0;           // 参考时间的平近点角
    double  dOmega0;       // 按参考时间计算的升交点经度
    quint8  BD2OrBD3flag;  // 1=二代, 2=三代
} BD_EphemDataStruct;


// ---- 解析函数 ---------------------------------------------------------------
namespace BDEphemLoader {

/**
 * @brief 把 txt 文件中的列 2-16 解析为 BD_EphemDataStruct 列表。
 * @param filePath   txt 路径
 * @param outList    输出：解析成功的星历数组
 * @param skipHeader 跳过的表头行数（默认 0，即没有表头）
 * @return 成功解析的行数；出错返回 -1。
 */
inline int loadFromTxt(const QString &filePath,
                       QVector<BD_EphemDataStruct> &outList,
                       int skipHeader = 0)
{
    outList.clear();

    QFile file(filePath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        qWarning() << "打开文件失败:" << filePath << file.errorString();
        return -1;
    }

    QTextStream in(&file);
    in.setCodec("UTF-8");  // 若为 GBK/GB18030 请改 setCodec("GB18030")

    int lineNo = 0;
    int parsed = 0;
    while (!in.atEnd()) {
        ++lineNo;
        QString rawLine = in.readLine();

        if (lineNo <= skipHeader)
            continue;

        // 去掉可能存在的行末 \r
        rawLine.remove(QLatin1Char('\r'));

        // 空行跳过
        QString trimmed = rawLine.trimmed();
        if (trimmed.isEmpty() || trimmed.startsWith('#'))
            continue;

        // 兼容空白 / Tab / 英文逗号：先把逗号替换成空格再分割
        QString normalized = rawLine;
        normalized.replace(QLatin1Char(','), QLatin1Char(' '));
        const QStringList cols = normalized.simplified().split(QLatin1Char(' '),
                                                              Qt::SkipEmptyParts);

        // 至少要有 16 列（col1 索引 + col2-16 数据）
        if (cols.size() < 16) {
            qWarning() << QString("第%1行列数不足16(实际%2)，已跳过：%3")
                              .arg(lineNo).arg(cols.size()).arg(rawLine);
            continue;
        }

        bool ok = true;
        BD_EphemDataStruct eph;
        bool allOk = true;

        // col 1 (cols[0]) 跳过（行号/标识）
        eph.usWeek        = cols[1].toUShort(&ok);  allOk &= ok;   // col 2
        eph.usZ_Week      = cols[2].toUShort(&ok);  allOk &= ok;   // col 3
        eph.dSecond       = cols[3].toDouble(&ok);  allOk &= ok;   // col 4
        eph.iPRN          = cols[4].toInt(&ok);     allOk &= ok;   // col 5
        eph.uiHealth      = cols[5].toUInt(&ok);    allOk &= ok;   // col 6
        eph.uiAODE        = cols[6].toUInt(&ok);    allOk &= ok;   // col 7
        eph.uiAODC        = cols[7].toUInt(&ok);    allOk &= ok;   // col 8
        eph.fToe          = cols[8].toFloat(&ok);   allOk &= ok;   // col 9
        eph.dRootA        = cols[9].toDouble(&ok);  allOk &= ok;   // col 10
        eph.dEcc          = cols[10].toDouble(&ok); allOk &= ok;   // col 11
        eph.dOmega        = cols[11].toDouble(&ok); allOk &= ok;   // col 12
        eph.dDeltaN       = cols[12].toDouble(&ok); allOk &= ok;   // col 13
        eph.dM0           = cols[13].toDouble(&ok); allOk &= ok;   // col 14
        eph.dOmega0       = cols[14].toDouble(&ok); allOk &= ok;   // col 15
        eph.BD2OrBD3flag  = static_cast<quint8>(cols[15].toUInt(&ok));
        allOk &= ok;                                                   // col 16

        if (!allOk) {
            qWarning() << QString("第%1行有字段解析失败，已跳过：%2")
                              .arg(lineNo).arg(rawLine);
            continue;
        }

        outList.append(eph);
        ++parsed;
    }

    return parsed;
}

} // namespace BDEphemLoader

#endif // BDEPHEM_TXT_LOADER_H
