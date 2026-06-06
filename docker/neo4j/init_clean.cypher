// Smart-HR Neo4j 鐭ヨ瘑鍥捐氨鍒濆鍖栬剼鏈?// @author QinFeng Luo
// @date 2026/01/09

// 鍒涘缓绾︽潫
CREATE CONSTRAINT skill_name IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT category_code IF NOT EXISTS FOR (c:SkillCategory) REQUIRE c.code IS UNIQUE;

// 鍒涘缓鎶€鑳藉垎绫昏妭鐐?MERGE (c1:SkillCategory {code: 'BACKEND', name: '鍚庣寮€鍙?, description: '鏈嶅姟绔紑鍙戠浉鍏虫妧鑳?})
MERGE (c2:SkillCategory {code: 'FRONTEND', name: '鍓嶇寮€鍙?, description: '瀹㈡埛绔紑鍙戠浉鍏虫妧鑳?})
MERGE (c3:SkillCategory {code: 'DATABASE', name: '鏁版嵁搴?, description: '鏁版嵁搴撶浉鍏虫妧鑳?})
MERGE (c4:SkillCategory {code: 'DEVOPS', name: 'DevOps', description: '杩愮淮涓庨儴缃茬浉鍏虫妧鑳?})
MERGE (c5:SkillCategory {code: 'AI', name: '浜哄伐鏅鸿兘', description: 'AI涓庢満鍣ㄥ涔犵浉鍏虫妧鑳?})
MERGE (c6:SkillCategory {code: 'TESTING', name: '娴嬭瘯', description: '杞欢娴嬭瘯鐩稿叧鎶€鑳?})
MERGE (c7:SkillCategory {code: 'MANAGEMENT', name: '椤圭洰绠＄悊', description: '椤圭洰绠＄悊鐩稿叧鎶€鑳?})
MERGE (c8:SkillCategory {code: 'GENERAL', name: '閫氱敤鑳藉姏', description: '閫氱敤杞妧鑳?});

// ========== 鍚庣寮€鍙戞妧鑳?==========
// Java 鐢熸€?MERGE (java:Skill {name: 'Java', level: 2, description: 'Java 缂栫▼璇█', keywords: ['JDK', 'JVM', 'Java SE']})
MERGE (oop:Skill {name: '闈㈠悜瀵硅薄缂栫▼', level: 1, description: 'OOP 璁捐鎬濇兂', keywords: ['OOP', '灏佽', '缁ф壙', '澶氭€?]})
MERGE (spring:Skill {name: 'Spring Framework', level: 3, description: 'Spring 鏍稿績妗嗘灦', keywords: ['IoC', 'AOP', 'DI']})
MERGE (springboot:Skill {name: 'Spring Boot', level: 3, description: 'Spring Boot 蹇€熷紑鍙戞鏋?, keywords: ['鑷姩閰嶇疆', '璧锋渚濊禆']})
MERGE (springcloud:Skill {name: 'Spring Cloud', level: 4, description: 'Spring Cloud 寰湇鍔℃鏋?, keywords: ['寰湇鍔?, 'Nacos', 'Gateway']})
MERGE (springai:Skill {name: 'Spring AI', level: 4, description: 'Spring AI 妗嗘灦', keywords: ['LLM', 'Embedding', 'RAG']})
MERGE (mybatis:Skill {name: 'MyBatis', level: 3, description: 'MyBatis ORM 妗嗘灦', keywords: ['ORM', 'Mapper', 'SQL']})
MERGE (jpa:Skill {name: 'JPA', level: 3, description: 'Java Persistence API', keywords: ['Hibernate', 'ORM']})
MERGE (jvm:Skill {name: 'JVM 璋冧紭', level: 4, description: 'JVM 鎬ц兘璋冧紭', keywords: ['GC', '鍐呭瓨妯″瀷', '鎬ц兘浼樺寲']})
MERGE (concurrent:Skill {name: 'Java 骞跺彂缂栫▼', level: 4, description: 'Java 澶氱嚎绋嬩笌骞跺彂', keywords: ['澶氱嚎绋?, '閿?, '绾跨▼姹?]})

// Python 鐢熸€?MERGE (python:Skill {name: 'Python', level: 2, description: 'Python 缂栫▼璇█', keywords: ['Python3', 'PEP']})
MERGE (django:Skill {name: 'Django', level: 3, description: 'Django Web 妗嗘灦', keywords: ['MTV', 'ORM']})
MERGE (flask:Skill {name: 'Flask', level: 3, description: 'Flask 杞婚噺绾ф鏋?, keywords: ['寰鏋?, 'WSGI']})
MERGE (fastapi:Skill {name: 'FastAPI', level: 3, description: 'FastAPI 寮傛妗嗘灦', keywords: ['寮傛', 'OpenAPI']})

// Go 鐢熸€?MERGE (golang:Skill {name: 'Go', level: 2, description: 'Go 缂栫▼璇█', keywords: ['Golang', '鍗忕▼']})
MERGE (gin:Skill {name: 'Gin', level: 3, description: 'Gin Web 妗嗘灦', keywords: ['HTTP', '涓棿浠?]})

// Node.js 鐢熸€?MERGE (nodejs:Skill {name: 'Node.js', level: 2, description: 'Node.js 杩愯鏃?, keywords: ['V8', 'NPM', '浜嬩欢椹卞姩']})
MERGE (express:Skill {name: 'Express', level: 3, description: 'Express 妗嗘灦', keywords: ['涓棿浠?, '璺敱']})
MERGE (nestjs:Skill {name: 'NestJS', level: 3, description: 'NestJS 妗嗘灦', keywords: ['TypeScript', '瑁呴グ鍣?]})

// 鍚庣鎶€鑳藉叧绯?MERGE (java)-[:REQUIRES]->(oop)
MERGE (spring)-[:REQUIRES]->(java)
MERGE (springboot)-[:REQUIRES]->(spring)
MERGE (springcloud)-[:REQUIRES]->(springboot)
MERGE (springai)-[:REQUIRES]->(springboot)
MERGE (mybatis)-[:REQUIRES]->(java)
MERGE (jpa)-[:REQUIRES]->(java)
MERGE (jvm)-[:REQUIRES]->(java)
MERGE (concurrent)-[:REQUIRES]->(java)
MERGE (django)-[:REQUIRES]->(python)
MERGE (flask)-[:REQUIRES]->(python)
MERGE (fastapi)-[:REQUIRES]->(python)
MERGE (gin)-[:REQUIRES]->(golang)
MERGE (express)-[:REQUIRES]->(nodejs)
MERGE (nestjs)-[:REQUIRES]->(nodejs)

// 鍚庣鎶€鑳藉垎绫?MERGE (java)-[:BELONGS_TO]->(c1)
MERGE (spring)-[:BELONGS_TO]->(c1)
MERGE (springboot)-[:BELONGS_TO]->(c1)
MERGE (springcloud)-[:BELONGS_TO]->(c1)
MERGE (springai)-[:BELONGS_TO]->(c1)
MERGE (mybatis)-[:BELONGS_TO]->(c1)
MERGE (jpa)-[:BELONGS_TO]->(c1)
MERGE (python)-[:BELONGS_TO]->(c1)
MERGE (django)-[:BELONGS_TO]->(c1)
MERGE (flask)-[:BELONGS_TO]->(c1)
MERGE (fastapi)-[:BELONGS_TO]->(c1)
MERGE (golang)-[:BELONGS_TO]->(c1)
MERGE (gin)-[:BELONGS_TO]->(c1)
MERGE (nodejs)-[:BELONGS_TO]->(c1)
MERGE (express)-[:BELONGS_TO]->(c1)
MERGE (nestjs)-[:BELONGS_TO]->(c1)

// ========== 鍓嶇寮€鍙戞妧鑳?==========
MERGE (html:Skill {name: 'HTML/CSS', level: 1, description: 'Web 鍩虹', keywords: ['HTML5', 'CSS3', '甯冨眬']})
MERGE (js:Skill {name: 'JavaScript', level: 2, description: 'JavaScript 璇█', keywords: ['ES6+', 'DOM', '寮傛']})
MERGE (ts:Skill {name: 'TypeScript', level: 3, description: 'TypeScript 璇█', keywords: ['绫诲瀷绯荤粺', '娉涘瀷']})
MERGE (react:Skill {name: 'React', level: 3, description: 'React 妗嗘灦', keywords: ['Hooks', 'JSX', '缁勪欢鍖?]})
MERGE (vue:Skill {name: 'Vue', level: 3, description: 'Vue 妗嗘灦', keywords: ['鍝嶅簲寮?, '缁勫悎寮廇PI']})
MERGE (angular:Skill {name: 'Angular', level: 3, description: 'Angular 妗嗘灦', keywords: ['渚濊禆娉ㄥ叆', 'RxJS']})
MERGE (nextjs:Skill {name: 'Next.js', level: 4, description: 'Next.js 妗嗘灦', keywords: ['SSR', 'SSG', 'App Router']})
MERGE (webpack:Skill {name: 'Webpack', level: 3, description: 'Webpack 鏋勫缓宸ュ叿', keywords: ['鎵撳寘', 'Loader', 'Plugin']})
MERGE (vite:Skill {name: 'Vite', level: 3, description: 'Vite 鏋勫缓宸ュ叿', keywords: ['ESM', '鐑洿鏂?]})

// 鍓嶇鎶€鑳藉叧绯?MERGE (js)-[:REQUIRES]->(html)
MERGE (ts)-[:REQUIRES]->(js)
MERGE (react)-[:REQUIRES]->(js)
MERGE (vue)-[:REQUIRES]->(js)
MERGE (angular)-[:REQUIRES]->(ts)
MERGE (nextjs)-[:REQUIRES]->(react)
MERGE (webpack)-[:REQUIRES]->(js)
MERGE (vite)-[:REQUIRES]->(js)

// 鍓嶇鎶€鑳藉垎绫?MERGE (html)-[:BELONGS_TO]->(c2)
MERGE (js)-[:BELONGS_TO]->(c2)
MERGE (ts)-[:BELONGS_TO]->(c2)
MERGE (react)-[:BELONGS_TO]->(c2)
MERGE (vue)-[:BELONGS_TO]->(c2)
MERGE (angular)-[:BELONGS_TO]->(c2)
MERGE (nextjs)-[:BELONGS_TO]->(c2)
MERGE (webpack)-[:BELONGS_TO]->(c2)
MERGE (vite)-[:BELONGS_TO]->(c2)

// ========== 鏁版嵁搴撴妧鑳?==========
MERGE (sql:Skill {name: 'SQL', level: 2, description: 'SQL 鏌ヨ璇█', keywords: ['鏌ヨ', '绱㈠紩', '浼樺寲']})
MERGE (mysql:Skill {name: 'MySQL', level: 3, description: 'MySQL 鏁版嵁搴?, keywords: ['InnoDB', '涓讳粠', '鍒嗗簱鍒嗚〃']})
MERGE (postgresql:Skill {name: 'PostgreSQL', level: 3, description: 'PostgreSQL 鏁版嵁搴?, keywords: ['JSONB', '鎵╁睍']})
MERGE (redis:Skill {name: 'Redis', level: 3, description: 'Redis 缂撳瓨', keywords: ['缂撳瓨', '鏁版嵁缁撴瀯', '闆嗙兢']})
MERGE (mongodb:Skill {name: 'MongoDB', level: 3, description: 'MongoDB 鏂囨。鏁版嵁搴?, keywords: ['NoSQL', '鏂囨。', '鑱氬悎']})
MERGE (elasticsearch:Skill {name: 'Elasticsearch', level: 3, description: 'Elasticsearch 鎼滅储寮曟搸', keywords: ['鍏ㄦ枃妫€绱?, '鍒嗚瘝', '鑱氬悎']})
MERGE (neo4j:Skill {name: 'Neo4j', level: 3, description: 'Neo4j 鍥炬暟鎹簱', keywords: ['鍥炬暟鎹簱', 'Cypher', '鐭ヨ瘑鍥捐氨']})
MERGE (milvus:Skill {name: 'Milvus', level: 3, description: 'Milvus 鍚戦噺鏁版嵁搴?, keywords: ['鍚戦噺妫€绱?, 'RAG']})

// 鏁版嵁搴撴妧鑳藉叧绯?MERGE (mysql)-[:REQUIRES]->(sql)
MERGE (postgresql)-[:REQUIRES]->(sql)

// 鏁版嵁搴撴妧鑳藉垎绫?MERGE (sql)-[:BELONGS_TO]->(c3)
MERGE (mysql)-[:BELONGS_TO]->(c3)
MERGE (postgresql)-[:BELONGS_TO]->(c3)
MERGE (redis)-[:BELONGS_TO]->(c3)
MERGE (mongodb)-[:BELONGS_TO]->(c3)
MERGE (elasticsearch)-[:BELONGS_TO]->(c3)
MERGE (neo4j)-[:BELONGS_TO]->(c3)
MERGE (milvus)-[:BELONGS_TO]->(c3)

// ========== DevOps 鎶€鑳?==========
MERGE (linux:Skill {name: 'Linux', level: 2, description: 'Linux 鎿嶄綔绯荤粺', keywords: ['Shell', '鍛戒护琛?]})
MERGE (docker:Skill {name: 'Docker', level: 3, description: 'Docker 瀹瑰櫒', keywords: ['瀹瑰櫒', '闀滃儚', 'Compose']})
MERGE (k8s:Skill {name: 'Kubernetes', level: 4, description: 'Kubernetes 瀹瑰櫒缂栨帓', keywords: ['K8s', 'Pod', 'Service']})
MERGE (jenkins:Skill {name: 'Jenkins', level: 3, description: 'Jenkins CI/CD', keywords: ['Pipeline', '鑷姩鍖?]})
MERGE (git:Skill {name: 'Git', level: 2, description: 'Git 鐗堟湰鎺у埗', keywords: ['鍒嗘敮', '鍚堝苟', 'GitHub']})
MERGE (nginx:Skill {name: 'Nginx', level: 3, description: 'Nginx 鏈嶅姟鍣?, keywords: ['鍙嶅悜浠ｇ悊', '璐熻浇鍧囪　']})

// DevOps 鎶€鑳藉叧绯?MERGE (docker)-[:REQUIRES]->(linux)
MERGE (k8s)-[:REQUIRES]->(docker)

// DevOps 鎶€鑳藉垎绫?MERGE (linux)-[:BELONGS_TO]->(c4)
MERGE (docker)-[:BELONGS_TO]->(c4)
MERGE (k8s)-[:BELONGS_TO]->(c4)
MERGE (jenkins)-[:BELONGS_TO]->(c4)
MERGE (git)-[:BELONGS_TO]->(c4)
MERGE (nginx)-[:BELONGS_TO]->(c4)

// ========== AI 鎶€鑳?==========
MERGE (ml:Skill {name: '鏈哄櫒瀛︿範', level: 3, description: '鏈哄櫒瀛︿範鍩虹', keywords: ['ML', '鐩戠潱瀛︿範', '鏃犵洃鐫ｅ涔?]})
MERGE (dl:Skill {name: '娣卞害瀛︿範', level: 4, description: '娣卞害瀛︿範', keywords: ['绁炵粡缃戠粶', 'CNN', 'RNN']})
MERGE (pytorch:Skill {name: 'PyTorch', level: 3, description: 'PyTorch 妗嗘灦', keywords: ['寮犻噺', '鑷姩寰垎']})
MERGE (tensorflow:Skill {name: 'TensorFlow', level: 3, description: 'TensorFlow 妗嗘灦', keywords: ['Keras', '妯″瀷']})
MERGE (nlp:Skill {name: 'NLP', level: 4, description: '鑷劧璇█澶勭悊', keywords: ['鏂囨湰澶勭悊', '璇箟鐞嗚В']})
MERGE (cv:Skill {name: '璁＄畻鏈鸿瑙?, level: 4, description: '璁＄畻鏈鸿瑙?, keywords: ['鍥惧儚澶勭悊', '鐩爣妫€娴?]})
MERGE (llm:Skill {name: '澶ц瑷€妯″瀷', level: 4, description: 'LLM 澶ц瑷€妯″瀷', keywords: ['GPT', 'Prompt', '寰皟']})
MERGE (rag:Skill {name: 'RAG', level: 4, description: '妫€绱㈠寮虹敓鎴?, keywords: ['鍚戦噺妫€绱?, '鐭ヨ瘑搴?]})
MERGE (langchain:Skill {name: 'LangChain', level: 4, description: 'LangChain 妗嗘灦', keywords: ['Agent', 'Chain']})
MERGE (embedding:Skill {name: 'Embedding', level: 3, description: '鏂囨湰鍚戦噺鍖?, keywords: ['璇嶅悜閲?, '璇箟琛ㄧず']})

// AI 鎶€鑳藉叧绯?MERGE (dl)-[:REQUIRES]->(ml)
MERGE (pytorch)-[:REQUIRES]->(python)
MERGE (pytorch)-[:REQUIRES]->(dl)
MERGE (tensorflow)-[:REQUIRES]->(python)
MERGE (tensorflow)-[:REQUIRES]->(dl)
MERGE (nlp)-[:REQUIRES]->(dl)
MERGE (cv)-[:REQUIRES]->(dl)
MERGE (llm)-[:REQUIRES]->(nlp)
MERGE (rag)-[:REQUIRES]->(llm)
MERGE (rag)-[:REQUIRES]->(embedding)
MERGE (langchain)-[:REQUIRES]->(llm)
MERGE (springai)-[:RELATED_TO]->(rag)
MERGE (springai)-[:RELATED_TO]->(llm)
MERGE (milvus)-[:RELATED_TO]->(rag)
MERGE (neo4j)-[:RELATED_TO]->(rag)

// AI 鎶€鑳藉垎绫?MERGE (ml)-[:BELONGS_TO]->(c5)
MERGE (dl)-[:BELONGS_TO]->(c5)
MERGE (pytorch)-[:BELONGS_TO]->(c5)
MERGE (tensorflow)-[:BELONGS_TO]->(c5)
MERGE (nlp)-[:BELONGS_TO]->(c5)
MERGE (cv)-[:BELONGS_TO]->(c5)
MERGE (llm)-[:BELONGS_TO]->(c5)
MERGE (rag)-[:BELONGS_TO]->(c5)
MERGE (langchain)-[:BELONGS_TO]->(c5)
MERGE (embedding)-[:BELONGS_TO]->(c5)

// ========== 娴嬭瘯鎶€鑳?==========
MERGE (functest:Skill {name: '鍔熻兘娴嬭瘯', level: 2, description: '鍔熻兘娴嬭瘯', keywords: ['娴嬭瘯鐢ㄤ緥', '缂洪櫡']})
MERGE (autotest:Skill {name: '鑷姩鍖栨祴璇?, level: 3, description: '鑷姩鍖栨祴璇?, keywords: ['鑴氭湰', '妗嗘灦']})
MERGE (perftest:Skill {name: '鎬ц兘娴嬭瘯', level: 3, description: '鎬ц兘娴嬭瘯', keywords: ['鍘嬫祴', 'JMeter']})
MERGE (junit:Skill {name: 'JUnit', level: 3, description: 'JUnit 娴嬭瘯妗嗘灦', keywords: ['鍗曞厓娴嬭瘯', '鏂█']})
MERGE (selenium:Skill {name: 'Selenium', level: 3, description: 'Selenium UI娴嬭瘯', keywords: ['Web娴嬭瘯', '鍏冪礌瀹氫綅']})
MERGE (pytest:Skill {name: 'Pytest', level: 3, description: 'Pytest 娴嬭瘯妗嗘灦', keywords: ['Python娴嬭瘯', 'fixture']})

// 娴嬭瘯鎶€鑳藉叧绯?MERGE (autotest)-[:REQUIRES]->(functest)
MERGE (junit)-[:REQUIRES]->(java)
MERGE (selenium)-[:REQUIRES]->(autotest)
MERGE (pytest)-[:REQUIRES]->(python)

// 娴嬭瘯鎶€鑳藉垎绫?MERGE (functest)-[:BELONGS_TO]->(c6)
MERGE (autotest)-[:BELONGS_TO]->(c6)
MERGE (perftest)-[:BELONGS_TO]->(c6)
MERGE (junit)-[:BELONGS_TO]->(c6)
MERGE (selenium)-[:BELONGS_TO]->(c6)
MERGE (pytest)-[:BELONGS_TO]->(c6)

// ========== 椤圭洰绠＄悊鎶€鑳?==========
MERGE (scrum:Skill {name: 'Scrum', level: 2, description: 'Scrum 鏁忔嵎鏂规硶', keywords: ['Sprint', '杩唬']})
MERGE (agile:Skill {name: '鏁忔嵎寮€鍙?, level: 2, description: '鏁忔嵎寮€鍙戞柟娉曡', keywords: ['Agile', '杩唬']})
MERGE (jira:Skill {name: 'JIRA', level: 2, description: 'JIRA 椤圭洰绠＄悊宸ュ叿', keywords: ['浠诲姟绠＄悊', '鐪嬫澘']})
MERGE (requirement:Skill {name: '闇€姹傚垎鏋?, level: 3, description: '闇€姹傚垎鏋愯兘鍔?, keywords: ['PRD', '鐢ㄤ緥']})
MERGE (risk:Skill {name: '椋庨櫓绠＄悊', level: 3, description: '椋庨櫓绠＄悊', keywords: ['璇嗗埆', '搴斿']})

// 椤圭洰绠＄悊鎶€鑳藉叧绯?MERGE (scrum)-[:REQUIRES]->(agile)

// 椤圭洰绠＄悊鎶€鑳藉垎绫?MERGE (scrum)-[:BELONGS_TO]->(c7)
MERGE (agile)-[:BELONGS_TO]->(c7)
MERGE (jira)-[:BELONGS_TO]->(c7)
MERGE (requirement)-[:BELONGS_TO]->(c7)
MERGE (risk)-[:BELONGS_TO]->(c7)

// ========== 閫氱敤鑳藉姏 ==========
MERGE (comm:Skill {name: '娌熼€氳兘鍔?, level: 1, description: '娌熼€氳〃杈捐兘鍔?, keywords: ['琛ㄨ揪', '鍊惧惉']})
MERGE (team:Skill {name: '鍥㈤槦鍗忎綔', level: 1, description: '鍥㈤槦鍗忎綔鑳藉姏', keywords: ['閰嶅悎', '鍗忚皟']})
MERGE (learn:Skill {name: '瀛︿範鑳藉姏', level: 1, description: '鎸佺画瀛︿範鑳藉姏', keywords: ['鑷', '鎴愰暱']})
MERGE (problem:Skill {name: '闂瑙ｅ喅', level: 2, description: '闂鍒嗘瀽瑙ｅ喅鑳藉姏', keywords: ['鍒嗘瀽', '鏂规']})
MERGE (logic:Skill {name: '閫昏緫鎬濈淮', level: 2, description: '閫昏緫鎬濈淮鑳藉姏', keywords: ['鎺ㄧ悊', '鍒嗘瀽']})

// 閫氱敤鑳藉姏鍒嗙被
MERGE (comm)-[:BELONGS_TO]->(c8)
MERGE (team)-[:BELONGS_TO]->(c8)
MERGE (learn)-[:BELONGS_TO]->(c8)
MERGE (problem)-[:BELONGS_TO]->(c8)
MERGE (logic)-[:BELONGS_TO]->(c8)

// 杈撳嚭缁熻


