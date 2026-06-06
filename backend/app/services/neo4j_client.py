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


# 全局单例
neo4j_client = Neo4jClient()