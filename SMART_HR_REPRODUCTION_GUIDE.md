# 🎯 Smart-HR 智能招聘匹配系统 — 从零复现完整指南

## 📋 项目概述

**Smart-HR** 是一个基于 **Java Spring Boot + React** 的全栈招聘智能匹配系统，核心是 **知识图谱 + LLM** 双引擎混合匹配。


参考项目F:\develop\agent\smart-hr


### 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Java 17 + Spring Boot 3.3 + Maven |
| **前端** | React 18 + TypeScript + Vite + Ant Design 5 |
| **状态管理** | Zustand |
| **认证** | Spring Security + JWT |
| **数据库** | PostgreSQL 16 (pgvector) |
| **图数据库** | Neo4j 5 (知识图谱 60+技能节点) |
| **向量数据库** | Milvus 2.4 (简历/面试题向量) |
| **缓存** | Redis 7 |
| **AI 模型** | 阿里云百炼 DashScope + OpenAI (可切换) |
| **部署** | Docker Compose |

### 核心业务流

```
上传简历 → 文档解析(PDF/Word/TXT) → 技能提取(知识图谱匹配+AI辅助)
         → 简历向量化 → 存入Milvus
         → 选择岗位 → 混合匹配引擎
                      ├─ 知识图谱技能匹配 (50%)
                      └─ LLM综合评估 (50%)
         → 匹配结果
         → 面试题生成 (RAG: Milvus检索相似题 + LLM生成)
```

---

## 🗺️ 复现步骤一览 (共12步)

每个步骤都标注了：**可观测结果**、**耗时估计**、**理解要点**

---

## 第 1 步：项目骨架搭建（约15分钟）

### 做什么
用 IDEA 创建 Maven 项目，配置 `pom.xml` 和后端基础结构

### 具体操作

**1.1 创建 Maven 项目**
- 使用 IntelliJ IDEA → New Project → Maven
- GroupId: `com.smarthr`
- ArtifactId: `smart-hr-backend`
- Java 版本: 21

**1.2 创建后端目录结构**
```
src/main/java/com/smarthr/
├── SmartHrApplication.java
├── config/
├── controller/
│   ├── ai/
│   ├── auth/
│   ├── hr/
│   └── interview/
├── dto/
│   ├── ai/
│   ├── auth/
│   ├── match/
│   ├── resume/
│   ├── position/
│   └── interview/
├── entity/
├── exception/
├── repository/
├── security/
└── service/
    ├── ai/
    ├── document/
    ├── graph/
    ├── hr/
    ├── interview/
    ├── match/
    ├── rag/
    └── vector/
```

**1.3 配置 pom.xml**
- 添加 Spring Boot 3.3.8 parent
- 添加所有依赖（见参考项目 pom.xml）

**1.4 创建主启动类**

```java
package com.smarthr;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SmartHrApplication {
    public static void main(String[] args) {
        SpringApplication.run(SmartHrApplication.class, args);
    }
}
```

### ✅ 可观测结果
- [ ] Maven 依赖下载成功
- [ ] `mvn compile` 通过
- [ ] 启动 `SmartHrApplication` 看到 Spring Boot Banner（虽然会因为缺数据库报错，但启动框架正常）

### 📚 学习要点
- Spring Boot 3.x 的项目结构
- Maven 依赖管理（BOM、parent、scope）
- Java 模块化包结构设计

---

## 第 2 步：Docker 基础设施启动（约20分钟）

### 做什么
启动全部基础设施：PostgreSQL + Redis + Neo4j + Milvus(etcd+MinIO)

### 具体操作

**2.1 创建 docker 目录及配置文件**

创建 `docker/docker-compose.dev.yml` 文件，内容包含：
- PostgreSQL (pgvector:pg16) - 端口 15432
- Redis (7-alpine) - 端口 6379
- Neo4j (5-community) - 端口 7474(浏览器)/7687(Bolt)
- etcd - Milvus 依赖
- MinIO - Milvus 依赖
- Milvus (2.4.0) - 端口 19530

**2.2 创建数据库初始化脚本**

`docker/postgres/init.sql`：建5张表（users, positions, resumes, match_records, interview_records）

**2.3 创建预置岗位数据**

`docker/postgres/init-positions.sql`：插入20个岗位（Java初级/中级/高级、Python、React、Vue、全栈等）

**2.4 启动所有容器**

