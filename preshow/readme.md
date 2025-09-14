###核心数据文件说明
1. data/summary/compare.csv
用途：记录 4 个数据库的核心概览指标，是横向对比的基础数据。
列定义：
列名	数据类型	说明
database	文本	数据库名称（固定值：DBAASP、APD3、DRAMP、dbAMP）
total_entries	整数	数据库总条目数
avg_field_completeness_pct	整数（0-100）	关键字段的平均完整度百分比
updates_last_3y	整数	近 3 年的更新次数
latest_version	文本	最新版本标识（如 vX.Y、APD5 (2022)）
latest_update_date	日期（YYYY-MM-DD）	最新更新日期
ai_score_0_5	整数（0-5）	AI 友好性评分（评分依据见下文）
notes	文本	可选备注（如数据特殊性、异常说明）
1. data/summary/fields_coverage.csv
用途：记录各数据库在关键信息维度的覆盖情况，体现数据完整性。
列定义：
列名	数据格式	说明
database	文本	数据库名称（同 compare.csv）
sequence	百分比（0-100）/ 二进制（0/1）	是否包含肽序列信息
activity_MIC_target	百分比（0-100）/ 二进制（0/1）	是否包含活性数据、最小抑菌浓度（MIC）或靶标微生物信息
source_organism_or_type	百分比（0-100）/ 二进制（0/1）	是否包含肽的来源物种或类型（天然 / 合成等）信息
length_physchem	百分比（0-100）/ 二进制（0/1）	是否包含肽的长度或理化性质（净电荷、疏水性等）信息
modifications_PTMs	百分比（0-100）/ 二进制（0/1）	是否包含肽的修饰（环化等）或翻译后修饰（PTM）信息
publication_DOI_PMID	百分比（0-100）/ 二进制（0/1）	是否包含文献链接（DOI 或 PMID）
structure_PDB_or_pred	百分比（0-100）/ 二进制（0/1）	是否包含蛋白质数据银行（PDB）结构或预测结构信息
toxicity_hemolysis_cytotox	百分比（0-100）/ 二进制（0/1）	是否包含溶血或细胞毒性数据
1. data/summary/access_methods.csv
用途：记录各数据库的数据访问特性与使用许可，支撑可用性分析。
列定义：
列名	数据格式	说明
database	文本	数据库名称（同 compare.csv）
support_fasta	二进制（0/1）	是否支持 FASTA 格式数据导出（1 = 是，0 = 否）
support_csv_tsv	二进制（0/1）	是否支持 CSV/TSV 格式数据导出（1 = 是，0 = 否）
support_json	二进制（0/1）	是否支持 JSON 格式数据导出（1 = 是，0 = 否）
api_available	二进制（0/1）	是否提供公开 API 接口（1 = 是，0 = 否）
bulk_download	二进制（0/1）	是否支持批量数据下载（1 = 是，0 = 否）
license	文本	数据使用许可协议（如 CC BY-NC、研究可用等）
mirror_or_doi	文本	镜像站点链接或数据集 DOI / 存档信息
notes	文本	可选备注（如访问限制、格式说明）
1. data/summary/sources.json
用途：补充各数据库的基础信息，用于溯源与辅助验证。
核心字段：
每个数据库节点包含：homepage（官网主页）、download（下载入口说明）、api（API 相关信息）、latest_version（最新版本）、latest_update_date（最新更新日期）、notes（备注）。
_meta.retrieved_at：数据采集时间（由 fetch_db_stats.py 程序自动更新）。

###AI 友好性评分依据
ai_score_0_5（0-5 分）是评估数据库适配 AI 驱动研究流程便捷性的综合指标，基于 5 个等权重维度（各 1 分）：

标准化程度：数据字段定义清晰度、格式一致性，是否使用受控词汇（机器可读优先）。
格式可用性：是否提供 JSON、CSV/TSV 等机器友好型数据格式（格式越丰富得分越高）。
可访问性：是否支持 API 接口、批量下载，访问说明是否清晰。
许可协议：是否有明确且宽松的复用许可（如 CC 协议、MIT 协议）。
稳定性与持久性：是否有持续更新记录、稳定托管环境，是否提供数据集 DOI 等持久标识。
###数据来源与免责声明
1. 数据来源
data/summary/ 目录下的数据均来自各数据库官网的公开信息，所有数据均经过人工审核，并以 compare.csv 中记录的latest_update_date为基准验证准确性。
1. 免责声明
本打包文件中的数据、图表及评分仅用于信息参考，可能随数据库更新而变化；虽已尽力确保准确性，但不对信息的完整性或正确性提供担保。可视化程序按 “现状” 提供，不承担任何使用风险。用户在将本文件用于科研或其他用途前，需自行验证数据准确性。本文件作者与所对比的数据库无任何关联。