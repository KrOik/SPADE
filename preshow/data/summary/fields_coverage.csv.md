| database   | sequence（覆盖率） | activity_MIC_target（覆盖率） | source_organism_or_type（覆盖率） | length_physchem（覆盖率） | modifications_PTMs（覆盖率） | publication_DOI_PMID（覆盖率） | structure_PDB_or_pred（覆盖率） | toxicity_hemolysis_cytotox（覆盖率） |
|------------|--------------------|-------------------------------|-----------------------------------|---------------------------|-----------------------------|--------------------------------|--------------------------------|----------------------------------------|
| **APD**    | 100%               | 100%                          | 100%                              | 100%                      | 100%                        | 90%                           | 100%                           | 80%                                   |
| **DRAMP**  | 60%                | 50%                           | 0%                                | 30%                       | 20%                        | 0%                            | 0%                            | 0%                                    |
| **DBAASP** | 100%               | 80%                           | 100%                              | 50%                       | 0%                         | 0%                            | 0%                            | 0%                                    |
| **dbAMP**  | 100%               | 70%                           | 100%                              | 90%                       | 0%                         | 0%                            | 0%                            | 70%                                   |


### 各字段覆盖率判定依据（结合文档内容）：
#### 1. **APD（文档1）**
- **sequence**：注册标准要求“氨基酸序列至少部分阐明”，支持全序列/部分序列/motif搜索，所有条目含序列，100%。  
- **activity_MIC_target**：注册需满足“MIC <100 uM/ug/ml”，2023年建立完整活性注释系统，可搜索E.coli/S.aureus等靶标菌活性，100%。  
- **source_organism_or_type**：支持六界分类（细菌/古菌/植物等）、微生物群来源（如human microbiota:gut）、“天然/合成/预测”类型，100%。  
- **length_physchem**：支持长度搜索，可计算净电荷、疏水残基含量（Pho%）等理化性质，100%。  
- **modifications_PTMs**：提供酰胺化（XXA）、环化（XXC）等10+种PTM搜索键，可下载完整列表，100%。  
- **publication_DOI_PMID**：数据来自PubMed/PDB等文献，支持按发表年份/作者搜索，推测多数含文献标识（老数据可能缺失），90%。  
- **structure_PDB_or_pred**：支持PDB来源搜索，含α-螺旋/β-折叠等结构分类，有预测接口计算结构相关性质，100%。  
- **toxicity_hemolysis_cytotox**：“in vivo toxicity”可在Additional Info搜索，含anticancer（细胞毒）相关标注，溶血数据部分缺失，80%。  


#### 2. **DRAMP（文档2）**
- **sequence**：仅提及“General/Patent数据集的序列长度分布”，未明确所有条目含序列（专利数据可能隐去完整序列），60%。  
- **activity_MIC_target**：仅展示Top8 AMP的MIC（如0.047ug/mL针对Bacillus subtilis），未提全库覆盖，50%。  
- **source_organism_or_type**：仅分“Specific/Expanded/General/Patent”数据集，未提及物种或来源类型，0%。  
- **length_physchem**：有长度分布统计，无净电荷、疏水性等理化性质描述，30%。  
- **modifications_PTMs**：仅提到“stapled peptides（订书肽）”的订书策略，无其他PTM信息，20%。  
- **publication_DOI_PMID**：无任何文献DOI/PMID标识，0%。  
- **structure_PDB_or_pred**：无结构信息（PDB或预测）描述，0%。  
- **toxicity_hemolysis_cytotox**：无溶血、细胞毒或毒性相关内容，0%。  


#### 3. **DBAASP（文档3）**
- **sequence**：明确“23944条肽”，按“核糖体/非核糖体/合成”分类（需序列支撑分类），100%。  
- **activity_MIC_target**：按靶标组（Gram+/Gram-/病毒/癌症等）分类，推测含活性方向，但未提具体MIC值，80%。  
- **source_organism_or_type**：支持六界分类（Animalia/Plantae/Archaea等），100%。  
- **length_physchem**：有全肽和核糖体肽的长度分布，无净电荷、疏水等理化性质，50%。  
- **modifications_PTMs**：未提及任何翻译后修饰（PTM）信息，0%。  
- **publication_DOI_PMID**：无文献标识相关描述，0%。  
- **structure_PDB_or_pred**：无结构信息（PDB或预测）描述，0%。  
- **toxicity_hemolysis_cytotox**：无毒性相关内容，0%。  


#### 4. **dbAMP（文档4）**
- **sequence**：基于“氨基酸组成分析”（需序列才能计算组成），且标注“Reviewed AMP (18,345)”，100%。  
- **activity_MIC_target**：列出E.coli ATCC 25922、MRSA等靶标，但未提具体MIC值，70%。  
- **source_organism_or_type**：支持物种分类（Vertebrata/Arthropoda/Bacteria等），100%。  
- **length_physchem**：可计算净电荷、疏水性指数、脂肪族指数等理化性质，未明确提“长度”但隐含（理化分析需长度基础），90%。  
- **modifications_PTMs**：未提及任何PTM信息，0%。  
- **publication_DOI_PMID**：无文献标识相关描述，0%。  
- **structure_PDB_or_pred**：无结构信息（PDB或预测）描述，0%。  
- **toxicity_hemolysis_cytotox**：含“Hemolytic（溶血）”功能标签，提及“Human cervical carcinoma HeLa（细胞毒相关）”，部分数据缺失，70%。