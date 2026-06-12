import { useEffect, useState } from 'react'

const API = '/api/hr/resumes'
const POS_API = '/api/hr/positions'
const MATCH_API = '/api/hr/match'

interface Resume {
  id: number
  file_name: string
  content_preview: string
  extracted_skills: string[]
  created_at: string
}

interface MatchResult {
  position_id: number
  position_title: string
  company: string
  salary_range: string
  final_score: number
  graph_score: number
  llm_score: number
  match_grade: string
  recommend_level: number
  matched_skills: string[]
  missing_skills: string[]
}

interface MatchResponse {
  resume_id: number
  file_name: string
  skills: string[]
  total_positions: number
  results: MatchResult[]
}

interface Position {
  id: number
  title: string
  company: string
  salary_range: string
}

export default function ResumesPage({ onBack }: { onBack: () => void }) {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [matchResult, setMatchResult] = useState<MatchResponse | null>(null)
  const [positions, setPositions] = useState<Position[]>([])

  // 单个匹配弹窗
  const [matchModal, setMatchModal] = useState<{ resumeId: number; fileName: string } | null>(null)
  const [selectedPosId, setSelectedPosId] = useState<number | ''>('')
  const [singleMatching, setSingleMatching] = useState(false)
  const [singleResult, setSingleResult] = useState<any>(null)

  const loadResumes = () => {
    fetch(`${API}?page=0&size=50`)
      .then(r => r.json())
      .then(data => {
        setResumes(data.items || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => { loadResumes() }, [])

  // 仅上传简历
  const handleUploadOnly = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    const form = new FormData()
    form.append('file', file)
    try {
      await fetch(`${API}/upload`, { method: 'POST', body: form })
      loadResumes()
    } catch { }
    setUploading(false)
    // 清空 input 以便再次选择同一文件
    e.target.value = ''
  }

  // 上传并匹配所有岗位
  const handleUploadAndMatch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setMatchResult(null)
    const form = new FormData()
    form.append('file', file)
    try {
      const r = await fetch(`${API}/upload-and-match`, { method: 'POST', body: form })
      if (r.ok) {
        const data: MatchResponse = await r.json()
        setMatchResult(data)
        loadResumes()
      }
    } catch { }
    setUploading(false)
    e.target.value = ''
  }

  // 打开匹配弹窗
  const openMatchModal = async (resumeId: number, fileName: string) => {
    setMatchModal({ resumeId, fileName })
    setSelectedPosId('')
    setSingleResult(null)
    // 加载岗位列表
    const r = await fetch(`${POS_API}/all`)
    const d = await r.json()
    setPositions(Array.isArray(d) ? d : [])
  }

  // 执行单个匹配
  const handleSingleMatch = async () => {
    if (!matchModal || !selectedPosId) return
    setSingleMatching(true)
    setSingleResult(null)
    try {
      const r = await fetch(`${MATCH_API}/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_id: matchModal.resumeId, position_id: selectedPosId }),
      })
      if (r.ok) {
        setSingleResult(await r.json())
      }
    } catch { }
    setSingleMatching(false)
  }

  const getGradeColor = (g: string) => {
    if (g === 'A') return '#52c41a'
    if (g === 'B') return '#1890ff'
    if (g === 'C') return '#faad14'
    if (g === 'D') return '#ff4d4f'
    return '#999'
  }

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
          <span style={{ fontSize: 16, fontWeight: 600 }}>简历管理</span>
          <span style={{ fontSize: 13, opacity: 0.7 }}>共 {resumes.length} 份</span>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          {/* 仅上传 */}
          <label style={{
            background: '#1890ff', color: '#fff', padding: '8px 20px',
            borderRadius: 8, cursor: uploading ? 'not-allowed' : 'pointer',
            fontSize: 13, fontWeight: 600, opacity: uploading ? 0.6 : 1,
          }}>
            {uploading ? '上传中...' : '+ 上传简历'}
            <input type="file" accept=".pdf,.docx,.txt" onChange={handleUploadOnly}
              style={{ display: 'none' }} disabled={uploading} />
          </label>
          {/* 上传并匹配 */}
          <label style={{
            background: '#f26b38', color: '#fff', padding: '8px 20px',
            borderRadius: 8, cursor: uploading ? 'not-allowed' : 'pointer',
            fontSize: 13, fontWeight: 600, opacity: uploading ? 0.6 : 1,
          }}>
            {uploading ? '匹配中...' : '+ 上传并匹配全部'}
            <input type="file" accept=".pdf,.docx,.txt" onChange={handleUploadAndMatch}
              style={{ display: 'none' }} disabled={uploading} />
          </label>
        </div>
      </header>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: 24 }}>
        {/* 上传并匹配的结果 */}
        {matchResult && (
          <div style={{ background: '#fff', borderRadius: 12, padding: 24, marginBottom: 24, boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <div style={{ fontSize: 15, fontWeight: 600, color: '#1a1a2e' }}>
                匹配结果：{matchResult.file_name}
              </div>
              <button onClick={() => setMatchResult(null)} style={{
                background: 'transparent', border: 'none', color: '#999', cursor: 'pointer', fontSize: 18
              }}>✕</button>
            </div>
            <div style={{ fontSize: 13, color: '#666', marginBottom: 16 }}>
              共匹配 {matchResult.total_positions} 个岗位
              <span style={{ marginLeft: 12, color: '#999' }}>提取技能：{matchResult.skills?.join(', ')}</span>
            </div>
            <div style={{ display: 'grid', gap: 12 }}>
              {matchResult.results?.map(r => (
                <div key={r.position_id} style={{
                  display: 'flex', alignItems: 'center', gap: 16,
                  padding: '12px 16px', borderRadius: 10,
                  border: '1px solid #e8e8e8',
                }}>
                  <div style={{ textAlign: 'center', minWidth: 60 }}>
                    <div style={{ fontSize: 24, fontWeight: 700, color: getGradeColor(r.match_grade) }}>{r.final_score}</div>
                    <div style={{
                      fontSize: 11, fontWeight: 600, marginTop: 2,
                      color: '#fff', background: getGradeColor(r.match_grade),
                      borderRadius: 8, padding: '0 8px', display: 'inline-block',
                    }}>{r.match_grade}</div>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: '#1a1a2e' }}>{r.position_title}</div>
                    <div style={{ fontSize: 12, color: '#999' }}>{r.company} | {r.salary_range}</div>
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 4 }}>
                      {r.matched_skills?.slice(0, 5).map(s => (
                        <span key={s} style={{ fontSize: 11, background: '#f6ffed', color: '#52c41a', padding: '1px 8px', borderRadius: 8 }}>{s}</span>
                      ))}
                      {r.missing_skills?.slice(0, 3).map(s => (
                        <span key={s} style={{ fontSize: 11, background: '#fff2f0', color: '#ff4d4f', padding: '1px 8px', borderRadius: 8 }}>缺{s}</span>
                      ))}
                    </div>
                  </div>
                  <div style={{ fontSize: 12, color: '#999', textAlign: 'right', minWidth: 60 }}>
                    <div>图谱 {r.graph_score}</div>
                    <div>AI {r.llm_score}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {loading ? (
          <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>加载中...</div>
        ) : resumes.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 60, color: '#999' }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>📄</div>
            <div>暂无简历，点击左上角上传</div>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: 16 }}>
            {resumes.map(r => (
              <div key={r.id} style={{
                background: '#fff', borderRadius: 12, padding: 20,
                boxShadow: '0 1px 4px rgba(0,0,0,0.06)', border: '1px solid #e8e8e8',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: 15, color: '#1a1a2e' }}>📄 {r.file_name}</h3>
                    <span style={{ fontSize: 12, color: '#999' }}>
                      {new Date(r.created_at).toLocaleString('zh-CN')}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button onClick={() => openMatchModal(r.id, r.file_name)} style={{
                      background: '#f26b38', color: '#fff', border: 'none',
                      padding: '4px 14px', borderRadius: 6, cursor: 'pointer', fontSize: 12, fontWeight: 600,
                    }}>🎯 匹配</button>
                    <button onClick={async () => {
                      if (!confirm('确认删除？')) return
                      await fetch(`${API}/${r.id}`, { method: 'DELETE' })
                      loadResumes()
                    }} style={{
                      background: 'transparent', border: '1px solid #ff4d4f', color: '#ff4d4f',
                      padding: '4px 12px', borderRadius: 6, cursor: 'pointer', fontSize: 12,
                    }}>删除</button>
                  </div>
                </div>
                <div style={{ fontSize: 13, color: '#666', lineHeight: 1.6, marginBottom: 10, maxHeight: 60, overflow: 'hidden' }}>
                  {r.content_preview || '（暂无内容预览）'}
                </div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {(r.extracted_skills || []).map(s => (
                    <span key={s} style={{
                      background: 'rgba(82,196,26,0.1)', color: '#52c41a',
                      padding: '2px 10px', borderRadius: 12, fontSize: 12,
                    }}>✓ {s}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 匹配弹窗 */}
      {matchModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000,
        }} onClick={() => setMatchModal(null)}>
          <div style={{
            background: '#fff', borderRadius: 12, padding: 24, width: 560,
            maxHeight: '80vh', overflow: 'auto', boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
          }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ margin: 0, fontSize: 16, color: '#1a1a2e' }}>🎯 匹配岗位 — {matchModal.fileName}</h3>
              <button onClick={() => setMatchModal(null)} style={{
                background: 'transparent', border: 'none', fontSize: 20, cursor: 'pointer', color: '#999'
              }}>✕</button>
            </div>

            {/* 选择岗位 */}
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 13, color: '#666', marginBottom: 6, display: 'block' }}>选择岗位</label>
              <select value={selectedPosId} onChange={e => setSelectedPosId(Number(e.target.value) || '')}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14 }}>
                <option value="">请选择岗位</option>
                {positions.map(p => <option key={p.id} value={p.id}>{p.title} - {p.company} ({p.salary_range})</option>)}
              </select>
            </div>

            <button onClick={handleSingleMatch} disabled={singleMatching || !selectedPosId} style={{
              width: '100%', background: '#f26b38', color: '#fff', border: 'none',
              padding: '10px', borderRadius: 8, fontSize: 15, fontWeight: 600,
              cursor: singleMatching ? 'not-allowed' : 'pointer', opacity: singleMatching || !selectedPosId ? 0.6 : 1,
              marginBottom: 16,
            }}>{singleMatching ? '匹配中...' : '开始匹配'}</button>

            {/* 匹配结果 */}
            {singleResult && (
              <div>
                <div style={{ textAlign: 'center', marginBottom: 16 }}>
                  <div style={{ fontSize: 13, color: '#999', marginBottom: 4 }}>综合匹配度</div>
                  <div style={{
                    width: 80, height: 80, borderRadius: '50%', margin: '0 auto',
                    background: `conic-gradient(${getGradeColor(singleResult.match_grade)} ${singleResult.final_score}%, #f0f0f0 0)`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 22, fontWeight: 700, color: '#1a1a2e',
                  }}>{singleResult.final_score}</div>
                  <div style={{ marginTop: 4 }}>
                    <span style={{
                      background: `${getGradeColor(singleResult.match_grade)}20`,
                      color: getGradeColor(singleResult.match_grade),
                      padding: '2px 12px', borderRadius: 12, fontSize: 13, fontWeight: 600,
                    }}>等级 {singleResult.match_grade}</span>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                  <div style={{ textAlign: 'center', padding: 10, background: '#fafafa', borderRadius: 8 }}>
                    <div style={{ fontSize: 12, color: '#999' }}>图谱匹配</div>
                    <div style={{ fontSize: 18, fontWeight: 600, color: '#1a1a2e' }}>{singleResult.graph_score}</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: 10, background: '#fafafa', borderRadius: 8 }}>
                    <div style={{ fontSize: 12, color: '#999' }}>AI 评估</div>
                    <div style={{ fontSize: 18, fontWeight: 600, color: '#1a1a2e' }}>{singleResult.llm_score}</div>
                  </div>
                </div>

                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8, color: '#1a1a2e' }}>技能详情</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {singleResult.matched_skills?.length > 0 && (
                      <div>
                        <span style={{ fontSize: 12, color: '#52c41a' }}>✅ 已匹配 ({singleResult.matched_skills.length}) </span>
                        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 4 }}>
                          {singleResult.matched_skills.map((s: string) => <span key={s} style={{ background: '#f6ffed', color: '#52c41a', padding: '1px 8px', borderRadius: 8, fontSize: 11 }}>{s}</span>)}
                        </div>
                      </div>
                    )}
                    {singleResult.missing_skills?.length > 0 && (
                      <div>
                        <span style={{ fontSize: 12, color: '#ff4d4f' }}>❌ 缺失 ({singleResult.missing_skills.length}) </span>
                        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 4 }}>
                          {singleResult.missing_skills.map((s: string) => <span key={s} style={{ background: '#fff2f0', color: '#ff4d4f', padding: '1px 8px', borderRadius: 8, fontSize: 11 }}>{s}</span>)}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {singleResult.llm_report && (
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4, color: '#1a1a2e' }}>AI 分析</div>
                    <div style={{ fontSize: 12, color: '#666', lineHeight: 1.6, whiteSpace: 'pre-wrap', background: '#fafafa', padding: 12, borderRadius: 8 }}>
                      {singleResult.llm_report}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
