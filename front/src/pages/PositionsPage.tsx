import { useEffect, useState } from 'react'

const API = '/api/hr/positions'

interface Position {
  id: number
  title: string
  company: string
  salary_range: string
  experience: string
  education: string
  location: string
  skills: string[]
  responsibilities: string
  requirements: string
  created_at: string
}

export default function PositionsPage({ onBack }: { onBack: () => void }) {
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState<Position | null>(null)

  useEffect(() => {
    fetch(`${API}/all`)
      .then(r => r.json())
      .then(data => {
        setPositions(Array.isArray(data) ? data : data.items || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ padding: 40, textAlign: 'center' }}>加载中...</div>

  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5', fontFamily: '-apple-system, sans-serif' }}>
      <header style={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        padding: '16px 40px', display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', color: '#fff',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <button onClick={onBack} style={{
            background: 'transparent', border: '1px solid rgba(255,255,255,0.3)',
            color: '#fff', padding: '6px 16px', borderRadius: 8, cursor: 'pointer', fontSize: 13
          }}>← 返回</button>
          <span style={{ fontSize: 16, fontWeight: 600 }}>岗位管理</span>
          <span style={{ fontSize: 13, opacity: 0.7 }}>共 {positions.length} 个岗位</span>
        </div>
      </header>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: 24 }}>
        <div style={{ display: 'grid', gap: 16 }}>
          {positions.map(p => (
            <div key={p.id} style={{
              background: '#fff', borderRadius: 12, padding: 20,
              boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
              border: '1px solid #e8e8e8',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: 16, color: '#1a1a2e' }}>{p.title}</h3>
                  <span style={{ fontSize: 13, color: '#666' }}>{p.company}</span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ color: '#f26b38', fontWeight: 600, fontSize: 15 }}>{p.salary_range}</div>
                  <div style={{ fontSize: 12, color: '#999' }}>{p.experience} | {p.education}</div>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 12 }}>
                {(p.skills || []).map(s => (
                  <span key={s} style={{
                    background: 'rgba(242,107,56,0.1)', color: '#f26b38',
                    padding: '2px 10px', borderRadius: 12, fontSize: 12,
                  }}>{s}</span>
                ))}
              </div>
              <div style={{ fontSize: 13, color: '#666', lineHeight: 1.6, marginBottom: 8 }}>
                <strong>职责：</strong>{(p.responsibilities || '').slice(0, 100)}...
              </div>
              <div style={{ fontSize: 12, color: '#bbb' }}>
                {new Date(p.created_at).toLocaleDateString('zh-CN')} 创建
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
