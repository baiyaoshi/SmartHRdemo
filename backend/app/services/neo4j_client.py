# -*- coding: utf-8 -*-
"""Neo4j 图数据库客户端"""
import os
from neo4j import GraphDatabase


class Neo4jClient:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "neo4j123")
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def get_all_skills(self):
        with self._driver.session() as session:
            result = session.run(
                "MATCH (s:Skill) RETURN s.name AS name, s.level AS level, "
                "s.description AS description, s.keywords AS keywords "
                "ORDER BY s.name"
            )
            return [dict(r) for r in result]

    def find_skill_by_name(self, name: str):
        with self._driver.session() as session:
            result = session.run(
                "MATCH (s:Skill) WHERE s.name = $name RETURN s", name=name
            )
            record = result.single()
            return dict(record["s"]) if record else None

    def search_skills(self, keyword: str):
        with self._driver.session() as session:
            result = session.run(
                "MATCH (s:Skill) WHERE s.name CONTAINS $kw "
                "OR ANY(k IN s.keywords WHERE k CONTAINS $kw) "
                "RETURN s.name AS name, s.level AS level, s.description AS description "
                "ORDER BY s.name LIMIT 20",
                kw=keyword,
            )
            return [dict(r) for r in result]

    def match_skills_from_text(self, content: str) -> list[dict]:
        matched = []
        all_skills = self.get_all_skills()
        lower_content = content.lower()

        for skill in all_skills:
            name = skill["name"].lower()
            keywords = skill.get("keywords") or []

            if name in lower_content:
                matched.append({**skill, "match_type": "exact", "score": 1.0})
                continue

            for kw in keywords:
                if kw.lower() in lower_content:
                    matched.append({**skill, "match_type": "keyword", "score": 0.8})
                    break

        return matched

    def get_prerequisite_skills(self, skill_name: str):
        with self._driver.session() as session:
            result = session.run(
                "MATCH (s:Skill)-[:REQUIRES]->(pre:Skill) "
                "WHERE s.name = $name RETURN pre.name AS name, pre.level AS level",
                name=skill_name,
            )
            return [dict(r) for r in result]

    def get_related_skills(self, skill_name: str):
        with self._driver.session() as session:
            result = session.run(
                "MATCH (s:Skill)-[:RELATED_TO]->(rel:Skill) "
                "WHERE s.name = $name RETURN rel.name AS name, rel.level AS level",
                name=skill_name,
            )
            return [dict(r) for r in result]

    def check_skill_requirement(self, required_skill: str, candidate_skills: list[str]):
        if required_skill in candidate_skills:
            return 0

        with self._driver.session() as session:
            for candidate in candidate_skills:
                result = session.run(
                    "MATCH path = shortestPath("
                    "(c:Skill {name: $candidate})-[:REQUIRES*]->(r:Skill {name: $required})"
                    ") RETURN length(path) AS distance",
                    candidate=candidate, required=required_skill,
                )
                record = result.single()
                if record:
                    return record["distance"] + 1

            for candidate in candidate_skills:
                result = session.run(
                    "MATCH (c:Skill {name: $candidate})-[:RELATED_TO]-(r:Skill {name: $required}) "
                    "RETURN true AS related",
                    candidate=candidate, required=required_skill,
                )
                if result.single():
                    return 3

        return None

    def calculate_match_score(self, required_skills: list[str], candidate_skills: list[str]) -> dict:
        matched = []
        missing = []
        total_score = 0.0

        for req in required_skills:
            distance = self.check_skill_requirement(req, candidate_skills)
            if distance == 0:
                matched.append(req)
                total_score += 1.0
            elif distance == 1:
                matched.append(f"{req}(前置)")
                total_score += 0.8
            elif distance == 2:
                matched.append(f"{req}(间接)")
                total_score += 0.5
            elif distance == 3:
                matched.append(f"{req}(相关)")
                total_score += 0.3
            else:
                missing.append(req)

        extra = [s for s in candidate_skills if s not in required_skills
                 and s not in [m.split("(")[0] for m in matched]]

        max_score = len(required_skills) or 1
        score = (total_score / max_score) * 100

        return {
            "matched": matched,
            "missing": missing,
            "extra": extra,
            "score": round(score, 1),
        }



    def calculate_match_score(self, required_skills: list[str], candidate_skills: list[str]) -> dict:
        matched = []
        missing = []
        total_score = 0.0

        for req in required_skills:
            distance = self.check_skill_requirement(req, candidate_skills)
            if distance == 0:
                matched.append(req)
                total_score += 1.0
            elif distance == 1:
                matched.append(f"{req}(前置)")
                total_score += 0.8
            elif distance == 2:
                matched.append(f"{req}(间接)")
                total_score += 0.5
            elif distance == 3:
                matched.append(f"{req}(相关)")
                total_score += 0.3
            else:
                missing.append(req)

        extra = [s for s in candidate_skills if s not in required_skills
                 and s not in [m.split("(")[0] for m in matched]]

        max_score = len(required_skills) or 1
        score = (total_score / max_score) * 100

        return {
            "matched": matched,
            "missing": missing,
            "extra": extra,
            "score": round(score, 1),
        }

    # ==================== 知识图谱可视化 & 编辑 ====================

    def get_all_categories(self):
        """获取所有技能分类"""
        with self._driver.session() as session:
            result = session.run(
                "MATCH (c:SkillCategory) RETURN c.code AS code, c.name AS name, "
                "c.description AS description ORDER BY c.code"
            )
            return [dict(r) for r in result]

    def get_all_relations(self):
        """获取所有技能间的关系（用于前端画图）"""
        with self._driver.session() as session:
            result = session.run(
                "MATCH (s:Skill)-[r]->(t) "
                "RETURN s.name AS source, t.name AS target, type(r) AS type, "
                "s.level AS source_level, t.level AS target_level"
            )
            return [dict(r) for r in result]

    def get_advanced_skills(self, skill_name: str):
        """获取以该技能为前置的高级技能"""
        with self._driver.session() as session:
            result = session.run(
                "MATCH (s:Skill)<-[:REQUIRES]-(adv:Skill) "
                "WHERE s.name = $name RETURN adv.name AS name, adv.level AS level",
                name=skill_name,
            )
            return [dict(r) for r in result]

    def get_skill_category(self, skill_name: str):
        """获取技能所属分类"""
        with self._driver.session() as session:
            result = session.run(
                "MATCH (s:Skill)-[:BELONGS_TO]->(c:SkillCategory) "
                "WHERE s.name = $name RETURN c.code AS code, c.name AS name",
                name=skill_name,
            )
            record = result.single()
            return dict(record) if record else None

    def create_skill(self, name: str, level: int, description: str,
                     keywords: list[str], category_code: str,
                     requires: list[str], related_to: list[str]) -> dict:
        """创建技能节点并建立关系"""
        with self._driver.session() as session:
            # 创建技能节点
            session.run(
                "CREATE (s:Skill {name: $name, level: $level, "
                "description: $description, keywords: $keywords})",
                name=name, level=level, description=description, keywords=keywords,
            )

            # 关联分类
            session.run(
                "MATCH (s:Skill {name: $name}), (c:SkillCategory {code: $code}) "
                "CREATE (s)-[:BELONGS_TO]->(c)",
                name=name, code=category_code,
            )

            # 创建 REQUIRES 关系
            for req in requires:
                session.run(
                    "MATCH (s:Skill {name: $name}), (pre:Skill {name: $req}) "
                    "CREATE (s)-[:REQUIRES]->(pre)",
                    name=name, req=req,
                )

            # 创建 RELATED_TO 关系
            for rel in related_to:
                session.run(
                    "MATCH (s:Skill {name: $name}), (t:Skill {name: $rel}) "
                    "CREATE (s)-[:RELATED_TO]->(t)",
                    name=name, rel=rel,
                )

            return {"name": name, "level": level, "description": description, "keywords": keywords}

    def update_skill(self, name: str, data: dict):
        """更新技能属性"""
        sets = []
        params = {"name": name}
        for key, value in data.items():
            if key == "category_code":
                continue
            sets.append(f"s.{key} = ${key}")
            params[key] = value

        if sets:
            with self._driver.session() as session:
                session.run(
                    f"MATCH (s:Skill {{name: $name}}) SET {', '.join(sets)}",
                    **params,
                )

        # 更新分类
        if "category_code" in data:
            with self._driver.session() as session:
                session.run(
                    "MATCH (s:Skill {name: $name})-[r:BELONGS_TO]->() DELETE r",
                    name=name,
                )
                session.run(
                    "MATCH (s:Skill {name: $name}), (c:SkillCategory {code: $code}) "
                    "CREATE (s)-[:BELONGS_TO]->(c)",
                    name=name, code=data["category_code"],
                )

    def delete_skill(self, name: str):
        """删除技能节点（连带删除所有关系）"""
        with self._driver.session() as session:
            session.run(
                "MATCH (s:Skill {name: $name}) DETACH DELETE s",
                name=name,
            )


# 全局单例
neo4j_client = Neo4jClient()