```bash
cd docker
docker-compose -f docker-compose.dev.yml up -d
```

**2.5 验证服务状态**

```bash
docker-compose ps
# 所有服务应为 Up 状态
```

### ✅ 可观测结果
- [ ] `docker-compose ps` 显示所有服务为 Up
- [ ] 访问 `http://localhost:7474` 打开 Neo4j 浏览器（使用 neo4j/neo4j123 登录）
- [ ] 访问 `http://localhost:3300` 打开 Milvus Attu 管理界面
- [ ] `docker logs smarthr-postgres` 查看 PostgreSQL 初始化日志

### 📚 学习要点
- Docker Compose 多服务编排
- 服务间依赖和健康检查
- PostgreSQL + pgvector 扩展
- Neo4j 图数据库
- Milvus 向量数据库架构（etcd+MinIO+Milvus）

---

## 第 3 步：Neo4j 知识图谱初始化（约5分钟）

### 做什么
向 Neo4j 导入技能知识图谱（8个分类，60+技能节点）

### 具体操作

**3.1 创建初始化 Cypher 脚本**

`docker/neo4j/init.cypher`：
- 创建 8 个技能分类（后端开发、前端开发、数据库、DevOps、AI、测试、项目管理、通用能力）
- 创建 60+ 技能节点（Java、Spring、Spring Boot、React、Python、MySQL 等）
- 创建 REQUIRES（前置依赖）、RELATED_TO（相关）、BELONGS_TO（所属分类）关系

**3.2 手动执行（如果 docker 没有自动执行）**

```bash
# 进入 Neo4j 容器
docker exec -it smarthr-neo4j bin/cypher-shell -u neo4j -p neo4j123
# 在 cypher-shell 中执行
:source /var/lib/neo4j/import/init.cypher
# 验证
MATCH (s:Skill) RETURN count(s) as totalSkills;
```

### ✅ 可观测结果
- [ ] Neo4j 中 Skill 节点数量 >= 60
- [ ] 有 8 个 SkillCategory 节点
- [ ] 通过 Neo4j Browser 可视化查看技能关系图（运行 `MATCH (s:Skill)-[r:REQUIRES]->(t:Skill) RETURN s,r,t LIMIT 30`）

### 📚 学习要点
- 图数据库 vs 关系型数据库
- Cypher 查询语言基础
- 知识图谱的节点-关系模型设计
- 技能依赖链（Java → Spring → Spring Boot → Spring Cloud）

---

## 第 4 步：Milvus 题库种子数据（约5分钟）

### 做什么
向 Milvus 写入 10 道预置面试题作为题库

### 具体操作

**4.1 创建种子脚本**

`docker/seed_questions.py`：
- 使用 pymilvus 连接 Milvus
- 创建 `smart_hr_questions` 集合
- 写入 10 道企业支付相关的面试题（含伪向量）

**4.2 执行种子脚本**

```bash
# 如果容器自动执行失败，手动执行：
docker exec smarthr-question-seeder python /app/seed_questions.py
```

### ✅ 可观测结果
- [ ] Milvus 中 `smart_hr_questions` 集合存在
- [ ] 集合中实体数量 >= 10

---

## 第 5 步：后端实体与配置层（约30分钟）

### 做什么
创建 JPA 实体类、配置文件、Repository

### 具体操作

**5.1 application.yml 配置**
- 数据源（PostgreSQL）
- JPA (ddl-auto: update)
- Redis
- Neo4j
- Spring AI (DashScope + OpenAI)
- JWT
- Milvus 配置

**5.2 创建实体类**

| 实体 | 表名 | 关键字段 |
|------|------|---------|
| User | users | id, username, password, email, role(HR/INTERVIEWER), preferredModel |
| Position | positions | id, title, company, salaryRange, skills[], responsibilities, requirements |
| Resume | resumes | id, userId, fileName, content, extractedSkills[] |
| MatchRecord | match_records | id, resumeId, positionId, finalScore, graphScore, llmScore, matchedSkills[], missingSkills[], llmReport |
| InterviewRecord | interview_records | id, positionId, userId, difficulty, questionType, questions(JSONB) |

**5.3 创建 Repository**

