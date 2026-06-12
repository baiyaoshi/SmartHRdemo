import { useEffect, useState } from 'react'
import PositionsPage from './pages/PositionsPage'
import ResumesPage from './pages/ResumesPage'
import MatchPage from './pages/MatchPage'
import InterviewPage from './pages/InterviewPage'
import GraphPage from './pages/GraphPage'

const API_BASE = '/api'

function App() {
  const [health, setHealth] = useState('检查中...')
  const [page, setPage] = useState('home')

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(r => r.json())
      .then(d => setHealth(d.status))
      .catch(() => setHealth('连接失败'))
  }, [])

  const NavButton = ({ to, label }: { to: string; label: string }) => (
    <button onClick={() => setPage(to)} style={{
      background: page === to ? 'rgba(255,255,255,0.15)' : 'transparent',
      border: 'none', color: '#fff', padding: '8px 16px', borderRadius: 8,
      cursor: 'pointer', fontSize: 13, fontWeight: page === to ? 600 : 400,
    }}>{label}</button>
  )

  if (page === 'positions') {
    return <PositionsPage onBack={() => setPage('home')} />
  }
  if (page === 'resumes') {
    return <ResumesPage onBack={() => setPage('home')} />
  }
  if (page === 'match') {
    return <MatchPage onBack={() => setPage('home')} />
  }
  if (page === 'interview') {
    return <InterviewPage onBack={() => setPage('home')} />
  }
  if (page === 'graph') {
    return <GraphPage onBack={() => setPage('home')} />
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5', fontFamily: '-apple-system, sans-serif' }}>
      <header style={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        padding: '16px 40px', display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', color: '#fff',
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <span style={{ fontSize: 20 }}>🤖</span>
          <span style={{ fontSize: 16, fontWeight: 600 }}>Smart-HR</span>
          <NavButton to="home" label="首页" />
          <NavButton to="positions" label="岗位管理" />
          <NavButton to="graph" label="知识图谱" />
        </div>
        <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            fontSize: 13, color: health === 'ok' ? '#52c41a' : '#ff4d4f'
          }}>
            <span style={{
              width: 8, height: 8, borderRadius: '50%',
              background: health === 'ok' ? '#52c41a' : '#ff4d4f',
              display: 'inline-block'
            }} />
            {health === 'ok' ? '服务正常' : health}
          </span>
        </div>
      </header>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 20px' }}>
        <h2 style={{ fontSize: 22, color: '#1a1a2e', marginBottom: 24 }}>功能导航</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20 }}>
          {[
            { icon: '📋', title: '岗位管理', key: 'positions', desc: '查看、新增、编辑岗位信息' },
            { icon: '📄', title: '简历管理', key: 'resumes', desc: '上传简历，自动解析提取技能' },
            { icon: '🎯', title: '智能匹配', key: 'match', desc: '基于知识图谱+AI的人岗匹配' },
            { icon: '❓', title: '面试题生成', key: 'interview', desc: 'RAG+AI 生成定制面试题' },
            { icon: '🧠', title: '知识图谱', key: 'graph', desc: '技能图谱可视化查看与编辑' },
          ].map(card => (
            <div key={card.key} onClick={() => setPage(card.key)}
              style={{
                background: '#fff', borderRadius: 12, padding: 24,
                boxShadow: '0 2px 8px rgba(0,0,0,0.06)', cursor: 'pointer',
                border: '1px solid #e8e8e8',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.12)'; e.currentTarget.style.transform = 'translateY(-2px)' }}
              onMouseLeave={e => { e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)'; e.currentTarget.style.transform = 'none' }}
            >
              <div style={{ fontSize: 36, marginBottom: 12 }}>{card.icon}</div>
              <h3 style={{ margin: '0 0 8px', fontSize: 16, color: '#1a1a2e' }}>{card.title}</h3>
              <p style={{ margin: 0, fontSize: 13, color: '#666', lineHeight: 1.6 }}>{card.desc}</p>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 40, padding: '20px 0', borderTop: '1px solid #e8e8e8', textAlign: 'center', fontSize: 13, color: '#999' }}>
          Smart-HR v1.0
        </div>
      </div>
    </div>
  )
}

export default App
