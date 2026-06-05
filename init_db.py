# -*- coding: utf-8 -*-
"""Smart-HR 数据库初始化：建表 + 20个预置岗位"""
import json
from sqlalchemy import create_engine, text

DATABASE_URL = "mysql+pymysql://smarthr:smarthr123@localhost:13306/smarthr"
engine = create_engine(DATABASE_URL)


def init():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS positions (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                company VARCHAR(100),
                salary_range VARCHAR(50),
                experience VARCHAR(50),
                education VARCHAR(50),
                location VARCHAR(50),
                responsibilities TEXT,
                requirements TEXT,
                skills JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                deleted TINYINT(1) DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS resumes (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255),
                file_path VARCHAR(500),
                content LONGTEXT,
                extracted_skills JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS match_records (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                resume_id BIGINT NOT NULL,
                position_id BIGINT NOT NULL,
                final_score FLOAT,
                graph_score FLOAT,
                llm_score FLOAT,
                matched_skills JSON,
                missing_skills JSON,
                extra_skills JSON,
                llm_report TEXT,
                match_grade VARCHAR(10),
                recommend_level INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes(id),
                FOREIGN KEY (position_id) REFERENCES positions(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS interview_records (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                position_id BIGINT,
                skills JSON,
                difficulty VARCHAR(20),
                question_type VARCHAR(20),
                questions JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (position_id) REFERENCES positions(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))

        conn.commit()
        print("4 tables created successfully")

        result = conn.execute(text("SELECT COUNT(*) FROM positions"))
        count = result.scalar()
        if count > 0:
            print(f"Already has {count} positions, skip seed")
            return

        positions = [
            ('Java 初级开发工程师', 'Smart-HR科技', '8K-12K', '1-3年', '本科', '北京',
             '1. 参与公司核心业务系统的开发和维护\n2. 根据需求文档完成功能模块的编码工作',
             '1. 本科及以上学历，计算机相关专业\n2. 熟悉 Java 语言\n3. 熟悉 Spring Boot',
             ['Java', 'Spring Boot', 'MyBatis', 'MySQL', 'Git']),
            ('Java 中级开发工程师', 'Smart-HR科技', '15K-25K', '3-5年', '本科', '上海',
             '1. 负责核心业务系统的架构设计和开发\n2. 主导技术难点攻关',
             '1. 3年以上 Java 开发经验\n2. 精通 Spring Boot、Spring Cloud\n3. 熟悉 Redis、RabbitMQ',
             ['Java', 'Spring Boot', 'Spring Cloud', 'Redis', 'MySQL', 'RabbitMQ', 'Docker']),
            ('Java 高级开发工程师', 'Smart-HR科技', '30K-50K', '5-10年', '本科', '深圳',
             '1. 负责核心系统的架构设计\n2. 主导大型分布式系统的设计与实现',
             '1. 5年以上 Java 开发经验\n2. 精通分布式系统设计\n3. 精通 Spring Cloud',
             ['Java', 'Spring Cloud', 'Kubernetes', 'JVM 调优', 'Java 并发编程', 'Redis', 'MySQL', '分布式系统', '微服务']),
            ('Python 后端开发工程师', 'Smart-HR科技', '15K-25K', '2-4年', '本科', '杭州',
             '1. 负责公司数据平台后端服务开发\n2. 设计和实现 RESTful API 接口',
             '1. 2年以上 Python 开发经验\n2. 熟悉 Django 或 FastAPI',
             ['Python', 'Django', 'FastAPI', 'MySQL', 'PostgreSQL', 'Redis', 'Git', 'Linux']),
            ('Python AI 开发工程师', 'Smart-HR科技', '25K-40K', '3-5年', '硕士', '北京',
             '1. 负责 AI 模型的工程化落地\n2. 开发和优化 RAG、LLM 应用',
             '1. 3年以上 Python 开发经验\n2. 熟悉 PyTorch/TensorFlow\n3. 了解 LangChain、RAG',
             ['Python', 'PyTorch', 'TensorFlow', '机器学习', '深度学习', 'NLP', 'RAG', 'LangChain', '大语言模型', 'Milvus']),
            ('React 前端开发工程师', 'Smart-HR科技', '15K-25K', '2-4年', '本科', '上海',
             '1. 负责公司 Web 产品的前端开发\n2. 基于 React 技术栈开发高质量页面',
             '1. 2年以上前端开发经验\n2. 精通 React、TypeScript',
             ['React', 'TypeScript', 'JavaScript', 'HTML/CSS', 'Ant Design', 'Webpack', 'Vite', 'Git']),
            ('Vue 前端开发工程师', 'Smart-HR科技', '15K-25K', '2-4年', '本科', '广州',
             '1. 负责公司管理后台系统的前端开发\n2. 基于 Vue3 技术栈开发业务功能',
             '1. 2年以上前端开发经验\n2. 精通 Vue3、TypeScript',
             ['Vue', 'TypeScript', 'JavaScript', 'HTML/CSS', 'Element Plus', 'Vite', 'Git']),
            ('全栈开发工程师', 'Smart-HR科技', '20K-35K', '3-5年', '本科', '成都',
             '1. 负责公司产品的全栈开发\n2. 独立完成前后端功能开发',
             '1. 3年以上全栈开发经验\n2. 熟悉 React/Vue\n3. 熟悉 Node.js/Java/Python',
             ['React', 'Vue', 'Node.js', 'TypeScript', 'MySQL', 'Redis', 'Docker', 'Git']),
            ('软件测试工程师', 'Smart-HR科技', '10K-18K', '1-3年', '本科', '武汉',
             '1. 负责软件产品的功能测试\n2. 编写测试用例、执行测试计划',
             '1. 1年以上软件测试经验\n2. 熟悉软件测试理论和方法',
             ['功能测试', 'SQL', 'JIRA', '测试用例', '缺陷管理', '需求分析']),
            ('自动化测试工程师', 'Smart-HR科技', '18K-30K', '3-5年', '本科', '南京',
             '1. 负责自动化测试框架的搭建和维护\n2. 编写自动化测试脚本',
             '1. 3年以上测试经验，2年以上自动化经验\n2. 熟悉 Selenium、Pytest',
             ['自动化测试', 'Selenium', 'Pytest', 'Python', 'JMeter', 'Jenkins', 'Git']),
            ('机器学习算法工程师', 'Smart-HR科技', '30K-50K', '3-5年', '硕士', '北京',
             '1. 负责推荐系统、搜索排序等算法研发\n2. 设计和优化机器学习模型',
             '1. 3年以上算法开发经验\n2. 精通机器学习、深度学习算法',
             ['机器学习', '深度学习', 'Python', 'PyTorch', 'TensorFlow', '推荐系统', '特征工程', 'SQL']),
            ('NLP 算法工程师', 'Smart-HR科技', '35K-60K', '3-5年', '硕士', '上海',
             '1. 负责自然语言处理相关算法研发\n2. 设计和优化文本理解、生成模型',
             '1. 3年以上 NLP 算法经验\n2. 精通 Transformer 架构\n3. 熟悉 BERT、GPT',
             ['NLP', '深度学习', 'Python', 'PyTorch', 'Transformer', '大语言模型', 'BERT', '知识图谱', 'RAG']),
            ('技术项目经理', 'Smart-HR科技', '25K-40K', '5-8年', '本科', '北京',
             '1. 负责技术项目的全流程管理\n2. 制定项目计划、把控项目进度',
             '1. 5年以上项目管理经验\n2. 熟悉敏捷开发、Scrum',
             ['项目管理', 'Scrum', '敏捷开发', 'JIRA', '需求分析', '风险管理', '沟通能力', '团队协作']),
            ('产品经理', 'Smart-HR科技', '20K-35K', '3-5年', '本科', '杭州',
             '1. 负责产品的规划和设计\n2. 进行市场调研和竞品分析',
             '1. 3年以上产品经理经验\n2. 熟悉 Axure、Figma',
             ['产品设计', '需求分析', 'PRD', 'Axure', '用户研究', '数据分析', '沟通能力', '逻辑思维']),
            ('人力资源专员', 'Smart-HR科技', '8K-15K', '1-3年', '本科', '北京',
             '1. 负责公司招聘工作\n2. 办理员工入离职手续',
             '1. 1年以上 HR 相关工作经验\n2. 熟悉招聘流程',
             ['招聘', '人事管理', '员工关系', 'Office', '沟通能力', '团队协作']),
            ('HRBP', 'Smart-HR科技', '20K-35K', '5-8年', '本科', '上海',
             '1. 深入业务部门，提供 HR 解决方案\n2. 负责人人才盘点和组织诊断',
             '1. 5年以上 HR 经验\n2. 熟悉人力资源六大模块',
             ['HRBP', '人才发展', '绩效管理', '组织诊断', '员工关系', '沟通能力', '业务理解']),
            ('财务专员', 'Smart-HR科技', '10K-18K', '2-4年', '本科', '深圳',
             '1. 负责日常账务处理和凭证录入\n2. 编制财务报表',
             '1. 2年以上财务工作经验\n2. 熟悉会计准则',
             ['财务核算', '报表编制', '税务申报', 'Excel', '财务分析', '细致认真']),
            ('行政专员', 'Smart-HR科技', '6K-10K', '1-3年', '大专', '广州',
             '1. 负责公司日常行政事务管理\n2. 管理办公用品和固定资产',
             '1. 1年以上行政工作经验\n2. 熟练使用 Office',
             ['行政管理', 'Office', '会议组织', '沟通能力', '服务意识', '协调能力']),
            ('数据分析师', 'Smart-HR科技', '18K-30K', '2-4年', '本科', '北京',
             '1. 负责业务数据分析，提供决策支持\n2. 搭建数据看板和指标体系',
             '1. 2年以上数据分析经验\n2. 精通 SQL 和 Python\n3. 熟悉 Tableau',
             ['SQL', 'Python', '数据分析', 'Tableau', 'PowerBI', 'Excel', '统计学']),
            ('运维开发工程师', 'Smart-HR科技', '20K-35K', '3-5年', '本科', '上海',
             '1. 负责公司基础设施的运维和自动化\n2. 设计并实现 CI/CD 流水线',
             '1. 3年以上运维开发经验\n2. 精通 Linux、Docker、Kubernetes',
             ['Linux', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'Python', 'Shell', 'Nginx']),
        ]

        for p in positions:
            conn.execute(
                text("""INSERT INTO positions 
                    (title, company, salary_range, experience, education, location, responsibilities, requirements, skills) 
                    VALUES (:t, :c, :s, :e, :ed, :l, :r, :req, :sk)"""),
                {"t": p[0], "c": p[1], "s": p[2], "e": p[3], "ed": p[4], "l": p[5],
                 "r": p[6], "req": p[7], "sk": json.dumps(p[8], ensure_ascii=False)}
            )
        conn.commit()
        print(f"Inserted {len(positions)} positions successfully")


if __name__ == "__main__":
    init()