| Repository | 关键方法 |
|-----------|---------|
| UserRepository | findByUsername |
| PositionRepository | findByIdAndDeletedFalse, findByDeletedFalse |
| ResumeRepository | findByUserId, findAll |
| MatchRecordRepository | findByResumeId, findByPositionId |
| InterviewRecordRepository | findByUserId |
| SkillRepository (Neo4j) | findByName, findByKeyword, findPrerequisites, findRelatedSkills, findAdvancedSkills, findAllSkills |

**5.4 配置类**

| 配置 | 说明 |
|------|------|
| JwtProperties | JWT 密钥、过期时间配置 |
| MilvusProperties | Milvus 连接、集合名、维度等 |
| AIModelProperties | 阿里云/OpenAI 启停配置 |
| MilvusConfig | 创建 MilvusClientV2 Bean |
| SecurityConfig | Spring Security + JWT 无状态认证 |
| AIModelAutoConfiguration | AI 模型适配器装配 |
| OpenApiConfig | Swagger 文档配置 |

### ✅ 可观测结果
- [ ] 启动应用，控制台看到 JPA 自动建表日志
- [ ] 访问 `http://localhost:8080/swagger-ui.html` 能看到 Swagger 文档
- [ ] PostgreSQL 中看到所有表已创建（`\dt` 命令）

### 📚 学习要点
- JPA 实体映射（@Entity, @Table, @Column）
- @Enumerated 枚举映射
- JPA 自动 DDL（ddl-auto: update）
- Spring Data JPA Repository
- Spring Data Neo4j Repository + @Query 自定义 Cypher
- @ConfigurationProperties 属性绑定

---

## 第 6 步：认证与安全层（约20分钟）

### 做什么
实现 JWT 登录注册 + Spring Security 权限控制

### 具体操作

**6.1 创建安全组件**

| 类 | 说明 |
|------|------|
| UserPrincipal | 实现 UserDetails，包装 User 实体 |
| CustomUserDetailsService | 加载用户 |
| JwtTokenProvider | JWT 生成/解析/验证 |
| JwtAuthenticationFilter | 请求拦截验证 JWT |

**6.2 创建 AuthController 接口**

| 接口 | 路径 |
|------|------|
| POST 登录 | `/api/auth/login` |
| POST 注册 | `/api/auth/register` |
| GET 当前用户 | `/api/auth/me` |

