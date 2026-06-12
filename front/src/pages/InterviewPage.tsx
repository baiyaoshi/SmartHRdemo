import { useEffect, useState } from 'react'

const POS_API = '/api/hr/positions'
const INTERVIEW_API = '/api/interview/questions/generate'

interface Position { id: number; title: string; skills: string[] }

interface Question {
  question: string
  answer?: string
}

export default function InterviewPage({ onBack }: { onBack: () => void }) {
  const [positions, setPositions] = useState<Position[]>([])
  const [positionId, setPositionId] = useState<number | ''>('')
  const [customSkills, setCustomSkills] = useState('')
  const [difficulty, setDifficulty] = useState('MIDDLE')
  const [count, setCount] = useState(5)
  const [hasAnswer, setHasAnswer] = useState(true)
  const [loading, setLoading] = useState(false)
  const [questions, setQuestions] = useState<Question[]>([])
  const [error, setError] = useState('')
  const [expanded, setExpanded] = useState<number[]>([])

  useEffect(() => {
    fetch(`${POS_API}/all`).then(r => r.json()).then(d => setPositions(Array.isArray(d) ? d : []))
  }, [])

  const handleGenerate = async () => {
    setLoading(true); setError(''); setQuestions([])
    const skills = positionId ? [] : customSkills.split(/[,，\s]+/).filter(Boolean)
    try {
      const r = await fetch(INTERVIEW_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          position_id: positionId || null,
          skills,
          difficulty,
          count,
          question_type: 'MIXED',
          include_answers: hasAnswer,
          business_domain: '企业金融/支付',
        }),
      })
      const data = await r.json()
      if (!r.ok) { setError(data.detail || '生成失败'); return }
      setQuestions(data.questions || [])
    } catch { setError('请求失败') }
    setLoading(false)
  }

  const toggleExpand = (i: number) => {
    setExpanded(prev => prev.includes(i) ? prev.filter(x => x !== i) : [...prev, i])
  }

  const diffLabel: Record<string, string> = { JUNIOR: '初级', MIDDLE: '中级', SENIOR: '高级' }

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
        <span style={{ fontSize: 16, fontWeight: 600 }}>面试题生成</span>
      </header>

      <div style={{ maxWidth: 900, margin: '0 auto', padding: 24 }}>
        {/* 配置区 */}
        <div style={{ background: '#fff', borderRadius: 12, padding: 24, marginBottom: 20, boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={{ fontSize: 13, color: '#666', marginBottom: 6, display: 'block' }}>选择岗位（可选）</label>
              <select value={positionId} onChange={e => setPositionId(Number(e.target.value) || '')}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14 }}>
                <option value="">自定义技能</option>
                {positions.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
              </select>
            </div>
            <div>
              <label style={{ fontSize: 13, color: '#666', marginBottom: 6, display: 'block' }}>难度</label>
              <select value={difficulty} onChange={e => setDifficulty(e.target.value)}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14 }}>
                {Object.entries(diffLabel).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
          </div>
          {!positionId && (
            <div style={{ marginTop: 12 }}>
              <label style={{ fontSize: 13, color: '#666', marginBottom: 6, display: 'block' }}>自定义技能（逗号分隔）</label>
              <input value={customSkills} onChange={e => setCustomSkills(e.target.value)}
                placeholder="例如：Java, Spring Boot, Redis, MySQL"
                style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14 }} />
            </div>
          )}
          <div style={{ display: 'flex', gap: 16, marginTop: 12, alignItems: 'center' }}>
            <div>
              <label style={{ fontSize: 13, color: '#666', marginBottom: 4, display: 'block' }}>题目数量</label>
              <input type="number" value={count} min={1} max={10}
                onChange={e => setCount(Number(e.target.value) || 5)}
                style={{ width: 80, padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14 }} />
            </div>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 24, fontSize: 13, color: '#666', cursor: 'pointer' }}>
              <input type="checkbox" checked={hasAnswer} onChange={e => setHasAnswer(e.target.checked)}
                style={{ width: 16, height: 16 }} />
              包含答案
            </label>
          </div>
          <button onClick={handleGenerate} disabled={loading} style={{
            width: '100%', marginTop: 16, background: '#f26b38', color: '#fff', border: 'none',
            padding: '10px', borderRadius: 8, fontSize: 15, fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.6 : 1,
          }}>{loading ? '生成中...' : `生成 ${count} 道面试题`}</button>
          {error && <div style={{ color: '#ff4d4f', fontSize: 13, marginTop: 8 }}>{error}</div>}
        </div>

        {/* 题目列表 */}
        {questions.length > 0 && (
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
            <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 16, color: '#1a1a2e' }}>
              共 {questions.length} 道面试题
            </div>
            {questions.map((q, i) => (
              <div key={i} style={{
                border: '1px solid #e8e8e8', borderRadius: 10, marginBottom: 12,
                overflow: 'hidden',
              }}>
                <div onClick={() => toggleExpand(i)} style={{
                  padding: '14px 16px', cursor: 'pointer', display: 'flex',
                  justifyContent: 'space-between', alignItems: 'center',
                  background: expanded.includes(i) ? '#fafafa' : '#fff',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{
                      width: 24, height: 24, borderRadius: '50%', background: '#f26b38',
                      color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 12, fontWeight: 600, flexShrink: 0,
                    }}>{i + 1}</span>
                    <span style={{ fontSize: 14, color: '#1a1a2e', lineHeight: 1.5 }}>{q.question}</span>
                  </div>
                  <span style={{ fontSize: 12, color: '#999', marginLeft: 12 }}>
                    {expanded.includes(i) ? '收起' : '查看答案'}
                  </span>
                </div>
                {expanded.includes(i) && q.answer && (
                  <div style={{ padding: '0 16px 14px 50px', fontSize: 13, color: '#666', lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>
                    {q.answer}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
