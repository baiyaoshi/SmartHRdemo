import { useEffect, useState } from 'react'

const POS_API = '/api/hr/positions'
const RES_API = '/api/hr/resumes'
const MATCH_API = '/api/hr/match'

interface Position { id: number; title: string; company: string; salary_range: string }
interface Resume { id: number; file_name: string; extracted_skills: string[] }

interface MatchResult {
  id: number
  final_score: number
  graph_score: number
  llm_score: number
  matched_skills: string[]
  missing_skills: string[]
  extra_skills: string[]
  llm_report: string
  match_grade: string
  recommend_level: number
  position_title: string
}

export default function MatchPage({ onBack }: { onBack: () => void }) {
  const [positions, setPositions] = useState<Position[]>([])
  const [resumes, setResumes] = useState<Resume[]>([])
  const [positionId, setPositionId] = useState<number | ''>('')
  const [resumeId, setResumeId] = useState<number | ''>('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<MatchResult | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${POS_API}/all`).then(r => r.json()).then(d => setPositions(Array.isArray(d) ? d : []))
    fetch(`${RES_API}?page=0&size=50`).then(r => r.json()).then(d => setResumes(d.items || []))
  }, [])

  const handleMatch = async () => {
    if (!positionId || !resumeId) { setError('请选择岗位和简历'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const r = await fetch(`${MATCH_API}/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ position_id: positionId, resume_id: resumeId }),
      })
      const data = await r.json()
      if (!r.ok) { setError(data.detail || '匹配失败'); return }
      setResult(data)
    } catch { setError('请求失败') }
    setLoading(false)
  }

  const getGradeColor = (grade: string) => {
    if (grade === 'A') return '#52c41a'
    if (grade === 'B') return '#1890ff'
    if (grade === 'C') return '#faad14'
    return '#ff4d4f'
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5', fontFamily: '-apple-system, sans-serif' }}>
      <header style={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        padding: '16px 40px', display: 'flex', alignItems: 'center', color: '#fff',
      }}>
        <button onClick={onBack} style={{
          background: 'transparent', border: '1px solid rgba(255,255,255,0.3)',
          color: '#fff', padding: '6px 16px', borderRadius: 8, cursor: 'pointer', fontSize: 13, marginRight: 20
        }}>← 返回</button>
        <span style={{ fontSize: 16, fontWeight: 600 }}>智能匹配</span>
      </header>

      <div style={{ maxWidth: 800, margin: '0 auto', padding: 24 }}>
        {/* 选择区 */}
        <div style={{ background: '#fff', borderRadius: 12, padding: 24, marginBottom: 20, boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div>
              <label style={{ fontSize: 13, color: '#666', marginBottom: 6, display: 'block' }}>选择岗位</label>
              <select value={positionId} onChange={e => setPositionId(Number(e.target.value) || '')}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14 }}>
                <option value="">请选择</option>
                {positions.map(p => <option key={p.id} value={p.id}>{p.title} - {p.company}</option>)}
              </select>
            </div>
            <div>
              <label style={{ fontSize: 13, color: '#666', marginBottom: 6, display: 'block' }}>选择简历</label>
              <select value={resumeId} onChange={e => setResumeId(Number(e.target.value) || '')}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14 }}>
                <option value="">请选择</option>
                {resumes.map(r => <option key={r.id} value={r.id}>{r.file_name}</option>)}
              </select>
            </div>
          </div>
          <button onClick={handleMatch} disabled={loading} style={{
            width: '100%', background: '#f26b38', color: '#fff', border: 'none',
            padding: '10px', borderRadius: 8, fontSize: 15, fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.6 : 1,
          }}>{loading ? '匹配中...' : '开始匹配'}</button>
          {error && <div style={{ color: '#ff4d4f', fontSize: 13, marginTop: 8 }}>{error}</div>}
        </div>

        {/* 结果区 */}
        {result && (
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <div style={{ fontSize: 13, color: '#999', marginBottom: 8 }}>综合匹配度</div>
              <div style={{
                width: 100, height: 100, borderRadius: '50%', margin: '0 auto',
                background: `conic-gradient(${getGradeColor(result.match_grade)} ${result.final_score}%, #f0f0f0 0)`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 28, fontWeight: 700, color: '#1a1a2e',
              }}>{result.final_score}</div>
              <div style={{ marginTop: 8 }}>
                <span style={{
                  background: `${getGradeColor(result.match_grade)}20`, color: getGradeColor(result.match_grade),
                  padding: '2px 16px', borderRadius: 12, fontSize: 14, fontWeight: 600,
                }}>等级 {result.match_grade}</span>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 20 }}>
              {[
                { label: '图谱匹配', value: result.graph_score },
                { label: 'AI 评估', value: result.llm_score },
                { label: '推荐指数', value: `${result.recommend_level}/5` },
              ].map(item => (
                <div key={item.label} style={{ textAlign: 'center', padding: 12, background: '#fafafa', borderRadius: 8 }}>
                  <div style={{ fontSize: 13, color: '#999', marginBottom: 4 }}>{item.label}</div>
                  <div style={{ fontSize: 20, fontWeight: 600, color: '#1a1a2e' }}>{item.value}</div>
                </div>
              ))}
            </div>

            {/* 技能匹配 */}
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: '#1a1a2e' }}>技能匹配详情</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {result.matched_skills?.length > 0 && (
                  <div>
                    <div style={{ fontSize: 12, color: '#52c41a', marginBottom: 4 }}>✅ 已匹配 ({result.matched_skills.length})</div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {result.matched_skills.map(s => <span key={s} style={{ background: '#f6ffed', color: '#52c41a', padding: '2px 10px', borderRadius: 12, fontSize: 12 }}>{s}</span>)}
                    </div>
                  </div>
                )}
                {result.missing_skills?.length > 0 && (
                  <div>
                    <div style={{ fontSize: 12, color: '#ff4d4f', marginBottom: 4 }}>❌ 缺失 ({result.missing_skills.length})</div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {result.missing_skills.map(s => <span key={s} style={{ background: '#fff2f0', color: '#ff4d4f', padding: '2px 10px', borderRadius: 12, fontSize: 12 }}>{s}</span>)}
                    </div>
                  </div>
                )}
                {result.extra_skills?.length > 0 && (
                  <div>
                    <div style={{ fontSize: 12, color: '#1890ff', marginBottom: 4 }}>➕ 额外技能 ({result.extra_skills.length})</div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {result.extra_skills.map(s => <span key={s} style={{ background: '#e6f7ff', color: '#1890ff', padding: '2px 10px', borderRadius: 12, fontSize: 12 }}>{s}</span>)}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {result.llm_report && (
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 8, color: '#1a1a2e' }}>AI 分析报告</div>
                <div style={{ fontSize: 13, color: '#666', lineHeight: 1.8, whiteSpace: 'pre-wrap', background: '#fafafa', padding: 16, borderRadius: 8 }}>
                  {result.llm_report}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