**6.3 配置 SecurityConfig**
- 禁用 CSRF
- 白名单路径（/api/auth/login, /api/auth/register, /swagger-ui/**）
- JWT 无状态会话
- 角色权限（HR 有 /api/hr/**, INTERVIEWER 有 /api/interview/**）

### ✅ 可观测结果
- [ ] 使用 curl 或 Postman 注册用户：`POST /api/auth/register`
- [ ] 登录获取 Token：`POST /api/auth/login`
- [ ] 使用 Token 访问受保护接口：`GET /api/auth/me`
- [ ] 无 Token 访问返回 401
- [ ] 非 HR 角色访问 HR 接口返回 403

### 📚 学习要点
- Spring Security 过滤器链
- JWT 无状态认证机制
- BCrypt 密码加密
- 角色权限管理
- 自定义 UserDetailsService

---

## 第 7 步：文档解析与技能提取（约25分钟）

### 做什么
实现简历文件解析（PDF/Word/TXT）+ 技能提取（知识图谱+AI辅助）

### 具体操作

**7.1 DocumentParser**
- PDF 解析（Apache PDFBox 3）
- Word 解析（Apache POI）
- TXT 解析
- 空字节清理

**7.2 SkillExtractor**
- 从文本提取技能列表
- ① 知识图谱关键词匹配（遍历 Neo4j 所有技能节点）
- ② AI 辅助提取（可选）
- 技能归一化

**7.3 ResumeService + ResumeController**

| 接口 | 说明 |
|------|------|
| POST `/api/hr/resumes/upload` | 上传简历文件 |
| GET `/api/hr/resumes` | 获取简历列表 |
| GET `/api/hr/resumes/{id}` | 获取简历详情 |
| DELETE `/api/hr/resumes/{id}` | 删除简历 |

### ✅ 可观测结果
- [ ] 上传一个 PDF 简历返回成功
- [ ] 数据库中 `resumes` 表有记录，`content` 字段有解析出的文本
- [ ] `extracted_skills` 字段有提取出的技能数组
- [ ] 重新获取简历列表能看到上传的简历

### 📚 学习要点
- PDF/Word 文件解析技术
- 多格式文件处理策略
- 知识图谱关键词匹配提取
- 文件上传与存储

---

## 第 8 步：知识图谱技能匹配（约20分钟）

### 做什么
实现基于 Neo4j 知识图谱的技能匹配计算

### 具体操作

**8.1 SkillNode 模型**
Neo4j 节点实体：name, level, description, keywords

**8.2 SkillGraphService 核心方法**

| 方法 | 说明 |
|------|------|
| extractSkills(text) | 从文本提取技能（遍历所有节点，匹配名称和关键词） |
| calculateSkillMatch(candidateSkills, requiredSkills) | 计算技能匹配度 |
| calculatePartialMatch(requiredSkill, candidateSkills) | 计算部分匹配 |
| getSkillLearningPath(targetSkill) | 获取技能学习路径 |
| recommendSkillsToLearn(currentSkills, targetSkills) | 推荐需学习技能 |

**计分规则：**
- 直接匹配 → 1.0 分
- 相关技能（RELATED_TO）→ 0.5 分
- 前置技能（REQUIRES 反向）→ 0.3 分
- 高级技能（被 REQUIRES）→ 0.8 分

### ✅ 可观测结果
- [ ] 编写测试调用 `skillGraphService.extractSkills("熟悉Java和Spring Boot开发")` 返回 ["Java", "Spring Boot"]
- [ ] 调用 `calculateSkillMatch(["Java", "Spring"], ["Spring Boot", "MySQL"])` 能得到正确分数（Spring 是 Spring Boot 的前置技能，给 0.3 分）
- [ ] 调用 `getSkillLearningPath("Spring Cloud")` 返回 ["Java", "Spring", "Spring Boot", "Spring Cloud"]

### 📚 学习要点
- Neo4j @Node 实体映射
- Cypher 复杂查询（MATCH, OPTIONAL MATCH, 路径查询）
- Graph Service 设计模式
- 技能匹配算法设计（直接+部分+高级+前置）

---

## 第 9 步：向量存储与 RAG 服务（约30分钟）

### 做什么
实现 Milvus 向量存储 + Embedding 服务 + RAG 检索

### 具体操作

**9.1 VectorStore 接口**

```java
public interface VectorStore {
    void addDocument(VectorDocument document);
    void addDocuments(List<VectorDocument> documents);
    void deleteDocument(String id);
    void deleteDocuments(List<String> ids);
    List<VectorDocument> similaritySearch(float[] queryEmbedding, int topK);
    List<VectorDocument> similaritySearch(float[] queryEmbedding, int topK, String filter);
    VectorDocument getDocument(String id);
    boolean exists(String id);
    long count();
    String getStoreId();
}
```

**9.2 MilvusVectorStore 实现**
- 使用 MilvusClientV2 (v2.5.4 SDK)
- 集合：`smart_hr_resumes` (1536维, IVF_FLAT, COSINE)
- CRUD + 相似度搜索

**9.3 QuestionBankVectorStore**
- 独立集合：`smart_hr_questions`
- 用于面试题检索

**9.4 EmbeddingService**
- 封装 Spring AI EmbeddingModel
- text → 1536维向量
- 阿里云 text-embedding-v2

### ✅ 可观测结果
- [ ] 启动应用后 Milvus 集合自动创建
- [ ] 调用 EmbeddingService 能返回 float[] 向量
- [ ] 通过 Milvus Attu (`http://localhost:3300`) 能看到集合结构
- [ ] 插入文档后，相似度搜索能返回结果

### 📚 学习要点
- 向量数据库原理（IVF_FLAT 索引、COSINE 距离）
- Milvus SDK 使用
- Embedding 模型
- 向量存储接口设计（抽象+实现）

---

## 第 10 步：混合匹配引擎（⭐核心，约45分钟）

### 做什么
实现知识图谱 + LLM 双引擎混合匹配，这是系统的核心业务

### 具体操作

**10.1 MatchResult 模型**

```java
finalScore, ragScore, graphScore, llmScore,
matchedSkills, missingSkills, extraSkills,
llmReport, scoreDetails, matchGrade(A/B/C/D), recommendLevel(1-5)
```

**10.2 HybridMatchService 核心流程**

```
输入：简历内容 + 岗位JD + 技能列表
  1. 从简历提取技能（知识图谱）
  2. 计算知识图谱技能匹配分（0-100）
  3. 调用 LLM 进行综合评估（0-100）
     - 构建 Prompt（包含JD、简历、图谱匹配结果）
     - 调用 ModelRouter 选择 AI 模型
     - 解析 LLM 返回的评分和报告
  4. 最终得分 = GraphScore × 0.5 + LLMScore × 0.5
  5. 确定匹配等级和推荐指数
```

**10.3 AI 模型服务**

| 组件 | 说明 |
|------|------|
| AIModelAdapter | 适配器接口（chat, stream, embed） |
| AliyunAdapter | 阿里云百炼适配（Spring AI Alibaba） |
| OpenAIAdapter | OpenAI 适配 |
| ModelRegistry | 模型注册中心 |
| ModelRouter | 模型路由（按用户偏好选择） |

**10.4 MatchController 接口**

| 接口 | 说明 |
|------|------|
| POST `/api/hr/match` | 执行单次匹配 |
| POST `/api/hr/match/resume/{id}/positions` | 简历匹配所有岗位 |
| POST `/api/hr/match/position/{id}/resumes` | 岗位匹配所有简历 |
| GET `/api/hr/match/{id}` | 获取匹配详情 |
| GET `/api/hr/match` | 匹配历史分页 |

### ✅ 可观测结果
- [ ] POST `/api/hr/match` 返回完整的匹配结果
- [ ] 匹配结果包含：finalScore, graphScore, llmScore
- [ ] matchedSkills 和 missingSkills 正确列出
- [ ] llmReport 有 LLM 生成的评估报告
- [ ] matchGrade 正确（如 B、A）
- [ ] 切换 AI 模型后再匹配，使用不同模型

### 📚 学习要点（⭐重中之重）
- 混合匹配架构设计
- LLM Prompt 工程（system + user message）
- LLM 响应解析（正则提取评分）
- 加权评分算法
- AI 模型适配器模式
- 模型路由（按用户切换模型）

---

## 第 11 步：面试题生成（⭐RAG核心，约30分钟）

### 做什么
实现 RAG 面试题生成：从 Milvus 检索相似题 + LLM 参考生成

### 具体操作

**11.1 QuestionBankService**
- searchSimilarQuestions: 技能+难度+领域 → 向量化 → Milvus 检索
- 返回 topK 相似题目作为参考

**11.2 InterviewQuestionService 核心流程**

```
输入：岗位/技能 + 难度 + 题目类型 + 数量
  1. 获取技能列表（从岗位或直接指定）
  2. 调用 QuestionBankService 从 Milvus 检索相似题（RAG）
  3. 构建 Prompt（包含技能、难度、题库命中结果、业务域）
  4. 调用 LLM 生成
  5. 解析 AI 响应（JSON数组）
  6. 保存到 PostgreSQL
  7. 返回结果
  ↓
  如果 AI 调用失败 → 使用兜底默认题
```

**11.3 InterviewController 接口**

| 接口 | 说明 |
|------|------|
| POST `/api/interview/generate` | 自定义生成面试题 |
| POST `/api/interview/generate/position/{id}` | 按岗位快速生成 |
| POST `/api/interview/generate/skills` | 按技能列表快速生成 |
| GET `/api/interview/records` | 生成历史分页 |
| GET `/api/interview/records/{id}` | 面试记录详情 |
| DELETE `/api/interview/records/{id}` | 删除记录 |

### ✅ 可观测结果
- [ ] POST `/api/interview/generate` 返回 5 道面试题
- [ ] 题目中包含 "Smart-HR 科技" 公司名
- [ ] 题目与企业支付业务域相关
- [ ] interview_records 表有 JSONB 格式的题目记录
- [ ] 断开 AI 后生成，能返回兜底默认题
- [ ] 多次生成同一岗位，题目有变化（体现 LLM 的生成特性）

### 📚 学习要点（⭐核心）
- RAG 完整流程：检索 + 增强 + 生成
- Prompt 构建技巧（参考上下文+要求输出格式）
- LLM 输出解析（JSON 提取）
- 兜底策略（AI 失败时默认数据）
- JSONB 字段存储

---

## 第 12 步：前端实现（约60-90分钟）

### 做什么
用 React + TypeScript + Ant Design 实现完整前端

### 具体操作

**12.1 项目初始化**

```bash
npm create vite@latest front -- --template react-ts
cd front
npm install antd @ant-design/icons axios zustand react-router-dom dayjs
```

**12.2 请求封装 (api/request.ts)**
- Axios 拦截器自动添加 JWT Token
- 401 自动跳转登录页
- 统一错误处理

**12.3 API 层**
| 文件 | 接口 |
|------|------|
| auth.ts | login, register, getCurrentUser |
| ai.ts | getModels, getCurrentModel, switchModel |
| resume.ts | upload, getList, getById, delete |
| position.ts | getList, create, update, delete |
| match.ts | match, matchResumeToPositions, getRecords |
| interview.ts | generate, getRecords, delete |

**12.4 状态管理 (Zustand)**

| Store | 状态 |
|------|------|
| authStore | token, user, isAuthenticated, login, logout, setAuth |
| aiStore | models, currentModel, switchModel |

**12.5 页面组件**

**HR 相关：**
1. **Login/Register** - 登录注册，角色选择
2. **HR/Dashboard** - 工作台概览
3. **HR/ResumeUpload** - ⭐核心RAG页面：上传简历 → 技能展示 → 选岗位 → 匹配 → 看结果
4. **HR/PositionManage** - 岗位 CRUD 表格
5. **HR/MatchResult** - 匹配详情（得分、技能、LLM报告）
6. **HR/MatchHistory** - 匹配历史

**面试官相关：**
7. **Interviewer/Dashboard** - 工作台概览
8. **Interviewer/GenerateQuestions** - ⭐核心RAG页面：选岗位 → 参数设置 → 生成面试题
9. **Interviewer/QuestionHistory** - 生成历史

**通用组件：**
10. **MainLayout** - 主布局（导航+模型选择器）
11. **ModelSelector** - AI 模型切换

### ✅ 可观测结果
- [ ] `npm run dev` 启动前端 `http://localhost:3000`
- [ ] 登录页面正常显示
- [ ] 注册 HR 和 INTERVIEWER 用户
- [ ] 上传简历文件成功
- [ ] 岗位 CRUD 正常
- [ ] 匹配分析功能完整
- [ ] 面试题生成功能完整
- [ ] 模型切换功能可用
- [ ] 路由权限控制生效

### 📚 学习要点
- Vite 项目搭建
- React Router v6 路由配置（懒加载+受保护路由）
- Zustand 状态管理 + 持久化
- Ant Design 5 组件库
- Axios 拦截器
- TypeScript 在前端的应用

---

## 💡 知识点总结

完成本项目后你将掌握：

### 后端技能
1. **Spring Boot 3.x** 全栈开发
2. **Spring AI** 整合LLM（阿里云百炼+OpenAI）
3. **Spring Security + JWT** 认证授权
4. **Spring Data JPA/Neo4j** 多数据源
5. **知识图谱** Neo4j 设计 + Cypher 查询
6. **向量数据库** Milvus 使用
7. **RAG** 检索增强生成完整实现
8. **AI 适配器模式** 多模型路由
9. **混合匹配算法** 多维度加权评分
10. **PDF/Word 解析** 文档处理

### 前端技能
1. **React 18 + TypeScript**
2. **Vite** 构建工具
3. **Ant Design 5** 组件库
4. **Zustand** 轻量状态管理
5. **React Router v6** 路由+权限
6. **Axios** 请求封装

### 架构设计
1. **多引擎混合架构**（知识图谱 + LLM）
2. **RAG 模式**（检索 + 生成）
3. **适配器模式**（AI 模型切换）
4. **微服务架构预备**（清晰的模块划分）
5. **Docker 编排**（全套基础设施）

---

## 🐛 常见问题

| 问题 | 解决 |
|------|------|
| Milvus 连接失败 | 检查 etcd 和 MinIO 是否已启动 |
| AI 调用失败 | 检查 API Key 是否配置 |
| PDF 解析乱码 | 确认有 cleanText 移除空字节 |
| JWT 认证失败 | 确认 SECRET 一致 |
| Neo4j 查询空 | 手动执行 init.cypher |
| 前端 401 循环 | 检查 Token 是否过期 |

---

## 📄 环境变量

创建 `application-private.yml`（不提交到 Git）：

```yaml
spring:
  ai:
    dashscope:
      api-key: ${DASHSCOPE_API_KEY:你的阿里云百炼AK}
    openai:
      api-key: ${OPENAI_API_KEY:你的OpenAI AK}
```

或者在系统环境变量中设置。

---

**祝复现顺利！每一步都有可观测的结果，按顺序完成，逐步验证。**
