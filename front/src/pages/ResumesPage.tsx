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
  llm_report: string
}

interface MatchResponse {
  resume_id: number
  file_name: string
  skills: string[]
  total_positions: number
  results: MatchResult[]
}



export default function ResumesPage({ onBack }: { onBack: () => void }) {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [matchResult, setMatchResult] = useState<MatchResponse | null>(null)
  const [matchingResumeId, setMatchingResumeId] = useState<number | null>(null)
  const [expandedReport, setExpandedReport] = useState<number | null>(null)

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

  // 匹配简历与所有岗位（调后端批量接口）
  const handleMatchResume = async (resumeId: number) => {
    setMatchingResumeId(resumeId)
    setMatchResult(null)
    try {
      const r = await fetch(`/api/hr/batch-match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_id: resumeId }),
      })
      if (r.ok) {
        setMatchResult(await r.json())
      }
    } catch { }
    setMatchingResumeId(null)
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
                <div key={r.position_id}>
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: 16,
                    padding: '12px 16px', borderRadius: 10,
                    border: '1px solid #e8e8e8', cursor: 'pointer',
                  }} onClick={() => setExpandedReport(expandedReport === r.position_id ? null : r.position_id)}>
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
                    <div style={{ fontSize: 20, color: '#ccc', marginLeft: 4 }}>
                      {expandedReport === r.position_id ? '▲' : '▼'}
                    </div>
                  </div>
                  {expandedReport === r.position_id && r.llm_report && (
                    <div style={{
                      marginTop: -1, padding: '16px 20px', borderRadius: '0 0 10px 10px',
                      border: '1px solid #e8e8e8', borderTop: 'none', background: '#fafafa',
                      fontSize: 13, color: '#555', lineHeight: 1.8, whiteSpace: 'pre-wrap',
                    }}>
                      {r.llm_report}
                    </div>
                  )}
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
                    <button onClick={() => handleMatchResume(r.id)} disabled={matchingResumeId === r.id} style={{
                      background: '#f26b38', color: '#fff', border: 'none',
                      padding: '4px 14px', borderRadius: 6, cursor: matchingResumeId === r.id ? 'not-allowed' : 'pointer',
                      fontSize: 12, fontWeight: 600, opacity: matchingResumeId === r.id ? 0.6 : 1,
                    }}>{matchingResumeId === r.id ? '匹配中...' : '🎯 匹配全部'}</button>
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


    </div>
  )
}
