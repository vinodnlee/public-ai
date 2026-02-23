import { getAuthHeaders } from './authApi'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export interface SkillMeta {
  id: string
  name: string
  description: string
  target: string
}

export interface AgentConfig {
  enabled_skills: string[]
  skill_dirs: string[]
  mcp_servers: string[]
  available_skills: SkillMeta[]
}

export interface AgentConfigUpdateRequest {
  enabled_skills?: string[]
  skill_dirs?: string[]
  mcp_servers?: string[]
}

export async function getAgentConfig(): Promise<AgentConfig> {
  const res = await fetch(`${API_BASE}/api/agent-config`, {
    headers: getAuthHeaders(),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Load agent config failed: ${res.status} ${text}`)
  }
  return res.json()
}

export async function updateAgentConfig(
  payload: AgentConfigUpdateRequest
): Promise<AgentConfig> {
  const res = await fetch(`${API_BASE}/api/agent-config`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Update agent config failed: ${res.status} ${text}`)
  }
  return res.json()
}
