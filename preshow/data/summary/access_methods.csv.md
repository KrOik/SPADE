| database   | support_fasta | support_csv_tsv | support_json | api_available | bulk_download | license                                  | mirror_or_doi                                                                 | notes                                                                 |
|------------|---------------|-----------------|--------------|---------------|---------------|------------------------------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------|
| **APD**    | 1             | 0               | 0            | 0             | 1             | 开放获取（版权保护，无具体CC标识）        | 未提及镜像站点；无数据库专属DOI，数据来源含PubMed/PDB/Google Scholar/Swiss-Prot | APD3新增“Sequence downloads”页面支持序列批量下载，默认肽序列常用FASTA格式，无CSV/TSV/JSON格式提及；无API接口描述 |
| **DRAMP**  | 0             | 0               | 0            | 0             | 0             | 未提及                                    | 未提及                                                                     | 仅展示统计数据（如数据集分布、MICTop8），无任何数据下载入口、许可协议及镜像/DOI信息 |
| **DBAASP** | 0             | 0               | 0            | 0             | 0             | 未提及                                    | 未提及                                                                     | 仅呈现数据库组成（如23944条肽、六界来源分类）及长度分布，无数据下载功能、许可说明及镜像/DOI信息 |
| **dbAMP**  | 0             | 0               | 0            | 0             | 0             | 未提及                                    | 未提及                                                                     | 侧重功能标签（如溶血、抗HIV）、物种分类及理化性质对比，无数据下载入口、许可协议及镜像/DOI信息 |


### 各字段判定依据（严格基于文档内容）：
1. **support_fasta/support_csv_tsv/support_json**：  
   - 仅APD明确提及“Sequence downloads”（APD3新增功能），结合 antimicrobial peptide 数据库常规序列下载格式，推断支持FASTA（标1）；其余格式（CSV/TSV/JSON）无任何描述，标0。  
   - DRAMP、DBAASP、dbAMP仅展示统计结果，未提任何数据格式下载，均标0。  

2. **api_available**：  
   四个数据库的文档中均未提及“API接口”“程序调用”“开发者工具”等相关内容，均标0。  

3. **bulk_download**：  
   - APD因有“Sequence downloads”页面，可推断支持批量下载（标1）；  
   - 其余三个数据库无“批量下载”“数据导出”等入口描述，均标0。  

4. **license**：  
   - 仅APD说明“open access model”（开放获取）且“copyright-protected”（版权保护），但未标注具体CC协议（如CC BY、CC BY-NC）；  
   - 其余三个数据库未提及任何许可相关内容（如商用权限、非商用限制），均标“未提及”。  

5. **mirror_or_doi**：  
   - 四个数据库均未提及“镜像站点”“备份链接”，也未提供数据库专属DOI（数字对象标识符）或存档信息链接，均标“未提及”；APD仅说明数据来源（PubMed等），非数据库自身DOI。