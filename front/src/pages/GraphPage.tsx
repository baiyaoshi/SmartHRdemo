import { useEffect, useState } from 'react'

const API = '/api/graph'

interface Skill {
  name: string
  level: number
  description: string
  keywords: string[]
}

interface Category {
  code: string
  name: string
  description: string
}

interface Relation {
  source: string
  target: string
  type: string
}

const CATEGORY_COLORS: Record<string, string> = {
  BACKEND: '#1890ff',
  FRONTEND: '#52c41a',
  DATABASE: '#faad14',
  DEVOPS: '#722ed1',
  AI: '#f26b38',
  TESTING: '#eb2f96',
  MANAGEMENT: '#13c2c2',
  GENERAL: '#8c8c8c',
}

const CATEGORY_NAMES: Record<string, string> = {
  BACKEND: '后端开发', FRONTEND: '前端开发', DATABASE: '数据库',
  DEVOPS: 'DevOps', AI: '人工智能', TESTING: '测试',
  MANAGEMENT: '项目管理', GENERAL: '通用能力',
}

export default function GraphPage({ onBack }: { onBack: () => void }) {
  const [skills, setSkills] = useState<Skill[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [relations, setRelations] = useState<Relation[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)
  const [skillDetail, setSkillDetail] = useState<any>(null)
  const [detailLoading, setDetailLoading] = useState(false)

  // 新增/编辑弹窗
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '', level: 2, description: '', keywords: '',
    category_code: 'GENERAL', requires: '', related_to: '',
  })
  const [formError, setFormError] = useState('')
  const [saving, setSaving] = useState(false)

  const loadData = async () => {
    const [s, c, r] = await Promise.all([
      fetch(`${API}/skills`).then(r => r.json()),
      fetch(`${API}/categories`).then(r => r.json()),
      fetch(`${API}/relations`).then(r => r.json()),
    ])
    setSkills(Array.isArray(s) ? s : [])
    setCategories(Array.isArray(c) ? c : [])
    setRelations(Array.isArray(r) ? r : [])
    setLoading(false)
  }

  useEffect(() => { loadData() }, [])

  const loadSkillDetail = async (name: string) => {
    setDetailLoading(true)
    try {
      const r = await fetch(`${API}/skills/${encodeURIComponent(name)}`)
      if (r.ok) setSkillDetail(await r.json())
    } catch { }
    setDetailLoading(false)
  }

  const filteredSkills = skills.filter(s => {
    if (search && !s.name.toLowerCase().includes(search.toLowerCase())
      && !(s.keywords || []).some(k => k.toLowerCase().includes(search.toLowerCase()))) return false
    if (selectedCategory) {
      // 检查分类：从 relations 中找 BELONGS_TO
      const catRel = relations.find(r => r.source === s.name && r.type === 'BELONGS_TO')
      if (!catRel) return false
      // 从 categories 匹配 code
      const cat = categories.find(c => c.code === selectedCategory)
      if (!cat) return true
      return catRel.target === selectedCategory
    }
    return true
  })

  const getSkillCategory = (skillName: string): string => {
    const rel = relations.find(r => r.source === skillName && r.type === 'BELONGS_TO')
    return rel?.target || ''
  }

  const getLevelStars = (level: number) => '⭐'.repeat(level)

  const openCreateForm = () => {
    setFormData({ name: '', level: 2, description: '', keywords: '', category_code: 'GENERAL', requires: '', related_to: '' })
    setFormError('')
    setShowForm(true)
  }

  const openEditForm = (skill: Skill) => {
    const cat = getSkillCategory(skill.name)
    const reqs = relations.filter(r => r.source === skill.name && r.type === 'REQUIRES').map(r => r.target)
    const rels = relations.filter(r => r.source === skill.name && r.type === 'RELATED_TO').map(r => r.target)
    setFormData({
      name: skill.name,
      level: skill.level,
      description: skill.description || '',
      keywords: (skill.keywords || []).join(', '),
      category_code: cat || 'GENERAL',
      requires: reqs.join(', '),
      related_to: rels.join(', '),
    })
    setFormError('')
    setShowForm(true)
  }

  const handleSave = async () => {
    if (!formData.name.trim()) { setFormError('技能名称不能为空'); return }
    setSaving(true)
    setFormError('')

    const body = {
      name: formData.name.trim(),
      level: formData.level,
      description: formData.description.trim(),
      keywords: formData.keywords.split(/[,，\s]+/).filter(Boolean),
      category_code: formData.category_code,
      requires: formData.requires.split(/[,，\s]+/).filter(Boolean),
      related_to: formData.related_to.split(/[,，\s]+/).filter(Boolean),
    }

    try {
      // 检查是否已存在（编辑模式）
      const existing = skills.find(s => s.name === body.name)
      const isEdit = !!existing

      if (isEdit) {
        // 编辑：先更新属性
        await fetch(`${API}/skills/${encodeURIComponent(body.name)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            level: body.level,
            description: body.description,
            keywords: body.keywords,
            category_code: body.category_code,
          }),
        })
      } else {
        // 新增
        const r = await fetch(`${API}/skills`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        })
        if (!r.ok) {
          const err = await r.json()
          setFormError(err.detail || '创建失败')
          setSaving(false)
          return
        }
      }

      setShowForm(false)
      await loadData()
    } catch (e: any) {
      setFormError(e.message || '保存失败')
    }
    setSaving(false)
  }

  const handleDelete = async (name: string) => {
    if (!confirm(`确认删除技能「${name}」？此操作不可恢复。`)) return
    try {
      await fetch(`${API}/skills/${encodeURIComponent(name)}`, { method: 'DELETE' })
      setSelectedSkill(null)
      setSkillDetail(null)
      await loadData()
    } catch { }
  }

  const catColor = (code: string) => CATEGORY_COLORS[code] || '#8c8c8c'

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
          <span style={{ fontSize: 16, fontWeight: 600 }}>🧠 知识图谱</span>
          <span style={{ fontSize: 13, opacity: 0.7 }}>{skills.length} 个技能</span>
        </div>
        <button onClick={openCreateForm} style={{
          background: '#52c41a', color: '#fff', border: 'none',
          padding: '8px 20px', borderRadius: 8, cursor: 'pointer', fontSize: 13, fontWeight: 600,
        }}>+ 新增技能</button>
      </header>

      <div style={{ maxWidth: 1400, margin: '0 auto', padding: 24, display: 'flex', gap: 24 }}>
        {/* 左侧：分类 + 列表 */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* 搜索和分类筛选 */}
          <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
            <input value={search} onChange={e => setSearch(e.target.value)}
              placeholder="搜索技能名称或关键词..."
              style={{
                flex: 1, padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9',
                fontSize: 13, outline: 'none',
              }} />
            <select value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)}
              style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 13, minWidth: 120 }}>
              <option value="">全部分类</option>
              {categories.map(c => (
                <option key={c.code} value={c.code}>
                  {'■'} {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* 分类统计 */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
            {categories.map(c => {
              const count = relations.filter(r => r.source !== r.target && r.type === 'BELONGS_TO' && r.target === c.code).length
              return (
                <div key={c.code} onClick={() => setSelectedCategory(selectedCategory === c.code ? '' : c.code)}
                  style={{
                    padding: '4px 12px', borderRadius: 12, fontSize: 12, cursor: 'pointer',
                    background: selectedCategory === c.code ? catColor(c.code) : '#fff',
                    color: selectedCategory === c.code ? '#fff' : catColor(c.code),
                    border: `1px solid ${catColor(c.code)}`,
                    transition: 'all 0.2s',
                  }}>
                  {c.name} ({count})
                </div>
              )
            })}
          </div>

          {/* 技能列表 */}
          {loading ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>加载中...</div>
          ) : (
            <div style={{ display: 'grid', gap: 8 }}>
              {filteredSkills.map(s => {
                const cat = getSkillCategory(s.name)
                const color = catColor(cat)
                return (
                  <div key={s.name} onClick={() => { setSelectedSkill(s); loadSkillDetail(s.name) }}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 12,
                      padding: '10px 16px', background: '#fff', borderRadius: 10,
                      border: `1px solid ${selectedSkill?.name === s.name ? color : '#e8e8e8'}`,
                      borderLeft: `3px solid ${color}`,
                      cursor: 'pointer', transition: 'all 0.2s',
                    }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 14, fontWeight: 600, color: '#1a1a2e' }}>{s.name}</div>
                      <div style={{ fontSize: 11, color: '#999' }}>
                        {getLevelStars(s.level)} {CATEGORY_NAMES[cat] || cat}
                      </div>
                    </div>
                    {s.description && (
                      <div style={{ fontSize: 12, color: '#666', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {s.description}
                      </div>
                    )}
                    <div style={{ fontSize: 11, color: '#bbb' }}>
                      {s.keywords?.slice(0, 2).join(', ')}
                    </div>
                  </div>
                )
              })}
              {filteredSkills.length === 0 && (
                <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>无匹配技能</div>
              )}
            </div>
          )}
        </div>

        {/* 右侧：详情面板 */}
        <div style={{ width: 380, flexShrink: 0 }}>
          {!selectedSkill ? (
            <div style={{ background: '#fff', borderRadius: 12, padding: 40, textAlign: 'center', color: '#ccc' }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>🔍</div>
              <div style={{ fontSize: 14 }}>点击左侧技能查看详情</div>
            </div>
          ) : detailLoading ? (
            <div style={{ background: '#fff', borderRadius: 12, padding: 40, textAlign: 'center', color: '#999' }}>加载中...</div>
          ) : skillDetail ? (
            <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h3 style={{ margin: 0, fontSize: 16, color: '#1a1a2e' }}>{skillDetail.name}</h3>
                <div style={{ display: 'flex', gap: 6 }}>
                  <button onClick={() => openEditForm(selectedSkill)} style={{
                    background: '#1890ff', color: '#fff', border: 'none',
                    padding: '4px 12px', borderRadius: 6, cursor: 'pointer', fontSize: 12,
                  }}>编辑</button>
                  <button onClick={() => handleDelete(skillDetail.name)} style={{
                    background: '#ff4d4f', color: '#fff', border: 'none',
                    padding: '4px 12px', borderRadius: 6, cursor: 'pointer', fontSize: 12,
                  }}>删除</button>
                </div>
              </div>

              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 12, color: '#999', marginBottom: 2 }}>等级</div>
                <div style={{ fontSize: 14 }}>{getLevelStars(skillDetail.level)} Lv.{skillDetail.level}</div>
              </div>

              {skillDetail.description && (
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: 12, color: '#999', marginBottom: 2 }}>描述</div>
                  <div style={{ fontSize: 13, color: '#666', lineHeight: 1.6 }}>{skillDetail.description}</div>
                </div>
              )}

              {skillDetail.keywords && skillDetail.keywords.length > 0 && (
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>关键词</div>
                  <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                    {skillDetail.keywords.map((k: string) => (
                      <span key={k} style={{ background: '#f0f0f0', color: '#666', padding: '1px 8px', borderRadius: 8, fontSize: 11 }}>{k}</span>
                    ))}
                  </div>
                </div>
              )}

              {skillDetail.category && (
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: 12, color: '#999', marginBottom: 2 }}>分类</div>
                  <div style={{ fontSize: 13, color: catColor(skillDetail.category.code), fontWeight: 600 }}>
                    {skillDetail.category.name}
                  </div>
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
                <div style={{ background: '#fafafa', borderRadius: 8, padding: 10 }}>
                  <div style={{ fontSize: 11, color: '#999', marginBottom: 4 }}>前置技能</div>
                  {skillDetail.prerequisites?.length > 0 ? (
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {skillDetail.prerequisites.map((p: string) => (
                        <span key={p} style={{ background: '#e6f7ff', color: '#1890ff', padding: '1px 8px', borderRadius: 8, fontSize: 11 }}>{p}</span>
                      ))}
                    </div>
                  ) : (
                    <div style={{ fontSize: 12, color: '#ccc' }}>无</div>
                  )}
                </div>
                <div style={{ background: '#fafafa', borderRadius: 8, padding: 10 }}>
                  <div style={{ fontSize: 11, color: '#999', marginBottom: 4 }}>后继技能</div>
                  {skillDetail.advanced?.length > 0 ? (
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {skillDetail.advanced.map((a: string) => (
                        <span key={a} style={{ background: '#fff7e6', color: '#fa8c16', padding: '1px 8px', borderRadius: 8, fontSize: 11 }}>{a}</span>
                      ))}
                    </div>
                  ) : (
                    <div style={{ fontSize: 12, color: '#ccc' }}>无</div>
                  )}
                </div>
              </div>

              {skillDetail.related?.length > 0 && (
                <div>
                  <div style={{ fontSize: 12, color: '#999', marginBottom: 4 }}>相关技能</div>
                  <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                    {skillDetail.related.map((r: string) => (
                      <span key={r} style={{ background: '#f6ffed', color: '#52c41a', padding: '1px 8px', borderRadius: 8, fontSize: 11 }}>{r}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>

      {/* 新增/编辑弹窗 */}
      {showForm && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000,
        }} onClick={() => setShowForm(false)}>
          <div style={{
            background: '#fff', borderRadius: 12, padding: 24, width: 500,
            boxShadow: '0 8px 32px rgba(0,0,0,0.2)', maxHeight: '90vh', overflow: 'auto',
          }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h3 style={{ margin: 0, fontSize: 16, color: '#1a1a2e' }}>
                {skills.find(s => s.name === formData.name) ? '✏️ 编辑技能' : '➕ 新增技能'}
              </h3>
              <button onClick={() => setShowForm(false)} style={{
                background: 'transparent', border: 'none', fontSize: 20, cursor: 'pointer', color: '#999'
              }}>✕</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div>
                <label style={{ fontSize: 12, color: '#666', marginBottom: 4, display: 'block' }}>技能名称 *</label>
                <input value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })}
                  placeholder="例如：Rust"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14, boxSizing: 'border-box' }} />
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#666', marginBottom: 4, display: 'block' }}>等级</label>
                <select value={formData.level} onChange={e => setFormData({ ...formData, level: Number(e.target.value) })}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14 }}>
                  {[1, 2, 3, 4, 5].map(l => <option key={l} value={l}>Lv.{l} {'⭐'.repeat(l)}</option>)}
                </select>
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#666', marginBottom: 4, display: 'block' }}>描述</label>
                <textarea value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })}
                  placeholder="技能描述"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 13, minHeight: 60, boxSizing: 'border-box', resize: 'vertical' }} />
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#666', marginBottom: 4, display: 'block' }}>关键词（逗号分隔）</label>
                <input value={formData.keywords} onChange={e => setFormData({ ...formData, keywords: e.target.value })}
                  placeholder="例如：系统编程, 内存安全, 高性能"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14, boxSizing: 'border-box' }} />
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#666', marginBottom: 4, display: 'block' }}>分类</label>
                <select value={formData.category_code} onChange={e => setFormData({ ...formData, category_code: e.target.value })}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14 }}>
                  {categories.map(c => (
                    <option key={c.code} value={c.code}>{c.name} ({c.code})</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#666', marginBottom: 4, display: 'block' }}>前置技能（逗号分隔，学习本技能前需掌握）</label>
                <input value={formData.requires} onChange={e => setFormData({ ...formData, requires: e.target.value })}
                  placeholder="例如：Java, Spring Framework"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14, boxSizing: 'border-box' }} />
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#666', marginBottom: 4, display: 'block' }}>相关技能（逗号分隔）</label>
                <input value={formData.related_to} onChange={e => setFormData({ ...formData, related_to: e.target.value })}
                  placeholder="例如：RAG, LangChain"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid #d9d9d9', fontSize: 14, boxSizing: 'border-box' }} />
              </div>
            </div>

            {formError && <div style={{ color: '#ff4d4f', fontSize: 13, marginTop: 8 }}>{formError}</div>}

            <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
              <button onClick={() => setShowForm(false)} style={{
                flex: 1, background: '#fff', border: '1px solid #d9d9d9', color: '#666',
                padding: '10px', borderRadius: 8, cursor: 'pointer', fontSize: 14,
              }}>取消</button>
              <button onClick={handleSave} disabled={saving} style={{
                flex: 1, background: '#52c41a', color: '#fff', border: 'none',
                padding: '10px', borderRadius: 8, cursor: saving ? 'not-allowed' : 'pointer',
                fontSize: 14, fontWeight: 600, opacity: saving ? 0.6 : 1,
              }}>{saving ? '保存中...' : '保存'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
